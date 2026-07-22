# Quadro: dati, ground truth e assunzioni

**Dataset** (`jeanluke/anode_waveforms/*.h5`): 6 run, ognuno $10^4\times2000$ campioni
(float64), $f_s=100$ MS/s (assunto), 20 µs/record, **DC-coupled**. `anodewaves.npy` $=$
`run_Cs-137_28100` (record identici). Valori misurati/derivati (su 6000 record/run):

| nuclide | activity | dist [cm] | baseline [ADC] | dose [µSv/h] | $\lambda$ [Mcps] | Var | Msd | $g\propto\sqrt{\text{Msd}/\text{dose}}$ |
|---|---|---|---|---|---|---|---|---|
| Am-241 | 35.4 | 100 | 193 | 94 | 0.17 | 79.6 | 6.44 | 0.262 |
| Cs-137 | 19.4 | 180 | **3764** | 616 | 1.14 | 2732 | 41.6 | 0.260 |
| Cs-137 | 19.4 | 150 | 167 | 889 | 1.65 | 4516 | 47.0 | 0.230 |
| Cs-137 | 193.7 | 150 | 195 | 7900 | 14.6 | 2087 | 19.0 | 0.049 |
| Cs-137 | 193.7 | 100 | 194 | 17990 | 33.3 | 657 | 8.65 | 0.022 |
| Cs-137 | 193.7 | 80 | 195 | 28100 | 52.0 | 298 | 6.45 | 0.015 |

$\lambda$ = rate atteso (calib. Target 1 Mcps↔540 µSv/h, solo Cs-137). `baseline` =
mediana ADC $\approx$ proxy di HV: i 4 run a $\sim$195 sono a **stessa HV** (curva
gain–rate), il 616 a 3764 è a HV diversa; Am-241 ha energia diversa. La colonna $g$ è
confrontabile solo entro i Cs-137 a stessa HV (crolla 0.230→0.015, $\sim$15×).

**Dose $=$ ground truth (dato, NON stimato qui).** Viene dai metadati; verificato
$\text{dose}\approx 10^{6}\cdot\text{activity}/\text{distanza}^2$ (inverso del quadrato,
torna a $\pm6\%$ per i Cs-137). Per il Cs-137 monoenergetico la dose è $\propto$ al
**count rate** $\lambda$, quindi uso `dose` come proxy di $\lambda$ (calibrazione Target:
1 Mcps $\leftrightarrow$ 540 µSv/h). *La stima della dose DAL segnale (metodo Target) è
un'altra cosa, testata in* `target_test_report.md` *— qui la dose è l'input noto.*

**Gain "ground truth": NON c'è una misura indipendente.** Uso un **proxy relativo**
$g \propto \sqrt{\text{Msd}/\text{dose}}$, che segue da $\text{Msd}\propto \lambda\,g^2$
(a energia e forma d'impulso fisse) e $\lambda\propto\text{dose}$. Assunzioni: stessa
energia (Cs-137), stessa HV tra i run confrontati (stesso baseline ADC), Msd dominata
dal segnale (non dal rumore). È **relativo** (normalizzato), non assoluto.

**Regime:** tutti i run sono **oltre il ginocchio** (collasso), che sta a
$\lambda_\text{knee}\sim I_b/(q\,n_0\,G_0)\sim 180$ kcps a questa HV. **Nessun dato
"pre-crash/flat"** (vedi §fit).

**Cosa manca:** HV/gain assoluto per run (abbiamo solo il baseline ADC), efficienza del
rivelatore, conversione $Z(\eta)$, e un **run di dark/pedestal**.

## Relazioni: statistiche del segnale, proxy e gain-free

Con il gain che deriva/collassa, **non si "corregge"**: si sceglie una statistica in
cui il gain **si cancella**. Sotto scaling $A\to gA$: cumulanti di Campbell
$\kappa_n=\lambda\langle A^n\rangle I_n$ ($I_n=\int h^n$) scalano come $g^n$. Ecco cosa
misura ognuna e come scala:

| statistica | teoria | scala | equivale a | gain-free |
|---|---|---|---|---|
| media $m=\kappa_1$ | $\lambda\langle A\rangle I_1$ | $\propto g\,\lambda\langle A\rangle$ | corrente DC = dose non-comp. | no |
| Var $=\kappa_2$ | $\lambda\langle A^2\rangle I_2$ | $\propto g^2\lambda\langle A^2\rangle$ | potenza di fluttuazione | no |
| $\text{Msd}^1=C(0)-C(1)$ | $\lambda\langle A^2\rangle J_2$ | $\propto g^2\lambda$ | shot ad alta-f | no |
| skewness $\gamma_1=\kappa_3/\kappa_2^{3/2}$ | $\propto\lambda^{-1/2}$ | gain-free | $1/\sqrt{\text{occupancy}}$; segno = polarità | **sì** |
| eccesso kurtosi $\gamma_2=\kappa_4/\kappa_2^{2}$ | $\propto\lambda^{-1}$ | gain-free | $1/\text{occupancy}\approx1/(\lambda\tau_\text{eff})$ | **sì** |
| von Neumann $\text{Msd}/\text{Var}=1-\rho(1)$ | (forma) | gain-free | rise/roughness vs $\tau_\text{corr}$ | **sì** |
| CV potenza (per-record) | $\propto1/\sqrt{\text{occupancy}}$ | gain-free | # eventi per finestra | **sì** |

**Proxy utilizzabili** (il gain si cancella nei rapporti giusti):

| grandezza | proxy | equivale a | gain-free | requisiti / limiti |
|---|---|---|---|---|
| **rate $\lambda$** (DC) | $\text{mean}^2/\text{Var}$ | $\lambda\,\langle A\rangle^2/\langle A^2\rangle$ | **sì** | pedestal + Var noise-sub |
| rate $\lambda$ (AC) | $\kappa_2^2/\kappa_4$ | $\lambda\cdot(\text{SER,forma})$ | **sì** | pileup moderato; muore in gaussiano |
| **energia media** | $\eta=\text{Var}/\text{Msd}$ | $\langle A^2\rangle/\langle A\rangle$ | **sì** | shot risolto (fuori dai nostri dati) |
| energia (alt.) | $\kappa_3/\kappa_2$ | $\langle A^3\rangle/\langle A^2\rangle$ | no ($\propto g$) | drift-sensitive |
| pileup / regime | kurtosi, skewness | $1/\text{occupancy}$ | **sì** | monotòno con $\lambda\tau$; $\to0$ gaussiano |
| **gain (monitor)** | $\text{Var}/\text{mean}$ | $g\cdot\langle A^2\rangle/\langle A\rangle$ | no ($\propto g$) | noti $\lambda$ ed energia |

**In pratica:** il rate si prende con $\text{mean}^2/\text{Var}$ (`$\propto\lambda$`,
il gain si cancella *esattamente* — anche col crollo; validato in `pe_synth`), che
richiede solo il **pedestal** (dark run) e la sottrazione del rumore. Il gain, se serve
per l'energia, si **monitora** (non si corregge) da $\text{Var}/\text{mean}$.

**La kurtosi in dettaglio:** $\gamma_2=\dfrac{\kappa_4}{\kappa_2^{2}}=\dfrac{1}{\lambda}\dfrac{\langle A^4\rangle}{\langle A^2\rangle^{2}}\dfrac{I_4}{I_2^{2}}$
— adimensionale (gain-free), $\propto1/(\lambda\tau_\text{eff})$ = **inverso del numero
medio di impulsi sovrapposti**. Grande a basso rate (spiky), $\to0$ in pileup profondo
(gaussiano). È un **misuratore di occupancy, non di energia**; la skewness dà la stessa
info più il **segno** (polarità).

---

# Modello minimale omogeneo del gain ad alto rate

*(Punto di partenza: N stadi, parametri omogenei. La versione multi-stadio
completa/dinamica è più sotto come estensione.)*

## Ipotesi (tutte omogenee)
- $N$ stadi, resistori del partitore **tutti uguali** $R$.
- Corrente di bias del partitore $I_b = V_{HV}/(N R)$; tensione nominale per stadio $V_0 = I_b R = V_{HV}/N$.
- Legge di dinodo **uguale per tutti**: $\delta(V) = a\,V^{k}$, con $k \approx 0.7\text{–}0.8$.
- Gain nominale (a vuoto) $G_0 = (a\,V_0^{k})^{N}$.
- Corrente d'anodo (segnale): $I_a = q\,n_0\,\lambda\,G$ (carica × p.e./evento × rate × gain).

## Derivazione
Il gain è il prodotto delle amplificazioni di stadio, $G=\prod_{i=1}^{N}\delta_i=a^{N}\big(\prod_i V_i\big)^{k}$.
Il carico di segnale abbassa le tensioni; all'ordine dominante, nel caso omogeneo,
ogni stadio subisce la **stessa frazione di caduta** $\rho$: $\;V_i \simeq V_0(1-\rho)$, con $\rho \equiv I_a/I_b$.
Quindi $\;G = G_0(1-\rho)^{Nk}$, con $\rho = q\,n_0\,\lambda\,G/I_b$.
È **auto-consistente** ($G$ compare anche dentro $\rho$); sostituendo:
$\;G = G_0\big(1-\tfrac{q\,n_0\,\lambda}{I_b}\,G\big)^{Nk}$.

## Comportamento
Un'unica variabile di controllo: il **carico** $\rho = I_a/I_b$ (corrente d'anodo / corrente di bias).

- **Basso rate** ($I_a \ll I_b$): $G \approx G_0$ (piatto). Linearizzato:
  $G \approx G_0\,[\,1 - N k\,(q n_0 G_0/I_b)\,\lambda\,]$ → **droop lineare**, pendenza $\propto Nk/I_b$.
- **Collasso**: al crescere di $\lambda$, $\rho \to 1$ e $G \to 0$. Poiché $I_a = q n_0 \lambda G$
  e $G$ cala, **la corrente d'anodo si satura verso $\sim I_b$** (non può superare il bias).
  Ginocchio a $\;\lambda_{\max} \sim I_b/(q\,n_0\,G_0)\;$ (dove $I_a \sim I_b$).

Consistenza col brevetto: il limite "**max anode current 0.1 mA**" *è* la corrente
di bias tipica ($V_{HV}\sim 1$ kV, $\Sigma R\sim 10$ MΩ → $I_b\sim 0.1$ mA). Collasso a $I_a\sim I_b$ ⇔ tetto a 0.1 mA.

## Limite del modello minimale
Con parametri **omogenei e caduta uniforme** il gain è **monotòno**: piatto →
droop → collasso. **Niente "bump"** (la salita iniziale osservata). Il bump
richiede l'unica rottura di omogeneità che conta: gli **ultimi** stadi salgono di
tensione mentre i **primi** scendono (redistribuzione a segno opposto). È l'unico
ingrediente da aggiungere, e solo lì, se/quando serve modellare la salita.

## Forma risolta (per riferimento)
$G = G_0\,e^{-c\lambda G}$ (versione con caduta esponenziale, $c = Nk\,q n_0/(\delta I_b)$)
ha soluzione $G = W(c\lambda G_0)/(c\lambda)$ con $W$ la funzione di Lambert → gain
$\approx$ costante a basso rate, poi $\sim \ln(\lambda)/\lambda$ ad alto rate. La forma
$(1-\rho)^{Nk}$ dà un collasso più netto a $I_a\to I_b$. In entrambe: **un solo numero
adimensionale governa tutto, $I_a/I_b$.**

## Soluzione numerica e confronto coi dati (`gain_solve.py`)

Con $g\equiv G/G_0$ e $r\equiv I_a^{(0)}/I_b = q n_0 \lambda G_0/I_b$ (carico a gain
nominale), l'equazione è $g=(1-r g)^{Nk}$. La funzione $F(g)=g-(1-rg)^{Nk}$ è
strettamente crescente ($F'=1+Nk\,r(1-rg)^{Nk-1}>0$) ⇒ **radice unica** (nessun
equilibrio multiplo in questo ramo); risolta con brentq.

![soluzione e fit](gain_solve.png)

- **Sx**: gain relativo $g(r)$ — piatto per $r\ll1$, ginocchio a $r=1$, poi crollo.
- **Centro**: $I_a/I_b = r\,g \to 1$ per $r\to\infty$ — **la corrente d'anodo si satura
  alla corrente di bias** (il "tetto 0.1 mA" del brevetto).
- **Dx**: i 3 run a stessa configurazione (gain $\propto \sqrt{\text{Msd}/\text{dose}}$)
  cadono **sulla curva del modello** ($p=Nk=7.5$), fittando la sola scala di carico $\alpha$:

| run | gain dati (rel) | gain modello (rel) | r = α·dose |
|---|---|---|---|
| 7900 | 1.000 | 1.000 | 2194 |
| 17990 | 0.447 | 0.461 | 4996 |
| 28100 | 0.309 | 0.302 | 7804 |

Gain-drop 7900→28100: **misurato 3.2× , modello 3.3×**. Tutti i run stanno a
$r\gg1$ (ben oltre il ginocchio) → **regime di collasso**, dove $g\propto 1/\lambda$
($I_a$ clampata a $I_b$). Il ginocchio ($r\sim1$) e l'eventuale bump cadono a rate
più bassi ($\sim$ centinaia di kcps), non campionati a HV fissa → servirebbe uno
scan a HV fisso per testare la parte piatta e la salita.

## Sistema accoppiato completo: drop diversi per stadio (`gain_ladder.py`)

Qui **niente** approssimazione di caduta uniforme: ogni stadio ha la sua tensione,
ottenuta risolvendo il circuito. Il partitore è una **rete a scala** di resistori
(qui $R$ omogenei) su un alimentatore che tiene **fissa** la tensione totale
$V_{HV}$, cioè $\sum_i V_i = V_{HV}$ sempre.

**Nodi.** Numeriamo i nodi $U_0=0$ (catodo), $U_1,\dots,U_N$ (dinodi), $U_{N+1}=V_{HV}$
(anodo). La tensione acceleratrice dello stadio $i$ è il salto $V_i = U_i - U_{i-1}$,
e il guadagno di quel dinodo è $\delta_i = a\,V_i^{\kappa}$.

**Correnti nel tubo.** La corrente di fascio che *entra* nel dinodo $i$ è
$J_i = I_0\prod_{j=1}^{i-1}\delta_j$, con $I_0 = q\,n_0\,\lambda$ (corrente di catodo).
Il dinodo $i$ riceve $J_i$ ed **emette** $\delta_i J_i$ secondari: i $(\delta_i-1)J_i$
elettroni netti in più glieli deve **fornire il partitore**. Quindi al nodo $i$ il
tubo *preleva* dalla rete la corrente $t_i = (\delta_i-1)\,J_i$ — che **cresce verso
l'anodo**, perché $J_i$ si moltiplica di $\delta$ a ogni stadio (gli ultimi dinodi
caricano il partitore molto più dei primi).

**Kirchhoff (KCL) a ogni nodo dinodo** $i=1,\dots,N$ — la somma delle correnti al
nodo è nulla, cioè quanto arriva dai due resistori adiacenti eguaglia quanto preleva
il tubo:
$\;\dfrac{U_{i-1}-U_i}{R} + \dfrac{U_{i+1}-U_i}{R} = t_i = (\delta_i-1)\,J_i.$

Sostituendo $\delta_j=a\,(U_j-U_{j-1})^{\kappa}$ e $J_i=I_0\prod_{j=1}^{i-1}\delta_j$
si ottiene il **sistema non lineare accoppiato**, chiuso nelle sole incognite
$U_1,\dots,U_N$ (per $i=1,\dots,N$):

$\;\dfrac{U_{i-1}-2U_i+U_{i+1}}{R} \;=\; I_0\,\big[\,a\,(U_i-U_{i-1})^{\kappa}-1\,\big]\displaystyle\prod_{j=1}^{i-1} a\,(U_j-U_{j-1})^{\kappa}$

con condizioni al contorno $U_0=0$, $U_{N+1}=V_{HV}$, e $I_0=q\,n_0\,\lambda$. Il
membro sinistro è il Laplaciano discreto (corrente netta dei resistori al nodo $i$),
quello destro la corrente $t_i$ prelevata dal tubo. Sono **$N$ equazioni non lineari**
accoppiate (ogni $U_i$ compare in tutti i fattori $\prod$ per gli stadi a valle) →
risolte con `fsolve` + continuazione in $\lambda$. **Solubile senza problemi.**

*Check a vuoto* ($I_0=0$): resta $U_{i-1}-2U_i+U_{i+1}=0$ → rampa lineare,
$V_i=V_{HV}/(N{+}1)$ uniforme. Il gain totale è $G=\prod_i\delta_i=a^{N}\big(\prod_i V_i\big)^{\kappa}$.

![ladder](gain_ladder.png)

**Cosa emerge:**
1. **Redistribuzione** (sx): al crescere del rate il profilo si inclina — i primi
   stadi si **affamano** ($V_1: 91\to46$ V), gli **ultimi salgono sopra $V_0$**
   ($V_{10}\to122$ V). Il meccanismo qualitativo della collega (ultimi su / primi giù)
   **emerge da solo** dal circuito omogeneo, senza rompere a mano nulla.
2. **Ma il gain TOTALE resta monotòno decrescente — niente bump** (centro). Motivo
   netto: $G=a^{N}(\prod_i V_i)^{\kappa}$ e a **$\sum V_i=V_{HV}$ fissa** ogni
   redistribuzione a somma costante **abbassa $\prod_i V_i$** (disuguaglianza AM-GM)
   → il gain può *solo* scendere. Il ladder scende **più lento** dell'uniform-drop
   (la salita degli ultimi stadi compensa in parte), ma non risale mai.
3. **Corrente d'anodo** (dx): $I_a$ supera $I_b$ dove il modello è spinto oltre
   validità (lì il partitore è già saturo).

**Conclusione forte:** il **bump non può nascere dalla redistribuzione omogenea a
$V_{HV}$ fissa** — è un teorema (AM-GM), non un dettaglio numerico. Se il gain sale
davvero a rate moderato, serve fisica *fuori* da questo modello:
- primo stadio **protetto** ($R_1$ maggiore o zener) → $\prod_i V_i$ non più vincolato come sopra;
- **alimentatore non rigido** ($V_{HV}$ varia col carico);
- **space charge** / efficienza di raccolta al primo dinodo.
È qui, e solo qui, che conviene rompere l'omogeneità.

### Fit ai dati reali: stima della scala di carico (`gain_ladder_fit.py`)

Fittiamo il ladder ai **4 run a stessa HV** (baseline ADC ~195) del Cs-137 —
{889, 7900, 17990, 28100} µSv/h — includendo il run a rate **più basso, 889**
($\sim$1.65 Mcps), che è il più vicino alla "pre-rottura". Gain relativo
$\propto\sqrt{\text{Msd}/\text{dose}}$, dose $\propto\lambda$. Unico parametro libero:
la **scala di carico** $c$ ($I_0=c\,\lambda$, assorbe $q\,n_0$); $N,\kappa,R,V_{HV}$
fissati. Il ladder **riproduce i dati**: gain-drop 889→28100 **15× (dati) vs 15×
(modello)**, residuo $\sim9\times10^{-3}$.

| $N$ | $\kappa$ | $N\kappa$ | scala $c$ | gain modello (rel) | residuo |
|---|---|---|---|---|---|
| 10 | 0.75 | 7.5 | $1.2\times10^{-12}$ | $[1,\,0.197,\,0.099,\,0.068]$ | $8.9\times10^{-3}$ |
| 8 | 0.70 | 5.6 | $1.6\times10^{-11}$ | $[1,\,0.198,\,0.099,\,0.067]$ | $7.7\times10^{-3}$ |
| 12 | 0.80 | 9.6 | $8.2\times10^{-14}$ | $[1,\,0.196,\,0.099,\,0.068]$ | $9.7\times10^{-3}$ |
| 14 | 0.75 | 10.5 | $5.7\times10^{-15}$ | $[1,\,0.196,\,0.099,\,0.068]$ | $1.0\times10^{-2}$ |

(dati: $[1,\,0.213,\,0.095,\,0.066]$)

![fit ladder vs dati](gain_ladder_fit.png)

**Perché non basta il pre-crash?** (la domanda giusta.) Anche includendo 889 la
degenerazione **resta**: tutte le $(N,\kappa)$ fittano ugualmente bene. Il motivo è
che **anche 889 è già oltre il ginocchio**. Il ginocchio è dove $I_a\sim I_b$, cioè
$\lambda_{\text{knee}}\sim I_b/(q\,n_0\,G_0)\sim 180$ kcps a questa HV — circa **10×
sotto** il run più basso (889 $\approx$ 1.65 Mcps). Quindi **tutti** i run stanno in
collasso ($r\gg1$), dove $g\propto1/\lambda$ è universale (indipendente da $N,\kappa,R$);
889 estende solo il *lato crollo*, non tocca la parte piatta. Nella figura (sx) le
curve $(N,\kappa)$ coincidono su **tutti e 4** i punti e divergono solo a
$\lambda\ll\lambda(889)$, cioè al ginocchio non campionato.

**Cosa si stima:** la **scala di carico** (dove sei sulla curva di crollo) — ben
determinata; basta questa per correggere/prevedere il gain nel regime di lavoro.
**Cosa serve per $N,\kappa,R$:** dato **pre-crash vero**, cioè run a $\lesssim180$ kcps
(dose $\lesssim100$ µSv/h a questa HV) **oppure a HV più bassa** (che sposta il ginocchio
a rate più alto, dentro il range misurabile). Lì la curvatura del ginocchio discrimina.

---

# Proposal: Dynamic Multi-Stage Model of PMT Gain under High-Rate Operation

*(Estensione completa — utile in seguito; per ora si parte dal modello minimale sopra.)*

## Motivation

The gain of a photomultiplier tube (PMT) is usually treated as a static function of the applied high voltage. However, when the PMT is operated at high count rates using a passive resistive voltage divider, the gain becomes **activity dependent**.

The physical mechanism is well known:

- the average anode current increases with the event rate;
- the current flowing through the dynodes perturbs the voltage divider;
- the inter-dynode voltages change;
- the multiplication factor of each dynode changes;
- consequently, the total gain changes.

Most existing descriptions are empirical, expressing the gain as a function of average anode current,

$G = G(I_A)$,

without explicitly modeling the feedback responsible for this behavior.

The objective of this work is to formulate a **dynamic self-consistent model** in which the gain is an emergent quantity arising from the interaction between the electron multiplication chain and the voltage divider.

---

# Physical picture

A PMT is viewed as a cascade of $N$ multiplication stages.

Each stage is characterized by

- an inter-dynode voltage,
- a multiplication factor,
- an electron current.

The voltage divider distributes the high voltage among the stages, but the electron currents perturb the divider itself.

Therefore,

```
event rate
      ↓
electron current
      ↓
voltage divider perturbation
      ↓
inter-dynode voltages
      ↓
stage gains
      ↓
total gain
      ↓
electron current
```

forming a nonlinear feedback loop.

---

# State variables

For each dynode stage $i=1,\ldots,N$ define

- $V_i(t)$: voltage across stage $i$;
- $I_i(t)$: electron current through stage $i$;
- $\delta_i(t)$: multiplication factor of stage $i$.

The multiplication factor is assumed to depend only on the local voltage, $\delta_i=f_i(V_i)$.

A common approximation is $\delta_i=A_iV_i^{k_i}$, with $k_i\simeq0.7-0.8$.

---

# Electron multiplication

Assume an event rate $R$ and an average number of photoelectrons produced at the photocathode $n_0$.

The current entering the first dynode is $I_1=qRn_0$.

Each stage amplifies the electron population, so $I_2=qRn_0\delta_1$, $I_3=qRn_0\delta_1\delta_2$, and in general

$I_i = qRn_0 \prod_{k=1}^{i-1}\delta_k$

which immediately explains why the last dynodes sustain much larger currents.

---

# Voltage divider feedback

Let $R_i$ be the resistor associated with stage $i$, and $I_{bias}$ the divider current.

The current available at each stage is reduced by the electron current extracted downstream,

$I_i^{(div)} = I_{bias} - \sum_{k=i}^{N}I_k$.

The voltage across each stage becomes

$V_i = R_i \left( I_{bias} - \sum_{k=i}^{N}I_k \right)$

instead of remaining constant.

---

# Self-consistent nonlinear system

Substituting $I_k = qRn_0 \prod_{j=1}^{k-1}\delta_j$ and $\delta_j=f_j(V_j)$ gives

$V_i = R_i \left( I_{bias} - qRn_0 \sum_{k=i}^{N} \prod_{j=1}^{k-1} f_j(V_j) \right)$

for $i=1,\ldots,N$.

This is a coupled nonlinear system whose unknowns are the inter-dynode voltages.

---

# Emergent gain

The PMT gain is no longer imposed. Instead,

$G = \prod_{i=1}^{N}\delta_i = \prod_{i=1}^{N} f_i(V_i)$

emerges automatically once the nonlinear system has been solved.

Consequently, $G=G(R)$ is obtained as a prediction of the model rather than as an empirical calibration curve.

---

# Dynamic formulation

To account for transient behavior and parasitic capacitances, each node can be assigned a capacitance $C_i$.

The node dynamics become

$C_i\dfrac{dV_i}{dt} = I_{bias} - \sum_{k=i}^{N}I_k - \dfrac{V_i}{R_i}$.

The gain becomes $G(t) = \prod_i f_i(V_i(t))$.

The steady-state solution corresponds to the equilibrium point of the system.

---

# Stability analysis

The equilibrium voltages satisfy $\dfrac{dV_i}{dt}=0$.

Linearization around the equilibrium allows computation of

- stability;
- relaxation times;
- sensitivity to count rate;
- onset of saturation.

The model naturally predicts:

- gain drift;
- gain saturation;
- collapse of multiplication;
- possible hysteresis;
- multiple equilibrium points.

---

# Stochastic extension

The previous formulation assumes a deterministic event rate.

A more realistic description considers photon arrivals as a point process $N(t)$.

The electron currents become stochastic processes $I_i(t)$.

Consequently, $V_i(t)$ and $G(t)$ become stochastic state variables.

The resulting framework combines

- point processes,
- nonlinear dynamical systems,
- stochastic differential equations.

This formulation naturally incorporates fluctuations due to photon statistics without introducing empirical gain fluctuations.

---

# Alternative compartment model

Instead of directly modeling the currents, one may introduce the electron population at each stage.

Let $n_i(t)$ be the average number of electrons stored in stage $i$.

The dynamics become

$\dfrac{dn_i}{dt} = R\delta_{i-1} - \dfrac{n_i}{\tau_i}$.

The current is then $I_i=qn_i$.

The voltage divider and multiplication chain remain coupled exactly as before.

This representation resembles a compartment model and may provide a more physically interpretable description of electron transport.

---

# Expected outcomes

The proposed framework would provide

- a physically motivated model of activity-dependent gain;
- prediction of gain as a function of count rate without empirical fitting;
- description of transient gain evolution;
- stability analysis of the PMT operating point;
- extension to stochastic photon arrival processes;
- possible explanation of nonlinear saturation and hysteresis observed experimentally.

---

# Long-term perspectives

The same formalism could be extended to include

- space charge effects;
- active voltage dividers;
- photocathode recovery;
- afterpulsing;
- aging;
- pulse-height distributions;
- time resolution degradation at high rate.

Ultimately, the PMT is reformulated not as a static gain element but as a **nonlinear dynamical network** whose macroscopic behavior emerges from the interaction between electron multiplication and the biasing circuit.
