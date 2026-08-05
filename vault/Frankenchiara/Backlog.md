---
type: backlog
project: frankenchiara
updated: 2026-08-03
tags: [tipo/backlog, progetto/frankenchiara]
---

# Backlog

Voci aperte. Abbastanza contesto per voce da poterci lavorare mesi dopo senza ricostruire la
conversazione da cui è nata — cosa, perché conta, e da dove partire.

Spunta una voce invece di cancellarla: una voce fatta con il suo ragionamento è un registro
gratuito di cosa è cambiato e quando.

- [x] ~~Popolare `Architettura` leggendo il codice.~~ Fatto diversamente il 2026-08-03: la nota
  è stata sostituita da [[Codice]] (mappa file → cosa fa), perché per un repo di script di
  analisi le sezioni del template *Architettura* restavano vuote. Vedi [[Decisioni]].

- [ ] Far passare i momenti dello **spettro** allo stimatore invece di quelli della Gamma.
  Perché: `mssd_cumulant_estimate.ser_moments(cv)` calcola $m_2, m_4$ da una Gamma, e $m_4$ entra
  linearmente nella stima del rate; la sistematica viene scansionata su `cv ∈ {0, 0.3, 0.5, 1.0}`,
  cioè dentro una famiglia a un parametro che non può contenere il fattore 36 fra una Gamma e
  l'Eu152. Da dove partire: `ser_moments` accetta anche uno `energy_spectrum.Spectrum` e ne
  restituisce `moment(2)`/`moment(4)` — una riga; la parte vera è decidere quale spettro assumere
  sui run reali (Cs-137 e Am-241, ma con quale peak-to-total per *quel* cristallo?). Vedi
  [[Simulazione SDE]].

- [x] ~~Validare il modello NaI contro una misura.~~ Fatto in parte il 2026-08-03 con il PHA
  sull'Am-241 ([[Misure a basso rate]]): la **risoluzione** è confermata (FWHM/E misurata 30.2%
  a 59.5 keV → `res662` implicito 9.1% contro l'8% assunto) e il fotopicco cade dove deve.
  Resta aperto il pezzo sotto.

- [ ] Fittare `photofrac` e `backscatter` di `energy_spectrum.nai()` sull'istogramma PHA
  misurato. Perché: il PHA ha confermato picco e risoluzione ma **non i pesi relativi** —
  misurato CV 0.759 contro 0.252 del modello, perché il reale ha un continuo di bassa energia
  (scatter nel cristallo, energia parziale, righe L, soglia) e una coda alta che il modello non
  ha. Sono i due default messi a occhio, e dipendono da cristallo, geometria e schermo. Da dove
  partire: `pha_lowrate.photopeak` dà già l'istogramma calibrato; due parametri, un
  `minimize`. Nota che il continuo misurato include effetti di soglia che il modello non deve
  riprodurre — va tagliato via prima di fittare, o si fitta un artefatto dell'acquisizione.

- [ ] Rifittare i run reali con `spectrum=` invece di `ser_cv`. Perché: `sde_fit.py` e
  `fit_simulator.py` fittano ancora la Gamma, e i loro `ser_cv` (0.13→1.28 senza monotonia nella
  dose) sono probabilmente un artefatto. Con lo spettro fissato dal nuclide si perde un parametro
  libero e si guadagna un vincolo: se i fit restano buoni, è una conferma indipendente.

- [ ] **Prior SER da Personick** invece della scansione cieca. Perché: mettere
  $F = \langle A^2\rangle/\langle A\rangle^2$ nel range fisico di un PMT (F≈1.1–1.5, cioè
  CV≈0.3–0.7) stringe il sistematico ~×6 sul rate a ~×1.5 — è il singolo guadagno più grosso
  disponibile senza dati nuovi. Da dove partire: [[Letteratura]] (Personick 1971, open access),
  poi [[Spettro di ampiezza]]. Nota: ora che c'è uno spettro empirico, questa voce e le due
  sopra si sovrappongono — probabilmente la strada giusta è lo spettro, e il prior di Personick
  serve come sanity check su $m_2$.

- [ ] **Forward-model di level-crossing alla Roessl** per il CSP (pileup moderato): fit dello
  *spettro dei crossing* N(u) vs soglia. Perché: è informazione di λ non-varianza e non
  contaminata da $\kappa_3$ (che è il punto debole di tutti gli altri metodi). Da dove partire:
  [[Level crossing]], dove il test del solo mean-crossing è già fatto e satura. Da fare solo se
  il rate del CSP deve essere pinnato meglio.

- [ ] Aggiungere la **frequenza RMS da level-crossing** come cross-check di forma nel fit.
  Perché: è cheap ($\approx 220$ kHz per il CSP) e vincola rise+fall indipendentemente dalle
  metriche ACF/PSD che li sotto-pesano — lo stesso buco che ha già prodotto due errori in
  [[Fit dei parametri]].

- [ ] Riallineare `fit_results.json` con i suoi due consumatori. Perché: il file è stato
  rigenerato su un dataset diverso (chiavi `signals/run_Cs-137_*.h5`) mentre i due script che
  lo leggono si aspettano ancora le chiavi vecchie (`FAST` / `CSP`). Entrambi crashano nella parte
  "applica ai dati veri": `simulate_pmt.py` con `KeyError: 'FAST'` nel blocco plot,
  `mssd_cumulant_estimate.py` con `FileNotFoundError` su `signals/run_Cs-137_888.92.h5` — un
  percorso che non esiste (i run stanno in `data/anode_waveforms/`) e che comunque
  `np.load` non saprebbe leggere, essendo `.h5`. In tutti e due i self-check a monte passano,
  quindi la logica è sana: è solo la parte che tocca i file reali.
  Radice unica, quindi una decisione sola: **o** si rigenera `fit_results.json` sui due
  `.npy` di caratterizzazione (che è ciò per cui quei blocchi erano scritti), **o** i due
  consumatori passano ai run `.h5` con `h5py` e le chiavi nuove. La seconda è più utile ma
  vuole anche la mappa run → `kind` (anode/preamp), che per i run reali è sempre `anode`.
  Preesistente al 2026-08-03, non urgente.

- [x] ~~Verificare il segno del termine di carico $t_i$ in `gain_ladder.py`.~~ **Risolto il
  2026-08-03: il codice è giusto.** La KCL $(U_{i-1}-U_i)/R+(U_{i+1}-U_i)/R = +t_i$ non dice
  "corrente entrante nel nodo" ma $I_{i+1}-I_i$, cioè di quanto cresce la corrente di catena
  attraversando il nodo — un Laplaciano discreto. Prove: con $+t_i$ `fsolve` converge
  (residuo $8\cdot10^{-15}$), $I_{k+1}-I_k=t_k$ a $8\cdot10^{-11}$ relativo e
  $\sum_i t_i = I_a-I_0$ esattamente (conservazione globale); con $-t_i$ non converge e le
  correnti non tornano con nessun segno. Le correnti nei resistori crescono 85 → 211 µA verso
  l'anodo: **i $t_i$ tornano nelle resistenze**, ed è lì il meccanismo dell'affamamento. Vedi
  [[Gain ladder]].

- [ ] Verificare licenza e attribuzione di `Photomultiplier_schema_en.png`. Perché: figura
  di provenienza esterna usata in [[Rivelatore e dati]]; se la relazione va fuori serve
  l'attribuzione corretta. Da dove partire: il nome è quello di un file di Wikimedia
  Commons.

- [ ] **Mettere i resistori veri (tarati) in `gain_ladder.py`.** Perché: il codice prende
  $R$ come **scalare**, ma il partitore reale è 180K, 850K, 1M, 1M, 470K×6 ([[Hardware]]),
  e la taratura non è un dettaglio: i primi stadi hanno resistori più grandi, che è
  esattamente l'ingrediente "primo stadio protetto" che rompe la premessa dell'AM-GM. Con
  resistori uguali il teorema dice che il gain può solo scendere; **con questi non è
  dimostrato**. Da dove partire: `R` diventa un array di $N+1$ elementi in `build()` e nel
  residuo KCL (dove oggi compare `/R` due volte, diventano `/R[i]` e `/R[i+1]`) — mezz'ora.
  Poi rifare il fit e guardare se la monotonia sopravvive. Anche $\Sigma R$ va corretto:
  5.85 MΩ contro i 10 assunti, fattore 1.71.

- [x] ~~Stabilire quale board ha preso i dati.~~ **Risolto il 2026-08-03: Scionix + Handheld
  EVM (FRANKENSTEIN)**, non la GammaStream. Due prove dal confronto degli schemi
  ([[Catena di lettura]]): (i) la base **S2580 GammaStream non ha un ramo veloce** — la sua unica
  uscita è `Vout` dal CSP con τ ≈ 11 µs, che non può produrre il τ = 250 ns di
  del ramo FAST, e noi abbiamo entrambi i canali; (ii) la S2580 **accoppia l'anodo in AC**
  (C2 = 10 nF) mentre i nostri dati sono DC-coupled. Coerente anche col fatto che lo Scionix
  ha il partitore **integrato** e due soli cavetti (RG174 rosso HV, giallo segnale), che è
  quello che l'handheld si aspetta su `DET_IN`; la S2580 è una base per PMT nudo, ed è wirata
  per **HV positiva** mentre lo Scionix è a polarità negativa.
  ⚠️ **Da riaprire (2026-08-05):** il committente indica il digitizer come un **CAEN DT5780**.
  L'esclusione della *base GammaStream* resta valida, ma **la conclusione sull'Handheld non è
  più conclusiva**: DT5780 e board di preamp possono convivere (il DT5780 fornisce HV e
  alimentazione preamp su DB9 e digitizza, le board fanno CSP/FAST), però l'Handheld EVM ha un
  ADC **proprio** (coppie LVDS D0..D13) e quindi è autosufficiente. Da chiedere, non da dedurre.

- [x] ~~Confermare il sampling rate.~~ **Chiuso il 2026-08-05: sono 100 MS/s**, dalla scheda
  tecnica del **CAEN DT5780** (2× digitizer 100 MS/s, **14 bit**). Conferma anche i 14 bit, che
  avevo dedotto dal massimo osservato 4363 > 4095. L'argomento indiretto sui 230 ns del NaI —
  ACF 1/e = 26 campioni, che a 100 MS/s fanno 260 ns e a 65 MSPS ne farebbero 400, cioè 1.7× il
  cristallo — era giusto.

- [ ] **Quale dei 4 range d'ingresso del DT5780 era selezionato**, e i valori dei 4 range dal
  manuale. Perché: è **l'unico numero che manca** per il guadagno assoluto del PMT. Con 14 bit e
  50 Ω, il fotopicco Am-241 a 1146 ADC·campioni dà $G_\text{PMT}$ = 5.4×10⁵ con un range da
  3.7 Vpp e 1.4×10⁶ con 9.5 Vpp; gli altri due range danno valori non plausibili per un tubo a
  10 stadi a −570 V. I due candidati differiscono di 2.6×, **meno dell'incertezza sui pe/keV** —
  quindi in pratica il guadagno assoluto è già **1–2×10⁶** e basta un numero per fissarlo. Vedi
  [[Catena di lettura]]. Nota: il DT5780 ha anche un **offset DC con DAC a 16 bit per ingresso**,
  che è il meccanismo del piedistallo — il suo valore per run serve a [[Baseline]].

- [ ] Riconciliare la risoluzione assunta in `energy_spectrum.nai()`. Perché: ci sono tre
  numeri a 662 keV — **6.6%** dal testsheet del cristallo (s/n S1AB5195, misurato da
  Scionix), **8.0%** assunto nel codice, **9.1%** implicito dal nostro PHA sull'Am-241. Il
  9.1 è quello della nostra catena completa e probabilmente il numero giusto per modellare i
  nostri dati; il 6.6 è il pavimento del cristallo. I tre valori sono ora documentati nel
  docstring di `nai()`, ma il default è ancora 8.0. Da dove partire: decidere se il default
  diventa 9.1 (nostra catena) e rifare i confronti di [[Misure a basso rate]].

- [x] ~~Stabilire il settaggio di guadagno ×1/×4 per ciascun run.~~ **Risolto dai dati il
  2026-08-03: il guadagno elettronico non è cambiato fra i run.** Test: Msd va come $g^2$
  mentre $\gamma_1$ ed $\eta$ sono gain-free, quindi uno scalino ×4 darebbe **Msd ×16 a
  $\gamma_1$ fermo**. Nei 5 run il massimo salto di Msd è 2.5× ed è monotono; e il run 616,
  che ha baseline 3764 contro ~195 (22×), ha Msd 41.6 contro 46.95 del run 889 — rapporto
  0.89, quindi **non è uno scalino di guadagno**: il 616 differisce per *offset* (o HV).
  Conseguenza: il calo di gain 15× di [[Gain ladder]] **non è un artefatto di commutazione**.
  Caveat: il test assume che la fisica sia liscia nella dose; una commutazione che coincidesse
  esattamente con un cambio di dose potrebbe nascondersi in parte, ma un fattore 16 no.

- [ ] **Chiedere un run con il LED pulser.** Perché: è il singolo dato più utile e
  **l'hardware ce l'ha già** — LED blu integrato, impulso 3–3.5 V da 200–250 ns, picco di
  riferimento a 2.5–3 MeV, con la forma pilotata dal DAC ([[Catena di lettura]]). Un run LED darebbe in
  un colpo: **offset** e **guadagno** assoluti, la $h(t)$ della **sola elettronica** separata
  dalla scintillazione, e la **verifica definitiva dei 100 MS/s** (un impulso di durata nota
  misurato in campioni *è* la taratura del clock). Vale più di un dark run, ed è già montato.

- [ ] **Recuperare il fondo scala dell'ADC** (fogli 3–5 dei PDF in `hardware/`, non ancora
  aperti). Perché: è l'unico numero che manca per la **calibrazione assoluta** — con 50 Ω di
  carico e il fotopicco Am-241 a 1146 ADC·campioni si ottengono carica, elettroni e quindi
  $G_\text{PMT}$ ([[Catena di lettura]]). Con un ADC 12 bit / 2 V viene 1–2×10⁶, che per un tubo a
  −570 V torna. Sbloccherebbe energia assoluta e guadagno assoluto **senza dark run**, cose
  che [[Limiti]] elenca come non ottenibili.

- [ ] **Far girare `mssd_cumulant_estimate` sull'output di `pe_synth.py`.** Perché: risolve la
  discrepanza più grossa che resta. il canale FAST *è* il run 28100, che attende ~52 Mcps,
  ma i cumulanti danno **280 Mcps** — fattore 5.4. Ho escluso la spiegazione più ovvia:
  usare lo spettro vero invece della Gamma **peggiora** (con `ser_cv`=0.05 il fattore
  $m_4/m_2^2$ vale 1.01, con lo spettro Cs-137 su NaI diventa 1.96, quindi λ salirebbe di
  1.94×). Il sospettato che resta è il **clustering**: entro un evento gamma i ~6000
  fotoelettroni non sono indipendenti, e un processo a cluster ha cumulanti più grandi di un
  Poisson dello stesso rate. `pe_synth.py` simula esattamente quel processo Cox/branching con
  λ_γ **noto** — quindi basta dargli in pasto lo stimatore e vedere se restituisce λ_γ o
  qualcosa ~5× più grande. Codice già esistente, esperimento decisivo.

- [ ] Risolvere il conflitto **8 vs 10 stadi** del PMT. Perché: il datasheet Scionix dice
  "10 stage Hamamatsu R10601-100", un aggregatore dice 8. Entra in $G_0$ e nell'esponente di
  collasso $N\kappa$. **Non cambia le conclusioni** — il fit è già degenere in $(N,\kappa)$ e
  sono state provate $N$=8, κ=0.70 e $N$=10, κ=0.75 con residui equivalenti — ma va sistemato
  prima di scrivere un numero di guadagno assoluto. Da dove partire: aprire a mano il PDF
  Hamamatsu (link in [[Letteratura]]), che in automatico non si è fatto leggere.

- [ ] Capire la discrepanza sul **dove** droopa il partitore. Perché: la letteratura descrive
  droop sugli **stadi finali**, il nostro ladder trova i primi che si affamano e gli ultimi
  che *salgono* ([[Gain ladder]]). La mia ipotesi è che siano due regimi — la letteratura il
  transitorio (condensatori di disaccoppiamento che si scaricano durante l'impulso), noi lo
  stazionario DC — ma **è un'ipotesi non verificata sui paper**. Se fosse vera, il transitorio
  è un effetto in più che non modelliamo. Vedi [[Stato dell'arte]].

- [ ] Chiedere il **log di temperatura** dei run. Perché: il rivelatore ha un DS18B20
  integrato, la resa del NaI deriva di ~−0.3%/°C e la stabilità di gain è specificata a 20°C.
  Se i log esistono è una sistematica che si toglie gratis.

- [ ] ⚠️ **Chiedere la configurazione di acquisizione: il baseline restorer era attivo?**
  Perché: è la domanda che sblocca (o affossa) la raccomandazione numero uno del progetto. La
  media misurata è **195.0 ± 0.3 ADC su 300× di dose** — impossibile se fosse la corrente
  media d'anodo — e ho escluso dagli schematici sia l'accoppiamento AC sia un servo analogico
  ([[Baseline]]). Resta il **BLR in firmware**, che spiegherebbe tutto: livello inchiodato a
  lungo termine, fluttuazione per record che sopravvive e scala con l'ampiezza degli impulsi,
  setpoint impostabile (il run 616 sta 3591.6 ADC più in alto).
  **Se è così, un dark run non recupera la DC** e la richiesta giusta diventa "acquisite con
  il BLR disabilitato" — un cambio di configurazione, non un run in più. Serve anche il valore
  di `OFFSET` impostato dal DAC per ciascun run. Da dove partire: chi ha acquisito; nei
  metadati degli `.h5` non c'è (solo activity/distance/dose/nuclide).

- [ ] **Ricevere e archiviare la mappa dei parametri firmware** (in arrivo dalla collega), e
  confrontarla con le ipotesi di [[Baseline]]. Perché: è il documento che rende il baseline
  restorer **invertibile**, e quindi la DC recuperabile per calcolo invece che per misura — il
  che aggirerebbe il muro di `mean²/Var` senza acquisire niente di nuovo.
  **Cosa cercare, in ordine di importanza:**
  1. **baseline restorer**: attivo? lunghezza della finestra, velocità di aggiornamento,
     esistenza di un *hold-off / inhibit* durante gli impulsi. Finestra corta senza inibit =
     massima sottrazione in eccesso, ed è il meccanismo misurato (depressione di 10 ADC prima
     *e* dopo gli impulsi ad alto rate);
  2. **bit di polarità / invert input**: spiegherebbe perché vediamo impulsi positivi da un
     anodo che fisicamente va in negativo, e sarebbe la risposta banale al "il segnale può
     diventare negativo";
  3. **valore di `OFFSET` del DAC per run**: fissa il piedistallo (195 per cinque run, 3764 per
     il 616) e quindi il margine da zero — sul run 7900 sono solo **56 ADC**;
  4. **filtro di sagomatura** (trapezio / CR-RC): se abilitato, l'uscita è bipolare per
     costruzione e un pole-zero non compensato dà coda negativa;
  5. **numero di bit e formato dei campioni** (signed o unsigned): il massimo osservato è 4363,
     quindi **non sono 12 bit**; dai nomi delle net dell'handheld (D0..D13) sembrano 14, ma va
     confermato — entra in tutte le conversioni ADC→volt→carica della calibrazione assoluta
     ([[Catena di lettura]]).
  Da dove archiviarla: `Hardware/` per il documento, e i valori per-run in [[Baseline]].

Ciò che è diventato una vera decisione va invece in [[Frankenchiara/Decisioni|Decisioni]]; ciò
che è diventato un'indagine aperta diventa una nota `approfondimento` con `status`.

## Il muro che non è backlog

Il pileup profondo dell'anode (λ~10⁸, gaussiano) **non si supera** con nessuna delle voci qui
sopra: serve un run a rate più basso o un pedestal/dark. Non è una cosa da fare, è una cosa da
chiedere — vedi [[Limiti]].
