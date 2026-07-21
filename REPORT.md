# Caratterizzazione del rumore PMT come processo stocastico

**Dati:** `anodewaves.npy`, `culoculo.npy` — ciascuno 1000 record × 2000 campioni,
`float64`, ADC interi. `fs = 100 MS/s` → `dt = 10 ns`, finestra = **20 µs**/record.
I due file sono **indipendenti** (test rigoroso in §0.1): due canali/run diversi.

Le forme d'onda registrate (10 record, normalizzati e impilati): **continuo** =
`anodewaves` (fuzz veloce, τ~250 ns), **tratteggio** = `culoculo` (wandering
lento, integrazione del preamp di carica, τ~µs).

![segnali grezzi](signals.png)

---

## 0. TL;DR

Entrambi i segnali sono compatibili con un **processo di Poisson filtrato**
(shot noise / Campbell): impulsi a risposta ~esponenziale che arrivano con
statistica di Poisson, sommati in pileup.

| | `anodewaves` | `culoculo` |
|---|---|---|
| Forma singolo evento | 1 polo, unipolare | **unipolare, preamp di carica** (rise + fall) |
| τ da fit (rise / fall) | **17 ns / 257 ns** | **322 ns / 3787 ns** (τ_corr ≈ 2 µs) |
| PSD | Lorentziana, corner ≈ 650 kHz | ripida ~f⁻⁴, corner ≈ 100 kHz |
| Rumore elettronico σ_n | ≈ 1.5 ADC (~0.7 % var) | ≈ 5 ADC (<0.01 % var), + riga ~35–40 MHz |
| Non-gaussianità (kurt) | ≈ 0 (gaussiano) | +0.5 (leptocurtico) |
| Pileup | **profondo** (λτ ~ 70) | **moderato** |
| **Rate λ** | **~10⁸ Hz** (cumulanti+kurt; fit dà solo lim.inf. ~10⁷) | **~0.5–1.5 MHz** (fit+CV; degenere con SER) |
| **Energia media ⟨A⟩** | degenere (solo λ⟨A²⟩ dal bulk) | ~SER-dipendente (fattore ~6) |

Il punto chiave (§4): con questi dati (finestre a baseline sottratta, **senza
un run di pedestal/dark**) si misura bene la **varianza** `λ⟨A²⟩`, ma **rate ed
energia si separano solo se il segnale NON è in pileup gaussiano**. `culoculo`
lo consente; `anodewaves` no — lì serve la media (corrente DC).

### Quadro operativo: cosa sappiamo, come, con che confidenza

| Grandezza | `anodewaves` | `culoculo` | Metodo di stima |
|---|---|---|---|
| Tipo / forma `h` | anodo 1-polo, unipolare | preamp di **carica**, unipolare | fit Optuna MSM (ACF + PSD-Wasserstein), §6 |
| τ (rise / fall) | 17 ns / **257 ns** | 322 ns / **3787 ns** | idem; rise culoculo vincolato dalla banda media (§6) |
| Rumore σ_n | ≈ 1.5 ADC (~0.7 % var) | ≈ 5 ADC (<0.01 % var) | plateau PSD alta-f (misurato, non fittato), §6–7 |
| Pileup (λτ) | **profondo, ~70** | moderato, ~3 | da λ·τ; confermato da kurtosi / CV-floor |
| **Rate λ** | **~3×10⁸ Hz** (≳10⁸; banda SER ×~6) | **~0.5–1.5×10⁶ Hz** | anode: MSSD + cumulanti pari κ₂²/κ₄ (validato 0.98) + kurt≈0. culoculo: fluttuazione potenza (CV, §3) + fit (§6); i cumulanti falliscono (§7) |
| **⟨A⟩ energia media** | ~2.7 ADC *(relativa, SER-dip.)* | non separata (degenere) | κ₄/κ₂ (even-cumulant); scala **relativa** — assoluta serve calibrazione guadagno |
| Forma `P(A)` / SER | **non estraibile** | **non estraibile** | κ₂κ₄/κ₃² fallisce anche su sim (il pileup uccide κ₃); serve run risolto, §8 |
| **Dose** ∝ λ⟨A⟩ | non misurabile in assoluto | non misurabile in assoluto | serve **pedestal/dark** (media = corrente) + calibrazione ADC→keV, §9 |

*Grassetto = solido; corsivo = SER-dipendente (sistematico ×~6) o relativo; "non…" = intrinsecamente non ottenibile da questi dati (pileup / manca pedestal). Cautela anode: a λ~3×10⁸ gli eventi arrivano ogni ~3 ns < 10 ns di campionamento → ordine di grandezza. Probabile che gli "eventi" siano fotoelettroni singoli (P(A)=SER) per l'anode ed eventi/energia per culoculo — da confermare dal setup.*

---

## 0.1 I due file sono indipendenti (non è un file la versione filtrata dell'altro)

Graficando 5 record normalizzati sovrapposti *sembra* che i trend lenti si
somiglino. **È un artefatto di campionamento**, non correlazione reale. Verifica:

- **Coerenza spettrale** `γ²(f)` mediata su tutti i 1000 record: **piatta al
  floor `1/N`≈0.001 a ogni frequenza** (0–50 MHz). Se un file fosse la versione
  filtrata dell'altro, o condividessero una modulazione lenta comune, si vedrebbe
  `γ²→1` a bassa frequenza. Non c'è.
- **Test allineati vs mescolati.** Correlazione per-record del trend (<300 kHz):
  accoppiando `c[i]`–`a[i]` → media 0.00, **std 0.32**; accoppiando a caso
  `c[perm]`–`a[i]` → media 0.00, **std 0.32**. Distribuzioni **identiche** →
  l'indice di record non porta informazione → indipendenti.
- Di conseguenza il **14 % dei record ha |r|>0.5 per puro caso** (identico nel
  mescolato). Scegliendone 5 a occhio se ne trovano sempre alcuni "che tornano"
  (e altrettanti che si oppongono, r≈−0.77).

**Perché così tanta correlazione spuria:** `culoculo` ha `N_eff≈6.6` oscillazioni
lente *indipendenti* per finestra da 20 µs (§3). La correlazione tra due tracce
con ~6 gradi di libertà ha spread di sampling `≈1/√6≈0.4` — esattamente lo 0.32
osservato. Pochi "wiggle" per finestra ⇒ tante coincidenze.

![test indipendenza](independence_test.png)

---

## 1. Il modello: Poisson filtrato (shot noise)

Il segnale d'anodo di un PMT è una sovrapposizione di impulsi:

$$ y(t) = \sum_k A_k\, h(t-t_k) + n(t) $$

- `t_k` — tempi d'arrivo, processo di **Poisson** di rate `λ` (fotoelettroni/eventi);
- `A_k` — carica per evento (∝ energia), iid con distribuzione SER, momenti `⟨Aⁿ⟩`;
- `h(t)` — **risposta a singolo evento** (rivelatore+elettronica), integrali di forma `Iₙ = ∫hⁿ dt`;
- `n(t)` — rumore elettronico (bianco e/o colorato).

### Teorema di Campbell (cumulanti di y)
$$ \kappa_1 = \lambda\langle A\rangle I_1 + b,\quad
   \kappa_2 = \lambda\langle A^2\rangle I_2,\quad
   \kappa_n = \lambda\langle A^n\rangle I_n $$

Per `h` esponenziale a un polo, `h(t)=e^{-t/τ}`, l'**autocovarianza** è
$$ C(\Delta) = \lambda\langle A^2\rangle\,\tfrac{\tau}{2}\,e^{-|\Delta|/\tau} $$
cioè un processo con ACF esponenziale = **Ornstein–Uhlenbeck** guidato da Poisson
composto. È esattamente ciò che si osserva in `anodewaves` (τ = 250 ns).

Il "rumore autocorrelato/colorato" che vedi **è il processo stesso**: la
colorazione nasce dal filtro `h`, non da un rumore additivo colorato (che è
presente ma sottodominante). Vedi PSD: Lorentziana pura (anode) e a più poli
(culoculo), coerenti con `|H(f)|²`.

---

## 2. MSSD di von Neumann e disaccoppiamento rate / energia

**Mean Square of Successive Differences:**
$$ \text{MSSD} = \frac{1}{N-1}\sum_i (x_{i+1}-x_i)^2 = 2\,[C(0)-C(\delta)] $$
Rapporto di **von Neumann** `VN = MSSD / (2·Var)` → 1 per dato bianco, < 1 se
c'è correlazione seriale. Misurati:

- `anodewaves`: VN = 0.0225 → `C(δ)/C(0) = 0.977` (τ ≫ δ, come atteso);
- `culoculo`: VN = 2.4·10⁻⁴ → `C(δ)/C(0) = 0.9998` (fortemente sovracampionato).

### Perché la MSSD serve in dosimetria (il metodo che citavi)
In modo-corrente, con `h` fissata, valgono due osservabili **indipendenti**:

$$ \underbrace{m = \lambda\langle A\rangle I_1}_{\text{media (corrente DC)}}
   \qquad
   \underbrace{v = \lambda\langle A^2\rangle I_2}_{\text{varianza}\;\approx\;\text{MSSD}} $$

da cui il **disaccoppiamento**:

$$ \boxed{\;\bar E \;\propto\; \frac{v}{m} \;\propto\; \frac{\langle A^2\rangle}{\langle A\rangle}\;}
   \quad\text{(energia media, indip. dal rate)} $$
$$ \boxed{\;\lambda \;\propto\; \frac{m^2}{v}\;}
   \quad\text{(rate, indip. dall'energia)} $$

e per consistenza `dose ∝ λ·Ē ∝ m` (la sola corrente). **La MSSD si usa al posto
della varianza semplice perché usa solo differenze successive → cancella derive
lente** (1/f, termiche, baseline wander) che gonfierebbero `v`. Questo è il
contributo di von Neumann.

### Limite trovato su QUESTI dati
1. **Manca `m`.** I record sono a baseline sottratta e non c'è un pedestal/dark:
   la corrente DC `λ⟨A⟩I₁` non è recuperabile. Quindi il metodo media-MSSD
   classico **non si chiude**. Si può usare la variante a **cumulanti alti**
   (non richiede la media): energia da `κ₃/κ₂`, rate da `κ₂²/κ₄` o dalla
   fluttuazione di potenza tra record (§3).
2. **Attenzione all'uso della MSSD su processo lento.** Con `culoculo`
   sovracampionato (VN≈2·10⁻⁴) la MSSD misura quasi solo il contenuto ad alta
   frequenza (derivata + rumore), **non** la varianza totale di shot noise. Per
   il termine di Campbell `v` va usata la `C(0)` piena (o l'integrale dell'ACF);
   la MSSD è ottimale quando il processo è campionato ~alla sua τ_corr, oppure
   come stima di `v` robusta alle derive quando `τ_corr ≲ δ`.

---

## 3. Rate senza calibrazione: fluttuazione di potenza tra record

Osservabile pulita e **gain-free**: la potenza per record `Q_j = Σ_i x_{ij}²`.
Per Poisson composto `E[Q]²/Var(Q) = Λ/(1+CV_w²)`, con `Λ = λT` numero medio di
eventi per finestra e `CV_w` dispersione del contributo per impulso. Quindi

$$ \Lambda \;\approx\; (1+CV_w^2)\cdot \frac{E[Q]^2}{\mathrm{Var}(Q)} = \frac{1+CV_w^2}{CV_Q^2} $$

**Cautela (limite gaussiano):** in pileup profondo il processo è gaussiano e
`CV_Q` **satura** al valore di puro campionamento `CV_floor = √(2/N_eff)`,
`N_eff = T/τ_corr` = numero di tempi di correlazione nella finestra. Sotto quel
floor non c'è più informazione di conteggio.

| | `CV_Q` misurato | `CV_floor` (gauss.) | `N_eff` | interpretazione |
|---|---|---|---|---|
| `anodewaves` | 0.170 | **0.173** | 67 | **al floor** → gaussiano, λ solo limitato in basso |
| `culoculo` | 0.635 | 0.549 | 6.6 | **sopra** il floor → conteggio misurabile |

**Rate stimati** (SER = spettro di ampiezza; esp. ⇒ `1+CV_w²≈6`, stretto ⇒ ≈1.4):

- `culoculo`: `Λ ≈ 14–59` eventi/20 µs → **λ ≈ 0.7 – 3 MHz**;
- `anodewaves`: `λτ ≳ 1` ⇒ **λ ≳ 4 MHz**; il forward-matching (§5) satura verso
  ~10–40 MHz. Superiormente **indeterminato** con la sola statistica di fluttuazione.

---

## 4. Pileup

- **`anodewaves` — pileup profondo.** Skew −0.12, eccesso di kurtosi ≈ 0
  (gaussiano); `CV_Q` al floor. La granularità di singolo evento è persa: la
  varianza dà `λ⟨A²⟩` ma **λ e ⟨A⟩ non si separano** da questi dati. Per
  romperla serve la **media sopra pedestal** (corrente) oppure un **run a basso
  rate / dark** (SER e guadagno assoluto).
- **`culoculo` — pileup moderato.** Kurtosi *pooled* +0.5 (dovuta alla
  dispersione della varianza tra record → statistica di conteggio), mentre
  intra-record è sub-gaussiana (il lento vagare integrato entro finestra è
  limitato). La varianza per record fluttua del ±60 %: pochi eventi per finestra.

---

## 5. Simulazione coerente (SDE) — `simulate_pmt.py`

Ricetta a tre blocchi (tutto in `simulate_pmt.py`, con self-check):

1. **Eccitazione: Poisson composto.** Arrivi Poisson(λ), marche `A_k` da SER
   (Gamma con media e `CV` regolabili; esponenziale = `CV=1`, PMT reale ≈ 0.3–0.5).
2. **Filtro di forma `h(t)`** (la "risposta esponenziale"):
   - anode → bi-esponenziale un polo (`τ_fall=250 ns`, rise ~20 ns), unipolare;
   - culoculo → **preamp di carica, unipolare** (bi-esponenziale, `rise≈0.7 µs`,
     `fall≈2.4 µs`): integra la corrente del rivelatore, area positiva (ha un DC).
3. **Rumore elettronico** additivo: bianco, oppure **colorato OU** (`noise_tau`)
   per riprodurre un floor non piatto.

Sono forniti due generatori equivalenti:

- `simulate_events()` — **somma esatta** di impulsi (qualsiasi `h`, consigliato);
- `simulate_ou_sde()` — integrazione **Euler–Maruyama del jump-SDE**
  (la forma "equazione differenziale stocastica" che chiedevi, valida per `h` a un polo):

$$ dY = -\frac{Y}{\tau}\,dt + dJ(t),\qquad J=\sum_k A_k\ \text{ai tempi di Poisson} $$
$$ Y_{n+1} = e^{-\delta/\tau}\,Y_n + (\text{salto }A_k\text{ se evento in }[n,n{+}1)) $$

Per la forma multipolo (preamp) si filtra la stessa corrente Poisson con un
filtro lineare di stato (state-space) `H(s)`; nel codice si usa `simulate_events`
con la `h` del preamp (`h_preamp`), che è la via pulita per una `h` arbitraria.

**Validazione** (figura sotto): modello (rosso) vs dati (nero) su ACF, PSD e
distribuzione di potenza per record.

![validazione](model_validation.png)

`anodewaves` combacia su tutti e tre i piani. `culoculo` combacia bene su
potenza e corner; i tempi del preamp (`h_preamp`, rise/fall) si possono
raffinare sull'ACF misurata.

> **Nota (forma di culoculo).** In una versione precedente l'ACF sembrava
> *bipolare* (zero-crossing a ~4.7 µs). È un **artefatto della sottrazione della
> baseline per-record**: su un segnale con `τ_corr` pari a una frazione grande
> della finestra, togliere la media forza l'ACF sotto zero ai lag grandi. Un
> preamp di carica **unipolare** (bi-esponenziale) sottoposto alla *stessa*
> sottrazione riproduce esattamente quello zero-crossing → la forma vera è
> unipolare, coerente con l'integrazione di carica.

---

## 6. Fit quantitativo dei parametri — Optuna (`fit_simulator.py`)

Invece di tarare a mano, i parametri del simulatore sono fittati ai dati con
**method of simulated moments** (Optuna TPE, 500 trial/file). Il guadagno assoluto
è degenere ed esce dal conto: tutte le metriche sono scale-free. Metriche
(fisicamente distinte → fit identificabile):

| metrica | vincola | note |
|---|---|---|
| ACF normalizzata (0–5 µs) | forma `h` (rise, fall) + rumore | backbone |
| **PSD, distanza di Wasserstein** su log-f | forma spettrale + posizione floor | PMF normalizzata |
| CV della potenza per-record | occupancy (rate) | |
| eccesso di kurtosi | larghezza SER / occupancy | debole (vedi sotto) |
| **frazione di potenza 0.3–8 MHz** | rise-time / morfologia fine | vedi §*morfologia* |

Guadagno arbitrario → il rumore è passato come **frazione dell'RMS** del segnale.
Validato con seed fresco (contro l'overfit di una realizzazione MC).

**Rumore: misurato, non fittato.** Le metriche ACF/PSD-Wasserstein lavorano su
spettri *normalizzati* → sono **cieche al livello assoluto del floor di rumore**.
Lasciarlo libero lo faceva sovrastimare (per culoculo `noise_frac`≈0.02, cioè
σ_n≈11 ADC contro i ~4–5 ADC reali) → la simulazione veniva troppo *ruvida* e le
serie temporali di culoculo **non somigliavano** a quelle vere (pur avendo ACF/PSD
giuste!). La ruvidità visiva è dominata dal rumore ad alta-f, che quelle metriche
non vincolano. Fix: **σ_n misurato dal plateau PSD ad alta frequenza e fissato**
(stessa stima di §7, validata ~1 %).

**Morfologia: era il rise-time, non il rumore** (dettaglio in `findings_approaches.md`).
Sistemato il rumore, culoculo restava un po' troppo liscio. La PSD reale ha un
eccesso di potenza in **banda media 0.5–8 MHz** (fino a ~3×), che il rumore bianco
*non* può fornire (vive alla f alta, e ne rovinerebbe il floor). È invece un **rise
più veloce**: il fit lo aveva smussato (ACF/Wasserstein sotto-pesano quella banda).
Aggiunta una metrica sulla **frazione di potenza 0.3–8 MHz** → rise da 528 → **322 ns**,
`dy`-std (roughness) da 7.0 → 7.4 vs 8.3 reale, morfologia ora coerente. Lezione:
per matchare la *forma d'onda* (non solo gli spettri integrati) serve una metrica
sensibile alla scala fine.

**Risultati** (`fit_results.json`, figura `fit_validation.png`):

| | `anodewaves` | `culoculo` |
|---|---|---|
| λ | 1.6×10⁷ Hz *(lim. inf., vedi §7)* | 5.6×10⁵ Hz *(banda 5–8×10⁵)* |
| τ_rise / τ_fall | 17 ns / 257 ns | 322 ns / 3787 ns |
| ser_cv | 0.05 *(non affidabile)* | 0.22 |
| noise_frac (σ_n) | 0.087 (≈1.5 ADC) | 0.009 (≈5 ADC) — **misurato, non fittato** |
| match ACF 1/e | 270→270 ns | 2500→2640 ns |
| PSD Wasserstein | 0.014 dec | 0.006 dec |
| morfologia (dy-std) | — | 8.3 → 7.4 (rise corretto) |

La forma (ACF, PSD, distribuzione di potenza) è riprodotta molto bene per
entrambi. **Avvertenza `anodewaves`:** la kurtosi dei dati è ≈0 (gaussiano), ma
lo shot-noise ha sempre eccesso di kurtosi ≥0 → il fit non può eguagliare uno
0 (o leggermente negativo) e la CV è satura al floor gaussiano (insensibile a λ):
perciò il λ del fit è di fatto un **limite inferiore**. Il valore alto vero emerge
dai cumulanti (§7). Le bande di degenerazione (trial near-best) confermano
`anodewaves` λ∈[1.2,1.9]×10⁷ e la coppia (λ, ser_cv) accoppiata.

---

## 7. Stima rate/energia con MSSD + cumulanti superiori (`mssd_cumulant_estimate.py`)

Il metodo richiesto (von Neumann/MSSD + Campbell). Cumulanti del processo di
Poisson filtrato: `κ_n = λ ⟨Aⁿ⟩ S_n`. Due forme:
- **MSSD/incrementi**: `Δy=y[i+1]−y[i]` (kernel `g=h(t)−h(t−dt)`), `S_n=J_n=∫gⁿ` →
  **drift-robust** (è la MSSD: `κ₂[Δy]=`MSSD).
- **bulk**: `y` (media globale tolta), `S_n=I_n=∫hⁿ`.

**Disaccoppiamento con cumulanti PARI** (κ₂, κ₄), per entrambe le forme:
$$ \lambda = \frac{\kappa_2^2}{\kappa_4}\frac{m_4 S_4}{m_2^2 S_2^2}
   \quad(\text{rate, ASSOLUTO, gain-free}),\qquad
   \langle A\rangle=\sqrt{\frac{\kappa_4}{\kappa_2}\frac{m_2 S_2}{m_4 S_4}}
   \quad(\text{energia, relativa}) $$
con `m_n=⟨Aⁿ⟩/⟨A⟩ⁿ` momenti SER (Gamma, da `ser_cv`).

**Accorgimenti presi** (tutti nel codice):
1. **cumulanti pari** κ₂,κ₄ → `S₂,S₄>0` sempre: nessun integrale dispari che si
   annulla (`∫(Δh)³≈0`!), nessuna ambiguità di polarità.
2. **incrementi Δy** → uccidono DC/derive lente (principio di von Neumann).
3. **momenti grezzi attorno a 0** per Δy (E[Δy]=0 esatto) → niente bias da
   sottrazione media.
4. **κ₄ è immune al rumore gaussiano** (solo κ₂ è gonfiato); σ_n² è misurato
   **dai dati** dal plateau della PSD ad alta frequenza (`σ_n²=S₀·f_Nyq`, mediana
   robusta alle righe di disturbo — validato a ~1 %). *NB: usare `noise_frac×var`
   sbaglia di ordini di grandezza perché confonde la varianza a bassa-f, enorme,
   col rumore ad alta-f che la MSSD effettivamente vede.*
5. **bootstrap sui record** per la CI; si riporta la frazione di resample con κ₄>0.
6. **κ₄→0 (gaussiano/pileup profondo) → rate = limite inferiore**.
7. `λ` gain-free; `⟨A⟩` scala relativa (assoluta serve calibrazione di guadagno).
8. **sensibilità SER** scansionata (sistematico dominante).

**Validazione (imprescindibile):** su dati simulati con λ noto = 1.00 MHz, il
metodo MSSD recupera **9.8×10⁵ Hz (ratio 0.98)** ed energia entro ~2 %. Il metodo
è quindi corretto; sui dati veri conta *in quale regime* cade il segnale:

**`anodewaves` — MSSD funziona.** Rise ripido (16 ns ≈ 1.6 campioni) → gli
incrementi sono "a salti" → κ₄[Δy]>0 robusto (100 % bootstrap).
$$ \lambda \approx 2.8\times10^8\ \text{Hz}\quad(\text{banda SER } 2.7\times10^8\text{–}1.6\times10^9),
   \qquad \langle A\rangle\approx 2.7\ \text{ADC (rel.)} $$
Deep pileup (λτ≈70). **Concorda con la kurtosi ≈0** (che richiede λτ≫1): il fit
CV-based (15 MHz) era solo un limite inferiore. *Cautela:* a questo rate gli
eventi arrivano ogni ~3.6 ns < 10 ns di campionamento → il valore assoluto è
al limite del regime risolvibile; robustamente **λ ≳ 10⁸ Hz, pileup profondo**.
Il metodo bulk fallisce (κ₄≈0, gaussiano) — coerente.

**`culoculo` — il metodo NON è affidabile qui (e va detto).** Due ragioni fisiche:
- rise lento (426 ns ≈ 42 campioni) → ogni evento spalma la salita su molti
  campioni → **incrementi lisci → κ₄[Δy]≈0** (bootstrap 14 % >0) → MSSD inutilizzabile;
- il bulk κ₄ è **distorto negativo** dal minuscolo `N_eff≈7` (tempi di
  correlazione per finestra): la varianza dello stimatore di κ₄ (∝ Var della
  varianza campionaria, enorme con N_eff piccolo) è confrontabile col segnale, e
  spinge κ₄<0; per giunta la riga di disturbo a 35–40 MHz e la quantizzazione ADC
  contaminano i momenti alti.

→ Per `culoculo` il rate affidabile viene dalla **fluttuazione della potenza (§3)
e dal fit (§6): λ ≈ 1 MHz**. I cumulanti superiori servirebbero più tempi di
correlazione (record più lunghi o più numerosi) per convergere.

**In sintesi:** la macchina MSSD+cumulanti è validata e dà il rate assoluto *quando
il rise è risolto e ci sono abbastanza N_eff*; su questi dati funziona per l'anode
(→ λ~10⁸ Hz, pileup profondo) e va sostituita da CV/fit per culoculo (→ ~1 MHz).
Il sistematico dominante resta sempre lo **spettro SER** (fattore ~6).

---

## 8. Distribuzione delle ampiezze P(A) ed energia (`amplitude_ser.py`)

Gli `A_k` sono le cariche/ampiezze di singolo evento; `P(A)` è la SER (single-electron
response, strumentale) oppure lo spettro di energia per evento. Cosa se ne cava:

- **Ogni cumulante = un momento**: `κ_n = λ⟨Aⁿ⟩I_n`. I rapporti cancellano λ e il
  guadagno → **momenti normalizzati** = forma di `P(A)`. Es. combinazione
  λ-indipendente per la larghezza SER:
  $$ \frac{\kappa_2\kappa_4}{\kappa_3^2}=\frac{\langle A^2\rangle\langle A^4\rangle}{\langle A^3\rangle^2}\cdot\frac{I_2I_4}{I_3^2},\qquad \text{Gamma: }\frac{\langle A^2\rangle\langle A^4\rangle}{\langle A^3\rangle^2}=\frac{1+3\,\mathrm{CV}^2}{1+2\,\mathrm{CV}^2} $$

- **In pratica la forma di P(A) NON è estraibile da dati in pileup.** Serve l'odd
  cumulante `κ₃`, che in pileup è (a) piccolo (il segnale gaussianizza,
  `κ₃→0` come `~1/√(λτ)`) e (b) ha varianza di stima enorme; stando **al quadrato al
  denominatore**, l'errore esplode. Dimostrato: anche una **simulazione pulita con
  10⁴ record e CV nota** recupera male (`CV=0.8→1.1, 0.5→0.42, 0.3→fallisce`); sui
  dati veri è inutilizzabile. `anodewaves` (gaussiano) non dà nulla sulla forma;
  `culoculo` neppure (N_eff~7 + artefatti).

- **Cosa resta misurabile:** `λ` (cumulanti pari, §7), `λ⟨A²⟩` (varianza), e — con un
  pedestal — l'**energia media per evento** `⟨A²⟩/⟨A⟩` (Campbelling, rate-indipendente).
  L'**energia assoluta** (keV) richiede calibrazione di guadagno; lo **spettro P(A)
  completo** richiede **eventi risolti** (run a basso rate/dark → istogramma delle aree
  dei singoli impulsi). Nota: il λ~10⁸ Hz dell'anode suggerisce che lì gli "eventi"
  siano **fotoelettroni singoli** (P(A)=SER), mentre culoculo (preamp, ~1 MHz) è più
  a livello di evento/energia.

---

## 9. Cosa misurare per chiudere il conto (dose)

Il collo di bottiglia è la **degenerazione rate ↔ energia in pileup**. Per
romperla, in ordine di efficacia:

1. **Run di pedestal / dark** (o beam-off): dà lo zero assoluto → recuperi la
   **media** `m = λ⟨A⟩I₁`. Con `m` e la MSSD (`v`) chiudi
   `Ē ∝ v/m`, `λ ∝ m²/v`, `dose ∝ m`. Entrambe le risposte sono **unipolari**
   (`I₁=∫h≠0`), quindi il DC è fisico e questo funziona per entrambi i canali —
   l'ho perso solo sottraendo la baseline per-record, non è AC-coupling.
2. **Run a basso rate in modo-conteggio**: singoli impulsi isolati → misuri
   direttamente `h(t)`, il guadagno di singolo evento e lo **spettro SER**
   (quindi `CV_w`, che qui è l'incertezza dominante sul rate).
3. Con quei due, la fluttuazione di potenza (§3) diventa una misura assoluta di
   λ anche ad alto rate, e la MSSD dà la dose disaccoppiata come nel metodo che
   citavi.

---

### File
- `simulate_pmt.py` — simulatore (event-sum + jump-SDE) + self-check.
- `fit_simulator.py` — fit Optuna MSM (ACF + PSD-Wasserstein + CV + kurtosi) → `fit_results.json`.
- `mssd_cumulant_estimate.py` — stima rate/energia MSSD + cumulanti superiori, con validazione.
- `amplitude_ser.py` — estrazione (fallita, dimostrata) della forma SER dai cumulanti (§8).
- `signals.png` — forme d'onda grezze registrate (§0).
- `model_validation.png` — modello (tarato a mano) vs dati.
- `fit_validation.png` — fit Optuna vs dati (ACF/PSD/potenza).
- `independence_test.png` — coerenza + test allineati/mescolati (§0.1).
- `analisi_1.py` — script Welch/coerenza/filtri di partenza.
- `possible_approaches.md` — bibliografia/idee di partenza; `findings_approaches.md` — revisione + test.
