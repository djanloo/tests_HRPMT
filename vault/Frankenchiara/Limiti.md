---
type: nota
project: frankenchiara
updated: 2026-08-04
tags: [tipo/nota, progetto/frankenchiara]
---

# Limiti: cosa non si può misurare, e cosa servirebbe

Un buon metodo si giudica anche da cosa dichiara *impossibile* con questi dati. Questa
nota tiene insieme i muri e il prezzo per abbatterli.

## Il riinquadramento: quanto fuori specifica stiamo

Prima dei limiti di metodo, va detto il limite di **hardware**, perché li spiega quasi tutti.
Numeri del costruttore, non nostri ([[Stato dell'arte]]):

- Scionix dichiara che i 470 kΩ fra dinodi — quelli del nostro partitore — sono *"sufficient
  for count rates up to approx. 50.000 c/s"*. I nostri run stanno a **0.39–52 Mcps**, cioè
  **8× a 1040× oltre**;
- la regola di progetto vuole $I_b \ge 10\,I_a$: con $I_b = 97$ µA servirebbe
  $I_a < 9.7$ µA, e anche il run **più basso** (Am-241) sta a ~45 µA, **4.6× oltre**;
- il massimo assoluto del tubo (0.1 mA di corrente d'anodo media) è praticamente $I_b$.

> Il crollo di gain non è un effetto sottile: **stiamo lavorando 1–3 ordini di grandezza fuori
> dall'inviluppo di progetto**, e il 15× era garantito. La domanda giusta non è "perché il gain
> crolla" ma "quanto si può spingere la stima *dentro* il crollo".

## Cosa NON si può misurare

- **La forma dello spettro di ampiezza P(A) / SER non è estraibile in pile-up.**
  Servirebbe il cumulante *dispari* $\kappa_3$, che in pile-up è (a) piccolo (il segnale
  gaussianizza, $\kappa_3 \to 0$) e (b) rumorosissimo da stimare. Dimostrato: anche una
  simulazione pulita con $10^4$ record e CV nota lo recupera male. Per lo spettro P(A)
  completo servono **eventi risolti** (run a basso rate / dark). Dettagli in
  [[Spettro di ampiezza]].

- **In pile-up profondo (anodo, λτ ≈ 12–70) resta solo $\lambda\langle A^2\rangle$** (la
  varianza). Rate ed energia **non si separano** dal solo bulk del segnale: la
  granularità di singolo evento è persa. Per romperla serve la **media sopra il
  pedestal** o un **run a basso rate**. Vedi [[Pile-up e occupancy]].

- **L'energia assoluta (keV) richiede la calibrazione di gain.** Le nostre stime di
  energia sono **relative**; η dà l'ordine di grandezza, non la spettroscopia.

- **Il rate assoluto porta un sistematico ~×6 dovuto alla larghezza della SER** (il
  momento $\langle A^2\rangle/\langle A\rangle^2$, l'*excess noise factor* di
  Personick). Si stringe con un prior fisico sulla SER, o si azzera con un run a basso
  rate che la misuri.

- **I parametri del partitore ($N, \kappa, R$) separatamente**: tutti i run sono oltre il
  ginocchio, dove $g \propto 1/\lambda$ universalmente. Vedi [[Gain ladder]].

## Cosa manca per chiudere davvero il conto

La pipeline gain-free ([[Stima della dose]]) funziona senza dati aggiuntivi. Ma per
**chiudere il conto in assoluto** e coprire l'estremo alto-rate, in ordine di efficacia:

1. **Un'acquisizione con il baseline restorer DISABILITATO** (una volta sola). Sbloccherebbe
   la media, quindi `mean²/Var` = rate assoluto gain-free che **non satura** in pile-up
   profondo (dove la skewness invece si appiattisce). È il punto peggiore della pipeline, e
   resta il singolo dato mancante più prezioso.

   ⚠️ **Non basta un dark run**, come questa nota diceva fino al 2026-08-04. La media misurata
   è **195.0 ± 0.3 ADC su 300× di dose**: la componente continua **non è già più nel dato**, e
   la toglie quasi certamente un baseline restorer in firmware ([[Baseline]]). Un dark run
   darebbe lo zero *del restorer*, non lo zero vero. È un cambio di configurazione, non un run
   in più. In alternativa: misurare la corrente media d'anodo con uno strumento esterno al
   digitizer, che darebbe anche la costante ADC↔µA.

2. **Uno scan a HV fissa variando solo il rate**, e/o run a rate ≲ 180 kcps: dà la parte
   *pre-crash* della curva di gain → discrimina i parametri del ladder ($N,\kappa,R$)
   oltre alla sola scala di carico.

3. **Un run a basso rate in modo-conteggio**: impulsi isolati → misura diretta di $h(t)$,
   del gain di singolo evento e dello **spettro SER** — che azzera il sistematico ×6
   dominante sul rate.

Con (1) e (3), la fluttuazione di potenza diventa una misura assoluta di λ anche ad alto
rate, e la MSSD dà la dose disaccoppiata come nel metodo classico
([[Stima del rate dai cumulanti]]).

## Il muro hardware

Da notare un limite invalicabile via software: dentro il gain-crash, gli stadi di
moltiplicazione "saltano" (excess noise), quindi **energia e dose assoluta degradano**.
`mean²/Var` recupera il **rate** attraverso il crash, ma la parte alta della dinamica si
salva solo con l'hardware (partitore attivo/booster, o il controllo HV attivo del
[[Metodo Target]]).

> **Il software estende il range *prima* del crollo, non ti salva *dentro*.**

## Sulla letteratura

Sulla letteratura esplorata (Roessl–Fourier/level-crossing, Personick, Rice,
Lowen–Teich): la direzione è giusta e già implementata — trattare il segnale come
Poisson filtrato / Campbell. Il **level-crossing di Rice/Roessl** è stato testato come
stima alternativa di λ: funziona a basso rate ($N(u) \approx \lambda$) ma **satura in
pile-up** alla frequenza RMS della forma d'impulso — stesso muro dei cumulanti. Resta
utile come *misura di forma* indipendente, non come proiettile d'argento per il rate.
Dettagli in [[Level crossing]] e [[Letteratura]].
