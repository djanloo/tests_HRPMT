---
type: nota
project: frankenchiara
updated: 2026-07-21
tags: [tipo/nota, progetto/frankenchiara]
---

# Fit dei parametri del simulatore (Optuna)

Come si tarano i parametri del simulatore sui dati reali, e le due lezioni pagate per
arrivarci — una sul rumore, una sul rise-time. Sono la stessa lezione due volte.

Codice: `fit_simulator.py` (forma a convoluzione), `sde_fit.py` (forma SDE). Il
simulatore è in [[Simulazione SDE]].

## Method of simulated moments

Invece di tarare a mano, i parametri sono fittati ai dati con **method of simulated
moments** (Optuna TPE, 500 trial/file). Il guadagno assoluto è degenere ed esce dal
conto: tutte le metriche sono scale-free. Metriche (fisicamente distinte → fit
identificabile):

| metrica | vincola | note |
|---|---|---|
| ACF normalizzata (0–5 µs) | forma `h` (rise, fall) + rumore | backbone |
| **PSD, distanza di Wasserstein** su log-f | forma spettrale + posizione floor | PMF normalizzata |
| CV della potenza per-record | occupancy (rate) | |
| eccesso di kurtosi | larghezza SER / occupancy | debole |
| **frazione di potenza 0.3–8 MHz** | rise-time / morfologia fine | aggiunta dopo, vedi sotto |

Guadagno arbitrario → il rumore è passato come **frazione dell'RMS** del segnale.
Validato con seed fresco (contro l'overfit di una realizzazione MC).

## Lezione 1: il rumore va misurato, non fittato

Le metriche ACF/PSD-Wasserstein lavorano su spettri *normalizzati* → sono **cieche al
livello assoluto del floor di rumore**. Lasciarlo libero lo faceva sovrastimare (per
il CSP `noise_frac`≈0.02, cioè σ_n≈11 ADC contro i ~4–5 ADC reali) → la simulazione
veniva troppo *ruvida* e le serie temporali del CSP **non somigliavano** a quelle
vere (pur avendo ACF/PSD giuste!).

La ruvidità visiva è dominata dal rumore ad alta-f, che quelle metriche non vincolano.
Fix: **σ_n misurato dal plateau PSD ad alta frequenza e fissato** (stessa stima usata in
[[Stima del rate dai cumulanti]], validata ~1 %).

## Lezione 2: era il rise-time, non il rumore

Sistemato il rumore, il CSP restava un po' troppo liscio. L'ipotesi iniziale era
aggiungere rumore post-preamp. **Test → è sbagliata.** Confronto della PSD
reale/simulata per bande (rapporto reale/sim, dovrebbe →1):

| banda | fit (rise 528 ns) | + rumore bianco ×3 | rise 200 ns |
|---|---|---|---|
| 0.5–2 MHz | 2.95 | 2.95 | 0.62 |
| 2–8 MHz | 2.19 | 0.94 | 0.43 |
| 30–50 MHz (floor) | 1.01 | **0.18** ✗ | 1.00 |
| dy-std (reale 8.3) | 7.0 | 14.7 | 8.5 |

Al segnale reale manca potenza **nella banda media 0.5–8 MHz** (fino a ~3×), ma al floor
(30–50 MHz) combacia già. Il **rumore bianco** riempie la banda *sbagliata* (alta-f) e
rovina il floor (0.18 = 5× troppo). Un **rise più veloce** (~250–350 ns invece dei 528
ns fittati) riempie esattamente la banda giusta e porta la roughness (`dy`-std) da 7.0 a
~8.3.

**Perché il fit aveva sbagliato il rise:** le metriche ACF (pesata uniforme su 500 lag)
e PSD-Wasserstein (su spettro *normalizzato*, distanza broad) **sotto-pesano la banda
media / i lag corti** → il rise era mal vincolato e usciva troppo lento. Stesso identico
meccanismo per cui prima usciva troppo rumore.

**Fix implementato:** aggiunto all'obiettivo un termine sulla **frazione di potenza
nella banda 0.3–8 MHz** (`_MID` in `fit_simulator.py`), che vincola direttamente il
rise. Rifit completo → **rise 528 → 322 ns**, `dy`-std 7.0 → 7.4 vs 8.3 reale, ACF-1e
ancora ✓. La morfologia delle serie temporali ora combacia.

*(Un tentativo col rapporto di von Neumann lag-1 non funziona: la MSSD del CSP è
dominata dal rumore, che confonde il termine — la frazione di potenza in banda è più
pulita.)*

> **Lezione generale:** per matchare la **forma d'onda** (non solo gli spettri
> integrati) serve una metrica sensibile alla scala fine.

## Risultati

`fit_results.json`, figura in [[Validazione a verità nota]]:

| | `FAST` | `CSP` |
|---|---|---|
| λ | 1.6×10⁷ Hz *(lim. inf., vedi sotto)* | 5.6×10⁵ Hz *(banda 5–8×10⁵)* |
| τ_rise / τ_fall | 17 ns / 257 ns | 322 ns / 3787 ns |
| ser_cv | 0.05 *(non affidabile)* | 0.22 |
| noise_frac (σ_n) | 0.087 (≈1.5 ADC) | 0.009 (≈5 ADC) — **misurato, non fittato** |
| match ACF 1/e | 270→270 ns | 2500→2640 ns |
| PSD Wasserstein | 0.014 dec | 0.006 dec |
| morfologia (dy-std) | — | 8.3 → 7.4 (rise corretto) |

La forma (ACF, PSD, distribuzione di potenza) è riprodotta molto bene per entrambi.

**Avvertenza sul canale FAST:** la kurtosi dei dati è ≈0 (gaussiano), ma lo shot-noise ha
sempre eccesso di kurtosi ≥0 → il fit non può eguagliare uno 0 (o leggermente negativo)
e la CV è satura al floor gaussiano (insensibile a λ): perciò il λ del fit è di fatto un
**limite inferiore**. Il valore alto vero emerge dai cumulanti
([[Stima del rate dai cumulanti]]). Le bande di degenerazione (trial near-best)
confermano per il FAST λ∈[1.2,1.9]×10⁷ e la coppia (λ, ser_cv) accoppiata.

## Il parametro sospetto: ser_cv

Il fit tratta la larghezza della distribuzione di ampiezza come parametro libero. Sui 5
run Cs-137 (`sde_fit_results.json`) esce fra **0.13 e 1.28 senza monotonia nella dose** —
un parametro fisico del rivelatore non si muove così. È il sintomo di una famiglia a un
parametro costretta ad approssimare una forma che non le appartiene: vedi
[[Spettro di ampiezza]] e [[Backlog]].
