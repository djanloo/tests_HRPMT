---
type: nota
project: frankenchiara
updated: 2026-07-23
tags: [tipo/nota, progetto/frankenchiara]
---

# La pipeline di dose

**Il risultato principale.** Lo stimatore di dose finale — deployabile, che usa **solo
statistiche gain-free** e **nessun pedestal / dark run / correzione di gain**.

Codice: `dose_estimation/dose_pipeline.py`, calibrazione in `calibration.json`.

## L'idea

$\dot H = k\,\lambda\,\langle E\rangle$. Il rate λ dalla **skewness** $\gamma_1$
(proxy di occupancy, gain-free); l'energia $\langle E\rangle$ da **η** (gain-free).
Niente statistiche gain-dipendenti a runtime. Vedi [[Statistiche gain-free]] per
perché queste e non altre, e [[Metodo Target]] per cosa è stato corretto.

## La pipeline

1. Dal blocco di forme d'onda calcola le feature gain-free: $\gamma_1$ (skew),
   $\eta = \text{Var}/\text{Msd}$, $\gamma_2$ (kurt).
2. **Auto-diagnosi del regime** dalla kurtosi + stabilità di $\gamma_1$: se $\gamma_1$
   è instabile / $\gamma_2 \gg 1$ → *bassissimo rate, impulsi risolti* → la pipeline
   dice "**conta gli impulsi**" (fuori dal metodo statistico; è il caso Am-241).
   Altrimenti procede.
3. **Rate** da $\gamma_1$ via calibrazione; **energia** da η; **dose** da
   $\ln\dot H = a + b\,\text{asinh}(\gamma_1)$.

Calibrazione su questi dati (Cs-137):

$$ \ln(\dot H\,[\mu\text{Sv/h}]) = 9.685 - 2.158\,\text{asinh}(\gamma_1) $$
$$ \ln(\langle E\rangle\,[\text{keV}]) = 1.38 + 1.17\,\ln(\eta) $$

L'$\text{asinh}$ — seno iperbolico inverso — è usato al posto del logaritmo perché è
quasi lineare vicino a zero e logaritmico per $|\gamma_1|$ grande, e soprattutto
**accetta anche skewness negative**: nel pile-up profondo $\gamma_1$ può diventare
leggermente $<0$, dove un $\ln$ esploderebbe.

## Rate ed energia estratti

| nuclide | dose | $\gamma_1$ | $\eta$ | rate stimato | energia stimata (vera) |
|---|---|---|---|---|---|
| Am-241 | 94 | +14.4* | 13.2 | *conta impulsi* | 81 keV (59.5) |
| Cs-137 | 616 | +2.17 | 65.8 | 1.1 Mcps | 531 keV (662) |
| Cs-137 | 889 | +1.83 | 96.1 | 1.6 Mcps | 826 keV (662) |
| Cs-137 | 7900 | +0.10 | 110 | 24 Mcps | 967 keV (662) |
| Cs-137 | 17990 | +0.02 | 76 | 29 Mcps | 629 keV (662) |
| Cs-137 | 28100 | −0.13 | 46 | 39 Mcps | 350 keV (662) |

\*$\gamma_1$ di Am-241 instabile (h1 +1.6 vs h2 +24.8) → regime a impulsi risolti. Rate
assoluto da calibrazione Target (1 Mcps ↔ 540 µSv/h, Cs-137 2×2″ NaI).

## Il risultato

Dalla sola forma statistica del segnale si stima la dose entro un **fattore ×1.24
mediano (×1.98 massimo) su 2.5 decadi**, in **leave-one-out**:

![[dose_result.png]]
*Dose stimata vs vera (solo skewness gain-free), Cs-137. A destra i tre proxy gain-free
vs dose.*

| dose vera [µSv/h] | dose stimata (LOO) | fattore d'errore |
|---|---|---|
| 616 | 602 | ×1.02 |
| 889 | 812 | ×1.09 |
| 7900 | 15680 | ×1.98 |
| 17990 | 14490 | ×1.24 |
| 28100 | 17650 | ×1.59 |

## Cos'è il leave-one-out, e perché il numero è onesto

La calibrazione ha 2 parametri ($a,b$) e i punti Cs sono solo 5. Se fittassi su tutti e
5 e misurassi l'errore *sugli stessi 5*, starei barando: misurerei quanto bene una
retta ci passa in mezzo, non quanto predice una misura *nuova*.

Il LOO evita questo. Per ogni run $i$:

1. **butto via** il run $i$;
2. **ri-fitto** la calibrazione sui **4 run rimasti**;
3. **predìco** la dose del run $i$ con quella calibrazione — che **non l'ha mai visto**;
4. confronto stima vs dose vera → fattore d'errore.

Ripetuto per tutti e 5 (5 ri-fit indipendenti), dà un errore **fuori-campione** — la
stima onesta di quanto sbaglierei su una misura mai usata per tarare. È il numero che
conta per l'uso reale, ed è per questo che sta come risultato principale invece
dell'errore di fit in-sample (più basso ma bugiardo).

Note: (i) solo la calibrazione del **rate** è in LOO (Cs-137, energia fissa, 5 punti su
2.5 decadi); l'Am-241 sta fuori (regime a impulsi risolti). (ii) 5 punti sono pochi:
l'LOO su così pochi dati è la cosa più onesta possibile *con questi dati*, ma resta un
campione piccolo — per questo è affiancato alla validazione sintetica a verità nota
([[Validazione a verità nota]]), dove i punti sono tanti e la dose vera è imposta.

## Perché è robusto (e "commercializzabile")

- **Gain-free by design**: skewness ed η sono rapporti di cumulanti → il gain (che
  deriva/collassa) **si cancella**. Funziona anche sul run 616 a **HV diversa**.
- **Niente dark run / pedestal / correzione di gain**: una sola statistica per la dose.
- **Stabile** nel regime continuo (Cs: $\gamma_1, \eta$ coincidono tra metà dei record).
- **Autodiagnosi del regime**: la stessa pipeline sa quando è a bassissimo rate
  ($\gamma_1$ instabile) e dice "conta gli impulsi".

## Limiti onesti

L'energia è rozza (~×1.5, buona per il fattore di conversione, non per spettroscopia);
ad alto rate $\gamma_1 \to 0$ (pile-up profondo) e la sensibilità cala (il punto
peggiore, 7900, è proprio alla transizione); la calibrazione $a,b$ va ri-tarata per un
altro tubo/HV, ma la *struttura* gain-free è trasferibile.

Il quadro completo di cosa resta fuori portata è in [[Limiti]], e in [[Stato dell'arte]] c'è
il confronto con ciò che il costruttore e la letteratura dicono ottenibile.
