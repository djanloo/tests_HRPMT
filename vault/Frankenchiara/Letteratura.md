---
type: riferimento
project: frankenchiara
updated: 2026-08-04
tags: [tipo/riferimento, progetto/frankenchiara]
---

# Letteratura

Due parti: il **giudizio** sui riferimenti chiave (cosa danno davvero per il nostro
problema) e la **reading list** completa raccolta dagli agenti di ricerca.

## I riferimenti chiave, uno per uno

**Roessl & Daerr, *A Fourier approach to pulse pile-up in photon-counting X-ray
detectors* (Med. Phys. 2016)** — il più rilevante. Identifica il pile-up con il
**problema del level-crossing di un processo shot-noise** e dà una formula di Fourier
esatta per il numero atteso di conteggi in funzione del flusso, per forma d'impulso e
risposta arbitrarie. C'è anche il companion SPIE *"On the analogy between pulse-pile-up
and level-crossing of shot noise"*. **Utile** come modello forward per un rivelatore a
*soglia/conteggio*; per il nostro caso (forma d'onda continua, no soglia) l'idea del
level-crossing è testabile ma ha un limite — vedi [[Level crossing]].
→ https://pubmed.ncbi.nlm.nih.gov/26936714/ ,
https://www.spiedigitallibrary.org/conference-proceedings-of-spie/9783/97831H

**Personick, *Statistics of a General Class of Avalanche Detectors* (BSTJ 1971)** — dà
la distribuzione del guadagno di valanga e l'**excess noise factor**
$F=\langle G^2\rangle/\langle G\rangle^2$. È **esattamente** il momento SER
$m_2=\langle A^2\rangle/\langle A\rangle^2$ che domina i nostri sistematici (il "fattore
~6" su rate/energia). Confronta anche modo-corrente vs photon-counting = la nostra
distinzione Campbelling vs pulse-counting. **Utile** per mettere un prior fisico sulla
larghezza SER (invece di scansionarla alla cieca) — vedi [[Spettro di ampiezza]] e
[[Backlog]]. Open access su archive.org. → https://archive.org/details/bstj50-10-3075

**Rice, *Mathematical Analysis of Random Noise* (1944)** — la sorgente della teoria del
level-crossing. Formula chiave (processo gaussiano stazionario):
$N(u) = (1/2\pi)\sqrt{\lambda_2/\lambda_0}\exp(-u^2/2\lambda_0)$, con
$\lambda_0=\text{Var}$, $\lambda_2=\text{Var}$(derivata). **Utile** ma in pileup gaussiano
il crossing dà la *forma*, non λ ([[Level crossing]]).

**Lowen & Teich, *Power-Law Shot Noise* (IEEE IT 1990)** — shot noise con risposta a
legge di potenza $h(t)\propto t^{-\alpha}$ → spettri $1/f^\beta$ / frattali. **Non è il
nostro caso:** le nostre PSD sono Lorentziane / 2-poli con floor bianco, τ finito, non
1/f. La *macchina* (cumulanti di Campbell) è la stessa, ma il regime power-law non si
applica. Da tenere solo se emergesse struttura 1/f (non c'è).

**Cox & Isham *Point Processes* / Papoulis *Probability, Random Variables and Stochastic
Processes*** — testi di riferimento, framework generale (processi puntuali, cumulanti).
Nessun risultato specifico nuovo per noi.

**Brevetto US2021/0055429 A1 (Stein)** — il metodo Target. PDF nella root del repo.
Vedi [[Metodo Target]].

### Giudizio d'insieme

La direzione è giusta e già implementata: trattiamo il segnale come **Poisson filtrato /
Campbell** e stimiamo λ dalle statistiche del continuo, senza pulse-finding. Il valore
aggiunto della letteratura è:

1. Personick → prior sulla SER;
2. Roessl/Rice → level-crossing come stima/cross-check;
3. conferma che **tutti** questi metodi sbattono contro lo stesso muro in pileup gaussiano
   profondo (anode): la forma d'onda perde la granularità e resta solo
   $\lambda\langle A^2\rangle$ ([[Pile-up e occupancy]]).

---

## Sul gain ad alto rate e su questo rivelatore

Raccolti il 2026-08-03; il commento ragionato sta in [[Stato dell'arte]], qui i puntatori.

- **Experiment and modeling of scintillation photon-counting and current measurement for PMT
  gain stabilization**, NIM A 2015 — usa uno **Scionix 51B51/2** (variante col PMT da 2"),
  stabilizza il gain combinando photon counting e integrazione di carica, senza hardware
  aggiuntivo. Fonte dei **10 pe/keV**, che per la nostra variante da 1.5" è un limite
  superiore.
  → https://www.sciencedirect.com/science/article/abs/pii/S0168900215001515
- **Effects of high count rate and gain shift on isotope-identification algorithms** —
  conseguenze applicative dello shift di gain.
  → https://www.sciencedirect.com/science/article/abs/pii/S016890020901701X
- **Response of G-NUMEN LaBr₃(Ce) detectors to high counting rates** → https://arxiv.org/pdf/2307.07818
- **Simplified PMT Model** → https://arxiv.org/pdf/0809.4210
- **Scionix, Voltage dividers** — la guida del costruttore: il limite dei ~50 kcps per i
  470 kΩ e la regola $I_b \ge 10\,I_a$. → https://scionix.nl/voltage-dividers/
- **Scionix, Tutorial of scintillation detectors (2018)** →
  https://scionix.nl/wp-content/uploads/2022/09/Tutorial-of-SCIONIX-scintillation-detectors-2018-3-.pdf
- **Hamamatsu, R10601 / R10601-100 datasheet** — il nostro PMT. Il PDF non si è fatto leggere
  in automatico, va aperto a mano: serve per il conteggio degli stadi.
  → https://www.hamamatsu.com/content/dam/hamamatsu-photonics/sites/documents/99_SALES_LIBRARY/etd/R10601_-100_TPMH1334E.pdf

---

## Reading list completa

Recuperata dagli agenti di ricerca (la deep-research è morta per limite di spesa API,
non per merito). URL raccolti prima del blocco; titoli annotati a memoria/riconoscimento,
da verificare. Raggruppata per famiglia di metodo.

### Shot noise / Campbell / decompounding
- Lowen & Teich, *Power-Law Shot Noise*, IEEE IT 1990 — https://www3.nd.edu/~mhaenggi/ee87021/Lowen-1990-Information%20Theory.pdf
- *Non-Parametric Decompounding of Pulse Pile-Up Under Gaussian Noise With Finite Data Sets* (molto pertinente: recupero della distribuzione dei salti di un compound-Poisson dalla somma) — https://www.researchgate.net/publication/340014103
- *Poisson Process and Shot Noise* (rassegna) — https://www.researchgate.net/publication/335830450
- Variance-stabilizing transforms per intensity estimators di shot noise — https://www.researchgate.net/publication/372671705
- Cambridge, *Review on Poisson, Cox, Hawkes, shot-noise-Poisson and dynamic contagion processes* — https://www.cambridge.org/core/journals/annals-of-actuarial-science/article/abs/165DE537F3835621CA67311342BAA281

### Higher-order statistics / cumulanti / polispettri
- *Factorial cumulants reveal interactions in counting statistics* — https://arxiv.org/pdf/1507.04579
- Noise intensity-intensity correlations e 4° cumulante dello shot noise foto-assistito — https://www.researchgate.net/publication/257530079
- Signal processing with higher-order spectra (lecture CMU) — https://www.cs.cmu.edu/~pmuthuku/mlsp_page/lectures/Signal_proc_with_higher_order_spectra.pdf
- Rosenblatt, cumulant / higher-order / poly-spectra — https://www.researchgate.net/publication/241008888

### Fotoni / ottica / HBT / photon counting
- Shot-noise-intensity vs photon counting: equivalenza (Zmuidzinas vs Lieu) — https://arxiv.org/pdf/1501.03219
- Hanbury-Brown–Twiss con fotoni interagenti — https://www.researchgate.net/publication/45646555
- Shot noise in sistemi mesoscopici (rassegna) — https://www.researchgate.net/publication/355286101
- arXiv (photon statistics / flusso): 1609.01607, 1805.01262, 0711.0719, 1410.5930

### Neuroscienze — fluctuation/noise analysis, quantal & rate
- *A Method to Estimate Synaptic Conductances From Membrane Potential Fluctuations* — https://www.researchgate.net/publication/8568568 ; J.Neurophysiol https://journals.physiology.org/doi/full/10.1152/jn.00528.2012
- Quantal / variance-mean analysis del rilascio sinaptico — PMC: PMC3704362, PMC5122579, PMC2231069, PMC2278972, PMC1303444
- J.Neurosci (quantal/release): /content/24/10/2345 , /content/28/50/13563 , /content/30/4/1441
- Rate/spike inference & synaptic input — PubMed 14667542, 2426389, 1706951, 15136605

### Deconvoluzione (sparsa / FRI / calcium) & ML
- Sampling Signals with Finite Rate of Innovation (Vetterli/Blu/Dragotti) + caso rumoroso — https://www.researchgate.net/publication/3318328 , /37420678 , /220735296
- OASIS — *Fast online deconvolution of calcium imaging data* — https://www.researchgate.net/publication/315059491 ; PLoS Comput Biol https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005423
- SURE-LET deconvoluzione sotto rumore Poisson — https://www.researchgate.net/publication/300340138
- ML pile-up: *Deep Learning Based Pile-Up Correction .. High-Count-Rate* — https://www.researchgate.net/publication/389459277 ; *Pile-up correction by Genetic Algorithm & ANN* — https://www.researchgate.net/publication/245122859

### Point process / Hawkes / jump-diffusion (statistica, finanza)
- MLE per Hawkes (self-excitation/inhibition) — https://www.researchgate.net/publication/349943886
- Lévy models review — https://www.stat.purdue.edu/~figueroa/Papers/LevyModelsReview.pdf
- Inference/simulazione per spatial point process; marked point patterns bayesiani — RG 265716392, 24054052

### Pile-up nucleare (analisi-side, per confronto)
- Pile-up correction ad alto rate (gamma spectroscopy) — RG 337788711, 333636734 ; NIM S0168900218304455, S0168900220307051
- Frontiers Physics, modello pile-up con dead time & retrigger — https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2023.1205638/full
- Nuclear Sci & Tech (2024) — https://link.springer.com/article/10.1007/s41365-024-01606-y
