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

Stima della dose da un PMT che lavora in pile-up estremo, trattando il segnale come un
processo stocastico continuo invece di cercare i singoli impulsi.

- Repository: `djanloo/tests_HRPMT` (GitHub, nessun `group`)
- Linguaggio: Python — mappa dei file in [[Codice]]
- Dove gira: locale

**In una riga:**

> Il segnale è shot noise; il gain è un traditore che collassa col rate; la salvezza sono
> i **rapporti gain-free** dei cumulanti (skewness → rate, η → energia), con cui si stima
> la **dose entro ×1.24 su 2.5 decadi** senza toccare l'hardware — e il modello *ladder*
> spiega perché il gain crolla come 1/λ.

## Il ragionamento, in ordine

Per chi legge da zero. Ogni nota è un soggetto, non un capitolo: si può anche entrare
dal mezzo.

1. [[Rivelatore e dati]] — il problema, il PMT, cosa c'è nei file
   ([[Hardware]] per il rivelatore, [[Catena di lettura]] per cosa leggiamo)
2. [[Shot noise]] — il modello di tutto
3. [[Cumulanti e Campbell]] — lo strumento matematico
4. [[Pile-up e occupancy]] — il muro fisico che decide cosa è misurabile
5. [[Statistiche gain-free]] — l'idea centrale, e la tabella maestra
6. [[Metodo Target]] — la prior art, e l'errore di segno che porta
7. [[Stima della dose]] — **il risultato principale**
8. [[Gain ladder]] — perché il gain crolla come 1/λ
   ([[Circuito equivalente del PMT]] per il modello circuitale sotto)
9. [[Limiti]] — cosa non si può misurare, e cosa servirebbe
10. [[Stato dell'arte]] — quanto fuori specifica stiamo, e chi ha fatto cosa

## Metodi, uno per uno

- [[Stima del rate dai cumulanti]] — MSSD di von Neumann, cumulanti pari, fluttuazione di
  potenza: il verdetto è diverso per i due canali
- [[Level crossing]] — Rice/Roessl, testato e ridimensionato
- [[Spettro di ampiezza]] — il sistematico dominante, e l'unica cosa non misurabile
- [[Misure a basso rate]] — PHA offline sull'Am-241: l'eccezione, dove P(A) si misura

## Simulazione e verifica

- [[Simulazione SDE]] — il simulatore: SDE a due poli, `expm`, e lo spettro di ampiezza
  empirico che ha sostituito la Gamma
- [[Fit dei parametri]] — il fit Optuna, e le due lezioni pagate (rumore, rise-time)
- [[Validazione a verità nota]] — i quattro livelli di verifica
- [[Indipendenza dei due file]] — un risultato negativo verificato

## Memoria di progetto

- [[Frankenchiara/Decisioni|Decisioni]] — perché è messo insieme così (registro in sola aggiunta)
- [[Frankenchiara/Backlog|Backlog]] — cosa resta aperto
- [[Letteratura]] — giudizio sui riferimenti chiave + reading list
- [[Punto di partenza]] — il brief originale, superato, conservato per il registro

Schema delle note e configurazione del vault in [[Projects]].

## Progetti collegati

Nessuno per ora.
