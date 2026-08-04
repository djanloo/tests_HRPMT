---
type: nota
project: frankenchiara
updated: 2026-07-23
tags: [tipo/nota, progetto/frankenchiara]
---

# Il rivelatore e i dati

Cosa stiamo guardando e con che cosa. Il problema che questi dati devono risolvere,
il rivelatore che li produce, e cosa c'è dentro i file.

## Il problema

Abbiamo un **fotomoltiplicatore (PMT)** accoppiato a uno scintillatore, che guarda
una sorgente radioattiva. Vogliamo misurare la **dose**. Il problema è che la
sorgente è così intensa che il PMT lavora a **rate altissimo**: gli impulsi
prodotti dai singoli eventi **si sovrappongono continuamente** (pile-up).

Il modo classico di fare dosimetria — *"riconosci ogni impulso, misurane
l'altezza, mettili in un istogramma"* (Pulse Height Analysis) — qui **non
funziona**: gli impulsi non sono più separabili. Il segnale digitizzato assomiglia
a un rumore continuo, non a una sequenza di picchi.

La proposta è ribaltare il punto di vista:

> Invece di combattere il pile-up cercando di separare gli impulsi, lo
> **modelliamo**. Trattiamo il segnale come un **processo stocastico continuo** e
> stimiamo la dose dalle sue **proprietà statistiche** (media, varianza,
> asimmetria, autocorrelazione…), senza mai cercare i singoli impulsi.

Questo approccio è standard in telecomunicazioni, fotonica, radar — ma poco usato
in elettronica nucleare, che resta ancorata al pulse-finding. È lì che sta lo
spazio per fare qualcosa di nuovo. Il modello è in [[Shot noise]].

## Come funziona un PMT

Un fotone di scintillazione strappa un elettrone dal **fotocatodo** (il
"fotoelettrone"); questo viene accelerato verso una serie di elettrodi, i
**dinodi**, ognuno dei quali moltiplica il numero di elettroni di un fattore
δ ≈ 3–5. Con ~10 dinodi in cascata si arriva a un **gain** complessivo
$G = \prod_i \delta_i \sim 10^6$: un singolo fotoelettrone diventa un milione di
elettroni, cioè un impulso di corrente misurabile all'**anodo**.

![[Photomultiplier_schema_en.png]]
*Il fotocatodo, la cascata sui dinodi con i secondari che si moltiplicano a ogni stadio,
il partitore resistivo in basso, e la lettura sulla resistenza d'anodo $R_a$ — che nel
nostro rivelatore è $R_L = 100$ k$\Omega$ ([[Hardware]]) — ma il carico che conta
davvero sono i 50 Ω di terminazione a valle ([[Catena di lettura]]).*

**Attenzione a una cosa nella figura**: è disegnata col **fotocatodo a massa** e
l'accelerazione positiva verso l'anodo. È la convenzione didattica, ma **non** quella di
questo banco: per leggere l'anodo in DC su uno shunt verso massa serve l'HV *negativa*,
con il catodo a $-V_{HV}$ e l'anodo a potenziale di massa. Vedi [[Hardware]] per il perché
e per lo schema nella convenzione giusta.

*(Figura di provenienza esterna, non prodotta qui: se finisce in una relazione va
verificata la licenza e messa l'attribuzione.)*

Il gain è il vero antagonista di questa storia — vedi [[Statistiche gain-free]] per
perché, e [[Gain ladder]] per il meccanismo.

## (a) I due canali di prelievo

Sullo stesso anodo ci sono **due punti di prelievo** — dettagli in [[Catena di lettura]]:

- **FAST** — il segnale su cui si lavora: preso sul carico d'anodo ($R_L = 100$ kΩ nella
  base, ma il carico vero sono i 50 Ω di terminazione a valle), $V = R\,I$, **nessuna
  filtrazione**. Banda del rivelatore, non di uno shaper: fuzz rapido, τ ≈ 250 ns. È il
  ramo di **tutti i sei run ufficiali** in `data/anode_waveforms/`;
- **CSP** — uscita del **preamplificatore di carica** a valle dello stesso anodo:
  **integra** la corrente, quindi vaga lentamente, τ ≈ µs. Un solo file, `csp.npy`,
  1000 record × 2000 campioni.

Tutto a $f_s = 100$ MS/s (cioè $\Delta t = 10$ ns, finestra di **20 µs** per record),
`float64` di ADC interi.

> **Provenienza dei numeri FAST qui sotto.** Sono misurati sui **primi 1000 record di
> `run_Cs-137_28100.h5`**, cioè sul run a 28100 µSv/h — non su un dataset separato. Il perché
> di questa attribuzione sta in [[Frankenchiara/Decisioni|Decisioni]] (2026-08-04).

**Il CSP non è la strada, ed è una scelta, non un caso.** Integrando e filtrando butta
via l'alta frequenza, che è esattamente dove sta l'informazione di conteggio: ad alto
rate la sua finestra di integrazione è più larga della spaziatura fra eventi, quindi il
pile-up è dentro la risposta e non si scioglie. Si vede nei numeri più sotto (incrementi
lisci, $\kappa_4 \approx 0$, $N_\text{eff} \approx 7$). Resta come **riferimento**: serve
a mostrare cosa succede quando si filtra, e come contro-prova che il modello shot-noise
regge anche con una $h$ diversa. Nessun risultato del progetto ci passa.

![[signals.png]]
*Dieci record grezzi dei due canali, normalizzati e impilati. Continuo = **FAST**
(fuzz veloce), tratteggio = **CSP** (wandering lento).*

Sono **indipendenti**: non è uno la versione filtrata dell'altro, e la somiglianza
apparente dei trend lenti è un artefatto — verifica rigorosa in
[[Indipendenza dei due file]].

### Cosa sappiamo dei due canali

*(colonna FAST = misure sul run Cs-137 28100; colonna CSP = `csp.npy`)*

| | `FAST` | `CSP` |
|---|---|---|
| Forma singolo evento | 1 polo, unipolare | **unipolare, preamp di carica** (rise + fall) |
| τ da fit (rise / fall) | **17 ns / 257 ns** | **322 ns / 3787 ns** (τ_corr ≈ 2 µs) |
| PSD | Lorentziana, corner ≈ 650 kHz | ripida ~f⁻⁴, corner ≈ 100 kHz |
| Rumore elettronico σ_n | ≈ 1.5 ADC (~0.7 % var) | ≈ 5 ADC (<0.01 % var), + riga ~35–40 MHz |
| Non-gaussianità (kurt) | ≈ 0 (gaussiano) | +0.5 (leptocurtico) |
| Pileup | **profondo** (λτ ~ 70) | **moderato** |
| **Rate λ** | **~10⁸ Hz** (cumulanti+kurt; il fit dà solo lim. inf. ~10⁷) | **~0.5–1.5 MHz** (fit+CV; degenere con SER) |
| **Energia media ⟨A⟩** | degenere (solo λ⟨A²⟩ dal bulk) | ~SER-dipendente (fattore ~6) |

Entrambi i segnali sono compatibili con un **processo di Poisson filtrato**
(shot noise / Campbell): impulsi a risposta ~esponenziale che arrivano con
statistica di Poisson, sommati in pileup.

Il punto chiave: con questi dati (finestre a baseline sottratta, **senza un run di
pedestal/dark**) si misura bene la **varianza** $\lambda\langle A^2\rangle$, ma
**rate ed energia si separano solo se il segnale NON è in pileup gaussiano**.
Il CSP lo consente; il FAST no — lì serve la media (corrente DC). Vedi
[[Pile-up e occupancy]] e [[Limiti]].

### Quadro operativo: cosa sappiamo, come, con che confidenza

| Grandezza | `FAST` | `CSP` | Metodo di stima |
|---|---|---|---|
| Tipo / forma `h` | anodo 1-polo, unipolare | preamp di **carica**, unipolare | fit Optuna MSM (ACF + PSD-Wasserstein), [[Fit dei parametri]] |
| τ (rise / fall) | 17 ns / **257 ns** | 322 ns / **3787 ns** | idem; rise del CSP vincolato dalla banda media |
| Rumore σ_n | ≈ 1.5 ADC (~0.7 % var) | ≈ 5 ADC (<0.01 % var) | plateau PSD alta-f (misurato, non fittato) |
| Pileup (λτ) | **profondo, ~70** | moderato, ~3 | da λ·τ; confermato da kurtosi / CV-floor |
| **Rate λ** | **~3×10⁸ Hz** (≳10⁸; banda SER ×~6) | **~0.5–1.5×10⁶ Hz** | anode: MSSD + cumulanti pari κ₂²/κ₄ (validato 0.98) + kurt≈0. CSP: fluttuazione di potenza + fit; i cumulanti falliscono. Vedi [[Stima del rate dai cumulanti]] |
| **⟨A⟩ energia media** | ~2.7 ADC *(relativa, SER-dip.)* | non separata (degenere) | κ₄/κ₂ (even-cumulant); scala **relativa** — assoluta serve calibrazione di guadagno |
| Forma `P(A)` / SER | **non estraibile** | **non estraibile** | κ₂κ₄/κ₃² fallisce anche su sim (il pileup uccide κ₃); serve run risolto. Vedi [[Spettro di ampiezza]] |
| **Dose** ∝ λ⟨A⟩ | non misurabile in assoluto | non misurabile in assoluto | serve **pedestal/dark** (media = corrente) + calibrazione ADC→keV. Vedi [[Limiti]] |

*Grassetto = solido; corsivo = SER-dipendente (sistematico ×~6) o relativo; "non…"
= intrinsecamente non ottenibile da questi dati (pileup / manca pedestal). Cautela
anode: a λ~3×10⁸ gli eventi arrivano ogni ~3 ns < 10 ns di campionamento → ordine
di grandezza. Probabile che gli "eventi" siano fotoelettroni singoli (P(A)=SER) per
l'anode ed eventi/energia per il CSP — da confermare dal setup.*

## (b) I sei run reali a dose nota

`data/anode_waveforms/*.h5` — è il dataset che permette di *verificare* tutto,
perché conosciamo la risposta. Ogni run è $10^4 \times 2000$ campioni,
**DC-coupled** (importante: vediamo il livello continuo, non solo le
fluttuazioni). Sorgenti **Am-241 e Cs-137** a distanze diverse, cioè a **dose
nota** che spazia su ~2.5 decadi:

| nuclide | dose [µSv/h] | rate atteso λ [Mcps] | occupancy λτ | regime |
|---|---|---|---|---|
| Am-241 | 94 | 0.17 | 0.04 | impulsi **risolti** |
| Cs-137 | 616 | 1.14 | 0.26 | pile-up leggero |
| Cs-137 | 889 | 1.65 | 0.38 | pile-up leggero |
| Cs-137 | 7900 | 14.6 | 3.4 | pile-up medio |
| Cs-137 | 17990 | 33.3 | 7.7 | pile-up forte |
| Cs-137 | 28100 | 52 | 12 | pile-up **profondo** |

![[real_waveforms.png]]
*I sei run reali a dose crescente: dagli impulsi quasi risolti (dose bassa) al fuzz
continuo (dose alta).*

Il rivelatore è uno **Scionix 51B51** — e vale sapere che a questi rate lavora 8–1040×
oltre il limite dichiarato dal costruttore ([[Stato dell'arte]]) — — NaI(Tl) Ø51×51 mm (il 2×2″) su PMT Hamamatsu
R10601-100 a 10 stadi, HV negativa ([[Hardware]]). La dose qui è un **input noto** (dai metadati;
verificata con la legge dell'inverso del quadrato
$\text{dose}\approx k\cdot\text{attività}/d^2$, torna a ±6%). L'obiettivo è
**ricostruirla dal segnale** — vedi [[Stima della dose]].

Il run **Am-241** è l'unico a impulsi risolti, e per questo sta fuori dallo
stimatore statistico: è il caso in cui la distribuzione delle ampiezze è
direttamente osservabile ([[Spettro di ampiezza]], [[Simulazione SDE]]).
