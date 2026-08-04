---
type: nota
project: frankenchiara
updated: 2026-07-23
tags: [tipo/nota, progetto/frankenchiara]
---

# Statistiche gain-free

L'idea centrale del progetto, e la ragione per cui la pipeline finale funziona. Qui
sta anche la tabella maestra: **il cuore operativo di tutto il lavoro**.

## Il problema: g è un traditore

**g — il gain del PMT**, il fattore di moltiplicazione dei dinodi. Il gain **scala
tutte le ampiezze**: se $g$ raddoppia, ogni impulso raddoppia, $A_k \to g\,A_k$. E in
questo rivelatore $g$ **non è costante**: con un partitore resistivo passivo, ad alto
rate il gain **deriva e poi collassa** ([[Gain ladder]] per il meccanismo).

Quindi qualunque statistica che dipenda da $g$ è inaffidabile: **non sappiamo separare
"più eventi" da "gain più basso"**. Questo è il muro contro cui sbatte l'approccio
ingenuo.

Da [[Cumulanti e Campbell]] sappiamo come il gain entra: $\kappa_n \propto g^n$, cioè
media $\propto g$, Var $\propto g^2$, $\kappa_3 \propto g^3$, $\kappa_4 \propto g^4$.

## L'idea chiave

La soluzione non è *correggere* il gain (non lo conosciamo), ma **scegliere
combinazioni di statistiche in cui $g$ si cancella da solo**.

Il trucco è banale una volta visto. Sappiamo che $\kappa_n \propto g^n$. Allora
costruiamo **rapporti in cui le potenze di $g$ si elidono**:

$$ \gamma_1 = \frac{\kappa_3}{\kappa_2^{3/2}} \propto \frac{g^3}{(g^2)^{3/2}} = \frac{g^3}{g^3} = 1 \quad(\text{gain-free!}) $$

$$ \gamma_2 = \frac{\kappa_4}{\kappa_2^{2}} \propto \frac{g^4}{g^4} = 1 \quad(\text{gain-free!}) $$

$$ \frac{\text{media}^2}{\text{Var}} \propto \frac{g^2}{g^2} = 1 \quad(\text{gain-free!}) $$

## La tabella maestra

> Prima di leggerla, due sigle che compaiono qui e le incontreremo spesso:
> **Msd** = *mean square successive difference*, una misura di potenza robusta alle
> derive lente (definita per bene sotto); per ora basta sapere che scala come la
> varianza, $\propto g^2$. **CV** = *coefficient of variation* = deviazione standard /
> media (una dispersione relativa, adimensionale). $\tau_\text{eff}$ è la durata
> efficace dell'impulso, $\approx \tau$.

| statistica | teoria (Campbell) | scala col gain | misura fisicamente | gain-free? |
|---|---|---|---|---|
| media $m=\kappa_1$ | $\lambda\langle A\rangle I_1$ | $\propto g$ | corrente DC ≈ dose non-compensata | ❌ |
| Var $=\kappa_2$ | $\lambda\langle A^2\rangle I_2$ | $\propto g^2$ | potenza di fluttuazione | ❌ |
| Msd $=C(0)-C(\delta)$ | $\propto \lambda\langle A^2\rangle$ (come Var, ad alta-f) | $\propto g^2$ | potenza shot ad alta-f | ❌ |
| skewness $\gamma_1$ | $\propto \lambda^{-1/2}$ | invariante | $1/\sqrt{\text{occupancy}}$; segno = polarità | ✅ |
| excess kurtosis $\gamma_2$ | $\propto \lambda^{-1}$ | invariante | $1/\text{occupancy} \approx 1/(\lambda\tau_\text{eff})$ | ✅ |
| von Neumann $\text{Msd}/\text{Var}$ | (forma) | invariante | rise/roughness vs $\tau_\text{corr}$ | ✅ |
| CV potenza per-record | $\propto 1/\sqrt{\text{occupancy}}$ | invariante | # eventi per finestra | ✅ |
| **mean²/Var** | $\lambda\langle A\rangle^2/\langle A^2\rangle$ | invariante | **rate λ** | ✅ |
| **η = Var/Msd** | $\langle A^2\rangle/\langle A\rangle$ | invariante | **energia media** | ✅ |

Due cose da notare:

- Le statistiche **gain-dipendenti** (media, Var, Msd) sono quelle che istintivamente
  useresti per misurare "quanto segnale c'è" — e sono proprio quelle rovinate dal
  crollo del gain. Nei dati reali infatti la varianza e la Msd **anti-correlano con la
  dose** (crescono e poi *scendono*!), perché il gain cala più in fretta di quanto il
  rate salga. Ingannevoli.
- Le statistiche **gain-free** (skewness, kurtosi, mean²/Var, η) sono la cassetta degli
  attrezzi buona.

Nel dettaglio, l'**excess kurtosis** merita una riga:

$$ \gamma_2 = \frac{\kappa_4}{\kappa_2^2} = \frac{1}{\lambda}\,\frac{\langle A^4\rangle}{\langle A^2\rangle^2}\,\frac{I_4}{I_2^2} \;\propto\; \frac{1}{\lambda\tau_\text{eff}} $$

cioè è **l'inverso dell'occupancy**: grande a basso rate (spiky), → 0 in pile-up
profondo (gaussiano). Non misura l'energia: misura **quanto è affollato** il segnale.
La skewness porta la stessa informazione ($\propto 1/\sqrt{\lambda\tau}$) più il
**segno** (la polarità dell'impulso). Sono i nostri "termometri" del regime — vedi
[[Pile-up e occupancy]].

## λ — il rate. Tre strade.

**Strada A — `mean²/Var` (in continua, DC).** È la stima più bella perché il gain si
cancella *esattamente*, per *qualunque* legge $g(\lambda)$:

$$ \frac{\text{media}^2}{\text{Var}} = \frac{(g\lambda\langle A\rangle I_1)^2}{g^2\lambda\langle A^2\rangle I_2} \;\propto\; \lambda\,\frac{\langle A\rangle^2}{\langle A^2\rangle} $$

Il gain sparisce anche *dentro il collasso*. Costo: serve la **media assoluta** del
segnale, cioè lo **zero vero** (il *pedestal*). Con dati a baseline sottratta non ce
l'abbiamo → serve un **dark run** ([[Limiti]]). È il pezzo mancante più prezioso.

**Strada B — cumulanti pari $\kappa_2^2/\kappa_4$ (in alternata, AC).** Non serve la
media:

$$ \lambda \;\propto\; \frac{\kappa_2^2}{\kappa_4}\cdot(\text{fattore di forma/SER}) $$

Funziona a pile-up **moderato**, ma **muore in pile-up profondo** (là
$\kappa_4 \to 0$ e il rapporto esplode). Sui nostri dati funziona per l'anodo veloce,
fallisce per il preamp lento. Dettaglio in [[Stima del rate dai cumulanti]].

**Strada C — via la skewness (occupancy).** Poiché
$\gamma_1 \propto 1/\sqrt{\lambda\tau}$, una **calibrazione** monotòna lega la
skewness al rate. È la strada che regge su tutto il range utile e che useremo nella
pipeline ([[Stima della dose]]).

## η — l'energia media

$$ \boxed{\;\eta \;\equiv\; \frac{\text{Var}}{\text{Msd}} \;\propto\; \frac{\langle A^2\rangle}{\langle A\rangle}\;} $$

**Chi è η, a parole:** è un **proxy dell'energia media per evento**, costruito come
rapporto tra due potenze (la varianza totale e la potenza shot ad alta frequenza).
Entrambe scalano come $g^2$, quindi nel rapporto **il gain sparisce**.
Dimensionalmente è un'energia (× costanti), e nei dati Cs cresce/decresce coerente con
l'energia depositata.

Il suo limite: vale solo **nel regime giusto** (pile-up pieno con granularità pe
risolta, basso rumore); fuori regime diventa rumoroso (sui nostri dati spesso ne siamo
ai margini, quindi η dà l'ordine di grandezza, non la spettroscopia).

## Msd, e perché von Neumann

**Msd** compare al denominatore di η e va spiegato perché è un attore ricorrente: è la
**Mean Square of Successive Differences**,

$$ \text{Msd} = \tfrac12\langle (x_{i+1}-x_i)^2\rangle = C(0)-C(\delta) $$

cioè la varianza delle differenze tra campioni successivi. Il suo pregio (dovuto a
**von Neumann**) è che, usando solo *differenze*, **cancella le derive lente** (drift
termici, baseline wander, 1/f) che gonfierebbero la varianza semplice. È una misura di
potenza *robusta alle derive*. Il suo uso come stimatore sta in
[[Stima del rate dai cumulanti]].
