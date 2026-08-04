---
type: nota
project: frankenchiara
updated: 2026-08-03
tags: [tipo/nota, progetto/frankenchiara]
---

# Simulazione SDE del segnale PMT

Come è fatto il simulatore che genera le waveform sintetiche, e con quale
distribuzione di ampiezza. Il modello fisico sotto è quello di [[Shot noise]] e
[[Cumulanti e Campbell]]; questa nota è l'implementazione.

Codice: `sde_pulse_sim.py` (SDE a due poli), `simulate_pmt.py` (forma a
convoluzione), `energy_spectrum.py` (spettro di ampiezza), `spectra/` (gli
istogrammi).

## Due generatori, stesso processo

Il segnale è shot noise, $y(t)=\sum_k A_k h(t-t_k)+n(t)$. Ci sono due modi di
generarlo e nel repo ci sono entrambi, perché servono a cose diverse.

| | `simulate_pmt.simulate_events` | `sde_pulse_sim.simulate_sde` |
|---|---|---|
| come | convoluzione FFT dei conteggi con `h` | time-stepping dello stato |
| `h` | qualunque, passata come array | implicita: bi-esponenziale a due poli |
| unità | guadagno arbitrario, rumore in frazione di RMS | ADC fisici |
| usato da | `fit_simulator.py`, `mssd_cumulant_estimate.py` | `sde_fit.py`, `target_test/` |

La forma SDE è quella "fisica": due SDE del primo ordine accoppiate,

$$dx_1 = -\frac{x_1}{\tau_r}dt + dJ(t), \qquad dx_2 = \left(-\frac{x_2}{\tau_f} + \frac{x_1}{\tau_r}\right)dt, \qquad y = x_2$$

con $J$ Poisson composto. La waveform **emerge dallo stepping dello stato**, non
da una convoluzione con un kernel analitico: è questo che la rende estendibile
(non-linearità, saturazione, baseline restorer) senza riscrivere il generatore.

### Perché `expm` e non Euler-Maruyama

Il tratto lineare fra due salti viene avanzato con la discretizzazione **esatta**
$\Phi = \exp(M\,\Delta t)$, non con Euler. Motivo misurato, non estetico: i
$\tau_r$ fittati sui run reali stanno fra 7 e 80 ns a 100 MS/s, cioè fra **0.7 e 8
campioni** (`sde_fit_results.json`). Con $\Delta t \sim \tau_r$ Euler-Maruyama
sbaglia di parecchio e per $\Delta t > 2\tau_r$ diverge, mentre `expm` è esatto
per costruzione a qualunque $\Delta t$. Resta un integratore di SDE — soluzione
esatta del segmento lineare fra i salti — non una convoluzione.

Il costo è un `Phi @ x` per campione, quindi il loop su `n_samp` è vettorizzato
sui record (`X` è `(n_rec, 2)`): 1000 record × 2000 campioni girano in pochi
secondi.

## Le marche $A_k$: qui stava il problema

Fino al 2026-08-03 le marche erano **Gamma** con media `ser_mean` e CV `ser_cv`.
La scelta non era fisica, era computazionale: la Gamma è chiusa sulla somma,

$$\sum_{i=1}^{c} \mathrm{Gamma}(k,\theta) = \mathrm{Gamma}(c\,k,\theta)$$

quindi la carica aggregata di un bin temporale con $c$ eventi si estrae in **un
solo sorteggio**, senza mai generare i singoli eventi. Elegante e veloce.

**Ma è il modello sbagliato.** Uno spettro di ampiezza reale ha fotopicchi, un
continuo Compton, picchi di fuga, righe X. Una Gamma è una gobba liscia: non ha
niente di tutto questo. In pileup profondo ($\lambda\tau \gg 1$) il teorema del
limite centrale nasconde la differenza e la Gamma passa; **a basso rate no**,
perché lì gli impulsi sono risolti e le loro altezze *sono* lo spettro, che
diventa direttamente osservabile. È esattamente il regime del run **Am-241 a 94
µSv/h**, quello che `dose_pipeline` già si rifiuta di trattare statisticamente
(§5 di `dose_estimation/dose_report.md`).

### Lo spettro empirico

`energy_spectrum.Spectrum` è un istogramma di altezza d'impulso, riscalato a
$\langle A\rangle = 1$. Così `ser_mean` conserva il suo significato (picco medio
in ADC) e lo spettro fornisce solo la *forma* — cioè esattamente i momenti
normalizzati $m_n = \langle A^n\rangle/\langle A\rangle^n$ che serve al teorema di
Campbell.

Il campionamento è CDF inversa sull'indice di canale più jitter uniforme dentro
il canale: il bin dell'MCA è una quantizzazione di un'ampiezza continua, non una
delta, e $U[i,i+1)$ ha media $i+\tfrac12$, che è il centro-bin usato da `scale` e
`moment`. Coerente per costruzione, quindi `sample()` riproduce i momenti
dell'istogramma a meno dell'errore MC.

Persa la chiusura della Gamma, l'aggregazione per bin si fa in modo esatto e
generale (`poisson_marks`): conteggi di Poisson per bin → altrettanti sorteggi
iid dallo spettro → `bincount` per rimetterli nei loro bin. Nessuna
approssimazione a nessun rate; il costo è generare $\sim\lambda\,\Delta t\,N$
eventi, trascurabile finché $\lambda\Delta t \ll 1$.

La Gamma **è rimasta** come default (`spectrum=None`): `sde_fit.py` e
`fit_simulator.py` fittano `ser_cv` ([[Fit dei parametri]]) e i loro `*_results.json` la
contengono.

## Gli spettri: due provenienze, da non confondere

### (a) Misurati — CAEN DDE

In `spectra/`, dal software di controllo del **Digital Detector Emulator**
(DT4800, `examples/spectra/`) — sono gli istogrammi da cui il DDE stesso
sintetizza gli impulsi, quindi sono esattamente la distribuzione che si
otterrebbe pilotando la scheda. Due formati, entrambi 16384 canali, entrambi
letti da `load()`: un count per riga (`.csv`, export DDE) e ANSI N42.42 con i
conteggi in `<ChannelData>` (`.xml`, export MC2 / DT5780).

| file | sorgente | CV | $m_2$ | $m_4$ |
|---|---|---|---|---|
| `Fe55.csv` | 5.9 keV, riga singola stretta | 0.14 | 1.02 | 1.09 |
| `Co57.csv` | NaI, 122 keV dominante + coda bassa | 0.38 | 1.15 | 1.66 |
| `co60HPGE.xml` | Co60 su HPGe, righe strette | 0.61 | 1.37 | 4.10 |
| `complex.csv` | miscela multi-nuclide, molti picchi | 0.72 | 1.51 | 5.83 |
| `Co60LowRes.csv` | NaI, 1173+1332 fusi, Compton largo | 0.75 | 1.56 | 5.30 |
| `EU-HPGE.xml` | Eu152 su HPGe, ~10 righe | 1.70 | 3.90 | **117** |

Scartati: `cobalto.csv` (byte-identico a `Co60LowRes.csv`) e i `*.spectrum`
(`Type=Peaks`: una lista di picchi sintetica, non un istogramma misurato).

### (b) Modellati — Cs137 e Am241 su NaI

**Il DDE non ha né cesio né americio**, e `isodb.mdb` non contiene dati di riga
leggibili. Ma i run reali sono **proprio Cs-137 e Am-241 su NaI 2×2″**
([[Rivelatore e dati]]), quindi servivano. `energy_spectrum.nai()` li costruisce da
fisica nota, con Monte Carlo sui canali di deposito:

- **fotopicco** a $E_0$ (661.657 / 59.541 keV);
- **continuo Compton** dalla sezione d'urto di **Klein-Nishina**, campionata per
  reiezione su $d\sigma/dP$ con $P=E'/E_0$; l'energia depositata è il rinculo
  dell'elettrone $T=E_0(1-P)$, quindi la spalla cade da sé alla **spalla Compton**
  $T_{max}=E_0\,2a/(1+2a)$ = 477 keV per il Cs-137;
- **picco di backscatter** a $E_0/(1+2a)$ = 184 keV (fotoni retrodiffusi da
  schermo e sorgente);
- **riga X** (32 keV Ba-K per il Cs, ~17 keV Np-L per l'Am);
- **risoluzione** del rivelatore, FWHM$/E = R_{662}\sqrt{662/E}$ con $R_{662}=8\%$
  → ~27% a 59.5 keV.

| | CV | $m_2$ | $m_4$ | fotopicco ricostruito |
|---|---|---|---|---|
| `Cs137(NaI,sim)` | 0.665 | 1.44 | 4.08 | 663.6 keV (661.7) |
| `Am241(NaI,sim)` | 0.252 | 1.06 | 1.29 | 59.4 keV (59.5) |

**Sono un modello, non una misura**, e vanno dichiarati tali in ogni risultato che
ne dipende: portano `.synthetic = True`, il `repr` dice `MODELLO` e il nome ha il
suffisso `(NaI,sim)`. Tutti i pesi in `NUCLIDES` sono override da keyword —
photofraction, backscatter, riga X, risoluzione sono manopole di taratura per un
cristallo, una geometria e uno schermo reali, non costanti di natura. Il default
`photofrac=0.30` a 662 keV è il peak-to-total tipico di un 2×2″.

### Il numero che conta: $m_4$

La colonna $m_4$ è la ragione per cui questo lavoro non è cosmetico (contesto completo
in [[Spettro di ampiezza]]).
`mssd_cumulant_estimate.py` stima il rate come
$\lambda = (\kappa_2^2/\kappa_4)\,(m_4 S_4)/(m_2^2 S_2^2)$: **$m_4$ entra
linearmente nella stima**. Una Gamma con CV 0.5 dà $m_4 = 3.28$; l'Eu152 su HPGe
dà **117**, un fattore **36**. Assumere una Gamma su una sorgente multi-riga
sbaglia il rate di oltre un ordine di grandezza, e non è un errore che si vede dai
residui: la sua unica traccia è la sistematica sul rate. È già scansionata come
sistematica in `mssd_cumulant_estimate.run` — ma *dentro la famiglia Gamma*, cioè
su un solo parametro, che non può contenere un fattore 36. Vedi [[Backlog]].

Un secondo indizio nella stessa direzione: i `ser_cv` fittati sui cinque run
Cs-137 vanno da **0.13 a 1.28** senza alcuna monotonia nella dose
(`sde_fit_results.json`). Un parametro fisico del rivelatore non si muove così: è
il sintomo di una famiglia a un parametro costretta ad approssimare una forma che
non le appartiene.

## Cosa verificano i controlli

`python energy_spectrum.py` (`--plot` per la figura). I punti 2-4 girano
sull'**Am-241**, che è il run reale a impulsi risolti:

1. tutti gli spettri della raccolta caricano, in entrambi i formati; sui
   modellati, il fotopicco cade sul canale giusto (entro il 3%) e la spalla
   Compton è al posto giusto (peso sotto i 477 keV 55× la valle sopra);
2. `sample()` riproduce media, $m_2$ e $m_4$ dell'istogramma (2M campioni);
3. **il controllo che conta** — a basso rate ($\lambda = 1.7\cdot10^5$ Hz, il rate
   del run Am-241 a 94 µSv/h) le altezze di picco estratte dalla waveform con
   `find_peaks` ricostruiscono lo spettro d'ingresso: media 98.5 ADC contro 100
   attesi, e **la struttura sopravvive** — riga X, fotopicco e la valle profonda
   fra i due;
4. Campbell: $\mathrm{var}(y) = \lambda\langle A^2\rangle I_2$ con
   $\langle A^2\rangle$ preso dallo spettro, rapporto misurato/previsto 0.92.

![[energy_spectrum.png]]

Il punto 3 è scritto come un test che **la Gamma non passa**, ed è verificato che
non la passi. Con lo spettro Am-241: riga X a densità 5.5e-3, valle 2.8e-5.
Con una Gamma di CV identica: riga X 5.5e-4 (dieci volte più bassa, cioè assente)
e valle 7.2e-3 (riempita). L'assert `riga X persa` scatta.

Le discrepanze residue dei punti 3-4 sono attese e note, non da inseguire:

- media di picco e CV leggermente spostate perché la soglia di `find_peaks` taglia
  la coda di bassa ampiezza e il pileup residuo somma coppie di impulsi vicini;
- varianza bassa dell'8% perché `simulate_sde` rimuove la media per record e gli
  impulsi a inizio record sono troncati (lo stato parte da zero).

Sono le stesse due distorsioni che agiscono sui dati reali, quindi il posto giusto
in cui tenerne conto è la stima, non il simulatore.

