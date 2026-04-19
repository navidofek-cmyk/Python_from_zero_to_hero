# Lekce 115 — Kubernetes pro Pythonistu

Kubernetes (K8s) je de facto standard pro orchestraci kontejnerů. Python vývojář nepotřebuje být K8s administrátor, ale měl by rozumět klíčovým konceptům a správně psát aplikace pro K8s prostředí.

---

## Klíčové koncepty

```
Cluster = skupina uzlů (nodes — fyzické nebo virtuální stroje)
Node    = jeden stroj v clusteru
Pod     = nejmenší deployovatelná jednotka — 1+ kontejnerů
Service = stabilní síťová identita pro skupinu podů
Deployment = deklarativní správa sady podů
Namespace = logická izolace zdrojů v clusteru
ConfigMap = nekritická konfigurace jako K8s objekt
Secret    = citlivá konfigurace (base64 kódovaná)
Ingress   = HTTP/HTTPS routing z internetu do Services
```

---

## 1. Základní Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-app
  namespace: production
  labels:
    app: python-app
    version: "1.5.3"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: python-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1       # Vždy alespoň 2 repliky dostupné
      maxSurge: 1             # Maximálně 4 pody najednou
  template:
    metadata:
      labels:
        app: python-app
        version: "1.5.3"
    spec:
      # Graceful shutdown — viz lekce 112
      terminationGracePeriodSeconds: 30

      containers:
        - name: app
          image: registry.example.com/python-app:1.5.3
          ports:
            - containerPort: 8000

          # Konfigurace Z prostředí (12-factor)
          env:
            - name: APP_ENV
              value: "production"
            - name: PORT
              value: "8000"
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: secret-key
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: database-url

          # Limity zdrojů — VŽDY nastavit!
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"

          # Probes — klíčové pro spolehlivý provoz
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3

          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
            successThreshold: 1

          startupProbe:
            httpGet:
              path: /health
              port: 8000
            failureThreshold: 30   # 30 * 10s = 5 minut na start
            periodSeconds: 10

          # Bezpečnostní kontext
          securityContext:
            runAsNonRoot: true
            runAsUser: 1001
            readOnlyRootFilesystem: true
            allowPrivilegeEscalation: false
```

---

## 2. Service a Ingress

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: python-app
  namespace: production
spec:
  selector:
    app: python-app
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP    # Interní přístup v clusteru

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: python-app
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: api-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: python-app
                port:
                  number: 80
```

---

## 3. ConfigMap a Secret

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  APP_NAME: "PythonApp"
  LOG_LEVEL: "INFO"
  MAX_WORKERS: "4"

---
# k8s/secret.yaml
# Pozor: hodnoty jsou base64 kódované (NE šifrované!)
# V produkci použijte: kubectl create secret generic app-secrets \
#   --from-literal=secret-key=$(openssl rand -base64 32) \
#   --from-literal=database-url="postgresql://..."
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
data:
  secret-key: c3VwZXItc2VjcmV0LWtleQ==    # base64
  database-url: cG9zdGdyZXNxbDovLy4uLg==  # base64
```

---

## 4. Graceful shutdown v Pythonu

Kubernetes posílá `SIGTERM` při vypínání podu. Aplikace musí dokončit aktivní požadavky a teprve pak skončit.

```python
import signal
import sys
import threading
import time


class GracefulShutdown:
    """Správce graceful shutdown pro K8s produkci."""

    def __init__(self, grace_period: int = 25) -> None:
        self._shutdown = threading.Event()
        self._grace_period = grace_period
        self._active_requests = 0
        self._lock = threading.Lock()

        signal.signal(signal.SIGTERM, self._handle_sigterm)
        signal.signal(signal.SIGINT, self._handle_sigterm)

    def _handle_sigterm(self, signum: int, frame: object) -> None:
        print(f"Přijat {signal.Signals(signum).name} — zahajuji graceful shutdown")
        self._shutdown.set()
        self._wait_for_requests()
        sys.exit(0)

    def _wait_for_requests(self) -> None:
        """Čeká na dokončení aktivních požadavků (max grace_period sekund)."""
        deadline = time.time() + self._grace_period
        while time.time() < deadline:
            with self._lock:
                if self._active_requests == 0:
                    break
            print(f"  Čekám na {self._active_requests} aktivní požadavky...")
            time.sleep(1)

    @property
    def is_shutting_down(self) -> bool:
        return self._shutdown.is_set()

    def track_request(self):
        """Context manager pro sledování počtu aktivních požadavků."""
        import contextlib

        @contextlib.contextmanager
        def _tracker():
            with self._lock:
                self._active_requests += 1
            try:
                yield
            finally:
                with self._lock:
                    self._active_requests -= 1

        return _tracker()
```

---

## 5. Health a Readiness probes v Pythonu

```python
import time
import threading

_START_TIME = time.time()
_ready = threading.Event()
_shutting_down = threading.Event()


def liveness() -> tuple[int, dict]:
    """
    Liveness probe — zjišťuje zda aplikace ŽIJE.
    Pokud vrátí 5xx, K8s pod restartuje.
    Kontroluj pouze fatální stav (deadlock, corrupt state).
    """
    if _shutting_down.is_set():
        return 503, {"status": "shutting_down"}
    return 200, {"status": "alive", "uptime": time.time() - _START_TIME}


def readiness() -> tuple[int, dict]:
    """
    Readiness probe — zjišťuje zda může pod PŘIJÍMAT PROVOZ.
    Pokud vrátí 5xx, K8s odebere pod ze Service (žádné nové požadavky).
    Kontroluj: DB spojení, cache dostupnost, warmup dokončen.
    """
    if not _ready.is_set():
        return 503, {"status": "not_ready", "reason": "initialization"}
    if _shutting_down.is_set():
        return 503, {"status": "not_ready", "reason": "shutting_down"}
    # Zde by byla kontrola DB, cache...
    return 200, {"status": "ready"}
```

---

## 6. Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: python-app
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: python-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## 7. PodDisruptionBudget — HA při aktualizacích

```yaml
# k8s/pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: python-app
  namespace: production
spec:
  minAvailable: 2    # Vždy alespoň 2 pody dostupné
  selector:
    matchLabels:
      app: python-app
```

---

## 8. Užitečné kubectl příkazy pro Python vývojáře

```bash
# Zobrazení logů
kubectl logs -f deployment/python-app -n production
kubectl logs -f deployment/python-app -n production --previous  # crash logs

# Exec do podu (debug)
kubectl exec -it deployment/python-app -n production -- /bin/sh

# Proměnné prostředí v podu
kubectl exec deployment/python-app -n production -- env | sort

# Aktualizace image (rolling update)
kubectl set image deployment/python-app app=registry.example.com/python-app:1.5.4

# Rollback
kubectl rollout undo deployment/python-app -n production

# Stav rollout
kubectl rollout status deployment/python-app -n production

# Port-forward pro debug
kubectl port-forward deployment/python-app 8080:8000 -n production
```

---

## Shrnutí

| Koncept | Python relevance |
|---------|-----------------|
| Liveness probe | `/health` — aplikace žije? |
| Readiness probe | `/ready` — může přijímat provoz? |
| Startup probe | Pomalý start (ML model loading) |
| SIGTERM handler | Graceful shutdown — dokončit požadavky |
| Resources limits | `requests`/`limits` CPU+memory |
| Secret | `valueFrom.secretKeyRef` → `os.environ` |
| Rolling update | Zero-downtime deploy |

---

## Cvičení

1. Implementujte kompletní `GracefulShutdown` třídu s context managerem `track_request()` a ověřte ji unit testem — simulujte SIGTERM uprostřed zpracování požadavku.
2. Rozšiřte `/health` endpoint o kontrolu dostupnosti všech backing services (DB, Redis, S3) s timeoutem 2 sekund pro každou kontrolu.
3. Napište Python skript, který pomocí `kubernetes` klientské knihovny (nebo `subprocess` + `kubectl`) monitoruje stav podů v namespace a posílá alert při pod restart count > 3.
4. Vytvořte Helm chart šablonu pro Python FastAPI aplikaci s parametrizovatelným počtem replik, resource limity a automaticky generovaným Secret.
