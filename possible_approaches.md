# PMT ad alto rate: modellizzazione stocastica del pile-up

## Problema

Nel mio caso il PMT lavora in un regime di **rate estremamente elevato**, tale per cui:

- gli impulsi sono quasi sempre sovrapposti (pile-up continuo);
- non è possibile discriminare i singoli eventi;
- l'obiettivo è stimare la **dose / rate della sorgente**, non necessariamente ricostruire ogni impulso.

Questo suggerisce di trattare il segnale come un **processo stocastico continuo**, anziché come una sequenza di impulsi da identificare.

---

# 1. Shot Noise Process (approccio principale)

Modello:

\[
x(t)=\sum_i A_i\,h(t-T_i)
\]

dove

- \(T_i\): tempi di arrivo (tipicamente processo di Poisson);
- \(A_i\): ampiezza casuale (guadagno PMT);
- \(h(t)\): risposta impulsiva PMT + elettronica.

Nel regime di alto rate gli impulsi si sovrappongono naturalmente, ma il modello resta valido.

L'obiettivo diventa stimare direttamente il parametro

\[
\lambda
\]

(rate degli eventi), senza effettuare pulse finding.

### Da approfondire

- Shot Noise Processes
- Poisson Shot Noise
- Campbell's theorem
- Rice Shot Noise

---

# 2. Compound Poisson Process

Modello ancora più realistico per un PMT:

\[
x(t)=\sum_i Q_i\,h(t-T_i)
\]

dove \(Q_i\) rappresenta la carica prodotta dal singolo evento (Single Electron Response del PMT).

Questo permette di ricavare analiticamente:

- media;
- varianza;
- PSD;
- autocorrelazione;
- cumulanti.

Tutte queste quantità dipendono direttamente dal rate della sorgente.

---

# 3. Rice Level Crossing Theory

Invece di identificare gli impulsi, si studiano statistiche del processo:

- crossing di soglia;
- zero crossing;
- massimi locali;
- permanenza sopra soglia.

Queste statistiche possono essere messe in relazione al rate di arrivo anche in presenza di forte pile-up.

---

# 4. PSD e statistiche del processo

In molti ambiti (ottica, telecomunicazioni) il flusso viene stimato tramite:

- spettro di potenza (PSD);
- autocorrelazione;
- Allan variance;
- distribuzione dell'ampiezza;
- cumulanti.

Non è necessario identificare i singoli impulsi.

---

# Letteratura consigliata

## Shot Noise

### Roessl et al.

*A Fourier approach to pulse pile-up in photon-counting x-ray detectors*

Idea:
- interpreta il pile-up come processo shot-noise;
- usa strumenti statistici/Fourier invece del pulse finding.

---

## Shot Noise classico

Personick

*Statistics of a General Class of Avalanche Detectors with Applications to Optical Communications*

Confronta misura in corrente e photon counting utilizzando modelli di shot noise.

---

## Testi consigliati

### Lowen & Teich

*Power-Law Shot Noise*

Ottimo punto di partenza per la teoria moderna dello shot noise.

---

### Cox & Isham

*Point Processes*

Testo fondamentale sui processi puntuali.

---

### Papoulis

*Probability, Random Variables and Stochastic Processes*

Per la teoria generale dei processi stocastici.

---

### Rice

*Mathematical Analysis of Random Noise* (1944)

Lavoro storico sulla teoria dei level crossing.

---

# Possibili statistiche da utilizzare

Piuttosto che fare pulse detection, valutare:

- media del segnale;
- varianza;
- PSD;
- autocorrelazione;
- distribuzione delle ampiezze;
- cumulanti;
- level crossing;
- zero crossing;
- spettro bis (bispectrum).

L'idea è stimare il rate della sorgente direttamente da queste statistiche.

---

# Direzione di ricerca

Una possibile metodologia è modellare il PMT come un

**Compound Poisson Shot Noise Process**

e stimare il parametro

\[
\lambda
\]

utilizzando esclusivamente le statistiche del segnale analogico continuo.

In questo approccio il pile-up non è un problema da correggere, ma una caratteristica naturale del processo da modellare.

---

# Osservazione

La letteratura di elettronica nucleare è ancora fortemente orientata verso:

- Pulse Height Analysis (PHA)
- Pulse Finding
- Pulse Fitting
- Pulse Deconvolution
- Pile-up Rejection
- Dead-time Correction

Gli approcci basati sulla teoria dei processi stocastici risultano invece molto più comuni in:

- telecomunicazioni;
- fotonica;
- ottica;
- radar;
- signal processing.

Questo lascia spazio a possibili sviluppi originali applicati alla dosimetria con PMT in regime di pile-up estremo.