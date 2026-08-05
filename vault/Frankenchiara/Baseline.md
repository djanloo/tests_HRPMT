---
type: approfondimento
project: frankenchiara
status: in-corso
updated: 2026-08-05
tags: [tipo/approfondimento, progetto/frankenchiara]
---

# La baseline: perché il valor medio non dipende dalla dose

Domanda aperta e importante, perché tocca la raccomandazione numero uno del progetto (il
dark run). **Il valor medio del segnale dovrebbe essere proporzionale alla dose**
($\kappa_1 = \lambda\langle A\rangle I_1$ per Campbell), e invece è lo stesso in tutti i run.

## L'osservazione

Media e mediana misurate sui primi 2000–3000 record di ciascun run:

| nuclide | dose [µSv/h] | mediana | **media** | p1 | p99 | max | std della media *per record* |
|---|---|---|---|---|---|---|---|
| Am-241 | 94 | 193.0 | **195.24** | 183 | 225 | 392 | 1.06 |
| Cs-137 | 616 | 3764.0 | **3786.76** | 3740 | 3975 | 4363 | 6.71 |
| Cs-137 | 889 | 167.0 | **195.21** | 129 | 429 | 1311 | 8.56 |
| Cs-137 | 7900 | 195.0 | **195.04** | 97 | 302 | 390 | 5.51 |
| Cs-137 | 17990 | 195.0 | **194.54** | 135 | 254 | 310 | 3.59 |
| Cs-137 | 28100 | 195.0 | **194.89** | 153 | 233 | 280 | 2.08 |

**La media è 195.0 ± 0.3 su 300× di dose.** E il run 616 non è un'eccezione: 3786.76 − 195.2
= 3591.6, cioè è lo *stesso* segnale su un piedistallo diverso. (La mediana invece si muove —
167 sul run 889 — ma è un effetto del pile-up sulla forma della distribuzione, non del livello.)

Una costanza allo **0.15% su 300× di rate** non può essere fisica. Se fosse
$\lambda\langle A\rangle$, con la dose che sale 300× e il gain che cala 15×
([[Gain ladder]]), la media dovrebbe salire di ~20×.

## Le ipotesi, confrontate con gli schematici

### 1. Il gain cancella esattamente il rate ($\lambda g$ = cost) — **esclusa dai dati**

Sarebbe la spiegazione elegante: in collasso $I_a$ si clampa a $I_b$, quindi
$\lambda g$ = cost e la media resta piatta. Il modello ladder lo prevede davvero.

**Ma non regge:** il run **Am-241 a 0.39 Mcps** è lontanissimo dal clamp (il ginocchio è a
~175 kcps, e con la sua energia 11× più bassa la corrente d'anodo è molto sotto $I_b$) e ha
**la stessa media** dei run in collasso profondo. Se fosse il clamp, la media dell'Am
dovrebbe essere sensibilmente più bassa. Non lo è.

### 2. Sottrazione software record per record — **esclusa dai dati**

Se ogni record fosse normalizzato alla sua media, la media *per record* sarebbe identica in
tutti. Invece **sparpaglia**, con std da 1.06 a 8.56 ADC. E lo sparpagliamento **cresce con
l'ampiezza degli impulsi** (8.56 sul run 889, che ha picchi fino a 1311 ADC; 2.08 sul 28100,
dove il gain è crollato e il massimo è 280) — cioè è la fluttuazione di shot che sopravvive.
Qualunque cosa fissi il livello, ha una **costante di tempo più lunga di un record** (20 µs).

### 3. Accoppiamento AC in catena — **esclusa dagli schematici**

Tracciata la catena FAST a 400 dpi sui fogli 10 e 9 di `7THAHELDEVXA`
([[Catena di lettura]]): `DET_IN` → **R55‖R53 = 100‖100 verso AGND** → R42/R206 (330) →
LMH6703 non invertenti → R22/R204 (33) → nodo comune → ADG619 → carrier → R169 (470) →
ADA4932. **Tutto resistivo, nessun condensatore in serie.** Gli unici condensatori sul
percorso di segnale sono C51 e C159 da 1 pF *verso massa* (compensazione), e C159 è pure
**non montato**.

### 4. Servo di DC analogico — **esclusa dagli schematici**

Il candidato naturale era il blocco `OFFSET`. Guardandolo da vicino: DAC8552 → `OFFSET` →
**OPA2192 (U34B) in buffer a guadagno unitario** (pin 6 richiuso sul pin 7) → R168 (470) →
ingresso **invertente** dell'ADA4932. È **iniezione open-loop**: non c'è nessun percorso di
ritorno dall'uscita o dal segnale verso `OFFSET`. `S1` è solo un ponticello che può mettere
l'iniezione a massa (offset on/off).

Un servo avrebbe bisogno di un integratore che *misura* la DC d'uscita e la reinietta. Non
c'è.

### 5. Baseline restorer nel firmware del digitizer — **compatibile con tutto**

È l'unica ipotesi che sopravvive, ed è anche la più banale: i digitizer CAEN hanno un
**baseline restorer** in firmware, con finestra configurabile. Con una finestra ≫ 20 µs:

- il livello a lungo termine viene inchiodato al setpoint → media 195.0 in tutti i run ✓
- la fluttuazione di shot *dentro* il record sopravvive → medie per record che sparpagliano
  in proporzione all'ampiezza degli impulsi ✓
- il setpoint è impostabile → spiega il run 616 a 3591.6 ADC più in alto ✓. Il pezzo che lo
  imposta è ora identificato: il **CAEN DT5780 ha un offset DC con DAC a 16 bit su ogni
  ingresso** ([[Catena di lettura]]). Su 14 bit di fondo scala, 195 ADC = 1.19 % e
  3764 = 22.97 %

Non compare in nessuno schematico perché è firmware. **Non l'ho verificato**: è un'ipotesi
che spiega tutte le osservazioni, non una misura.

## La conseguenza, che è grossa

[[Limiti]] elenca il **dark run** come "il singolo dato mancante più prezioso", perché
darebbe lo zero assoluto e sbloccherebbe `mean²/Var` — il solo stimatore di rate che
sopravvive al collasso del gain.

> **Se la DC è tolta da un baseline restorer, un dark run non la recupera.** Il BLR
> toglierebbe la DC anche nel dark run. Si otterrebbe lo zero *del restorer*, non lo zero
> vero.

La richiesta corretta non è "fateci un dark run" ma **"acquisite con il baseline restorer
disabilitato"** — o, in alternativa, una misura della corrente media d'anodo fatta fuori dal
digitizer (un multimetro sullo shunt). È un cambio di configurazione, non un run in più.

E cade anche l'affermazione, presente in [[Limiti]], che la media "è stata persa solo
sottraendo la baseline per-record, non è AC-coupling": la baseline per-record la togliamo
*noi* in analisi, ma la DC **non era già più nel dato**.

## Un dettaglio collaterale, spiegato

Il run **Cs-137 a 616 µSv/h ha picchi più discriminabili dell'Am-241**, che a prima vista
stupisce visto che l'Am è a rate più basso. Ma è solo energia: a ~10 pe/keV
([[Stato dell'arte]]) un evento Cs da 662 keV fa ~6600 fotoelettroni contro i ~550 di un
Am da 59.5 keV. **Gli impulsi del Cs sono ~12× più grandi**, quindi emergono dal rumore molto
meglio nonostante il rate maggiore. Si vede nella tabella: il run 889 arriva a 1311 ADC di
massimo, l'Am a 392.

## Il BLR confermato da una misura indipendente, e perché il segnale può diventare negativo

Domanda arrivata dalla collega: *a seconda dei parametri del firmware il segnale può diventare
negativo — perché?* La risposta conferma il BLR da una strada che non c'entra con la media.

### La misura: forma d'impulso media, allineata sui picchi

| run | undershoot (frazione del picco) | livello 600 ns **prima** del picco |
|---|---|---|
| Am-241, 0.39 Mcps | 0.4 % | +0.2 ADC |
| Cs-137 7900, ~15 Mcps | **13.1 %** | **−10.05 ADC** |

Il punto decisivo è la colonna di destra: ad alto rate la traccia è depressa **anche prima**
dell'impulso. Un undershoot da derivatore starebbe solo *dopo*, scalerebbe con l'impulso e ci
sarebbe anche a basso rate. Qui invece **tutto il livello di quiete è tirato giù, e solo quando
c'è attività**. È la firma di un baseline restorer che sottrae troppo.

Il meccanismo, a parole: il BLR forza media = piedistallo, quindi l'area positiva degli impulsi
**deve** essere bilanciata da un livello di quiete depresso. Più rate → più area di impulso →
depressione più profonda.

### Quanto siamo vicini allo zero

| run | piedistallo | minimo | sotto il piedistallo | margine da 0 |
|---|---|---|---|---|
| Am-241 94 | 193 | 173 | 20 | 173 |
| Cs-137 889 | 167 | 101 | 66 | 101 |
| **Cs-137 7900** | **195** | **56** | **139** | **56** |
| Cs-137 17990 | 194 | 88 | 106 | 88 |
| Cs-137 28100 | 195 | 108 | 87 | 108 |

Il rumore elettronico è σ ≈ 1.5 ADC, quindi 139 ADC sotto il piedistallo sono **90σ**: non è
rumore. E il margine da zero sul run 7900 è **56 ADC su 14 bit**, cioè 0.3 % del fondo scala.
**Non serve un meccanismo nuovo per andare negativi: basta un offset più basso o una depressione
un po' più profonda.** (Clipping non ancora presente: i valori bassi sono sparsi, passo 1 ADC.)

### Le cause possibili, in ordine di quanto i dati le sostengono

1. **Il BLR sottrae troppo** (misurato sopra). Parametri che lo governano: lunghezza della
   finestra, velocità di aggiornamento, presenza di un **hold-off durante gli impulsi**. Finestra
   corta e nessun inibit = massima sottrazione in eccesso.
2. **La polarità fisica è negativa comunque.** HV negativa e anodo su 50 Ω verso massa: gli
   elettroni che arrivano tirano l'anodo *in negativo* ([[Catena di lettura]]). Quello che vediamo
   positivo significa che qualcosa inverte, e se è un **bit di polarità** nel firmware, girarlo
   mostra il segnale vero. È la strada più banale.
3. **Un filtro di sagomatura abilitato** (trapezio, CR-RC): uscita **bipolare per costruzione**,
   e un pole-zero non compensato dà una coda negativa. Dipende da decay time e flat top.
4. **Signed vs unsigned**: se il firmware emette campioni signed già sottratti e il lettore li
   legge unsigned, non si vedono negativi ma **wraparound**. Da controllare come integrità del
   dato, visto che gli `.h5` sono `float64` — qualcuno ha convertito.

### Un tentativo di recuperare la DC, e perché muore

Se il BLR pinna la media, la **depressione** del livello di quiete *è* la DC rimossa. Misurata
come (media − moda):

| dose | 94 | 616 | 889 | 7900 | 17990 | 28100 |
|---|---|---|---|---|---|---|
| depressione [ADC] | 5.2 | 30.8 | **47.2** | 7.1 | −1.5 | −1.1 |

Non cresce con la dose, e non è un difetto del ragionamento: in **pileup profondo non esiste più
un livello di quiete**, la moda collassa sulla media perché la traccia è fuzz continuo. Quindi la
depressione misura la DC solo dove gli impulsi sono risolti — **cioè dove non ci serve**. È la
stessa forma di tutti gli altri limiti del progetto.

La via che resta: **con la mappa dei parametri del firmware il BLR diventa invertibile**, e la DC
si recupera per calcolo invece che per misura. È questo che rende la mappa un documento utile e
non solo una scheda tecnica.

## Cosa la chiuderebbe

1. **La configurazione di acquisizione** dei sei run: BLR attivo? con quale finestra? qual era
   il valore di `OFFSET` impostato dal DAC? È una domanda a chi ha acquisito, e chiude la nota.
2. Se il BLR fosse disattivabile: **due run a rate molto diversi con BLR off**. La media
   dovrebbe muoversi, e muoversi *come* $I_a(\lambda)$ del ladder — che sarebbe una verifica
   indipendente del modello di gain su una quantità che oggi buttiamo via.
3. In assenza di entrambi: misurare la corrente media d'anodo con uno strumento esterno,
   simultaneamente a un'acquisizione. Dà la costante di conversione ADC↔µA e chiude anche la
   [[Catena di lettura|calibrazione assoluta]].
