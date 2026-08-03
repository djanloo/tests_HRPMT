---
type: hub
manages: [Frankenchiara]
repo_root: []
checkout_roots: [C:/Users/gbecuzzi/Desktop/progetti_criminali]
tag_mirror: false
types:
  progetto: {archetype: entry}
  architettura: {archetype: static}
  decisioni: {archetype: log}
  bug: {archetype: tracked, statuses: [aperto, in-corso, risolto, chiuso], open: [aperto, in-corso]}
  approfondimento: {archetype: tracked, statuses: [aperto, in-corso, chiuso], open: [aperto, in-corso], ceiling: 500}
  manuale: {archetype: static}
  nota: {archetype: static}
  utente: {archetype: static}
  riferimento: {archetype: static}
updated: 2026-08-03
tags: [tipo/hub]
---

# Progetti

Hub del vault. Il nome del file resta `Projects.md` perché `vault.py` lo cerca con quel nome, e
`type: hub` perché è così che riconosce la nota che dichiara `manages:`.

`manages: [Frankenchiara]` è l'elenco **completo** delle cartelle a cui queste convenzioni si
applicano. Tutto ciò che sta fuori è invisibile: non letto, non modificato, non contato.
Aggiungere una cartella richiede una conferma esplicita.

## Indice

Una riga per progetto: risolve "lavoriamo su tests_HRPMT" in una cartella senza scandire il vault.

| Progetto | `repo` | `group` | Alias |
|---|---|---|---|
| [[Frankenchiara/Frankenchiara\|Frankenchiara]] | `djanloo/tests_HRPMT` | — | Frankenchiara, tests_HRPMT |

Query pronte in `Bases/`: `Progetti`, `Bug aperti`, `Note obsolete`.

## Schema delle note

I **nomi dei campi** frontmatter sono in inglese perché li legge `vault.py`; i **valori** e le
radici dei tag sono in italiano.

| campo | valori | su quali note |
|---|---|---|
| `type` | `hub`, `progetto`, `architettura`, `decisioni`, `backlog`, `bug`, `approfondimento`, `manuale`, `nota`, `utente`, `feedback`, `riferimento`, `toolbox` | tutte |
| `project` | slug, qui `frankenchiara` | tutte le note del progetto; omesso sull'hub |
| `status` | `aperto`, `in-corso`, `risolto`, `chiuso` | solo `bug` e `approfondimento` |
| `updated` | `YYYY-MM-DD` | tutte |
| `tags` | `tipo/<type>`, `progetto/<project>` | tutte |
| `repo` | percorso del repository, qui `djanloo/tests_HRPMT` | solo `progetto` |
| `local` | percorso assoluto del clone su questa macchina, slash in avanti | solo `progetto`, opzionale |
| `aliases` | ogni altro nome del progetto | solo `progetto` |

`local` è una cache, non la verità: vale su una macchina sola, va verificato prima di usarlo e
ri-derivato con `vault.py derive` quando non esiste più.

`group` è omesso e `repo_root` è vuoto: su GitHub i percorsi sono `owner/repo` e non c'è nessun
gruppo da derivare.

`tag_mirror: false` perché il controllo automatico "il tag rispecchia il `type`" di `vault.py`
cerca le radici inglesi `type/`/`project/`, che qui non esistono. Tutti gli altri controlli di
`vault.py doctor` restano attivi.

Nessuna nota oltre le ~400 righe: oltre quella soglia non si carica più in contesto senza
inquinarlo. Spezzala in un `Bug/` o in un approfondimento.

`approfondimento` ha `ceiling: 500` perché un'indagine con tabelle e risultati arriva
legittimamente più in là di una nota di memoria — serve a `REPORT.md`, 426 righe.

Nuove note partono dal template corrispondente in `Templates/`.
