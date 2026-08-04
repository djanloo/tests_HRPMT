---
type: nota
project: frankenchiara
updated: 2026-07-23
tags: [tipo/nota, progetto/frankenchiara]
---

# Il metodo Target, e perché va corretto

Prior art: esiste un metodo brevettato che fa esattamente dosimetria da PMT in
pile-up. Lo abbiamo applicato ai nostri run e trovato un errore di segno che vale la
pena raccontare, perché è istruttivo.

Brevetto **US2021/0055429 A1** (Stein), PDF nella root del repo. Codice:
`target_test/target_method.py`.

## Le equazioni operative

$$ \text{Msd} = \lambda\,\eta \;(\text{Eq.2}),\qquad \eta = \frac{\text{Var}}{\text{Msd}}\;(\text{Eq.3}),\qquad \dot H = Z(\eta)\cdot\text{Msd}\;(\text{Eq.4}) $$

cioè: dalla Msd e dalla Var ricava un rate $\hat\lambda = \text{Msd}^2/\text{Var}$ e
un'energia $\eta$, e compone la dose.

## Il test, e l'errore di segno

Applicato ai 6 run reali e — punto delicato — **validato con un simulatore a verità
nota** ([[Validazione a verità nota]]).

![[target_test.png]]
*Il metodo Target sui dati reali: le statistiche vs dose. Msd e λ̂ anti-correlano con
la dose (crollo del gain); la kurtosi decresce monotona con l'occupancy.*

- **$\eta = \text{Var}/\text{Msd}$ è gain-free** (∝ energia). Verificato: in una
  scansione di gain ×0.5–4 a rate ed energia fissi, η resta **costante a 18.0**.

- **$\hat\lambda = \text{Msd}^2/\text{Var} \propto g^2$** — cioè **NON** è gain-free!
  Nella stessa scansione scala come $g^2$ (10→41→164→656). Quindi quando il gain
  collassa, $\hat\lambda$ collassa con lui e **anti-correla con la dose**. È esattamente
  ciò che si vede nei dati reali (Msd e λ̂ scendono mentre la dose sale).

## La lezione

Il rate **non** va preso da $\text{Msd}^2/\text{Var}$ (porta il gain²), ma da
**`mean²/Var`** (gain-free, [[Statistiche gain-free]]) — che nella validazione
**sopravvive al crollo del gain** — o in alternativa dalla skewness.

Target è un ottimo punto di partenza, ma la sua stima di rate va sostituita con una
gain-free: è quella correzione che rende il metodo robusto al nostro hardware, dove il gain
crolla come $1/\lambda$ ([[Gain ladder]]).

Il suo **controllo HV attivo** resta però una delle poche strade *hardware* per spostare il
limite invece di aggirarlo ([[Stato dell'arte]]).

Il risultato di quella correzione è la pipeline in [[Stima della dose]].
