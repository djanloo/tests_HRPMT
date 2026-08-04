---
type: nota
project: frankenchiara
updated: 2026-07-21
tags: [tipo/nota, progetto/frankenchiara]
---

# I due file sono indipendenti

Risultato negativo verificato: il canale **FAST** e il **CSP** non sono lo stesso
segnale, e nessuno dei due è la versione filtrata dell'altro. Vale la pena una nota
sua perché la somiglianza apparente è convincente e ha già ingannato una volta.

Vedi [[Rivelatore e dati]] per cosa sono i due file.

## L'apparenza

Graficando 5 record normalizzati sovrapposti *sembra* che i trend lenti si
somiglino. **È un artefatto di campionamento**, non correlazione reale.

## Le due verifiche

- **Coerenza spettrale** $\gamma^2(f)$ mediata su tutti i 1000 record: **piatta al
  floor $1/N \approx 0.001$ a ogni frequenza** (0–50 MHz). Se un file fosse la
  versione filtrata dell'altro, o condividessero una modulazione lenta comune, si
  vedrebbe $\gamma^2 \to 1$ a bassa frequenza. Non c'è.

- **Test allineati vs mescolati.** Correlazione per-record del trend (<300 kHz):
  accoppiando `c[i]`–`a[i]` → media 0.00, **std 0.32**; accoppiando a caso
  `c[perm]`–`a[i]` → media 0.00, **std 0.32**. Distribuzioni **identiche** →
  l'indice di record non porta informazione → indipendenti.

Di conseguenza il **14 % dei record ha |r|>0.5 per puro caso** (identico nel
mescolato). Scegliendone 5 a occhio se ne trovano sempre alcuni "che tornano" (e
altrettanti che si oppongono, r≈−0.77).

![[independence_test.png]]
*La coerenza spettrale è piatta al floor a ogni frequenza; le correlazioni allineate
e mescolate hanno la stessa distribuzione → i due file sono indipendenti.*

## Perché così tanta correlazione spuria

`csp` ha $N_\text{eff} \approx 6.6$ oscillazioni lente *indipendenti* per
finestra da 20 µs. La correlazione tra due tracce con ~6 gradi di libertà ha spread
di sampling $\approx 1/\sqrt{6} \approx 0.4$ — esattamente lo 0.32 osservato.
Pochi "wiggle" per finestra ⇒ tante coincidenze.

Quel $N_\text{eff}$ piccolo non è solo una curiosità: è la stessa quantità che
rende inaffidabile la stima di $\kappa_4$ su `csp`
([[Stima del rate dai cumulanti]]) e che fissa il floor gaussiano della
fluttuazione di potenza.
