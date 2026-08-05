---
type: nota
project: frankenchiara
updated: 2026-08-05
tags: [tipo/nota, progetto/frankenchiara]
---

# La catena di lettura

Cosa stiamo leggendo, e come: il percorso del segnale dall'anodo all'ADC, tracciato sugli
schemi. Il *rivelatore* che lo produce sta in [[Hardware]].

Documenti in `hardware/`.

## La catena

```
sorgente → scintillatore NaI 2×2″ → PMT (fotocatodo + ~10 dinodi, G ~ 10⁶)
                                        ↓ anodo
                          ┌─────────────┴─────────────┐
                          ↓                           ↓
              resistenza di shunt              CSP (preamp di carica)
              V = R·I, nessun filtro           integra la corrente
                          ↓                           ↓
                    → DIGITIZER                 → (non usato)
                      100 MS/s, DC-coupled
```

## Quale board: la Handheld, non la GammaStream

Confronto degli schemi, che risolve la domanda:

| | Scionix + Handheld (usata) | S2580 GammaStream |
|---|---|---|
| polarità HV | **negativa** | **positiva** (+HV entra sul lato anodo via R5/R6) |
| accoppiamento anodo | **DC**, 50 Ω | **AC**, via C2 = 10 nF |
| carico d'anodo | **50 Ω** (R55‖R53 sull'handheld) | R11 = 49.9 Ω *dopo* il condensatore |
| partitore | 180K/850K/1M/1M/470K×6 — ΣR 5.85 MΩ | 100K + 270K×10 + trimmer 500K — ΣR ≈ 3.3 MΩ |
| front-end | LMH6703/ADA4857 veloce (×1/×4) **+** AD8065 CSP | **solo** CSP (AD8065, due τ ≈ 11 µs via relè K1) |
| ramo FAST | sì, separato | **non esiste** |

Le due prove che escludono la GammaStream: (i) non ha un ramo veloce, e la sua unica uscita
(CSP, τ ≈ 11 µs) non può dare il τ = 250 ns del ramo FAST — mentre noi abbiamo *entrambi*
i file; (ii) accoppia in AC, e i nostri dati sono DC-coupled. Coerente col resto: lo Scionix ha
il partitore **integrato** e due soli cavetti (RG174 rosso = HV, giallo = segnale), che è quello
che l'handheld si aspetta su `DET_IN`, mentre la S2580 è una base per PMT nudo.

> **Lo shunt è quindi 50 Ω.** $R_L$ = 100 kΩ nella base ‖ 50 Ω di terminazione = 49.98 Ω: i
> 100 kΩ sono irrilevanti. L'ADC vede $50\,\Omega \times I_a \times G_\text{el}$, con
> $G_\text{el}$ = 1 o 4.

## La catena di lettura, tracciata

Dai fogli 9–11 di `7THAHELDEVXA-0-0.pdf` (**Handheld EVM / FRANKENSTEIN**, gennaio 2025).
I fogli 10 e 11 sono **la stessa topologia con due op-amp alternativi** — `Preamp type 1` =
LMH6703, `Preamp type 2` = ADA4857 — quindi la traccia vale comunque, e quale sia montato
resta da confermare.

```
anodo Scionix (HV negativa)
  → R_L 100 kΩ verso massa                      (nella base Scionix)
  → 20 cm RG174 giallo
  → J59/J66  "DET_IN"                           (ingresso handheld)
  → terminazione R55‖R53 = 100‖100 = 50 Ω       ← IL CARICO VERO
  → R 330 → op-amp veloce, DUE canali in parallelo:
        /FG1 → G = 1     (Rf=330, Rg=110 NON MONTATO → anello aperto)
        /FG4 → G = 4     (1 + 330/110)
        selezione spegnendo l'altro (pin SD)
  → nodo comune (R 33 in serie su ciascuna uscita)
  ├── ramo FAST : → J2/J26  "FAST"              (uscita diretta, nessuna sagomatura)
  └── ramo CSP  : → R 49.9 → AD8065ARTZ integratore
                   feedback 33 kΩ ‖ 330 pF (×2 rami) → τ_CSP = 10.9 µs
                   reset con relè K1/K2 (5-1462037-4) via CSP_SET / CSP_RES
  → ADG619BRMZ (switch analogico SPDT) + jumper J4/J27 «1-2 CSP / 2-3 FAST»
  → J56/J63 → "Vpreamp" sul carrier
  → R 470 → ADA4932-1YCPZ (driver differenziale)
  → 22 Ω + 12 pF (anti-alias, f_c ≈ 600 MHz)
  → VADC_P / VADC_N                             (ADC differenziale)
```

In più, sul carrier (foglio 9): un **DAC8552** genera `OFFSET` → OPA2192 → `VCM` = 0.95 V, e
anche `LED_SHAPE` (la forma dell'impulso del LED). Le linee `CSP/FAST`, `/FG1`, `/FG4` passano
per **relè photoMOS AQY221N2S** pilotati da un expander I²C **TCA9534**: la selezione del
percorso e del guadagno è **software**.

## Cosa dice la traccia, in cinque punti

1. **Il carico d'anodo vero è 50 Ω**, non i 100 kΩ della base: i due 100 Ω di terminazione in
   parallelo danno 50 Ω, e 100 kΩ ‖ 50 Ω = 50 Ω. Quindi $V = R\,I$ con **R = 50 Ω**.

2. **"Nessuna filtrazione" è confermato e quantificato.** LMH6703 ha 1.2 GHz di banda,
   ADA4857 ~750 MHz, l'anti-alias sta a 600 MHz: **12× oltre il Nyquist** dei 50 MHz. Il ramo
   FAST non sagoma niente.

3. **Il τ ≈ 250 ns è la scintillazione, definitivamente.** Con 50 Ω e i ~20 pF dei 20 cm di
   RG174 l'RC vale **1 ns**: l'elettronica è 260× più veloce del τ osservato. Non può essere
   lei. Il NaI(Tl) decade con 230 ns.

4. **Il guadagno elettronico è 1 o 4, e si cambia da software.** ⚠️ Questo tocca
   [[Gain ladder]]: il proxy $g \propto \sqrt{\text{Msd}/\text{dose}}$ assume che il guadagno
   *elettronico* sia lo stesso fra i run, e l'hardware ha uno **scalino ×4**. Il run 616, che
   ho attribuito a "HV diversa" per la baseline 3764 contro ~195, potrebbe essere invece un
   altro settaggio di guadagno o di offset.

5. **La baseline non è la corrente d'anodo**, ed è un problema aperto grosso. La catena **è**
   DC-coupled — verificato qui sopra: nessun condensatore in serie, nessun servo analogico,
   e l'`OFFSET` del DAC entra open-loop attraverso un buffer a guadagno unitario. Eppure la
   media misurata è **195.0 ± 0.3 ADC su 300× di dose**. Quindi la componente continua viene
   rimossa **a valle dell'analogico**, quasi certamente da un baseline restorer in firmware.
   Tutto in [[Baseline]], compresa la conseguenza: il dark run raccomandato in [[Limiti]]
   **non basterebbe**.

E una spiegazione che mancava:

6. **Perché il CSP è inutilizzabile, in un numero.** τ_CSP = 10.9 µs contro un record di
   20 µs: **1.8 costanti di tempo per record**. Non puoi caratterizzare un processo da 10.9 µs
   in una finestra da 20. È la radice di tutto ciò che si osserva sul canale CSP —
   $N_\text{eff} \approx 6.6$, $\kappa_4$ distorto, MSSD inservibile
   ([[Stima del rate dai cumulanti]]) — e anche del perché il fit trovava
   τ_fall = 3.8 µs, cioè 2.9× meno del valore di progetto: in 20 µs quella coda non è
   misurabile.

## Il segnale che analizziamo: shunt all'anodo

**È preso da una resistenza di shunt sull'anodo**: la corrente d'anodo attraversa una
resistenza e si digitizza la tensione ai suoi capi, $V = R\,I$. **Nessuna
filtrazione, nessuna elettronica di forma in mezzo.**

Conseguenze, e sono quelle che rendono possibile tutto il resto del progetto:

- la banda è quella del rivelatore, non di uno shaper: $\tau_\text{fall} \approx 250$ ns
  con un rise di poche decine di ns ([[Rivelatore e dati]]);
- il segnale è **DC-coupled** fin qui, quindi il livello continuo *sarebbe* fisico — la
  corrente media d'anodo, $\lambda\langle A\rangle$ per Campbell. **Ma nel dato salvato non
  c'è più**: vedi [[Baseline]], ed è la ragione vera per cui `mean²/Var` non si chiude;
- $V = R\,I$ è lineare, quindi la statistica del segnale **è** la statistica della
  corrente: nessuna funzione di trasferimento da invertire prima di applicare
  [[Cumulanti e Campbell]];
- la granularità di singolo fotoelettrone sopravvive, ed è per questo che a basso rate
  un evento si vede come un *burst* di spike e non come un impulso liscio
  ([[Misure a basso rate]]).

Dato: `data/anode_waveforms/*.h5` (i 6 run a
dose nota).

## Il CSP, e perché sta fuori

A valle dello stesso anodo c'è anche un **preamplificatore di carica** (CSP), che
**integra** la corrente invece di leggerla: risposta unipolare con rise ~0.7 µs e fall
~2.4 µs, cioè un $\tau_\text{corr}$ di qualche µs contro i 250 ns dello shunt.

**Non è la strada, e il motivo è di banda.** Il CSP è troppo lento e troppo filtrato per
portare informazione utile ad alto rate:

- la sua finestra di integrazione è più larga della spaziatura fra eventi già a rate
  moderati, quindi il pile-up è dentro la risposta e non lo si può sciogliere;
- filtrando via l'alta frequenza si butta esattamente la parte del segnale che porta
  l'informazione di conteggio. Si vede nei numeri: sul dato CSP gli incrementi sono
  *lisci*, $\kappa_4[\Delta y] \approx 0$ (bootstrap 14% > 0), e la stima MSSD del rate
  **non è utilizzabile** — mentre sullo shunt, col rise risolto in ~1.6 campioni, la
  stessa stima funziona ([[Stima del rate dai cumulanti]]);
- in una finestra da 20 µs il CSP ha solo $N_\text{eff} \approx 6.6$ tempi di
  correlazione indipendenti, contro 67 dello shunt: pochissimi gradi di libertà, quindi
  stime dei momenti alti rumorose e distorte.

Dato: `csp.npy`. **Serve solo da riferimento** — per mostrare cosa succede quando si
filtra, e come contro-prova che il modello shot-noise regge anche su una $h$ diversa
([[Fit dei parametri]]). Nessun risultato del progetto ci passa.

> In una riga: lo shunt vede la corrente, il CSP vede il suo integrale. A questi rate
> l'informazione sta nella corrente.

## La calibrazione assoluta è ora a portata

Sapendo che il carico è 50 Ω, la carica di un evento si calcola in unità fisiche — cosa che
[[Limiti]] elencava come non ottenibile senza dark run:

$$ Q = N_{\text{ADC·campioni}} \times \text{LSB} \times \frac{\Delta t}{R_s\,G_\text{el}} $$

Col fotopicco Am-241 misurato a 1146 ADC·campioni ([[Misure a basso rate]]), $G_\text{el}=1$,
$\Delta t$ = 10 ns, $R_s$ = 50 Ω e ipotizzando un ADC a 12 bit / 2 V fondo scala
(LSB = 488 µV): $Q$ = 112 pC = 7.0×10⁸ elettroni. Con 6–10 pe/keV a 59.5 keV sono 360–595
fotoelettroni, quindi

$$ G_\text{PMT} = 1\text{–}2 \times 10^6 $$

che per un tubo a −570 V è **esattamente l'ordine giusto**: è una verifica di consistenza di
tutta la catena, non solo un numero.

Manca **un solo dato**: il fondo scala vero dell'ADC (fogli 3–5 dei PDF, non ancora aperti).
Con quello escono energia assoluta e guadagno assoluto senza dark run. Vedi [[Backlog]].

## Il digitizer: CAEN DT5780

Dichiarato dal committente il 2026-08-05: il digitizer — **e probabilmente anche l'alta
tensione** — è un **CAEN DT5780**, *Dual Digital Multi Channel Analyzer (HV & Preamplifier PS)*.
Non è fra i PDF in `Hardware/`, ma la scheda tecnica CAEN chiude o cambia diverse cose:

| specifica DT5780 | cosa risolve qui |
|---|---|
| 2× digitizer **100 MS/s, 14 bit**, ingressi single-ended BNC | **conferma i 100 MS/s** (fin qui solo assunti, sostenuti dai 230 ns del NaI) **e i 14 bit** (fin qui dedotti dal massimo osservato 4363 > 4095) |
| **range d'ingresso a 4 passi, configurabile via software** | un *secondo* controllo di guadagno, oltre al ×1/×4 della board di preamp |
| **offset DC regolabile con un DAC a 16 bit su ogni ingresso** | è il meccanismo del piedistallo: 195 ADC = 1.19 % del fondo scala, 3764 = 22.97 % ([[Baseline]]) |
| 2 canali **HV fino a ±5 kV**, uscite SHV | il "forse anche l'HV" è sì: una scatola fa entrambe le cose |
| alimentazione preamp **±12 V / 100 mA e ±24 V / 50 mA** su DB9 | è ciò che alimenterebbe i `±V_ANL` della board di preamp |
| 2 MCA digitali indipendenti da 16k, coincidenze/anticoincidenze | — |

**Una corroborazione che era già nel repo e non avevo collegato:** l'export N42 fra gli spettri
del DDE (`co60HPGE.xml`) dichiara `RadInstrumentModelName: DT5780P_358` e
`RadInstrumentComponentName: CAEN MC2 Software`. Un DT5780 era già passato da queste parti.

### Cosa questo cambia

1. **I 100 MS/s non sono più un'assunzione.** Cade la voce di [[Backlog]] che chiedeva di
   confermarli, e con essa il rischio di dover riscalare ogni τ e ogni λ di 1.54.
2. **14 bit confermati** → il fondo scala è 16383, e con il range d'ingresso noto l'LSB è
   determinato. La calibrazione assoluta (sotto) dipende ora da **un solo numero da chiedere**:
   quale dei 4 range era selezionato.
3. **Il baseline restorer è coerente**: la catena di firmware CAEN (DPP) ne ha uno con finestra
   configurabile, ed è l'ipotesi che [[Baseline]] tiene in piedi.
4. ⚠️ **Contraddice in parte la conclusione "la board è la Handheld"** che avevo tratto dagli
   schematici. Le due cose però possono convivere: il DT5780 fornisce HV e alimentazione preamp
   e fa la digitizzazione, mentre le board di preamp fanno il CSP/FAST — e la voce "alimentazione
   preamp su DB9" dice proprio che è un uso previsto. Ma l'Handheld EVM ha un ADC **proprio**
   (coppie LVDS D0..D13), quindi è un sistema autosufficiente. **Quale dei due ha digitizzato
   questi run va confermato**, e la mia deduzione precedente va considerata non conclusiva.

### La calibrazione assoluta, ora a un numero di distanza

Con 14 bit, dal fotopicco Am-241 a 1146 ADC·campioni su 50 Ω ([[Misure a basso rate]]),
$G_\text{el}=1$ e 10 pe/keV:

| range d'ingresso | LSB | $G_\text{PMT}$ implicito |
|---|---|---|
| 0.5 Vpp | 30.5 µV | 7.3×10⁴ |
| 1.4 Vpp | 85.4 µV | 2.1×10⁵ |
| 3.7 Vpp | 225.8 µV | **5.4×10⁵** |
| 9.5 Vpp | 579.8 µV | **1.4×10⁶** |

Solo gli ultimi due danno un guadagno plausibile per un PMT a 10 stadi a −570 V. Quindi
**sapere quale range era impostato chiude il guadagno assoluto** — e i due candidati restanti
differiscono di 2.6×, che è meno dell'incertezza sui pe/keV. In pratica: *il guadagno assoluto è
1–2×10⁶ e la calibrazione è già quasi fatta*.

(I valori dei 4 range non li ho verificati sul manuale: quelli in tabella sono i tipici di
questa famiglia. Va confermato insieme al range selezionato.)

## Elettronica di lettura

- `WS2580PARTAA-0-3.pdf` — CAEN **S2580, "PMT base for GammaStream"**, foglio *HV divider
  and preampli*: una base con partitore **e preamplificatore** (op-amp AD8065).
- `WS2580BASEIN-1-0.pdf` — CAEN **motherboard GammaStream**, foglio *input ch and ADC*:
  ADC **AD9629BCPZ-65** (12 bit, 65 MSPS).
- `7THAHELDEVXA-0-0.pdf`, `BHAHELDDEV01-0.PDF` — CAEN **Handheld EVM**, gennaio 2025,
  nome in codice **FRANKENSTEIN** (da cui il nome di questo progetto). Nei net-label
  compaiono `DET IN`, **`CSP`**, **`FAST`**, `SHAPE`, `TRIG`, `Vpreamp`, `LED`, e un
  selettore `CSP/FAST/FG4/FG1`.

> **`CSP` e `FAST` sono i nomi che l'hardware dà ai due percorsi**, e mappano sui due file:
> `csp.npy` è il ramo CSP, e i run `.h5` sono il ramo FAST. Meglio usare questi nomi che
> "shunt" e "preamp".

*Cautela su questi tre PDF: ne ho estratto le **etichette testuali**, non la topologia —
non ho tracciato le net. E sono board diverse: quale abbia preso questi dati va confermato.*

