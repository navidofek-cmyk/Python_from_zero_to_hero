# Lekce 155: Reinforcement Learning

Agent se učí jednat v prostředí — maximalizuje dlouhodobou odměnu. Základ pro herní AI, robotiku, optimalizaci.

---

## 🎮 Základní pojmy

```
Agent      → provádí akce
Prostředí  → reaguje, vrací stav + odměnu
Stav (s)   → co agent vidí
Akce (a)   → co agent dělá
Odměna (r) → zpětná vazba
Policy π   → strategie — jakou akci zvolit v daném stavu
Value V(s) → očekávaná celková odměna ze stavu s
Q(s,a)     → hodnota akce a ve stavu s

Bellmanová rovnice:
  Q(s,a) = r + γ · max_a' Q(s', a')
  γ ∈ [0,1] = discount factor (jak moc záleží na budoucnosti)
```

---

## 🌍 Vlastní prostředí — GridWorld

```python
import numpy as np
import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class GridWorld:
    """
    Mřížkové prostředí N×N.
    Agent začíná v [0,0], cíl je v [N-1,N-1].
    Některá pole jsou pasti (-1), cíl dá +10, pohyb -0.1.
    """
    n: int = 5
    pasti: tuple = ((1,1),(2,3),(3,1))

    def reset(self) -> tuple[int,int]:
        self.agent = (0, 0)
        return self.agent

    def krok(self, akce: int) -> tuple[tuple, float, bool]:
        """akce: 0=↑, 1=↓, 2=←, 3=→"""
        r, s = self.agent
        dr, ds = [(-1,0),(1,0),(0,-1),(0,1)][akce]
        nr = max(0, min(self.n-1, r+dr))
        ns = max(0, min(self.n-1, s+ds))
        self.agent = (nr, ns)

        if self.agent == (self.n-1, self.n-1):
            return self.agent, 10.0, True
        if self.agent in self.pasti:
            return self.agent, -5.0, True
        return self.agent, -0.1, False

    def stav_idx(self, stav: tuple) -> int:
        return stav[0] * self.n + stav[1]

    @property
    def n_stavu(self): return self.n * self.n
    @property
    def n_akci(self): return 4
```

---

## 📊 Q-Learning

```python
class QLearning:
    """Tabulkový Q-learning pro diskrétní prostředí."""

    def __init__(self, n_stavu: int, n_akci: int,
                 lr: float = 0.1, gamma: float = 0.95,
                 epsilon: float = 1.0, epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01):
        self.Q = np.zeros((n_stavu, n_akci))
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

    def vyber_akci(self, stav_idx: int) -> int:
        """ε-greedy policy."""
        if random.random() < self.epsilon:
            return random.randint(0, self.Q.shape[1]-1)
        return int(np.argmax(self.Q[stav_idx]))

    def aktualizuj(self, s: int, a: int, r: float, s_next: int, hotovo: bool):
        """Bellmanová aktualizace."""
        target = r if hotovo else r + self.gamma * np.max(self.Q[s_next])
        self.Q[s, a] += self.lr * (target - self.Q[s, a])

    def krok_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


def trenuj_q_learning(epochy: int = 2000) -> tuple[QLearning, list[float]]:
    env = GridWorld()
    agent = QLearning(env.n_stavu, env.n_akci)
    odmeny = []

    for ep in range(epochy):
        stav = env.reset()
        celkova_odmena = 0.0
        for _ in range(100):
            si = env.stav_idx(stav)
            akce = agent.vyber_akci(si)
            dalsi_stav, odmena, hotovo = env.krok(akce)
            agent.aktualizuj(si, akce, odmena, env.stav_idx(dalsi_stav), hotovo)
            celkova_odmena += odmena
            stav = dalsi_stav
            if hotovo:
                break
        agent.krok_epsilon()
        odmeny.append(celkova_odmena)

    return agent, odmeny


agent, odmeny = trenuj_q_learning()
print("Q-Learning GridWorld:")
print(f"  Průměrná odměna (posledních 200 epizod): {np.mean(odmeny[-200:]):.2f}")
print(f"  Epsilon: {agent.epsilon:.4f}")
```

---

## 🧠 Deep Q-Network (DQN)

```python
try:
    import torch
    import torch.nn as nn

    class DQN(nn.Module):
        def __init__(self, n_stavu: int, n_akci: int, skryte: int = 64):
            super().__init__()
            self.sit = nn.Sequential(
                nn.Linear(n_stavu, skryte), nn.ReLU(),
                nn.Linear(skryte, skryte), nn.ReLU(),
                nn.Linear(skryte, n_akci)
            )
        def forward(self, x): return self.sit(x)

    from collections import deque

    class ReplayBuffer:
        """Experience replay — přerušuje korelaci po sobě jdoucích přechodů."""
        def __init__(self, kapacita: int = 10000):
            self.buffer = deque(maxlen=kapacita)

        def uloz(self, s, a, r, s2, hotovo):
            self.buffer.append((s, a, r, s2, hotovo))

        def vzorek(self, batch_size: int):
            batch = random.sample(self.buffer, batch_size)
            s, a, r, s2, d = zip(*batch)
            return (
                torch.FloatTensor(s),
                torch.LongTensor(a),
                torch.FloatTensor(r),
                torch.FloatTensor(s2),
                torch.BoolTensor(d),
            )

        def __len__(self): return len(self.buffer)

    class DQNAgent:
        def __init__(self, n_stavu, n_akci, lr=1e-3, gamma=0.95,
                     epsilon=1.0, epsilon_decay=0.997, epsilon_min=0.01):
            self.n_akci = n_akci
            self.gamma = gamma
            self.epsilon = epsilon
            self.epsilon_decay = epsilon_decay
            self.epsilon_min = epsilon_min
            self.sit = DQN(n_stavu, n_akci)
            self.sit_cil = DQN(n_stavu, n_akci)  # target network
            self.sit_cil.load_state_dict(self.sit.state_dict())
            self.opt = torch.optim.Adam(self.sit.parameters(), lr=lr)
            self.buffer = ReplayBuffer()
            self.krok_cnt = 0

        def vyber_akci(self, stav: np.ndarray) -> int:
            if random.random() < self.epsilon:
                return random.randint(0, self.n_akci-1)
            with torch.no_grad():
                return int(self.sit(torch.FloatTensor(stav)).argmax())

        def uloz(self, *args): self.buffer.uloz(*args)

        def naucit(self, batch_size=64):
            if len(self.buffer) < batch_size: return
            s, a, r, s2, d = self.buffer.vzorek(batch_size)
            q = self.sit(s).gather(1, a.unsqueeze(1)).squeeze()
            with torch.no_grad():
                q_cil = r + self.gamma * self.sit_cil(s2).max(1)[0] * ~d
            loss = nn.MSELoss()(q, q_cil)
            self.opt.zero_grad(); loss.backward(); self.opt.step()
            self.krok_cnt += 1
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            if self.krok_cnt % 100 == 0:
                self.sit_cil.load_state_dict(self.sit.state_dict())

    print("\nDQN definován (PyTorch) — spusť trénink s GridWorld nebo CartPole.")

except ImportError:
    print("\nDQN vyžaduje PyTorch: uv add torch")
```

---

## 🎲 Policy Gradient (REINFORCE)

```python
def reinforce_demo():
    """Jednoduchý REINFORCE na CartPole (konceptuální ukázka)."""
    try:
        import torch, torch.nn as nn
    except ImportError:
        return

    class PolicySit(nn.Module):
        def __init__(self, n_stavu, n_akci):
            super().__init__()
            self.sit = nn.Sequential(
                nn.Linear(n_stavu, 128), nn.ReLU(),
                nn.Linear(128, n_akci), nn.Softmax(dim=-1)
            )
        def forward(self, x): return self.sit(x)

    def trenuj_epizodu(policy, env_reset_fn, env_step_fn, gamma=0.99):
        """Jedna epizoda + výpočet gradientu."""
        log_probs, odmeny = [], []
        stav = env_reset_fn()

        for _ in range(500):
            stav_t = torch.FloatTensor(stav).unsqueeze(0)
            probs = policy(stav_t)
            dist = torch.distributions.Categorical(probs)
            akce = dist.sample()
            log_probs.append(dist.log_prob(akce))

            stav, odmena, hotovo, *_ = env_step_fn(akce.item())
            odmeny.append(odmena)
            if hotovo: break

        # Diskontované odměny
        G, returns = 0, []
        for r in reversed(odmeny):
            G = r + gamma * G
            returns.insert(0, G)
        returns = torch.FloatTensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        # Policy gradient loss
        loss = -sum(lp * G for lp, G in zip(log_probs, returns))
        return loss, sum(odmeny)

    print("\nREINFORCE (Policy Gradient) — konceptuální demo OK")
    print("Pro spuštění: uv add gymnasium torch")
```

---

## 🎯 Srovnání RL algoritmů

| Algoritmus | Typ | Prostředí | Výhody |
|-----------|-----|-----------|--------|
| Q-Learning | off-policy, model-free | diskrétní | jednoduchý, konverguje |
| DQN | off-policy, deep | diskrétní | škáluje na velké stavové prostory |
| REINFORCE | on-policy, policy grad. | spojité/diskrétní | přímá optimalizace policy |
| PPO | on-policy, actor-critic | obojí | stabilní, populární |
| SAC | off-policy, actor-critic | spojité | pro robotiku |
| AlphaZero | model-based, MCTS | hry | superhumánní výkon ve hrách |

---

## ✏️ Cvičení

1. Rozšiř GridWorld na 10×10 s náhodně generovanými pastmi.
2. Implementuj **Double DQN** — dvě sítě zabraňují přeceňování Q hodnot.
3. Trénuj DQN na **CartPole** přes `gymnasium`: `uv add gymnasium`.
4. Implementuj **ε-greedy decay** s exponenciálním vs lineárním poklesem — porovnej konvergenci.
5. Implementuj **Monte Carlo Tree Search** pro hru Tic-Tac-Toe.
