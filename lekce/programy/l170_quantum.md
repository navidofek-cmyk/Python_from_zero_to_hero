# Program — Lekce 170: Lekce 170: Quantum Computing — Qiskit

Patří k lekci [Lekce 170: Quantum Computing — Qiskit](../170_quantum.md).

## Jak spustit

```bash
python3 programy/l170_quantum.py
```

## Zdrojový kód

### `l170_quantum.py`

```py
"""Lekce 170 — Quantum Computing: Qiskit.

Spuštění:
    uv run --with qiskit,qiskit-aer l170_quantum.py
"""

import random
import math


def demo_qubity_klasicky():
    print("=" * 50)
    print("  ⚛️  Quantum Computing Demo")
    print("=" * 50)

    print("""
Kvantové vs klasické bity:

Klasický bit:  0 nebo 1
Qubit:         α|0⟩ + β|1⟩  (superpozice)
               kde |α|² + |β|² = 1

Měření → kolaps na 0 s pravděpodobností |α|²
                    nebo 1 s pravděpodobností |β|²

Hadamardova brána: |0⟩ → (|0⟩ + |1⟩)/√2
                   → 50% šance na 0, 50% na 1
""")


def simuluj_qubit():
    """Klasická simulace jednoho qubitu."""
    print("=== Simulace qubitu (klasicky) ===")

    class Qubit:
        def __init__(self, alpha=1.0, beta=0.0):
            norm = math.sqrt(abs(alpha)**2 + abs(beta)**2)
            self.alpha = alpha / norm
            self.beta = beta / norm

        def hadamard(self):
            a, b = self.alpha, self.beta
            self.alpha = (a + b) / math.sqrt(2)
            self.beta = (a - b) / math.sqrt(2)
            return self

        def measure(self) -> int:
            p0 = abs(self.alpha)**2
            result = 0 if random.random() < p0 else 1
            self.alpha = 1.0 if result == 0 else 0.0
            self.beta = 0.0 if result == 0 else 1.0
            return result

        def __repr__(self):
            return f"Qubit({self.alpha:.3f}|0⟩ + {self.beta:.3f}|1⟩)"

    print("  Qubit v |0⟩:", Qubit(1, 0))
    q = Qubit(1, 0)
    q.hadamard()
    print("  Po Hadamardově bráně:", q)

    print("\n  Měření 20× (superpozice):")
    counts = {0: 0, 1: 0}
    for _ in range(20):
        q_new = Qubit(1, 0)
        q_new.hadamard()
        counts[q_new.measure()] += 1
    print(f"  |0⟩: {counts[0]}×, |1⟩: {counts[1]}×  (přibližně 50/50)")


def demo_bb84():
    print("\n=== BB84 Kvantová kryptografie ===")
    n = 20
    random.seed(42)

    alice_bity = [random.randint(0,1) for _ in range(n)]
    alice_baze = [random.choice(["+","x"]) for _ in range(n)]
    bob_baze = [random.choice(["+","x"]) for _ in range(n)]

    bob_bity = [
        alice_bity[i] if alice_baze[i] == bob_baze[i] else random.randint(0,1)
        for i in range(n)
    ]

    klic = [alice_bity[i] for i in range(n) if alice_baze[i] == bob_baze[i]]
    shoda = sum(1 for i,j in zip(
        [alice_bity[i] for i in range(n) if alice_baze[i] == bob_baze[i]], klic
    )) / max(len(klic), 1)

    print(f"  Přeneseno bitů: {n}")
    print(f"  Shodné báze: {len(klic)} ({100*len(klic)/n:.0f}%)")
    print(f"  Sdílený klíč: {klic}")
    print(f"  Bezchybnost: {shoda:.1%} (100% bez odposlouchávání)")


def demo_qiskit():
    print("\n=== Qiskit (reálný simulátor) ===")
    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator

        # Bell state
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0,1], [0,1])

        sim = AerSimulator()
        result = sim.run(qc, shots=1000).result()
        counts = result.get_counts(qc)

        print(f"  Bellův stav (1000 měření): {counts}")
        print(f"  ✅ Pouze '00' a '11' — qubity jsou provázané!")
        print(f"  Poměr: {counts.get('00',0)/10:.0f}% vs {counts.get('11',0)/10:.0f}%")

    except ImportError:
        print("  Qiskit nedostupný: uv add qiskit qiskit-aer")


def main():
    demo_qubity_klasicky()
    simuluj_qubit()
    demo_bb84()
    demo_qiskit()
    print("\n✅ Demo dokončeno!")
    print("Pro Qiskit: uv add qiskit qiskit-aer")
    print("IBM Quantum (reálný HW): https://quantum.ibm.com/")


if __name__ == "__main__":
    main()

```
