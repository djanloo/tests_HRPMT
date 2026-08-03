---
type: progetto
project: frankenchiara
repo: djanloo/tests_HRPMT
local: C:/Users/gbecuzzi/Desktop/progetti_criminali/frankenchiara
aliases: [Frankenchiara, tests_HRPMT]
updated: 2026-08-03
tags: [tipo/progetto, progetto/frankenchiara]
---

# Frankenchiara

Caratterizzazione del segnale di un PMT ad alto rate e stima della dose a partire da quel
segnale. Da riempire: cosa fa il progetto in una o due frasi, non un elenco di funzionalità.

- Repository: `djanloo/tests_HRPMT` (GitHub, nessun `group`)
- Linguaggio / build: Python
- Dove gira: locale

## Note

- [[Architettura]] — com'è messo insieme
- [[Decisioni]] — perché è messo insieme così
- [[Backlog]] — cosa resta aperto
- `Bug/` — una nota per indagine

Queste tre sono ancora scheletri dal template. Schema delle note e configurazione del vault in
[[Projects]].

## Il lavoro fatto

- [[RELAZIONE]] — la relazione completa, indice delle quattro parti del ragionamento
- [[REPORT]] — caratterizzazione del rumore PMT come processo stocastico (`in-corso`)
- [[findings_approaches]] — cosa hanno dato davvero i riferimenti, e il test del level-crossing
  di Rice/Roessl (`in-corso`)
- [[possible_approaches]] — revisione della letteratura e approcci candidati al pile-up
- [[references]] — reading list su decompounding e shot noise

Le 12 figure stanno in `img/`, copiate dalla root del repo perché Obsidian non renderizza
immagini fuori dal vault. **Sono copie, non si aggiornano da sole**: dopo aver rigenerato i
grafici con gli script, ricopiale con

```sh
cp signals.png independence_test.png model_validation.png fit_validation.png \
   dose_estimation/*.png target_test/*.png vault/Frankenchiara/img/
```

## Progetti collegati

Nessuno per ora.
