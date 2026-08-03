---
type: manuale
project: frankenchiara
updated: 2026-07-23
tags: [tipo/manuale, progetto/frankenchiara]
---

# High Rate PMT dose estimation

Indice della relazione. Il ragionamento sta nelle quattro note collegate; qui restano
solo cosa manca per chiudere il conto e la bibliografia.

## Indice del ragionamento

- [[Relazione - problema|1-2. Il problema, il rivelatore e i dati]]
- [[Relazione - modello|3-4. Il modello shot noise, i cumulanti e Campbell]]
- [[Relazione - dose|5-11. λ, gain, statistiche gain-free, pipeline di dose, validazione]]
- [[Relazione - ladder|12-13. Limiti onesti e il modello ladder della perdita di gain]]
- [[#14. Cosa manca per chiudere davvero il conto|14. Cosa manca per chiudere davvero il conto]]
- [[#15. File e bibliografia|15. File e bibliografia]]

---

## 14. Cosa manca per chiudere davvero il conto

La pipeline gain-free (§10) funziona senza dati aggiuntivi. Ma per **chiudere il
conto in assoluto** e coprire l'estremo alto-rate, in ordine di efficacia:

1. **Un run di dark / pedestal** (una volta sola). Dà lo **zero assoluto** →
   sblocca la media, quindi `mean²/Var` = rate assoluto gain-free che **non
   satura** in pile-up profondo (dove la skewness invece si appiattisce).
   Migliorerebbe proprio il punto peggiore della pipeline. È il singolo dato
   mancante più prezioso, e **non è "un altro segnale"**: è una misura di
   calibrazione.
2. **Uno scan a HV fissa variando solo il rate**, e/o run a rate ≲ 180 kcps: dà
   la parte *pre-crash* della curva di gain → discrimina i parametri del ladder
   ($N,\kappa,R$) oltre alla sola scala di carico.
3. **Un run a basso rate in modo-conteggio**: impulsi isolati → misura diretta di
   $h(t)$, del gain di singolo evento e dello **spettro SER** — che azzera il
   sistematico ×6 dominante sul rate.

Da notare un limite hardware invalicabile via software: dentro il gain-crash, gli
stadi di moltiplicazione "saltano" (excess noise), quindi **energia e dose
assoluta degradano**. `mean²/Var` recupera il **rate** attraverso il crash, ma la
parte alta della dinamica si salva solo con l'hardware (partitore attivo/booster,
o il controllo HV attivo del metodo Target). **Il software estende il range
*prima* del crollo, non ti salva *dentro*.**

---

## 15. File e bibliografia

**Codice e figure**

| file | cosa fa |
|---|---|
| `simulate_pmt.py` | simulatore shot-noise (somma di impulsi + jump-SDE) + self-check |
| `fit_simulator.py` | fit Optuna dei parametri (ACF + PSD-Wasserstein + banda media + CV) |
| `mssd_cumulant_estimate.py` | stima rate/energia da MSSD + cumulanti pari, con validazione |
| `amplitude_ser.py` | tentativo (fallito, e dimostrato tale) di estrarre P(A) dai cumulanti |
| `analisi_1.py` | Welch / coerenza / filtri di partenza |
| `target_test/target_method.py` | metodo Target sui 6 run reali |
| `target_test/pe_synth.py` | simulatore a livello di fotoelettrone (verità nota) |
| `target_test/gain_solve.py` | modello minimale del gain (equazione auto-consistente) |
| `target_test/gain_ladder.py` | **modello ladder completo** del partitore (KCL accoppiato) |
| `target_test/gain_ladder_fit.py` | fit del ladder ai 4 run a stessa HV |
| `dose_estimation/dose_pipeline.py` | pipeline di dose finale + calibrazione + LOO |
| `dose_estimation/synth_validation.py` | validazione della dose su verità nota |

**Riferimenti chiave**

- **Roessl & Daerr**, *A Fourier approach to pulse pile-up in photon-counting
  X-ray detectors*, Med. Phys. 2016 — pile-up come level-crossing di shot noise;
  forward-model di Fourier.
- **Personick**, *Statistics of a General Class of Avalanche Detectors*, BSTJ
  1971 — l'*excess noise factor* $F = \langle G^2\rangle/\langle G\rangle^2$ =
  il nostro momento SER, prior fisico sul sistematico ×6.
- **Rice**, *Mathematical Analysis of Random Noise*, 1944 — teoria del level
  crossing.
- **Lowen & Teich**, *Power-Law Shot Noise*, IEEE IT 1990 — shot noise (regime
  power-law, non il nostro, ma stessa macchina di Campbell).
- **Cox & Isham**, *Point Processes*; **Papoulis**, *Probability, Random
  Variables and Stochastic Processes* — framework generale.
- Brevetto **US2021/0055429 A1** (Stein) — metodo Target.

---

### In una riga

> Il segnale è shot noise; il gain è un traditore che collassa col rate; la
> salvezza sono i **rapporti gain-free** dei cumulanti (skewness → rate, η →
> energia), con cui si stima la **dose entro ×1.24 su 2.5 decadi** senza toccare
> l'hardware — e il modello *ladder* spiega perché il gain crolla come 1/λ.
