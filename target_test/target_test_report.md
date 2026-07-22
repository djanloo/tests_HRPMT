# Test del metodo Target sui dati reali + validazione sintetica

**Esperimento.** Applico l'algoritmo Target (brevetto US2021/0055429 A1, Stein; NSS
2018) ai 6 run reali a dose nota, poi **valido tutto con un simulatore a livello di
fotoelettrone** (il modello del brevetto) con verità nota. Assunzioni: `fs = 100 MS/s`
(Δ=10 ns ≈ 4 % di τ_NaI≈230 ns, dentro il vincolo Δ<5 %τ), **DC-coupled**, gain PMT
**non controllato** (partitore passivo). `anodewaves.npy` = `run_Cs-137_28100` (record
identici). Codice: `target_method.py` (reale), `pe_synth.py` (sintetico).

> **Nota di correzione.** Una prima versione di questo report aveva **invertito lo
> scaling di gain** di η e λ̂. La validazione sintetica (§3) lo ha smascherato:
> **η=Var/Msd è gain-free** (∝ energia), **λ̂=Msd²/Var ∝ gain²**. Sotto è corretto.

Equazioni (i_Δ = campioni di corrente): `Msd=λη` (Eq.2), `η=Var/Msd` (Eq.3),
`Ḣ=Z(η)·Msd` (Eq.4). Definizioni operative in fondo (§0).

## 1. Valori attesi dal setting (a priori)

`dose ≈ k·activity/distanza²` — inverse-square verificata (k≈1.0×10⁶ per i Cs-137).
Rate predetto (calibrazione Target 1 Mcps↔540 µSv/h, Cs-137 2×2″ NaI):

| run | dose µSv/h | λ predetto | λτ (pileup) |
|---|---|---|---|
| Am-241 | 94 | 0.17 Mcps | 0.04 (risolto) |
| Cs-137 | 616 | 1.14 Mcps | 0.26 |
| Cs-137 | 889 | 1.65 Mcps | 0.38 |
| Cs-137 | 7900 | 14.6 Mcps | 3.4 |
| Cs-137 | 17990 | 33.3 Mcps | 7.7 |
| Cs-137 | 28100 | 52 Mcps | 12 (profondo) |

## 2. Risultati sui dati reali

| nuclide | dose | λ_pred | Var | Msd¹ | η=Var/Msd | λ̂=Msd²/Var | kurt |
|---|---|---|---|---|---|---|---|
| Am-241 | 94 | 0.17 | 79.6 | 6.44 | 12.4 | 0.52 | +6.9 |
| Cs-137 | 616 | 1.14 | 2732 | 41.6 | 65.7 | 0.63 | +5.7 |
| Cs-137 | 889 | 1.65 | 4516 | 47.0 | 96.2 | 0.49 | +4.0 |
| Cs-137 | 7900 | 14.6 | 2087 | 19.0 | 109.8 | 0.17 | −0.3 |
| Cs-137 | 17990 | 33.3 | 657 | 8.65 | 76.0 | 0.11 | −0.1 |
| Cs-137 | 28100 | 52 | 298 | 6.45 | 46.1 | 0.14 | −0.08 |

Figura: `target_test.png` (etichette corrette secondo §3–4).

## 2bis. Cosa misura ogni statistica, e quali proxy

Processo $y=\sum_k A_k\,h(t-t_k)$: rate $\lambda$, ampiezza per evento $A$ ($\propto$
energia), gain $g$ (scala le ampiezze, $A\to gA$), forma $h$. Cumulanti di Campbell:
$\kappa_n=\lambda\langle A^n\rangle I_n$, con $I_n=\int h^n$.

**Cosa misura ogni statistica** (scala col gain $g$ e col rate $\lambda$):

| statistica | teoria | scala | equivale a | gain-free |
|---|---|---|---|---|
| media $m=\kappa_1$ | $\lambda\langle A\rangle I_1$ | $\propto g\,\lambda\langle A\rangle$ | corrente DC = dose non-comp. | no |
| Var $=\kappa_2$ | $\lambda\langle A^2\rangle I_2$ | $\propto g^2\lambda\langle A^2\rangle$ | potenza di fluttuazione | no |
| $\text{Msd}^1=C(0)-C(1)$ | $\lambda\langle A^2\rangle J_2$ | $\propto g^2\lambda$ | shot ad alta-f (Target: $\lambda\eta$) | no |
| skewness $\gamma_1=\kappa_3/\kappa_2^{3/2}$ | $\propto \lambda^{-1/2}$ | gain-free | $1/\sqrt{\text{occupancy}}$; segno = polarità | **sì** |
| eccesso kurtosi $\gamma_2=\kappa_4/\kappa_2^{2}$ | $\propto \lambda^{-1}$ | gain-free | $1/\text{occupancy}\approx 1/(\lambda\tau_\text{eff})$ | **sì** |
| von Neumann $\text{Msd}/\text{Var}=1-\rho(1)$ | (forma) | gain-free | rise/roughness vs $\tau_\text{corr}$ | **sì** |
| CV potenza (per-record) | $\propto 1/\sqrt{\text{occupancy}}$ | gain-free | # eventi per finestra | **sì** |

**Proxy utilizzabili:**

| grandezza | proxy | equivale a | gain-free | requisiti / limiti |
|---|---|---|---|---|
| **rate $\lambda$** (DC) | $\text{mean}^2/\text{Var}$ | $\lambda\,\langle A\rangle^2/\langle A^2\rangle$ | **sì** | pedestal + Var noise-sub |
| rate $\lambda$ (AC) | $\kappa_2^2/\kappa_4$ | $\lambda\cdot(\text{fattore SER,forma})$ | **sì** | pileup moderato; muore in gaussiano ($\kappa_4\to0$) |
| **energia media** | $\eta=\text{Var}/\text{Msd}$ | $\langle A^2\rangle/\langle A\rangle$ | **sì** | shot risolto (fuori dai nostri dati) |
| energia (alt.) | $\kappa_3/\kappa_2$ | $\langle A^3\rangle/\langle A^2\rangle$ | no ($\propto g$) | drift-sensitive |
| pileup / regime | kurtosi, skewness | $1/\text{occupancy}$ | **sì** | monotòno con $\lambda\tau$; $\to0$ = gaussiano |
| **gain (monitor)** | $\text{Var}/\text{mean}$ | $g\cdot\langle A^2\rangle/\langle A\rangle$ | no ($\propto g$) | noti $\lambda$ ed energia |
| dose non-comp. | mean (Target: Msd) | $\lambda\eta$ | no | pedestal; degrada nel gain-crash |

**La kurtosi in dettaglio** (la domanda): $\gamma_2=\dfrac{\kappa_4}{\kappa_2^{2}}=\dfrac{1}{\lambda}\,\dfrac{\langle A^4\rangle}{\langle A^2\rangle^{2}}\,\dfrac{I_4}{I_2^{2}}$
— **adimensionale (gain-free)**, $\propto 1/(\lambda\tau_\text{eff})$ = **inverso del numero medio di
impulsi sovrapposti**. Grande a basso rate (impulsi risolti, "spiky"), $\to 0$ in pileup
profondo (gaussiano). È un **misuratore di occupancy/pileup, non di energia**. La skewness
$\gamma_1\propto 1/\sqrt{\lambda\tau_\text{eff}}$ porta la stessa informazione, più il **segno**
(= polarità dell'impulso). *Nei dati:* kurtosi $+6.9\to -0.08$ da Am-241 (risolto) a
Cs-137 28100 (pileup profondo) — coerente con l'occupancy crescente (§2, §4).

## 3. Validazione sintetica (pe-level, verità nota) — `pe_synth.py`

Generatore Cox/branching: γ Poisson(λ) → η fotoelettroni ciascuno (∝energia) → decadimento
esponenziale τ → shot pe (Poisson) → j = gain·n_pe + rumore. Risultati:

- **SCAN gain** (λ,η fissi): **η=Var/Msd = 18.0 costante** su gain ×0.5–4; **λ̂=Msd²/Var
  scala ×g²** (10→41→164→656). ⇒ **η gain-free, λ̂ ∝ gain².**
- **SCAN λ** (gain fisso): mean, Var, Msd, λ̂ **tutti ∝ λ**; η **costante**. ⇒ il metodo
  Target **funziona** quando il gain è fisso e c'è granularità pe.
- **SCAN energia**: η=Var/Msd **cresce con eta_pe** ⇒ è un proxy di energia.
- **SCAN rumore**: rumore bianco → **η scende** (18→7), **λ̂ sale** (82→542).
- **SCAN gain-crash iniettato** `g(λ)=g₀/(1+λ/λc)` (+rumore): **Msd, λ̂, mean diventano
  non-monotoni** (salgono e poi *scendono*, esattamente come i dati reali!), MA
  **`mean²/Var` recupera λ** (0.45,1.34,4.4,12.9,24 per λ=1,3,10,30,60 Mcps) perché
  **il gain si cancella esattamente**: `mean²/Var = (gλE)²/(g²λE²) = λ`, per *qualsiasi* g(λ).

![validazione sintetica](pe_synth_validation.png)

## 4. Interpretazione corretta dei dati reali

- **η varia (46–110) ma per Cs-137 dovrebbe essere COSTANTE** (gain-free + energia
  fissa 662 keV). Poiché η è gain-free (§3), la variazione **non è deriva di gain**: è
  **rottura del metodo** — rumore (scan rumore: η↓) e regime fuori validità (a basso
  rate gli impulsi sono risolti, la relazione pe-shot di Msd non vale; a 100 MS/s la
  Msd è dominata da rise+rumore, non dalla granularità pe).
- **Msd, λ̂ anti-correlano con la dose** → è il **gain crash** (λ̂∝gain²). Estraendo il
  gain: `Msd/dose ∝ gain²` dà **gain in calo ~×17** sul range (monotòno; l'eventuale
  "bump" iniziale è sotto i ~15 Mcps, non campionato a stessa HV).
- **kurtosi ↔ pileup**: +5.7→−0.08 con λτ 0.26→12 → **il regime di pileup predetto
  dalla dose è corretto** (cross-validazione pulita e gain-free).
- **`mean²/Var` (rate gain-free, DC)**: sulla serie a stessa config traccia la dose
  **nella direzione giusta** (ratios 1:3.15:7 vs dose 1:2.28:3.56 con pedestal=0),
  **al contrario** di Msd/λ̂. Ma è **sensibile al pedestal** (con baseline vicino al
  segnale si appiattisce) → **serve un run di dark/pedestal** per fissare lo zero.

## 5. Conclusioni e ricetta

1. **Il rate gain-free si misura con `λ ∝ mean²/Var`** (non con Msd/λ̂, che portano il
   gain²). Validato in sim: **sopravvive al crollo del gain**. Richiede: (i) **DC-coupling**
   (ce l'abbiamo), (ii) il **pedestal** (serve un dark run — motivo forte per *tenere* la DC).
2. **η=Var/Msd è il proxy di energia gain-free**, ma **solo nel regime valido** (pileup
   pieno, pe risolti, basso rumore). Sui nostri dati spesso ne siamo fuori → η non affidabile.
3. **kurtosi/non-gaussianità** = ottimo indicatore *gain-free* del regime di pileup
   (utile per sapere se sei nel regime dove η vale).
4. **Il gain crash (~×17) è il limite hardware.** Il software (`mean²/Var`) recupera il
   **rate** attraverso il crash, ma **energia e dose assoluta** degradano nel crash
   (saltano stadi di moltiplicazione → excess-noise) → per la parte alta serve HW
   (partitore attivo/booster, o il controllo HV attivo di Target). Il software estende
   il range *prima* del crollo, non ti salva *dentro*.

**Prossimi passi suggeriti:** (a) **dark/pedestal run** → chiudere `mean²/Var` in assoluto;
(b) **scan a HV fisso** variando solo il rate → misurare la curva gain(rate) da `Msd/λ`
e fittare il modello grey-box del partitore; (c) stimare i parametri (τ, η_pe, rumore) dai
run risolti (616) e rigenerare col `pe_synth` per prove di convalida controllate.

---

## 0. Relazioni usate (definizioni operative)

Statistiche pooled sui record, media per-record tolta (per Var; irrilevante per le differenze).
- **Var** = ⟨(x−x̄_r)²⟩.
- **Msd^m** = `binom(2m,m)⁻¹·⟨(𝒟^m x)²⟩`; **Msd¹ = ½⟨(xᵢ₊₁−xᵢ)²⟩ = C(0)−C(1)** (usata nei rapporti).
- **η = Var/Msd¹** (energia, **gain-free**), **λ̂ = (Msd¹)²/Var** (**∝ gain²·λ**).
- **rate gain-free (DC)**: **`mean²/Var = λ`** (il gain si cancella; serve il pedestal per la media di segnale).
- **rumore**: `σ_n² = median(PSD[f>0.6 f_Nyq])·f_Nyq`; correzioni `Var−σ_n²`, `Msd¹−σ_n²`.
- **kurtosi** pooled di `x−x̄_r`. **Predetti**: dose∝act/d², `λ_pred=dose/540` [Mcps per µSv/h], `λτ`, τ=230 ns.
- **Scaling di gain** `j→g·j`: Var,Msd → ×g²; quindi η invariante, λ̂ ×g², **mean²/Var invariante**.
