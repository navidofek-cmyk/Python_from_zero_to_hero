# Lekce 170: Quantum Computing — Qiskit

Quantum computing využívá kvantové jevy (superpozice, provázanost) pro výpočty exponenciálně rychlejší než klasické počítače.

---

## 🚀 Instalace

```bash
uv add qiskit qiskit-aer
```

---

## ⚛️ Základní pojmy

```
Qubit       = kvantový bit — superpozice |0⟩ a |1⟩
|0⟩ a |1⟩  = bázové stavy (Diracova notace)
|ψ⟩ = α|0⟩ + β|1⟩ kde |α|² + |β|² = 1

Hadamardova brána (H): |0⟩ → (|0⟩ + |1⟩)/√2  (superpozice)
CNOT brána: podmíněná negace — provázanost
Měření: kolaps superpozice na 0 nebo 1
```

---

## 🔌 První kvantový obvod

```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.visualization import circuit_drawer


def prvni_obvod():
    """Hadamardova brána — superpozice jednoho qubitu."""
    qc = QuantumCircuit(1, 1)   # 1 qubit, 1 klasický bit
    qc.h(0)                      # Hadamard — uvede do superpozice
    qc.measure(0, 0)             # změř qubit 0 → klasický bit 0

    print("=== Obvod (ASCII) ===")
    print(qc)

    simulator = AerSimulator()
    job = simulator.run(qc, shots=1000)
    vysledky = job.result().get_counts(qc)
    print(f"\nVýsledky (1000 měření): {vysledky}")
    print("→ Přibližně 50% '0' a 50% '1' (superpozice)")
    return vysledky


# zvni_vysledky = prvni_obvod()
print("Spusť: prvni_obvod() pro demo superpozice")
```

---

## 🔗 Bellův stav — provázanost

```python
def belluv_stav():
    """
    Bellův stav = maximálně provázané qubity.
    Měření jednoho okamžitě určuje druhý.
    """
    qc = QuantumCircuit(2, 2)
    qc.h(0)          # superpozice prvního qubitu
    qc.cx(0, 1)      # CNOT — prováže oba qubity
    qc.measure([0, 1], [0, 1])

    print("\n=== Bellův stav (2 provázané qubity) ===")
    print(qc)

    simulator = AerSimulator()
    vysledky = simulator.run(qc, shots=1000).result().get_counts()
    print(f"\nVýsledky: {vysledky}")
    print("→ Pouze '00' nebo '11' — nikdy '01' nebo '10'!")
    print("→ Qubity jsou vždy korelované bez ohledu na vzdálenost")
    return vysledky


# belluv_stav()
print("Spusť: belluv_stav() pro demo provázanosti")
```

---

## 🔢 Deutschův algoritmus

První kvantový algoritmus exponenciálně rychlejší než klasický. Určí jestli je funkce konstantní nebo vyvážená jedním voláním (klasicky 2 volání).

```python
def deutschuv_algoritmus(konstantni: bool = True):
    """
    Deutschův algoritmus.
    Oracle pro konstantní f(x) = 0: bez změny
    Oracle pro vyvážená f(x) = x: CNOT
    """
    qc = QuantumCircuit(2, 1)

    # Inicializace
    qc.x(1)          # qubit 1 do |1⟩
    qc.h(0)          # qubit 0 do superpozice
    qc.h(1)          # qubit 1 do superpozice

    # Oracle (černá skříňka)
    if not konstantni:
        qc.cx(0, 1)  # vyvážená funkce

    # Hadamard na qubit 0
    qc.h(0)
    qc.measure(0, 0)

    simulator = AerSimulator()
    vysledky = simulator.run(qc, shots=1).result().get_counts()
    mereni = list(vysledky.keys())[0]

    print(f"\n=== Deutschův algoritmus ===")
    print(f"  Funkce: {'konstantní' if konstantni else 'vyvážená'}")
    print(f"  Výsledek: {mereni} → {'konstantní' if mereni == '0' else 'vyvážená'}")
    print(f"  ✅ {'Správně' if (mereni == '0') == konstantni else '❌ Chyba'}")
    return mereni


# deutschuv_algoritmus(konstantni=True)
# deutschuv_algoritmus(konstantni=False)
print("Spusť: deutschuv_algoritmus() pro Deutschův algoritmus")
```

---

## 🔐 BB84 — kvantová kryptografie

```python
import random


def bb84_protokol(n_bitu: int = 10) -> tuple[list, float]:
    """
    BB84 kvantový distribuce klíčů (simulace).
    Alice pošle qubity, Bob měří — sdílí tajný klíč bez možnosti odposlouchávání.
    """
    # Alice generuje náhodné bity a báze
    alice_bity = [random.randint(0, 1) for _ in range(n_bitu)]
    alice_baze = [random.choice(["+", "x"]) for _ in range(n_bitu)]

    # Bob náhodně vybírá báze pro měření
    bob_baze = [random.choice(["+", "x"]) for _ in range(n_bitu)]

    # Bob měří (pokud báze shodná → správný bit, jinak náhodný)
    bob_bity = []
    for i in range(n_bitu):
        if alice_baze[i] == bob_baze[i]:
            bob_bity.append(alice_bity[i])
        else:
            bob_bity.append(random.randint(0, 1))

    # Veřejné srovnání bázi (bez odhalení bitů)
    sdileny_klic = []
    for i in range(n_bitu):
        if alice_baze[i] == bob_baze[i]:
            sdileny_klic.append(alice_bity[i])

    shoda = sum(a == b for a, b in zip(
        [alice_bity[i] for i in range(n_bitu) if alice_baze[i] == bob_baze[i]],
        sdileny_klic
    )) / max(len(sdileny_klic), 1)

    print(f"\n=== BB84 Kvantová kryptografie ===")
    print(f"  Přeneseno bitů: {n_bitu}")
    print(f"  Shodné báze: {len(sdileny_klic)}")
    print(f"  Sdílený klíč: {sdileny_klic}")
    print(f"  Bezchybnost: {shoda:.1%}")

    return sdileny_klic, shoda


klic, shoda = bb84_protokol(20)
```

---

## 📊 Quantum Approximate Optimization (QAOA) — náhled

```python
def qaoa_info():
    """Informace o QAOA — optimalizace na kvantovém počítači."""
    info = """
=== QAOA (Quantum Approximate Optimization Algorithm) ===

Problém: Max-Cut grafu — rozděl uzly do dvou skupin tak, aby co
         nejvíce hran vedlo mezi skupinami.

Klasicky: NP-hard pro velké grafy
QAOA:     Kvantový přístup k aproximaci řešení

Kroky:
  1. Zakóduj problém jako kvantový Hamiltonián
  2. Připrav parametrizovaný kvantový obvod (p vrstev)
  3. Klasický optimizer najde nejlepší parametry
  4. Výsledek měření → aproximace řešení

Výhodné pro: kombinatorická optimalizace (TSP, scheduling, portfolio)
Limitace: NISQ éra — šum v dnešních kvantových počítačích

Spuštění na reálném hardware:
  from qiskit_ibm_runtime import QiskitRuntimeService
  service = QiskitRuntimeService(channel="ibm_quantum", token="...")
  backend = service.least_busy(simulator=False, operational=True)
"""
    print(info)


qaoa_info()
```

---

## 🎯 Stav quantum computingu 2024

| Oblast | Stav |
|--------|------|
| Počet qubitů | 100–1000 (NISQ éra) |
| Chybovost | ~0.1–1% na bránu |
| Kvantová výhoda | prokázána pro specifické úlohy |
| Šifrování (Shor) | potřeba ~4000 logických qubitů |
| Optimalizace (QAOA) | experimentální |
| Simulace chemie | nejslibnější krátkodobě |
| Dostupnost | IBM, Google, Amazon Braket (cloud) |

---

## ✏️ Cvičení

1. Implementuj **3-qubitový Groverův algoritmus** — hledání v nestrukturované databázi O(√N).
2. Postav **kvantový teleportační protokol** — přenáší kvantový stav pomocí provázanosti.
3. Napiš **kvantovou verzi coin flipping** — dokaž, že je nepadělatelná.
4. Experimentuj s IBM Quantum — spusť svůj obvod na reálném kvantovém počítači.
5. Implementuj **Quantum Fourier Transform** a porovnej s klasickým FFT.
