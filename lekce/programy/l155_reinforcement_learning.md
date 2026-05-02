# Program — Lekce 155: Lekce 155: Reinforcement Learning

Patří k lekci [Lekce 155: Reinforcement Learning](../155_reinforcement_learning.md).

## Jak spustit

```bash
python3 programy/l155_reinforcement_learning.py
```

## Zdrojový kód

### `l155_reinforcement_learning.py`

```py
"""Lekce 155 — Reinforcement Learning: Q-Learning na GridWorld.

Spuštění:
    uv run --with numpy l155_reinforcement_learning.py
"""

import numpy as np
import random
import time


class GridWorld:
    def __init__(self, n=5, pasti=((1,1),(2,3),(3,1))):
        self.n = n
        self.pasti = set(pasti)
        self.agent = (0, 0)

    def reset(self):
        self.agent = (0, 0)
        return self.agent

    def krok(self, akce):
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

    def idx(self, stav): return stav[0]*self.n + stav[1]


class QLearning:
    def __init__(self, n_s, n_a, lr=0.1, gamma=0.95, eps=1.0, eps_decay=0.995, eps_min=0.01):
        self.Q = np.zeros((n_s, n_a))
        self.lr, self.gamma = lr, gamma
        self.eps, self.eps_decay, self.eps_min = eps, eps_decay, eps_min

    def akce(self, si):
        if random.random() < self.eps:
            return random.randint(0, self.Q.shape[1]-1)
        return int(np.argmax(self.Q[si]))

    def update(self, s, a, r, s2, done):
        target = r if done else r + self.gamma * np.max(self.Q[s2])
        self.Q[s, a] += self.lr * (target - self.Q[s, a])
        self.eps = max(self.eps_min, self.eps * self.eps_decay)


def main():
    print("=" * 50)
    print("  🎮 Reinforcement Learning — Q-Learning")
    print("=" * 50)

    env = GridWorld()
    agent = QLearning(env.n*env.n, 4)
    random.seed(42)
    np.random.seed(42)

    epochy = 2000
    odmeny = []
    t = time.perf_counter()

    for ep in range(epochy):
        stav = env.reset()
        odmena_celkem = 0.0
        for _ in range(100):
            si = env.idx(stav)
            akce = agent.akce(si)
            dalsi, odmena, done = env.krok(akce)
            agent.update(si, akce, odmena, env.idx(dalsi), done)
            odmena_celkem += odmena
            stav = dalsi
            if done: break
        odmeny.append(odmena_celkem)
        if (ep+1) % 500 == 0:
            prumer = np.mean(odmeny[-200:])
            print(f"  Epocha {ep+1:5d}: prům. odmena={prumer:.2f}, ε={agent.eps:.3f}")

    print(f"\nTrénink dokončen za {(time.perf_counter()-t)*1000:.0f}ms")
    print(f"Finální průměrná odmena: {np.mean(odmeny[-200:]):.2f}")

    # Vizualizuj Q-policy
    print("\nNaučená policy (↑↓←→):")
    simboly = ["↑","↓","←","→"]
    for r in range(env.n):
        radek = ""
        for s in range(env.n):
            if (r,s) == (env.n-1, env.n-1): radek += "G "
            elif (r,s) in env.pasti: radek += "X "
            else: radek += simboly[int(np.argmax(agent.Q[env.idx((r,s))]))] + " "
        print("  " + radek)

    print("\n✅ Demo dokončeno!")


if __name__ == "__main__":
    main()

```
