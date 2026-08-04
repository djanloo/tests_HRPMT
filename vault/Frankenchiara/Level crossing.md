---
type: nota
project: frankenchiara
updated: 2026-07-21
tags: [tipo/nota, progetto/frankenchiara]
---

# Level crossing (Rice / Roessl)

L'idea più promettente della revisione di letteratura, testata e ridimensionata. Non è
un proiettile d'argento per il rate, ma resta utile come misura di forma.

Riferimenti in [[Letteratura]]: Rice 1944 (la teoria), Roessl & Daerr 2016 (il
forward-model per rivelatori a soglia).

## L'idea

Invece di identificare gli impulsi, si conta quante volte il segnale **attraversa una
soglia** $u$ verso l'alto. Per un processo gaussiano stazionario, Rice dà

$$ N(u) = \frac{1}{2\pi}\sqrt{\frac{\lambda_2}{\lambda_0}}\,\exp\!\left(-\frac{u^2}{2\lambda_0}\right) $$

con $\lambda_0 = \text{Var}$ e $\lambda_2 = \text{Var}$(derivata). A basso rate ogni
impulso attraversa la soglia una volta, quindi $N(u) \approx \lambda$: si contano gli
eventi senza cercarli.

## Il test

Rate di attraversamenti verso l'alto della soglia $u=0$, su dati simulati (forma
preamp), vs λ vero:

| λ vero | N(0)/λ | N(0) [Hz] |
|---|---|---|
| 5×10⁴ | 54 | 2.7×10⁶ |
| 2×10⁵ | 5.4 | 1.1×10⁶ |
| 1×10⁶ | 0.22 | 2.2×10⁵ |
| 5×10⁶ | 0.05 | 2.4×10⁵ |
| 2×10⁷ | 0.01 | 2.2×10⁵ |

**Risultato:** a **basso** rate $N(u)\approx\lambda$. In **pileup** il mean-crossing rate
**satura** a ~2.2×10⁵ Hz *indipendente da λ*: è la **frequenza RMS della forma**
$(1/2\pi)\sqrt{\lambda_2/\lambda_0}$, cioè misura la *forma d'impulso*, non il rate.

Stesso muro del pileup dei cumulanti — vedi la tabella in [[Pile-up e occupancy]].

## Conclusione onesta

Il level-crossing **non è un proiettile d'argento** per il nostro regime (anode pileup
profondo). MA:

- è una **misura di forma indipendente e robusta** (la freq RMS ≈ 220 kHz per il CSP
  cross-controlla il rise+fall fittati in [[Fit dei parametri]]) — cheap e vale la pena
  aggiungerla;
- in pileup *moderato* (il CSP) lo **spettro dei crossing** (rate vs soglia) contiene
  informazione di λ oltre alla varianza — è la parte del forward-model di Roessl che
  potrebbe battere i cumulanti ($\kappa_3$ rumoroso). Vale un test dedicato se serve
  spingere il CSP. Vedi [[Backlog]].
