# Program — Lekce 107: Lekce 107: Idempotence, retry, timeouty, circuit breaker

Patří k lekci [Lekce 107: Idempotence, retry, timeouty, circuit breaker](../107_retry_circuit_breaker.md).

## Jak spustit

```bash
python3 programy/l107_retry_circuit_breaker.py
```

## Zdrojový kód

### `l107_retry_circuit_breaker.py`

```py
"""Lekce 107 — Idempotence, retry, timeouty, circuit breaker."""

from __future__ import annotations

import functools
import random
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TypeVar

# Poznámka: v produkci doporučujeme knihovnu 'tenacity':
#   pip install tenacity
#   from tenacity import retry, stop_after_attempt, wait_exponential

T = TypeVar("T")


# ── Retry s exponential backoff ───────────────────────────────────────────────

def retry_s_backoff(
    fn: Callable[[], T],
    max_pokusy: int = 3,
    zakladni_zpozdeni: float = 0.1,   # 0.1s pro demo (prod: 1.0)
    nasobitel: float = 2.0,
    max_zpozdeni: float = 5.0,
    jitter: bool = True,
) -> T:
    """Provede funkci s exponential backoff retry logikou."""
    posledni_vyjimka: Exception | None = None

    for pokus in range(1, max_pokusy + 1):
        try:
            return fn()
        except Exception as exc:
            posledni_vyjimka = exc
            if pokus == max_pokusy:
                raise

            zpozdeni = min(zakladni_zpozdeni * (nasobitel ** (pokus - 1)), max_zpozdeni)
            if jitter:
                zpozdeni += random.uniform(0, zpozdeni * 0.2)

            print(f"  [retry] Pokus {pokus}/{max_pokusy} selhal: {exc}. "
                  f"Čekám {zpozdeni:.3f}s...")
            time.sleep(zpozdeni)

    assert posledni_vyjimka is not None
    raise posledni_vyjimka


# ── Dekorátor @retry ──────────────────────────────────────────────────────────

def retry(
    max_pokusy: int = 3,
    vyjimky: tuple[type[Exception], ...] = (Exception,),
    zakladni_zpozdeni: float = 0.1,
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Dekorátor pro automatický retry.

    Příklad s tenacity (prod):
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
        def volej_api(): ...
    """
    def dekorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: object, **kwargs: object) -> T:
            for pokus in range(1, max_pokusy + 1):
                try:
                    return fn(*args, **kwargs)
                except vyjimky as exc:
                    if pokus == max_pokusy:
                        raise
                    if on_retry:
                        on_retry(pokus, exc)
                    zpozdeni = zakladni_zpozdeni * (2 ** (pokus - 1))
                    time.sleep(zpozdeni)
            raise RuntimeError("Nedosažitelné")  # mypy appeasement
        return wrapper
    return dekorator


# ── Circuit Breaker ───────────────────────────────────────────────────────────

class StavCB(Enum):
    CLOSED = auto()       # Normální provoz — volání prochází
    OPEN = auto()         # Vypnut — volání okamžitě odmítnuta
    HALF_OPEN = auto()    # Zkušební — jedno testovací volání


class CircuitBreakerOtevren(Exception):
    pass


class CircuitBreaker:
    """
    Implementace Circuit Breaker patternu.

    Stavy: CLOSED → (N selhání) → OPEN → (timeout) → HALF_OPEN → CLOSED
    """

    def __init__(
        self,
        prah_selhani: int = 3,
        timeout_obnovy: float = 5.0,
        nazev: str = "CB",
    ) -> None:
        self.nazev = nazev
        self.stav = StavCB.CLOSED
        self._prah = prah_selhani
        self._timeout = timeout_obnovy
        self._pocet_selhani = 0
        self._pocet_uspechu = 0
        self._otevreno_v: datetime | None = None

    def __call__(self, fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: object, **kwargs: object) -> T:
            self._zkontroluj_prechod()
            if self.stav == StavCB.OPEN:
                raise CircuitBreakerOtevren(
                    f"[{self.nazev}] Circuit Breaker je OPEN — volání odmítnuto"
                )
            try:
                vysledek = fn(*args, **kwargs)
                self._pri_uspechu()
                return vysledek
            except CircuitBreakerOtevren:
                raise
            except Exception:
                self._pri_selhani()
                raise
        return wrapper

    def _zkontroluj_prechod(self) -> None:
        if self.stav == StavCB.OPEN and self._otevreno_v is not None:
            uplynulo = (datetime.now() - self._otevreno_v).total_seconds()
            if uplynulo >= self._timeout:
                print(f"  [{self.nazev}] Timeout vypršel → přechod do HALF_OPEN")
                self.stav = StavCB.HALF_OPEN

    def _pri_uspechu(self) -> None:
        self._pocet_uspechu += 1
        if self.stav == StavCB.HALF_OPEN:
            print(f"  [{self.nazev}] Testovací volání úspěšné → přechod do CLOSED")
        self._pocet_selhani = 0
        self.stav = StavCB.CLOSED

    def _pri_selhani(self) -> None:
        self._pocet_selhani += 1
        if self.stav == StavCB.HALF_OPEN:
            print(f"  [{self.nazev}] Testovací volání selhalo → zpět do OPEN")
            self._otevreno_v = datetime.now()
            self.stav = StavCB.OPEN
        elif self._pocet_selhani >= self._prah:
            print(f"  [{self.nazev}] Dosažen práh {self._prah} selhání → přechod do OPEN")
            self.stav = StavCB.OPEN
            self._otevreno_v = datetime.now()

    def statistiky(self) -> dict[str, object]:
        return {
            "stav": self.stav.name,
            "pocet_selhani": self._pocet_selhani,
            "pocet_uspechu": self._pocet_uspechu,
            "otevreno_v": self._otevreno_v.isoformat() if self._otevreno_v else None,
        }


# ── Idempotentní handler ──────────────────────────────────────────────────────

class IdempotentniHandler:
    """
    Zpracuje požadavek pouze jednou — při opakování vrátí uložený výsledek.
    Používá se např. pro platby: Idempotency-Key: <uuid> v HTTP hlavičce.
    """

    def __init__(self) -> None:
        self._zpracovane: dict[str, object] = {}
        self._pocitadlo = 0

    def zpracuj(self, idempotency_key: str, castka: float) -> dict[str, object]:
        if idempotency_key in self._zpracovane:
            print(f"  [idempotence] Duplikát klíče {idempotency_key[:8]}... → vracím uložený výsledek")
            return {"status": "duplicate", **self._zpracovane[idempotency_key]}  # type: ignore[return-value]

        self._pocitadlo += 1
        vysledek: dict[str, object] = {
            "platba_id": self._pocitadlo,
            "castka": castka,
            "cas": datetime.now().isoformat(),
        }
        self._zpracovane[idempotency_key] = vysledek
        return {"status": "created", **vysledek}


# ── Simulace nespolehlivé služby ──────────────────────────────────────────────

class SlabaSit:
    """Simuluje nestabilní síťové připojení."""

    def __init__(self, pravdepodobnost_uspechu: float = 0.4) -> None:
        self._p = pravdepodobnost_uspechu
        self._volani = 0

    def volej(self, url: str) -> str:
        self._volani += 1
        if random.random() > self._p:
            raise ConnectionError(f"Timeout při připojení na {url} (volání #{self._volani})")
        return f"Data z {url} (volání #{self._volani})"


# ── Demo ──────────────────────────────────────────────────────────────────────

def main() -> None:
    random.seed(42)   # reprodukovatelnost výstupu

    print("=== Retry + Circuit Breaker demo ===\n")

    # --- Retry s backoff ---
    print("--- Retry s exponential backoff ---")
    sit = SlabaSit(pravdepodobnost_uspechu=0.3)

    try:
        vysledek = retry_s_backoff(
            fn=lambda: sit.volej("https://api.example.com/data"),
            max_pokusy=4,
            zakladni_zpozdeni=0.05,
        )
        print(f"  Úspěch: {vysledek}")
    except ConnectionError as exc:
        print(f"  Všechny pokusy selhaly: {exc}")

    # --- Dekorátor @retry ---
    print("\n--- Dekorátor @retry ---")
    sit2 = SlabaSit(pravdepodobnost_uspechu=0.5)

    def log_retry(pokus: int, exc: Exception) -> None:
        print(f"  [on_retry] Pokus {pokus} → {exc}")

    @retry(
        max_pokusy=3,
        vyjimky=(ConnectionError,),
        zakladni_zpozdeni=0.05,
        on_retry=log_retry,
    )
    def nacti_uzivatel(user_id: int) -> str:
        return sit2.volej(f"https://api.example.com/users/{user_id}")

    try:
        data = nacti_uzivatel(42)
        print(f"  Výsledek: {data}")
    except ConnectionError as exc:
        print(f"  Nepodařilo se: {exc}")

    # --- Circuit Breaker ---
    print("\n--- Circuit Breaker ---")
    cb = CircuitBreaker(prah_selhani=2, timeout_obnovy=0.2, nazev="API-CB")
    nestabilni_sit = SlabaSit(pravdepodobnost_uspechu=0.1)  # 90% selhání

    @cb
    def volej_nestabilni(url: str) -> str:
        return nestabilni_sit.volej(url)

    for i in range(7):
        try:
            vysledek = volej_nestabilni("https://nestabilni.example.com")
            print(f"  Volání {i+1}: OK → {vysledek}")
        except CircuitBreakerOtevren as exc:
            print(f"  Volání {i+1}: ODMÍTNUTO → {exc}")
        except ConnectionError as exc:
            print(f"  Volání {i+1}: CHYBA SÍŤ → {exc}")

    print(f"\n  Statistiky CB: {cb.statistiky()}")

    # Simulace recovery — po timeout se CB přepne do HALF_OPEN
    print(f"\n  Čekám na recovery timeout ({cb._timeout}s)...")
    time.sleep(cb._timeout + 0.05)

    # Teď se CB přepne do HALF_OPEN a zkusí jedno volání
    stabilni_sit = SlabaSit(pravdepodobnost_uspechu=1.0)

    @cb
    def volej_stabilni(url: str) -> str:
        return stabilni_sit.volej(url)

    try:
        print(f"  Testovací volání (HALF_OPEN)...")
        # Pozn: musíme použít wrapper přímo na novém objektu
        # Pro demo zavoláme _zkontroluj_prechod a pak přímé volání
        cb._zkontroluj_prechod()
        print(f"  Stav CB po timeout: {cb.stav.name}")
    except Exception as exc:
        print(f"  Chyba: {exc}")

    # --- Idempotence ---
    print("\n--- Idempotence: platby s Idempotency-Key ---")
    handler = IdempotentniHandler()
    klic = "550e8400-e29b-41d4-a716-446655440000"

    for i in range(3):
        vysledek = handler.zpracuj(klic, castka=299.0)
        print(f"  Pokus {i+1}: status={vysledek['status']}, platba_id={vysledek['platba_id']}")

    # Jiný klíč = nová platba
    jiny_klic = "660e8400-e29b-41d4-a716-446655440001"
    vysledek2 = handler.zpracuj(jiny_klic, castka=150.0)
    print(f"  Nový klíč:  status={vysledek2['status']}, platba_id={vysledek2['platba_id']}")

    print("\n--- Shrnutí technik ---")
    techniky = [
        ("Retry + backoff",    "Přechodné chyby sítě"),
        ("Circuit Breaker",    "Kaskádové selhání závislostí"),
        ("Idempotence key",    "Duplikátní požadavky (platby, e-maily)"),
        ("Timeout",            "Každé I/O (httpx(timeout=5), asyncio.wait_for)"),
    ]
    for technika, usecase in techniky:
        print(f"  {technika:22s} → {usecase}")


if __name__ == "__main__":
    main()

```
