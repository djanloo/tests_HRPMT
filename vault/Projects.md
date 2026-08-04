---
type: hub
manages: [Frankenchiara]
repo_root: []
checkout_roots: [C:/Users/gbecuzzi/Desktop/progetti_criminali]
tag_mirror: false
types:
  progetto: {archetype: entry}
  decisioni: {archetype: log}
  backlog: {archetype: static}
  approfondimento: {archetype: tracked, statuses: [aperto, in-corso, chiuso], open: [aperto, in-corso]}
  nota: {archetype: static}
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

Query pronte in `Bases/`: `Note obsolete` (cosa riverificare contro il codice, più vecchie in
cima).

## Una nota per soggetto

Le note sono **soggetti**, non capitoli: si chiamano col nome della cosa di cui parlano
(`Shot noise`, `Gain ladder`, `Spettro di ampiezza`) e si linkano fra loro. Niente prefissi
di serie e niente numerazione — l'ordine di lettura sta nell'entry point del progetto, dove
può cambiare senza rinominare nulla.

Il corollario è che una nota va spezzata quando parla di due cose, non quando è lunga.

**Niente sezioni "Collegamenti".** I link vivono **nel discorso**, dove una frase dice perché
l'altra nota serve lì. Un elenco di rimandi in fondo produce un grafo quasi completamente
connesso — in cui tutto è collegato a tutto e quindi nessun collegamento porta informazione —
e duplica link che il corpo ha già. Se un rimando non si riesce a giustificare in mezza frase
dentro il testo, non serve: Obsidian mostra già i backlink, e una nota a un hop di distanza è
raggiungibile senza scriverlo.

## Schema delle note

I **nomi dei campi** frontmatter sono in inglese perché li legge `vault.py`; i **valori** e le
radici dei tag sono in italiano.

| campo | valori | su quali note |
|---|---|---|
| `type` | `hub`, `progetto`, `decisioni`, `backlog`, `approfondimento`, `nota`, `riferimento` | tutte |
| `project` | slug, qui `frankenchiara` | tutte le note del progetto; omesso sull'hub |
| `status` | `aperto`, `in-corso`, `chiuso` | solo `approfondimento` |
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
inquinarlo. Se una nota ci arriva, quasi sempre parla di due soggetti — spezzala in due.

`approfondimento` è il solo tipo tracciato: serve a un'indagine ancora aperta, quella che in
un vault di software sarebbe un bug. Al momento non ce ne sono: il lavoro chiuso è diventato
note di soggetto, e ciò che resta aperto sta in `Backlog.md`.

Niente `Templates/`: i template servivano una volta per progetto ed erano già istanziati.
`/obsidian:project` li rigenera se un giorno il vault ospita un secondo progetto.

**Cancellati il 2026-08-03**: il tipo `bug` con la sua cartella, il suo template e la sua Base
(mai usati, e in un vault sperimentale-teorico non hanno senso); i tipi `architettura`,
`manuale`, `utente`, `feedback`, `toolbox` (nessuna istanza). La nota *Architettura* è stata
sostituita da `Codice.md`, che per un repo di script di analisi dice qualcosa di vero.
