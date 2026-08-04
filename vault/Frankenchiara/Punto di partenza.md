---
type: nota
project: frankenchiara
updated: 2026-07-21
tags: [tipo/nota, progetto/frankenchiara]
---

# Punto di partenza (documento originale)

**Documento storico**, conservato per il registro: è il brief scritto *prima* di
qualunque analisi, che proponeva la direzione. Tutto il suo contenuto è stato superato
dal lavoro fatto — la mappa di cosa l'ha sostituito è alla fine.

Non aggiornarlo: se qualcosa qui è sbagliato, la correzione va nella nota che l'ha
superato.

---

## Problema

Nel mio caso il PMT lavora in un regime di **rate estremamente elevato**, tale per cui:

- gli impulsi sono quasi sempre sovrapposti (pile-up continuo);
- non è possibile discriminare i singoli eventi;
- l'obiettivo è stimare la **dose / rate della sorgente**, non necessariamente
  ricostruire ogni impulso.

Questo suggerisce di trattare il segnale come un **processo stocastico continuo**,
anziché come una sequenza di impulsi da identificare.

## 1. Shot Noise Process (approccio principale)

$$ x(t)=\sum_i A_i\,h(t-T_i) $$

dove $T_i$ sono i tempi di arrivo (tipicamente processo di Poisson), $A_i$ l'ampiezza
casuale (guadagno PMT), $h(t)$ la risposta impulsiva PMT + elettronica.

Nel regime di alto rate gli impulsi si sovrappongono naturalmente, ma il modello resta
valido. L'obiettivo diventa stimare direttamente il parametro $\lambda$ (rate degli
eventi), senza effettuare pulse finding.

Da approfondire: Shot Noise Processes, Poisson Shot Noise, Campbell's theorem, Rice
Shot Noise.

## 2. Compound Poisson Process

Modello ancora più realistico per un PMT:

$$ x(t)=\sum_i Q_i\,h(t-T_i) $$

dove $Q_i$ rappresenta la carica prodotta dal singolo evento (Single Electron Response
del PMT). Questo permette di ricavare analiticamente media, varianza, PSD,
autocorrelazione, cumulanti — tutte quantità che dipendono direttamente dal rate della
sorgente.

## 3. Rice Level Crossing Theory

Invece di identificare gli impulsi, si studiano statistiche del processo: crossing di
soglia, zero crossing, massimi locali, permanenza sopra soglia. Queste statistiche
possono essere messe in relazione al rate di arrivo anche in presenza di forte pile-up.

## 4. PSD e statistiche del processo

In molti ambiti (ottica, telecomunicazioni) il flusso viene stimato tramite spettro di
potenza (PSD), autocorrelazione, Allan variance, distribuzione dell'ampiezza, cumulanti.
Non è necessario identificare i singoli impulsi.

## Possibili statistiche da utilizzare

Piuttosto che fare pulse detection, valutare: media del segnale, varianza, PSD,
autocorrelazione, distribuzione delle ampiezze, cumulanti, level crossing, zero
crossing, spettro bis (bispectrum).

## Direzione di ricerca

Una possibile metodologia è modellare il PMT come un **Compound Poisson Shot Noise
Process** e stimare il parametro $\lambda$ utilizzando esclusivamente le statistiche del
segnale analogico continuo.

In questo approccio il pile-up non è un problema da correggere, ma una caratteristica
naturale del processo da modellare.

## Osservazione

La letteratura di elettronica nucleare è ancora fortemente orientata verso Pulse Height
Analysis (PHA), Pulse Finding, Pulse Fitting, Pulse Deconvolution, Pile-up Rejection,
Dead-time Correction.

Gli approcci basati sulla teoria dei processi stocastici risultano invece molto più
comuni in telecomunicazioni, fotonica, ottica, radar, signal processing.

Questo lascia spazio a possibili sviluppi originali applicati alla dosimetria con PMT in
regime di pile-up estremo.

---

## Cosa ha superato cosa

| sezione qui | dove vive adesso |
|---|---|
| Problema | [[Rivelatore e dati]] |
| §1 Shot Noise, §2 Compound Poisson | [[Shot noise]], [[Cumulanti e Campbell]] |
| §3 Rice Level Crossing | [[Level crossing]] — testato, satura in pileup |
| §4 PSD e statistiche | [[Statistiche gain-free]] (la tabella maestra) |
| Possibili statistiche | idem; il bispectrum non è stato provato |
| Letteratura consigliata | [[Letteratura]], con il giudizio su ciascun riferimento |
| Direzione di ricerca | fatta: [[Stima della dose]] |
| Osservazione (l'originalità) | ancora valida, ripresa in [[Rivelatore e dati]] |

Il pezzo mancante che questo documento non prevedeva, e che si è rivelato il vero
antagonista: il **gain che collassa col rate** ([[Gain ladder]],
[[Statistiche gain-free]]).
