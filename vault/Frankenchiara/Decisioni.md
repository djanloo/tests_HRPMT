---
type: decisioni
project: frankenchiara
updated: 2026-08-03
tags: [tipo/decisioni, progetto/frankenchiara]
---

# Decisioni

Registro in sola aggiunta. Una voce per decisione importante — cambi di architettura, scelta di
librerie, cambi di API pubblica, compromessi deliberati. Non i dettagli di implementazione di
routine.

Mai modificare o cancellare una voce passata. Una decisione che non vale più riceve una **nuova**
voce che dice cosa l'ha sostituita e perché; la vecchia resta, perché il senso del registro è
mostrare cosa si credeva all'epoca.

Forma della voce — data, cosa è stato deciso, perché, cosa è stato scartato:

- **YYYY-MM-DD** — cosa è stato deciso.
  Perché: il ragionamento, inclusa la misura o il vincolo che l'ha imposto.
  Scartato: le alternative, e cosa non funzionava in ciascuna.

## Voci

- **2026-08-03** — vault Obsidian di memoria dentro il repo, in `vault/`, in italiano.
  Perché: le note vengono versionate insieme al codice che descrivono, e la root del repo resta
  pulita.
  Scartato: vault nella root del repo (`Templates/`, `Bases/`, `Projects.md`, `.obsidian/` in
  mezzo agli script); vault fuori dal repo (le note si separano dal codice).

Vedi [[Architettura]] per lo stato attuale prodotto da queste decisioni.
