---
type: nota
project: frankenchiara
updated: 2026-08-03
tags: [tipo/nota, progetto/frankenchiara]
---

# Misure a basso rate: PHA offline sull'Am-241

Quando l'occupancy è bassa ([[Pile-up e occupancy]]) gli eventi sono separati, e si può fare
la misura che tutto il resto del progetto è costruito per evitare: **pulse-height analysis**. È l'unico modo di
misurare $P(A)$ direttamente ([[Spettro di ampiezza]]), quindi l'unico modo di attaccare
il sistematico dominante invece di assumerlo.

Codice: `pha_lowrate.py`. Dato: `data/anode_waveforms/run_Am-241_93.56.h5`,
10000 record × 2000 campioni a 100 MS/s.

## Il fatto che decide il metodo

Su questo rivelatore a questo gain, **un gamma non è un impulso liscio**: è un *burst* di
spike da fotoelettrone singolo, spalmato sul decadimento di scintillazione, con decine di
massimi locali dentro. Misurato sull'Am-241: ACF 1/e = **260 ns**, ridotta a $r=0.06$ a
~1 µs.

![[pha_am241.png]]
*(sx) un record reale: il grezzo (sottile) è granuloso di fotoelettroni; l'integrale sul
gate (spesso) è ciò che identifica gli eventi. (dx) lo spettro misurato contro il modello
NaI di `energy_spectrum.nai()`.*

Conseguenza: **il peak-finding sulla traccia grezza conta fotoelettroni, non eventi.** Ci
sono cascato in ordine, e vale la pena tenere il registro perché sono tre errori diversi:

| tentativo | cosa dava | perché è sbagliato |
|---|---|---|
| `find_peaks(height=5σ)` | 77 eventi/record | soglia **assoluta**: la coda di un impulso da 43 ADC resta sopra 7.8 ADC per ~2τ, e le ondulazioni di rumore su quella coda fanno un massimo nuovo ogni pochi campioni |
| `find_peaks(prominence=5σ)` | 113 eventi/record | la prominenza risolve la coda, ma i massimi sono **dentro un evento**: sono i singoli fotoelettroni |
| integrale su gate | **7.8 eventi/record** | l'energia di un evento è la sua **carica**, non l'altezza di un suo spike |

Attesi ~3/record dalla tabella dose→rate, ma quel numero viene dalla calibrazione Target
del **Cs-137** applicata all'Am — a 59.5 keV serve ~11× più eventi per la stessa dose,
quindi non era mai stato valido per questo run. Vedi [[Rivelatore e dati]].

## Il metodo, in quattro passi

1. **baseline per record** (mediana): i run sono DC-coupled, la baseline è reale;
2. **σ del rumore** dal plateau della PSD ad alta frequenza — riuso di
   `mssd_cumulant_estimate.noise_var`, già validato a ~1% ([[Stima del rate dai cumulanti]]);
3. **gate di integrazione** pari a 4× l'ACF 1/e misurata → 104 campioni (1.04 µs). Somma
   scorrevole su `cumsum`: i suoi massimi locali sono dove il gate inquadra meglio un
   burst. Soglia $5\sigma\sqrt{\text{gate}}$ = 80 ADC·campioni;
4. **veto di pile-up**: si scarta un evento se un altro cade entro 2 gate.

L'altezza restituita è la **prominenza** della somma scorrevole, non il suo valore
assoluto: così un burst che siede sulla coda del precedente porta la propria carica e non
quella che ha ereditato. È la correzione del classico bias di tail-riding del PHA, gratis.

### Il pile-up, e come si sa che è sotto controllo

Il veto scarta il **62%** degli eventi, che sembra tanto per un'occupancy di 0.10. Non lo
è: a 0.39 Mcps con un gate di 1 µs la probabilità che un vicino cada dentro 2 gate è
~2·2·1.04/2.6 ≈ 60%, quindi il numero è quello atteso. Il punto non è quanti se ne
scartano, è **se lo scarto sposta la misura**:

| veto | scartati | centroide fotopicco | deriva |
|---|---|---|---|
| 0 gate | 0.1% | 1136 | — |
| 1 gate | 0.1% | 1136 | +0.0% |
| 2 gate | 62.1% | 1146 | +0.9% |
| 4 gate | 97.8% | 1137 | −0.8% |

Il centroide si muove entro l'1% mentre la statistica cala di 40×: **il pile-up non sta
distorcendo il fotopicco**. È l'unico controllo che conta, ed è nel `__main__` come
assert. Nota che senza veto la contaminazione è già minima sul *centroide* — la
prominenza da sola fa quasi tutto il lavoro; il veto serve alla coda alta.

## Il risultato

- **rate**: 0.39 Mcps (occupancy $\lambda\tau$ = 0.10);
- **fotopicco**: 1146 ADC·campioni → calibrazione **51.9 keV per 1000 ADC·campioni**;
- **risoluzione**: **FWHM/E = 30.2%** a 59.5 keV.

Da tenere presente leggendo questi numeri: anche a 94 µSv/h il rivelatore sta **8× oltre** il
rate per cui il suo partitore è dichiarato ([[Stato dell'arte]]), quindi il gain è già in
calo — la calibrazione keV/ADC qui ricavata vale per *questo* run, non in assoluto.

### Il modello NaI è validato sulla risoluzione

Il modello sotto esame è quello di [[Simulazione SDE]]. `energy_spectrum.nai()` assume `res662 = 8%` scalato come $1/\sqrt{E}$, che a 59.5 keV
predice **26.7%**. Misurato 30.2% → **res662 implicito 9.1%**. Un punto percentuale di
scarto su una manopola messa a occhio: il modello di risoluzione regge.

### Il continuo no

CV dello spettro modellato **0.252**, CV della carica misurata **0.759**. La figura
(destra) mostra dove sta la differenza: il misurato ha un **continuo di bassa energia**
sotto il fotopicco (scatter Compton nel cristallo, eventi a energia parziale, righe L, e
la regione di soglia) e una **coda alta** oltre il fotopicco, mentre il modello è quasi
solo due gaussiane.

Quindi: fotopicco e risoluzione **confermati**, pesi relativi fra picco, continuo e
backscatter **non confermati** — che è esattamente la voce di [[Backlog]] aperta su
`photofrac`/`backscatter`. Questo dato la può chiudere: basta fittare quei due pesi
sull'istogramma misurato invece di lasciarli al default.

## Quando NON usarlo

Il modulo si rifiuta sopra `OCC_MAX = 0.15`. Su ogni run Cs-137 di questo dataset
($\lambda\tau$ da 0.26 a 12) il PHA è privo di senso per costruzione: gli eventi non sono
separabili, ed è precisamente il motivo per cui esiste [[Stima della dose]]. L'Am-241 a 94
µSv/h è l'unico run del dataset in cui questa misura è lecita — la stessa ragione per cui
`dose_pipeline` lo mette fuori dallo stimatore statistico e dice "conta gli impulsi".

