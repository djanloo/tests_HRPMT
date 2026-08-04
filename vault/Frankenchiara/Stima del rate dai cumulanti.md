---
type: nota
project: frankenchiara
updated: 2026-07-21
tags: [tipo/nota, progetto/frankenchiara]
---

# Stima del rate dai cumulanti (MSSD + Campbell)

Il metodo classico di dosimetria in modo-corrente, la sua variante a cumulanti alti, e
la terza via della fluttuazione di potenza. Validato a verità nota, e con un verdetto
diverso per ciascuno dei due canali.

Codice: `mssd_cumulant_estimate.py`. Teoria: [[Cumulanti e Campbell]],
[[Statistiche gain-free]].

## MSSD di von Neumann e disaccoppiamento rate / energia

**Mean Square of Successive Differences:**

$$ \text{MSSD} = \frac{1}{N-1}\sum_i (x_{i+1}-x_i)^2 = 2\,[C(0)-C(\delta)] $$

Rapporto di **von Neumann** $\text{VN} = \text{MSSD}/(2\,\text{Var})$ → 1 per dato
bianco, < 1 se c'è correlazione seriale. Misurati:

- `FAST`: VN = 0.0225 → $C(\delta)/C(0) = 0.977$ (τ ≫ δ, come atteso);
- `CSP`: VN = 2.4·10⁻⁴ → $C(\delta)/C(0) = 0.9998$ (fortemente sovracampionato).

### Perché la MSSD serve in dosimetria

In modo-corrente, con $h$ fissata, valgono due osservabili **indipendenti**:

$$ \underbrace{m = \lambda\langle A\rangle I_1}_{\text{media (corrente DC)}}
   \qquad
   \underbrace{v = \lambda\langle A^2\rangle I_2}_{\text{varianza}\;\approx\;\text{MSSD}} $$

da cui il **disaccoppiamento**:

$$ \boxed{\;\bar E \;\propto\; \frac{v}{m} \;\propto\; \frac{\langle A^2\rangle}{\langle A\rangle}\;}
   \quad\text{(energia media, indip. dal rate)} $$
$$ \boxed{\;\lambda \;\propto\; \frac{m^2}{v}\;}
   \quad\text{(rate, indip. dall'energia)} $$

e per consistenza $\text{dose} \propto \lambda\bar E \propto m$ (la sola corrente).
**La MSSD si usa al posto della varianza semplice perché usa solo differenze
successive → cancella derive lente** (1/f, termiche, baseline wander) che gonfierebbero
$v$. Questo è il contributo di von Neumann.

### Il limite su QUESTI dati

1. **Manca $m$.** I record sono a baseline sottratta e non c'è un pedestal/dark: la
   corrente DC $\lambda\langle A\rangle I_1$ non è recuperabile. Quindi il metodo
   media-MSSD classico **non si chiude**. Si può usare la variante a **cumulanti alti**
   (non richiede la media): energia da $\kappa_3/\kappa_2$, rate da
   $\kappa_2^2/\kappa_4$ o dalla fluttuazione di potenza tra record.

2. **Attenzione all'uso della MSSD su processo lento.** Con il CSP sovracampionato
   (VN≈2·10⁻⁴) la MSSD misura quasi solo il contenuto ad alta frequenza (derivata +
   rumore), **non** la varianza totale di shot noise. Per il termine di Campbell $v$ va
   usata la $C(0)$ piena (o l'integrale dell'ACF); la MSSD è ottimale quando il
   processo è campionato ~alla sua $\tau_\text{corr}$, oppure come stima di $v$ robusta
   alle derive quando $\tau_\text{corr} \lesssim \delta$.

## Il disaccoppiamento con cumulanti PARI

Cumulanti del processo di Poisson filtrato: $\kappa_n = \lambda \langle A^n\rangle S_n$.
Due forme:

- **MSSD/incrementi**: $\Delta y = y[i+1] - y[i]$ (kernel $g = h(t)-h(t-dt)$),
  $S_n = J_n = \int g^n$ → **drift-robust** (è la MSSD: $\kappa_2[\Delta y] = $MSSD);
- **bulk**: $y$ (media globale tolta), $S_n = I_n = \int h^n$.

$$ \lambda = \frac{\kappa_2^2}{\kappa_4}\frac{m_4 S_4}{m_2^2 S_2^2}
   \quad(\text{rate, ASSOLUTO, gain-free}),\qquad
   \langle A\rangle=\sqrt{\frac{\kappa_4}{\kappa_2}\frac{m_2 S_2}{m_4 S_4}}
   \quad(\text{energia, relativa}) $$

con $m_n = \langle A^n\rangle/\langle A\rangle^n$ i momenti della distribuzione di
ampiezza. **Attenzione**: sono assunti, non misurati, e $m_4$ entra *linearmente* —
vedi [[Spettro di ampiezza]] e [[Simulazione SDE]] per quanto vale l'assunzione.

### Gli otto accorgimenti (tutti nel codice)

1. **cumulanti pari** $\kappa_2,\kappa_4$ → $S_2,S_4>0$ sempre: nessun integrale
   dispari che si annulla ($\int(\Delta h)^3\approx 0$!), nessuna ambiguità di polarità.
2. **incrementi $\Delta y$** → uccidono DC/derive lente (principio di von Neumann).
3. **momenti grezzi attorno a 0** per $\Delta y$ ($E[\Delta y]=0$ esatto) → niente bias
   da sottrazione media.
4. **$\kappa_4$ è immune al rumore gaussiano** (solo $\kappa_2$ è gonfiato);
   $\sigma_n^2$ è misurato **dai dati** dal plateau della PSD ad alta frequenza
   ($\sigma_n^2 = S_0 \cdot f_\text{Nyq}$, mediana robusta alle righe di disturbo —
   validato a ~1 %). *NB: usare `noise_frac × var` sbaglia di ordini di grandezza perché
   confonde la varianza a bassa-f, enorme, col rumore ad alta-f che la MSSD
   effettivamente vede.*
5. **bootstrap sui record** per la CI; si riporta la frazione di resample con
   $\kappa_4>0$.
6. **$\kappa_4 \to 0$ (gaussiano/pileup profondo) → rate = limite inferiore**.
7. $\lambda$ gain-free; $\langle A\rangle$ scala relativa (assoluta serve calibrazione
   di guadagno).
8. **sensibilità SER** scansionata (sistematico dominante).

### Validazione, e il verdetto per i due canali

Su dati simulati con λ noto = 1.00 MHz, il metodo MSSD recupera **9.8×10⁵ Hz
(ratio 0.98)** ed energia entro ~2 %. Il metodo è quindi corretto; sui dati veri conta
*in quale regime* cade il segnale.

**`FAST` — MSSD funziona.** Rise ripido (16 ns ≈ 1.6 campioni) → gli incrementi
sono "a salti" → $\kappa_4[\Delta y]>0$ robusto (100 % bootstrap).

$$ \lambda \approx 2.8\times10^8\ \text{Hz}\quad(\text{banda SER } 2.7\times10^8\text{–}1.6\times10^9),
   \qquad \langle A\rangle\approx 2.7\ \text{ADC (rel.)} $$

Deep pileup (λτ≈70). **Concorda con la kurtosi ≈0** (che richiede λτ≫1): il fit
CV-based (15 MHz) era solo un limite inferiore. *Cautela:* a questo rate gli eventi
arrivano ogni ~3.6 ns < 10 ns di campionamento → il valore assoluto è al limite del
regime risolvibile; robustamente **λ ≳ 10⁸ Hz, pileup profondo**. Il metodo bulk
fallisce ($\kappa_4\approx 0$, gaussiano) — coerente.

**`CSP` — il metodo NON è affidabile qui (e va detto).** Due ragioni fisiche:

- rise lento (426 ns ≈ 42 campioni) → ogni evento spalma la salita su molti campioni →
  **incrementi lisci → $\kappa_4[\Delta y]\approx 0$** (bootstrap 14 % >0) → MSSD
  inutilizzabile;
- il bulk $\kappa_4$ è **distorto negativo** dal minuscolo $N_\text{eff}\approx 7$
  (tempi di correlazione per finestra): la varianza dello stimatore di $\kappa_4$ (∝ Var
  della varianza campionaria, enorme con $N_\text{eff}$ piccolo) è confrontabile col
  segnale, e spinge $\kappa_4<0$; per giunta la riga di disturbo a 35–40 MHz e la
  quantizzazione ADC contaminano i momenti alti.

→ Per il CSP il rate affidabile viene dalla **fluttuazione della potenza** (sotto)
**e dal fit** ([[Fit dei parametri]]): λ ≈ 1 MHz. I cumulanti superiori servirebbero
più tempi di correlazione (record più lunghi o più numerosi) per convergere.

**In sintesi:** la macchina MSSD+cumulanti è validata e dà il rate assoluto *quando il
rise è risolto e ci sono abbastanza $N_\text{eff}$*; su questi dati funziona per
l'anode (→ λ~10⁸ Hz, pileup profondo) e va sostituita da CV/fit per il CSP (→ ~1 MHz).
Il sistematico dominante resta sempre lo **spettro SER** (fattore ~6).

## Terza via: fluttuazione di potenza tra record

Osservabile pulita e **gain-free**: la potenza per record $Q_j = \sum_i x_{ij}^2$. Per
Poisson composto $E[Q]^2/\text{Var}(Q) = \Lambda/(1+CV_w^2)$, con $\Lambda = \lambda T$
numero medio di eventi per finestra e $CV_w$ dispersione del contributo per impulso.
Quindi

$$ \Lambda \;\approx\; (1+CV_w^2)\cdot \frac{E[Q]^2}{\mathrm{Var}(Q)} = \frac{1+CV_w^2}{CV_Q^2} $$

**Cautela (limite gaussiano):** in pileup profondo il processo è gaussiano e $CV_Q$
**satura** al valore di puro campionamento $CV_\text{floor} = \sqrt{2/N_\text{eff}}$,
$N_\text{eff} = T/\tau_\text{corr}$ = numero di tempi di correlazione nella finestra.
Sotto quel floor non c'è più informazione di conteggio.

| | $CV_Q$ misurato | $CV_\text{floor}$ (gauss.) | $N_\text{eff}$ | interpretazione |
|---|---|---|---|---|
| `FAST` | 0.170 | **0.173** | 67 | **al floor** → gaussiano, λ solo limitato in basso |
| `CSP` | 0.635 | 0.549 | 6.6 | **sopra** il floor → conteggio misurabile |

**Rate stimati** (SER = spettro di ampiezza; esp. ⇒ $1+CV_w^2\approx 6$, stretto ⇒
≈1.4):

- `CSP`: $\Lambda \approx 14$–$59$ eventi/20 µs → **λ ≈ 0.7 – 3 MHz**;
- `FAST`: $\lambda\tau \gtrsim 1$ ⇒ **λ ≳ 4 MHz**; il forward-matching satura
  verso ~10–40 MHz. Superiormente **indeterminato** con la sola statistica di
  fluttuazione.
