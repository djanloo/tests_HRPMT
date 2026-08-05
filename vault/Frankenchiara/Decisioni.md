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

- **2026-08-03** — le marche $A_k$ dei simulatori possono venire da uno **spettro di ampiezza
  empirico** (`energy_spectrum.py`, argomento `spectrum=`), non più solo da una Gamma. La Gamma
  resta il default.
  Perché: la Gamma era una scelta computazionale, non fisica — è chiusa sulla somma, quindi la
  carica aggregata di un bin si estraeva in un sorteggio. Ma è unimodale e liscia, e uno spettro
  vero ha fotopicchi, continuo Compton e righe X. In pileup profondo il CLT nasconde la
  differenza; a basso rate no, e il run Am-241 a 94 µSv/h è proprio lì. La misura che decide:
  $m_4=\langle A^4\rangle$ entra **linearmente** nella stima del rate di
  `mssd_cumulant_estimate`, e vale 3.28 per una Gamma CV 0.5 contro 117 per l'Eu152 su HPGe —
  fattore 36, invisibile nei residui. Corroborante: i `ser_cv` fittati sui 5 run Cs-137 vanno da
  0.13 a 1.28 senza monotonia nella dose, che è il sintomo di una famiglia a un parametro
  costretta su una forma che non le appartiene.
  Scartato: (i) togliere la Gamma — `sde_fit.py` e `fit_simulator.py` la fittano e i loro
  `*_results.json` la contengono, quindi si rompevano quattro file per nessun guadagno;
  (ii) mantenere la chiusura analitica con una mistura di Gamma — approssima una forma che si
  può invece campionare esattamente; (iii) approssimare i conteggi per bin a 0/1 dato
  $\lambda\Delta t \ll 1$ — `poisson_marks` è esatto a ogni rate per lo stesso costo.

- **2026-08-03** — Cs137 e Am241 su NaI sono **modellati** (`energy_spectrum.nai()`:
  Klein-Nishina + fotopicco + backscatter + riga X + risoluzione), non misurati, e marcati come
  tali (`.synthetic`, suffisso `(NaI,sim)`).
  Perché: sono le due sorgenti dei run reali, quindi le più utili di tutte, ma il DDE non ne
  spedisce nessuna delle due (ha Co57, Co60, Fe55, Eu152, una miscela) e `isodb.mdb` non contiene
  dati di riga leggibili. La fisica è nota e verificabile: il controllo automatico ritrova il
  fotopicco entro il 3% e la spalla Compton a 477 keV.
  Scartato: (i) spedire solo gli spettri misurati e usare il Co57 al posto del Cs137 — nuclide
  sbagliato, $m_4$ sbagliato, e sarebbe passato per una misura; (ii) scaricare uno spettro NaI
  misurato dal web — i dati numerici per canale non sono reperibili in modo affidabile, solo
  grafici; (iii) fonderli nella cartella `spectra/` come CSV insieme ai misurati — avrebbe
  cancellato la distinzione fra misura e modello, che è la cosa da non perdere.

- **2026-08-03** — vault ristrutturato: **una nota per soggetto**, nome = nome della cosa.
  Sciolte `RELAZIONE`, `REPORT`, le quattro `Relazione - *`, `findings_approaches`,
  `references` in 17 note-soggetto; cancellati il tipo `bug` con cartella, template e Base,
  e la nota *Architettura*.
  Perché: era una relazione lineare (§1→§15) travestita da vault. Le note si concatenavano
  per numero invece di essere linkabili per soggetto, il che produceva tre sintomi misurabili:
  (i) quattro duplicazioni — shot noise in 3 note, Campbell in 2, bibliografia in 3, tabella
  dei file in 2; (ii) `REPORT.md` a 426 righe, sopra il ceiling, non caricabile per una
  domanda piccola; (iii) tre livelli di indice (`Projects` + `Frankenchiara` + `RELAZIONE`)
  per un vault con un progetto. Il prefisso `Relazione - ` era una cartella travestita da
  nome file, e la numerazione impediva di riordinare senza rinominare.
  Scartato: (i) solo rinominare, lasciando i confini dov'erano — non toglieva né le
  duplicazioni né il file sopra il ceiling; (ii) note per tema, ~8 da 150-200 righe — più
  comode da navigare ma diverse restavano multi-argomento, cioè il problema di partenza;
  (iii) tenere `RELAZIONE` come percorso di lettura compilabile con uno script — l'ordine
  vive nell'entry point e uno script in più per concatenare note è debito senza committente.
  Backup delle 1631 righe originali nello scratchpad di sessione prima della rimozione; il
  contenuto è comunque in git.

- **2026-08-03** — `Codice.md` al posto di *Architettura*.
  Perché: il template *Architettura* (Componenti / Flusso dei dati / Vincoli / Trappole)
  descrive un servizio con processi che si parlano. Questo repo è ~15 script di analisi che
  girano a mano: il "flusso dei dati" è un `json` scritto da uno e letto da un altro, i
  "componenti" sono file. Una mappa file → cosa fa dice qualcosa di vero; le quattro sezioni
  del template sono rimaste vuote per due settimane, che è la loro risposta.
  Scartato: riempire *Architettura* forzando il contenuto nelle sue sezioni.

- **2026-08-03** — cancellato il **modello minimale omogeneo** del gain (`gain_solve.py`, la sua
  figura, e le ~75 righe in `gain_model_proposal.md`). Resta solo il ladder risolto.
  Perché: era fuorviante e non usato. Fuorviante perché la sua ipotesi centrale — tutti gli
  stadi cadono della stessa frazione $\rho$ — è **falsa**, e il ladder mostra che è falsa nel
  modo che conta: i primi stadi si affamano (91→46 V) mentre gli ultimi salgono (→122 V). Un
  lettore che parte dal minimale impara un meccanismo sbagliato e poi deve disimpararlo. Non
  usato perché nessuno importa `gain_solve` e il fit ai dati reali passa dal ladder. E il
  ladder non è complicato: sono $N$ equazioni di Kirchhoff con `fsolve`, non giustificano un
  modello-giocattolo che faccia da rampa d'accesso.
  Conservati, riattaccati al ladder: il ginocchio $\lambda_\text{knee}\sim I_b/(q n_0 G_0)$ e
  il cross-check col brevetto (il tetto di targa "0.1 mA" *è* la corrente di bias) — sono
  proprietà del circuito, non dell'approssimazione uniforme.
  Scartato: tenerlo come sezione "storica" — un modello sbagliato in una nota di memoria viene
  riletto come vero; il registro di cosa si credeva sta qui, che è il posto giusto.

- **2026-08-03** — il PHA offline si fa **integrando la carica su un gate**, non cercando i
  picchi (`pha_lowrate.py`).
  Perché: su questo rivelatore un evento è un *burst* di spike da fotoelettrone singolo lungo
  il decadimento di scintillazione (ACF 1/e = 260 ns, coda a ~1 µs), non un impulso liscio. Il
  peak-finding conta fotoelettroni: misurato 113 massimi/record contro ~3 eventi attesi. Nessun
  veto di pile-up lo aggiusta, perché i conteggi in eccesso sono *dentro* un evento, non fra
  due. L'energia di un evento è la sua carica.
  Scartato: (i) soglia assoluta `height=5σ` — la coda di un impulso resta sopra soglia per ~2τ
  e le ondulazioni di rumore su di essa fanno massimi nuovi (77/record); (ii) `prominence` sulla
  traccia grezza — risolve la coda ma non il fatto che i massimi sono fotoelettroni
  (113/record); (iii) sottrarre una baseline locale pre-impulso per il tail-riding — la
  prominenza della somma scorrevole lo fa già.
  Verificato che il pile-up non distorca: allargando il veto da 0 a 4 gate la statistica cala
  di 40× e il centroide del fotopicco si muove entro l'1%. Vedi [[Misure a basso rate]].

- **2026-08-03** — il secondo canale di caratterizzazione si chiama **`csp`** (`csp.npy`), non
  più col nome di lavoro precedente, e la sua natura è dichiarata: è l'uscita di un
  **preamplificatore di carica a valle dell'anodo**. Il canale su cui si lavora
  (`anodewaves`) è preso da una **resistenza di shunt all'anodo**, $V=R\,I$, non filtrato.
  Perché: il nome di lavoro era uno scherzo interno e il progetto è diventato una cosa seria
  — la relazione va letta da altri. Ma il rinominare è l'occasione per scrivere il fatto
  fisico che il nome nascondeva: i due file non sono "due canali qualsiasi", sono **due punti
  di prelievo sullo stesso anodo**, uno crudo e uno integrato.
  Conseguenza dichiarata: **il CSP resta fuori dai risultati.** Integrando filtra via l'alta
  frequenza, che è dove sta l'informazione di conteggio; ad alto rate la sua finestra di
  integrazione è più larga della spaziatura fra eventi, quindi il pile-up è dentro la
  risposta e non si scioglie. Le misure lo dicono: incrementi lisci
  ($\kappa_4[\Delta y]\approx 0$, bootstrap 14% > 0 → MSSD inutilizzabile) e
  $N_\text{eff}\approx 6.6$ tempi di correlazione per finestra contro 67 dello shunt. Serve
  solo da riferimento e da contro-prova su una $h$ diversa.
  Scartato: (i) tenere il nome vecchio con una nota a piè di pagina — resta nei nomi dei file
  e nelle figure; (ii) buttare il dato CSP — è la contro-prova che il modello shot-noise non
  è tarato su una sola forma d'impulso.
  Nuove note [[Hardware]] (il rivelatore) e [[Catena di lettura]] (cosa leggiamo e come).

- **2026-08-03** — `Hardware.md` spezzata in **[[Hardware]]** (il rivelatore) e
  **[[Catena di lettura]]** (cosa leggiamo e come).
  Perché: era arrivata a 416 righe, sopra il ceiling di 400, e conteneva **due soggetti**
  distinti che rispondono a due domande diverse — "cos'è il rivelatore" (cristallo, PMT,
  partitore, datasheet, sigla) e "cosa sto leggendo" (i 50 Ω, il guadagno ×1/×4, CSP vs FAST,
  quale board, la calibrazione assoluta). Il confine era netto e le due metà escono a 225 e 215
  righe. Come dice il criterio in [[Projects]]: una nota va spezzata quando parla di due cose,
  non quando è lunga — qui valevano entrambe.
  Fatto anche: rediretti gli 11 link in entrata che riguardavano la *lettura* e non il
  rivelatore (per esempio `$R_L$` e il carico vero, la polarità DC-coupled, l'offset del DAC),
  lasciando su [[Hardware]] quelli sul partitore e sui datasheet.
  Scartato: tenere una nota sola sforando il ceiling — è la soglia oltre cui non si carica più
  in contesto per una domanda piccola, che è tutto il punto dello schema.

- **2026-08-04** — cancellato `anodewaves.npy` e ogni suo riferimento; il dataset ufficiale è
  `data/anode_waveforms/*.h5` (cartella rinominata da `jeanluke`). Il canale d'anodo si chiama
  ora **FAST**, quello del preamp **CSP**, come li chiama l'hardware.
  Perché: `anodewaves.npy` era uno studio preliminare, e **conteneva esattamente i primi 1000
  record di `run_Cs-137_28100.h5`** — verificato bit per bit il 2026-08-04
  (`np.array_equal` True su quel run, False su tutti gli altri cinque). Quindi era un
  duplicato parziale del dataset ufficiale sotto un altro nome: due nomi per lo stesso dato
  sono un invito a sbagliare attribuzione.
  **Conseguenza importante per come si leggono le note:** i risultati attribuiti ad
  "anodewaves" **non sono stati cancellati, sono stati riattribuiti** — erano misure vere sul
  run Cs-137 a 28100 µSv/h, solo chiamate col nome sbagliato. Vale per i τ fittati
  (17/257 ns), il λ da cumulanti (~2.8×10⁸ Hz), la kurtosi ≈ 0, il CV al floor gaussiano e il
  test di indipendenza contro il CSP.
  Scartato: (i) cancellare anche i risultati insieme al nome — sarebbe stato buttare misure
  buone; (ii) tenere il file come "copia di comodo" — è la duplicazione che ha creato il
  problema; (iii) lasciare il nome storico nei docstring del codice — sta qui, che è il
  registro di cosa si chiamava come.
  Nota: `csp.npy` **resta**, perché non ha equivalente nel dataset ufficiale (i sei run sono
  tutti sul ramo FAST) ed è la contro-prova su una $h$ diversa.

- **2026-08-04** — **eliminate tutte le sezioni "Collegamenti"**; i link stanno solo nel
  discorso.
  Perché: producevano un grafo quasi completamente connesso, in cui ogni nota rimanda a ogni
  altra e quindi nessun rimando porta informazione. Misurato prima dell'intervento: 23% dei
  link erano ripetizioni interne, e le sezioni in fondo erano la fonte principale. Un link
  dentro una frase dice *perché* l'altra nota serve lì; un elenco in fondo dice solo che i due
  argomenti sono vicini — cosa che in questo progetto è vera per qualunque coppia di note.
  Come: delle 15 voci nelle 6 sezioni, **6 assorbite** nel testo dove c'era una dipendenza vera
  (es. il rimando alla metà gemella dopo lo split di Hardware, l'occupancy che rende lecito il
  PHA, il modello NaI che il PHA valida), **4 scartate** perché raggiungibili in un hop
  (Circuito equivalente → Statistiche gain-free passa da Gain ladder), le altre erano
  duplicati di link già nel corpo.
  Risultato: 255 link, 15% di ripetizioni, 0 orfane. Convenzione scritta in [[Projects]] per
  non farla ricrescere.
  Scartato: tenere le sezioni con la regola "solo link non già nel corpo" — è quello che avevo
  fatto il giorno prima, e restava un elenco di vicinanze topiche.

- **2026-08-05** — cancellata la nota *Indipendenza dei due file* (decisione tua, nel commit
  `rmvd useless stuff`); il risultato che conteneva è stato **riassorbito** in
  [[Rivelatore e dati]].
  Perché: era una nota da 50 righe su un solo risultato negativo — i canali FAST e CSP non
  sono lo stesso segnale — che dopo il chiarimento sull'hardware è diventato quasi ovvio: sono
  due punti di prelievo diversi, uno crudo e uno integrato ([[Catena di lettura]]), quindi che
  siano indipendenti non stupisce più nessuno.
  Cosa è stato conservato, e dove: la **spiegazione della correlazione spuria** —
  $N_	ext{eff}pprox 6.6$ oscillazioni indipendenti per finestra danno spread di
  campionamento $1/\sqrt{6}pprox 0.4$, contro lo 0.32 osservato — vive ora nel paragrafo di
  [[Rivelatore e dati]] che dice che i due canali sono indipendenti. Serve ancora, perché lo
  stesso $N_	ext{eff}$ piccolo è la ragione per cui $\kappa_4$ sul CSP è inservibile.
  Ripulite le 4 referenze rimaste appese.

Vedi [[Codice]] per lo stato attuale prodotto da queste decisioni, e
[[Simulazione SDE]] per come è implementato il simulatore.
