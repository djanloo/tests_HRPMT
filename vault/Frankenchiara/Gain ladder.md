---
type: nota
project: frankenchiara
updated: 2026-07-23
tags: [tipo/nota, progetto/frankenchiara]
---

# Il modello ladder della perdita di gain

Uno spin-off laterale ma bello, e spiega **perché** il gain collassa — cioè perché tutto
il resto del progetto ha dovuto diventare gain-free ([[Statistiche gain-free]]).

Codice: `target_test/gain_ladder.py` (il modello), `target_test/gain_ladder_fit.py` (fit).

## Il meccanismo, a parole

Il gain di un PMT è dato dalle tensioni tra i dinodi, che a riposo sono fissate da un
**partitore resistivo** (una catena di resistori tra l'alta tensione e massa). Ma quando
il rate è alto, la **corrente d'anodo** diventa importante: gli elettroni moltiplicati
vengono "prelevati" dal partitore, ne **perturbano le tensioni**, e quindi **cambiano il
gain**. Si crea un anello di retroazione:

```
rate ↑  →  corrente elettronica ↑  →  perturba il partitore
     →  tensioni tra dinodi ↓  →  gain ↓  →  (corrente d'anodo)
```

## Lo schema

Il circuito è quello nella figura di [[Rivelatore e dati]] (catena di resistori in basso,
lettura sulla resistenza d'anodo), e la netlist con i valori sta in [[Hardware]].

La parte che nessuna figura di libro mostra, ed è il cuore del modello: a ogni nodo dinodo
il tubo scambia con il partitore un termine di carico

$$ t_i = (\delta_i - 1)\,J_i, \qquad J_i = I_0\prod_{j<i}\delta_j $$

cioè i secondari che ogni dinodo emette li paga la catena di resistori, e $J_i$ cresce di
$\delta$ a ogni stadio — per questo **gli ultimi dinodi caricano il partitore molto più
dei primi**.

### I $t_i$ tornano nelle resistenze, ed è lì il meccanismo

Va detto esplicitamente perché è la cosa che rende il modello non banale. Le correnti nei
resistori **non sono tutte uguali a $I_b$**: crescono verso l'anodo, di esattamente $t_i$
a ogni nodo. Con $I_0 = 3\cdot10^{-10}$ A:

| resistore | R1 | R2 | … | R8 | R9 | R10 | R11 |
|---|---|---|---|---|---|---|---|
| corrente [µA] | 84.97 | 84.97 | … | 87.08 | 92.56 | 113.6 | **211.1** |

L'ultimo resistore porta **2.5× il primo**. Ed è per questo che il profilo di tensione si
inclina: $V_i = I_i R$ con $I_i$ diverse. **Senza questo, non c'è meccanismo** — sarebbe
solo una caduta uniforme.

Se disegni i generatori di corrente ai nodi per spiegare il **meccanismo**, non farli tornare
a massa: il ritorno è attraverso il tubo, fino a $I_a$ all'anodo. Se invece ti serve un
**circuito equivalente** da simulare, il sink verso GND è lecito e dà gli stessi numeri —
perché qui l'anodo *è* a massa e la corrente d'anodo ci torna via $R_L$. I due quadri e il
perché coincidono stanno in [[Circuito equivalente del PMT]].

### Il segno del termine di carico (verificato)

La KCL nel codice è $(U_{i-1}-U_i)/R + (U_{i+1}-U_i)/R = +t_i$, e **è giusta** — il
quadro a *current sink* di [[Circuito equivalente del PMT]] dà lo stesso segno per costruzione. Con $U$
crescente verso l'anodo quel membro sinistro **non** è "la corrente entrante nel nodo": vale
$I_{i+1}-I_i$, cioè di quanto la corrente di catena cresce attraversando il nodo. È un
Laplaciano discreto, ed è quello che dice la tabella sopra.

Verificato numericamente il 2026-08-03, perché una lettura affrettata di quel termine dà il
segno opposto:

- con $+t_i$: `fsolve` converge (residuo $8\cdot10^{-15}$), $I_{k+1}-I_k = t_k$ a $8\cdot10^{-11}$
  relativo, e **$\sum_i t_i = I_a - I_0$ esattamente** — conservazione globale della carica;
- con $-t_i$: `fsolve` non converge (residuo $5.6\cdot10^{-5}$), le correnti nei resistori
  sono non monotone e non tornano con nessuno dei due segni. Non è una soluzione.

Due convenzioni da tenere a mente, entrambe verificate:

- **Catodo a $-V_{HV}$, anodo a massa.** È l'unico schema compatibile con la lettura
  DC-coupled su shunt verso massa ([[Catena di lettura]]). Il codice risolve con $U_0=0$ e
  $U_{N+1}=V_{HV}$, cioè l'etichettatura a HV positiva: è una **scelta di gauge**, non un
  disaccordo — il modello dipende solo dalle differenze $V_i$ e dal vincolo
  $\sum_i V_i = V_{HV}$, quindi traslare tutti i potenziali non cambia nulla.
- **$N$ dinodi → $N+1$ gap → $N+1$ resistori**, e solo i primi $N$ moltiplicano. Con
  $N=10$, $V_{HV}=1$ kV e $I_b=0.1$ mA: 11 resistori da 909 kΩ, $\Sigma R = 10$ MΩ, e a
  vuoto 90.9 V per gap — che è il "$V_1 = 91$ V" citato sotto.

## Il modello

Si risolve il circuito, e non è complicato: sono $N$ equazioni di Kirchhoff. Il partitore
è una **rete a scala** ("ladder") di resistori con l'alimentatore che tiene
$\sum_i V_i = V_{HV}$ fissa. Numerati i nodi $U_0=0$ (catodo), $U_1,\dots,U_N$ (dinodi),
$U_{N+1}=V_{HV}$ (anodo):

- tensione dello stadio $i$: $V_i = U_i - U_{i-1}$, gain di stadio
  $\delta_i = a V_i^\kappa$;
- corrente di fascio che entra nel dinodo $i$: $J_i = I_0 \prod_{j<i}\delta_j$ (con
  $I_0 = q n_0 \lambda$), che **cresce verso l'anodo** perché si moltiplica a ogni stadio;
- il dinodo $i$ preleva dal partitore $t_i = (\delta_i - 1)J_i$.

La **legge di Kirchhoff** (KCL) ad ogni nodo dà il sistema non lineare accoppiato:

$$ \frac{U_{i-1} - 2U_i + U_{i+1}}{R} = (\delta_i - 1)\,J_i,\qquad i = 1,\dots,N $$

(a sinistra il Laplaciano discreto = corrente netta dei resistori; a destra la corrente
prelevata dal tubo). $N$ equazioni, risolte numericamente con continuazione in λ. A vuoto
($I_0=0$) torna la rampa lineare $V_i = V_{HV}/(N{+}1)$, come dev'essere.

![[gain_ladder.png]]
*(sx) profilo di tensione per stadio — i primi stadi si affamano, gli ultimi salgono;
(centro) gain totale monotòno decrescente, niente bump; (dx) corrente d'anodo che satura
verso I_b.*

### Cosa emerge

1. **Redistribuzione** (sx): al crescere del rate il profilo di tensione si inclina — i
   **primi stadi si affamano** ($V_1: 91\to 46$ V), gli **ultimi salgono sopra $V_0$**
   ($V_{10}\to 122$ V). Il meccanismo qualitativo "ultimi su / primi giù" **emerge da
   solo** dal circuito omogeneo, senza rompere nulla a mano.

2. **Ma il gain totale resta monotòno decrescente — niente "bump".** Questo è un
   **teorema**, non un dettaglio numerico: essendo $G \propto (\prod_i V_i)^\kappa$ e
   $\sum_i V_i = V_{HV}$ *fissa*, ogni redistribuzione a somma costante **abbassa il
   prodotto** $\prod_i V_i$ (disuguaglianza delle medie, **AM-GM**). Quindi il gain può
   *solo* scendere. La salita degli ultimi stadi rallenta la discesa, ma **non la
   inverte mai**.

   → Conseguenza forte: se in un esperimento il gain *salisse* davvero a rate moderato
   (il "bump" che a volte si osserva), **non** potrebbe nascere da questa
   redistribuzione. Servirebbe fisica *fuori* dal modello: primo stadio protetto
   (zener/$R_1$ maggiore), alimentatore non rigido, o *space charge* al primo dinodo.

   ⚠️ **E il partitore vero ce l'ha, quel primo stadio protetto.** Dai datasheet
   ([[Hardware]]) la catena è **tarata**: 180K, 850K, 1M, 1M, poi 470K×6 — i primi stadi
   hanno resistori più grandi, che è esattamente l'ingrediente che rompe la premessa
   "tutti uguali" su cui poggia l'AM-GM. **Il teorema vale per resistori uguali; questo
   tubo non li ha**, quindi per questo hardware la monotonia non è dimostrata. Il codice
   prende $R$ come scalare e non può nemmeno rappresentarlo. Vedi [[Backlog]].

3. **La corrente d'anodo satura verso $I_b$** (dx): non può superare la corrente di bias
   del partitore. Il ginocchio della curva sta dove $I_a \sim I_b$, cioè a
   $\lambda_\text{knee} \sim I_b/(q n_0 G_0) \sim 175$ kcps a questa HV
   ($\Sigma R$ = 5.85 MΩ, −570 V).

   ✅ **E questo numero è validato dall'esterno.** Scionix dichiara i 470 kΩ del nostro
   partitore *"sufficient for count rates up to approx. 50.000 c/s"*, e la letteratura
   riporta che un partitore **tarato** — il nostro — alza la carica di saturazione di
   **≥4×**: 50 × 4 = **~200 kcps**, contro i 175 kcps del ladder, che non era tarato su quel
   numero. Due strade indipendenti che concordano — [[Stato dell'arte]].

**Cross-check col brevetto** ([[Metodo Target]]): il limite tipico di targa "**max anode
current 0.1 mA**" *è* la corrente di bias tipica ($V_{HV}\sim 1$ kV,
$\Sigma R\sim 10$ MΩ → $I_b \sim 0.1$ mA). Il collasso a $I_a \sim I_b$ **è** quel tetto,
ricavato da un vincolo di circuito invece che letto da una tabella.

## Come si stima il gain dai segnali

Prima del fit serve un gain *misurato* da confrontare col modello, e **non c'è una misura
indipendente**: nessun readback di HV, nessuna sorgente di riferimento, nessun dark run.
Quindi si costruisce un **proxy relativo** dai soli segnali, e lo si deriva da Campbell.

### La derivazione, in tre passi

**(1) Cosa misura la Msd.** La *mean square successive difference* è
$\text{Msd} = \tfrac12\langle(\Delta x)^2\rangle = C(0)-C(\delta)$ (`target_method.msd`,
calcolata per record e poi mediata). Per [[Cumulanti e Campbell]] è un $\kappa_2$ su
kernel $g = h(t)-h(t-\delta)$, quindi

$$ \text{Msd} \;\propto\; \lambda\,\langle A^2\rangle $$

a forma d'impulso $h$ fissata. Il rumore gaussiano ci aggiunge $\sigma_n^2$, che viene
**sottratto esplicitamente** (misurato dal plateau PSD ad alta frequenza, come in
[[Stima del rate dai cumulanti]]); il codice riporta anche `noise_frac_of_msd` per far
vedere quanto pesa.

**(2) Dove entra il gain.** Il gain scala tutte le ampiezze, $A \to g A$, quindi
$\langle A^2\rangle \to g^2\langle A^2\rangle$:

$$ \text{Msd} \;\propto\; \lambda\,g^2\,\langle A^2\rangle_0 $$

con $\langle A^2\rangle_0$ fissato dall'energia della sorgente. Questa è la stessa
dipendenza $\propto g^2$ per cui la Msd è **inutilizzabile** come proxy di dose
([[Statistiche gain-free]]) — qui la si sfrutta al contrario: se la dose è nota, quel
$g^2$ diventa l'incognita interessante.

**(3) Si elimina λ con la dose nota.** Il Cs-137 è monoenergetico, quindi
$\text{dose} \propto \lambda \times$ (energia fissa) $\propto \lambda$. Sostituendo:

$$ \boxed{\;g \;\propto\; \sqrt{\frac{\text{Msd}}{\text{dose}}}\;} $$

### I numeri

Solo i **4 run a stessa HV** (baseline ADC ~195), normalizzati al run 889:

| dose [µSv/h] | Msd | $\sqrt{\text{Msd}/\text{dose}}$ | $g$ relativo |
|---|---|---|---|
| 889 | 46.95 | 0.2298 | 1.000 |
| 7900 | 19.00 | 0.0490 | 0.213 |
| 17990 | 8.65 | 0.0219 | 0.095 |
| 28100 | 6.45 | 0.0152 | 0.066 |

→ caduta di gain **15.2×** fra 889 e 28100 µSv/h. È il numero che il ladder deve
riprodurre.

### Le cinque assunzioni, ognuna un modo di sbagliare

1. **Stessa energia** per tutti i run confrontati → solo Cs-137. L'**Am-241 è escluso**
   (59.5 vs 662 keV: $\langle A^2\rangle_0$ è un altro numero).
2. **Stessa HV** → solo i 4 run a baseline ADC ~195. Il run **616 è escluso**: baseline
   3764, cioè un'altra HV, quindi un altro $G_0$ e un altro punto sulla curva.
3. **Msd dominata dal segnale**, non dal rumore — verificato sottraendo $\sigma_n^2$ e
   riportando la frazione residua.
4. **Stessa forma $h$** fra i run: se il rise cambiasse col rate, cambierebbe anche
   l'integrale di forma e la proporzionalità si romperebbe.
5. **dose $\propto \lambda$**, vero per una sorgente monoenergetica.

**È relativo, non assoluto**: dà *dove ti trovi* sulla curva di crollo, non $G_0$. Per il
gain assoluto servirebbe un dark run ([[Limiti]]).

### Due onestà sul proxy

**La scelta Msd-vs-Var sposta il risultato.** Usando la varianza al posto della Msd —
stessa derivazione, $\text{Var} \propto \lambda\langle A^2\rangle$ — la caduta viene
**21.9×** invece di 15.2×. Si preferisce la Msd perché usa solo differenze successive e
quindi è robusta alle derive lente (von Neumann), mentre la Var raccoglie anche il
wandering di baseline. Ma il numero dipende dal proxy al ~40%: il "15×" va letto come
ordine di grandezza verificato, non come misura al percento.

**Cosa sta davvero testando il fit.** L'unico ingrediente *misurato* è la Msd; la dose è
un input noto dai metadati. Quindi fittare $g_\text{data}$ contro il ladder equivale a
chiedersi se **la Msd cresce con la dose più lentamente del lineare, e in esattamente il
modo predetto dal circuito**. Non è circolare — dose e Msd sono indipendenti — ma è utile
sapere che il contenuto empirico è quello, una sola curva sub-lineare, ed è anche il
motivo per cui un solo parametro libero basta a fittarla.

## Il ladder riproduce i dati reali

Fit ai **4 run a stessa HV** con il gain relativo appena costruito, e un solo parametro
libero (la scala di carico $c$; $N,\kappa,R,V_{HV}$ fissati). Il ladder **riproduce il
calo di gain 15× misurato** (modello 15×, residuo ~$9\times 10^{-3}$):

![[gain_ladder_fit.png]]
*(sx) le curve (N,κ) coincidono su tutti e 4 i punti e divergono solo al ginocchio non
campionato; (dx) la curva continua del ladder passa per i 4 punti misurati — il calo di
gain 15× è riprodotto.*

**Cosa si stima bene:** la *scala di carico* — dove ti trovi sulla curva di crollo — che
basta per prevedere/correggere il gain nel regime di lavoro.

**Cosa resta degenere:** i parametri $N, \kappa, R$ separatamente. Il motivo (e la
domanda giusta) è che **tutti** i run, anche il più basso (889 µSv/h ≈ 1.65 Mcps), sono
**oltre il ginocchio** — che qui sta a $\lambda_\text{knee}\sim 180$ kcps, ~10× più in
basso. Nel regime di collasso ($r \gg 1$) vale universalmente $g \propto 1/\lambda$,
indipendente da $N,\kappa,R$: quei parametri si discriminerebbero solo con dati
**pre-crash veri** (rate ≲ 180 kcps, o una HV più bassa che sposta il ginocchio nel range
misurabile). Vedi [[Limiti]] e.

## Morale dello spin-off

Il gain di questo PMT, ad alto rate, **crolla come $1/\lambda$** perché la corrente
d'anodo satura alla corrente di bias del partitore. Ecco *perché* media/Var/Msd sono
inservibili per la dose, e perché tutta la pipeline ([[Stima della dose]]) è costruita su
statistiche gain-free.
