---
type: nota
project: frankenchiara
updated: 2026-07-23
tags: [tipo/nota, progetto/frankenchiara]
---

# Pile-up e occupancy

Quanto è "affollato" il segnale, e quanta informazione sopravvive all'affollamento.
È il numero che decide quale metodo di stima è applicabile.

## L'occupancy λτ

Il numero adimensionale che conta è l'**occupancy**:

$$ \text{occupancy} = \lambda\,\tau = \text{numero medio di impulsi che si sovrappongono in un tempo } \tau $$

dove τ è la durata di un impulso. Tre regimi, e tre comportamenti diversi:

1. **λτ ≪ 1 — impulsi risolti.** Gli impulsi sono isolati, ben separati. Il segnale è
   "spiky": tante zone di baseline e picchi occasionali → distribuzione fortemente
   **asimmetrica e a coda lunga** → $\kappa_3, \kappa_4$ **grandi**.
   (Caso Am-241, λτ = 0.04.) È il solo regime in cui il PHA classico è lecito, ed è quello
   che sfrutta [[Misure a basso rate]].

2. **λτ ~ 1 — pile-up moderato.** Gli impulsi cominciano a sovrapporsi ma la
   granularità si intravede ancora.

3. **λτ ≫ 1 — pile-up profondo.** Migliaia di impulsi si sommano ad ogni istante. Qui
   entra in gioco il **teorema del limite centrale**: la somma di tantissimi contributi
   indipendenti tende a una **gaussiana**. E per una gaussiana
   ([[Cumulanti e Campbell]]) **$\kappa_3, \kappa_4 \to 0$**. Il segnale diventa un
   fuzz gaussiano liscio, che ha perso ogni memoria del "quanti erano" e "quanto
   grandi". (Caso Cs-137 28100, λτ = 12.)

## La tensione centrale del progetto

> Più il rate è alto (regime che ci interessa!), più il segnale **gaussianizza**, più
> le informazioni di conteggio e di energia **evaporano** dai cumulanti alti. È un
> muro fisico, non un difetto di metodo.

Lo vediamo direttamente nei dati: l'excess kurtosis passa da **+6.9** (Am-241,
risolto) a **−0.08** (Cs 28100, gaussiano) monotonamente con l'occupancy prevista. Il
regime di pile-up predetto dalla dose è quindi **confermato dal segnale**, e in modo
*gain-free* (kurtosi e skewness non dipendono da $g$, [[Statistiche gain-free]]) — un
cross-check pulito.

## I due canali di caratterizzazione

- **`FAST` — pileup profondo.** Skew −0.12, eccesso di kurtosi ≈ 0 (gaussiano);
  la CV della potenza per record è al floor. La granularità di singolo evento è persa:
  la varianza dà $\lambda\langle A^2\rangle$ ma **λ e ⟨A⟩ non si separano** da questi
  dati. Per romperla serve la **media sopra pedestal** (corrente) oppure un **run a
  basso rate / dark** (SER e guadagno assoluto).

- **`CSP` — pileup moderato.** Kurtosi *pooled* +0.5 (dovuta alla dispersione
  della varianza tra record → statistica di conteggio), mentre intra-record è
  sub-gaussiana (il lento vagare integrato entro finestra è limitato). La varianza per
  record fluttua del ±60 %: pochi eventi per finestra.

Vedi [[Rivelatore e dati]] per il quadro completo dei due canali, e [[Limiti]] per
cosa questo rende definitivamente non misurabile.

## Conseguenza per i metodi

Ogni metodo di stima del rate sbatte contro lo stesso muro, ognuno a modo suo:

| metodo | dove muore |
|---|---|
| cumulanti pari $\kappa_2^2/\kappa_4$ | $\kappa_4 \to 0$ in pileup profondo → il rapporto esplode → solo limite inferiore |
| fluttuazione di potenza per record | la CV satura al floor gaussiano $\sqrt{2/N_\text{eff}}$ |
| level crossing (Rice/Roessl) | il crossing rate satura alla frequenza RMS della forma |
| skewness $\gamma_1$ | $\gamma_1 \to 0$, la sensibilità cala ma non si annulla — è la più resistente |

È per questo che la pipeline finale ([[Stima della dose]]) è costruita sulla
skewness e non sui cumulanti quarti.
