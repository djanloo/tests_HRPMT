---
type: nota
project: frankenchiara
updated: 2026-08-03
tags: [tipo/nota, progetto/frankenchiara]
---

# Circuito equivalente del PMT a polarità negativa

Il modello circuitale di prim'ordine da cui parte [[Gain ladder]]: come si rappresenta il
tubo come rete elettrica, e perché il verso delle correnti è la cosa da non sbagliare.

*Testo di Gianluca, conservato in inglese come scritto — la riconciliazione col codice e coi
numeri è nella sezione italiana in fondo.*

---

## Equivalent Circuit Model of a Negative Polarity PMT

When modeling the gain degradation of a photomultiplier tube (PMT) with a **passive voltage
divider**, it is important to distinguish between:

1. **Electron flow inside the PMT vacuum**
2. **Conventional current in the electrical circuit**

These two have opposite directions.

### Electron Flow

In a **negative polarity PMT**:

- Photocathode: **-HV** (e.g. -1000 V)
- Anode: **0 V**
- Dynodes are biased at progressively less negative potentials.

Electrons are emitted by the photocathode and accelerated toward the anode through the dynode
chain:

```text
Photocathode (-HV)
        │
        ▼
       D1
        ▼
       D2
        ▼
      ...
        ▼
     Anode (0 V)
```

### Conventional Current in the Voltage Divider

The passive divider continuously draws a bias current from the power supply.

The conventional current flows from the highest potential to the lowest:

```text
 GND (0 V)
    │
    R
    │
   Dn
    │
    R
    │
  ...
    │
    R
    │
 Photocathode (-HV)
```

Therefore,

$$ I_{\mathrm{divider}} : 0\;\mathrm{V} \rightarrow -HV $$

### Modeling the Dynodes

When electrons strike a dynode they are absorbed by the metal surface.

To keep the dynode at the correct bias voltage, the voltage divider must replenish the lost
charge. Consequently, each dynode behaves as a **current sink** connected to the corresponding
divider node.

An equivalent representation is

```text
          R
----------o---------
          │
        Dynode
          │
          ↓ Ii
         GND
```

where:

- $I_i$ is the average current drawn by the $i$-th dynode.
- Increasing photon rate increases $I_i$.

### Physical Interpretation

As the count rate increases:

1. More electrons are multiplied.
2. Larger average dynode currents are drawn.
3. The current through the passive divider changes.
4. Voltage drops across the divider resistors increase.
5. Inter-dynode voltages are redistributed.
6. The secondary emission ratio of each dynode changes.
7. The overall PMT gain decreases.

This mechanism explains the gain degradation observed in passive-divider PMTs operating at
high count rates.

### Notes

For a first-order equivalent circuit:

- The resistor ladder models the voltage divider.
- Each dynode is represented as a current sink.
- The anode is represented by the largest current sink, corresponding to the average anode
  current.

This model captures the essential feedback mechanism responsible for gain compression while
remaining simple enough for circuit analysis or SPICE simulations.

---

## Come si aggancia al codice e ai numeri

### Conferma il segno del termine di carico

Il **current sink** tira corrente **fuori** dal nodo del partitore. È esattamente il $+t_i$
che `gain_ladder.py` mette a destra della KCL, e che era stato verificato numericamente
([[Gain ladder]]): la conservazione globale dà $\sum_i t_i = I_a - I_0$ esatto, e
$I_{k+1}-I_k = t_k$ a $8\cdot10^{-11}$.

I due quadri coincidono anche sul verso lungo la catena. Questa nota dice che la corrente di
bias scorre **GND → … → fotocatodo**, cioè dall'anodo verso il catodo, e che a ogni dinodo
una parte viene deviata nel sink. Quindi la corrente nei resistori **decresce** andando verso
il catodo — ed è quello che si misura sulla soluzione:

| resistore | R11 (lato anodo) | R10 | R9 | … | R1 (lato catodo) |
|---|---|---|---|---|---|
| corrente [µA] | **211.1** | 113.6 | 92.6 | … | 84.97 |

### Il sink verso GND: quando è lecito e quando no

C'è un punto in cui questa rappresentazione e il quadro fisico sembrano contraddirsi, e vale
chiarirlo perché altrove nel vault è scritto "non far tornare i $t_i$ a massa".

- **Fisicamente** gli elettroni che un dinodo perde arrivano dal partitore e finiscono
  **all'anodo attraverso il vuoto**, non a massa. Il percorso di ritorno è il tubo.
- **Come circuito equivalente** il sink verso GND è però corretto, e per una ragione precisa:
  in questo rivelatore l'anodo *è* a potenziale di massa, e la corrente d'anodo torna
  effettivamente al nodo di massa attraverso il carico $R_L$ ([[Catena di lettura]]). Quindi le
  **correnti nei rami del partitore sono identiche** nei due modelli; cambia solo per quale
  strada la carica ci arriva.

Morale operativa: per una simulazione SPICE o per il conto delle tensioni, sink verso GND —
è più semplice e dà gli stessi numeri. Per disegnare uno schema che spieghi *il meccanismo*,
il ritorno va per il tubo, altrimenti sembra che il partitore alimenti massa invece del
fascio.

### Cosa il modello di prim'ordine non contiene

Dai datasheet del rivelatore vero ([[Hardware]]) mancano tre cose, in ordine di importanza:

1. **I resistori non sono uguali.** Il partitore Scionix è tarato: 180K, 850K, 1M, 1M, poi
   470K×6. I primi stadi hanno resistori più grandi — cioè il "primo stadio protetto" che
   rompe la premessa del teorema AM-GM su cui poggia la monotonia del gain. Nel modello a
   ladder $R$ è ancora uno scalare. Vedi [[Backlog]].
2. **I condensatori di disaccoppiamento** sugli ultimi stadi (C1 = 1000 pF/2 kV,
   C2 = 10 nF/1 kV): forniscono la corrente d'impulso che i resistori non riescono a seguire.
   Il modello è **stazionario** e li ignora — va bene per la curva gain-vs-rate, non per i
   transitori. Sono anche l'ingrediente da aggiungere per la versione dinamica
   ($C_i\,dV_i/dt$) abbozzata in `target_test/gain_model_proposal.md`.
3. **$I_i$ è una corrente media.** Il modello risolve il regime stazionario; le fluttuazioni
   di Poisson del rate rendono $I_i$ un processo stocastico, ed è lì che questo modello
   incontrerebbe [[Shot noise]].

