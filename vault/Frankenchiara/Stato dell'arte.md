---
type: nota
project: frankenchiara
updated: 2026-08-03
tags: [tipo/nota, progetto/frankenchiara]
---

# Stato dell'arte: chi ha fatto cosa con questo hardware

Cosa dicono costruttore e letteratura sul nostro rivelatore e sul crollo di gain ad alto
rate. Serve a due cose: sapere cosa è già noto (per non riscoprirlo) e sapere **quanto
fuori specifica stiamo lavorando**, che è il riinquadramento più utile emerso finora. Il lato
statistico della bibliografia — decompounding, cumulanti, level-crossing — sta invece in
[[Letteratura]].

*Fonti raccolte il 2026-08-03 via ricerca web. Dove non ho letto il paper completo ma solo
abstract o sintesi di ricerca, è segnalato — vale come indizio, non come citazione.*

## Il numero del costruttore che riinquadra tutto

Scionix, sulla propria pagina dei partitori di tensione:

> "A standard resistor value between dynodes is 470 kΩ which is a compromise between bleeder
> current and gain stability which is **sufficient for count rates up to approx. 50.000 c/s**."

Il nostro partitore usa **470 kΩ** sugli stadi finali ([[Hardware]]). Confronto coi run:

| run | rate | volte il limite dichiarato |
|---|---|---|
| Am-241, 94 µSv/h — *misurato* col PHA | 0.39 Mcps | **8×** |
| Cs-137, 889 µSv/h | 1.65 Mcps | **33×** |
| Cs-137, 28100 µSv/h | 52 Mcps | **1040×** |

E la regola di progetto, sempre da Scionix: *"the average bleeder current should be always
defined as at least 10 times larger than the average anode current in the detector."* Con
$I_b = 97$ µA questo vuol dire $I_a < 9.7$ µA. Stimando $I_a$ col rate misurato sull'Am-241
si ottengono ~45 µA, cioè **4.6× oltre — e quello è il run più basso**. Il massimo assoluto
del tubo (0.1 mA di corrente d'anodo media) è praticamente $I_b$.

> **Il crollo di gain non è un effetto sottile che stiamo estraendo: stiamo lavorando 1–3
> ordini di grandezza fuori dall'inviluppo di progetto.** Il 15× era garantito.

Va detto in apertura di qualunque relazione, perché cambia la domanda da "perché il gain
crolla?" a "quanto lontano si può spingere la stima *dentro* il crollo?".

## Il ginocchio del ladder, validato dall'esterno

Due strade indipendenti, e concordano:

| strada | $\lambda_\text{knee}$ |
|---|---|
| Scionix: 470 kΩ buono fino a ~50 kcps, e un partitore **tarato** alza la carica di saturazione di **≥4×** (letteratura) | ~200 kcps |
| il nostro ladder ($\Sigma R$ = 5.85 MΩ, −570 V) | ~175 kcps |

Il modello non era tarato su quel numero, quindi è una verifica vera. Vedi [[Gain ladder]].

La letteratura conferma anche che **il taper si sceglie deliberatamente per il rate**, al
prezzo di un gain più basso a pari HV — cioè Scionix ha già fatto quella scelta per noi, ed
è il motivo per cui il teorema AM-GM (che assume resistori uguali) non si applica a questo
tubo.

## Il meccanismo è textbook, non nostro

La letteratura descrive il nostro stesso meccanismo: gli shift di gain indotti dal rate si
spiegano con le fluttuazioni di tensione sui dinodi, quando la corrente di moltiplicazione
supera la capacità della rete di bias di rifornire il dinodo, alterando la distribuzione di
tensione su tutto il partitore.

Ma con una frase che apre lo spazio per un contributo:

> *"Gain shift effects have not been completely quantified in the case of NaI(Tl)
> detectors."*

Quindi il meccanismo è noto, la **quantificazione** su NaI no. È lì che sta il valore di
[[Gain ladder]] e della [[Stima della dose]].

**Una discrepanza che non ho risolto.** La letteratura parla di droop sugli **stadi finali**,
mentre il nostro ladder trova i primi stadi che si affamano e gli ultimi che *salgono*. La
mia ipotesi è che siano due regimi — loro il transitorio (i condensatori di disaccoppiamento
che si scaricano durante l'impulso), noi lo stazionario DC — ma **è un'ipotesi, non l'ho
verificata sui paper**. Vedi [[Backlog]].

## Chi ha usato questo rivelatore

Nessuno con la nostra variante esatta (`51B51/1.5M-E1-L-T-X-NEG`), ma tre lavori vicini.
Attenzione alle varianti: le sigle cambiano il PMT e quindi i numeri di raccolta luce.

- **[Experiment and modeling of scintillation photon-counting and current measurement for PMT
  gain stabilization](https://www.sciencedirect.com/science/article/abs/pii/S0168900215001515)**
  (NIM A, 2015) — **il più pertinente.** Usa uno **Scionix 51B51/2** e combina *photon
  counting* con l'integrazione di carica classica per stabilizzare il gain **senza hardware
  aggiuntivo**. È l'approccio complementare al nostro: loro stabilizzano il gain, noi
  rendiamo la stima insensibile al gain ([[Statistiche gain-free]]). Da qui viene anche il
  numero di **10 pe/keV**, misurato — ma su un PMT da 2", vedi il caveat sotto.
- **[Effects of high count rate and gain shift on isotope-identification
  algorithms](https://www.sciencedirect.com/science/article/abs/pii/S016890020901701X)** —
  applicativo: come il rate alto e lo shift di gain degradano l'identificazione dei
  radionuclidi.
- **[Response of G-NUMEN LaBr₃(Ce) detectors to high counting
  rates](https://arxiv.org/pdf/2307.07818)** e **[Simplified PMT
  Model](https://arxiv.org/pdf/0809.4210)** — modelli di PMT ad alto rate su un altro
  scintillatore, utili per confronto di approccio.

Altre varianti Scionix in letteratura, **non confrontabili coi nostri numeri**: `51B51/SiP-E3-X`
(lettura a **SiPM**, non PMT) usata nel lavoro su afterglow NaI/CsI per COSI e in uno studio
di discriminazione Cs-134/137.

## Il caveat sulle varianti: 10 pe/keV non sono i nostri

I 10 pe/keV del paper sono misurati su un `51B51/**2**`, dove il `/2` è un **PMT da 2"**
(51 mm), cioè della stessa faccia del cristallo. Il nostro `/1.5M` è un **PMT da 1.5"**
(38 mm), con area utile di fotocatodo Ø34 mm su un cristallo Ø51 mm: rapporto d'area nudo
$(34/51)^2 = 0.44$. Non è proporzionale (c'è interfaccia ottica e riflettore) ma la perdita
di raccolta è reale.

> **10 pe/keV è un limite superiore per noi**, non una misura.

Impatto sul guadagno assoluto stimato ([[Catena di lettura]]): 1.17×10⁶ a 10 pe/keV, 1.95×10⁶ a 6 —
resta 1–2×10⁶ in ogni caso, quindi la conclusione tiene con ~40% di incertezza.

## Cosa si può e cosa non si può fare

**Non si può**, e adesso con numeri del costruttore invece che nostri:

- **avere gain stabile a questi rate con un partitore passivo.** Siamo 8–1040× oltre il
  limite dichiarato; nessuna correzione software cambia il fatto che $I_a \gtrsim I_b$;
- **fare spettroscopia** nei run Cs: il pile-up e il gain che collassa insieme distruggono la
  scala d'energia ([[Limiti]]);
- **usare la corrente media come dose** senza conoscere l'offset del DAC ([[Catena di lettura]]).

**Si può**, ed è ciò che il progetto ha fatto:

- **stimare la dose con statistiche gain-free** entro ×1.24 mediano su 2.5 decadi
  ([[Stima della dose]]) — perché il gain si cancella nei rapporti di cumulanti, invece di
  essere corretto;
- **fare PHA sul run risolto** (Am-241) e misurare P(A) direttamente
  ([[Misure a basso rate]]);
- **quantificare** il crollo con un modello di circuito che riproduce il 15× misurato
  ([[Gain ladder]]) — che è esattamente ciò che la letteratura dice non essere stato fatto
  per il NaI(Tl).

**Si potrebbe**, con hardware:

- **partitore attivo o booster** sugli ultimi stadi: la letteratura riporta che la
  configurazione a partitore attivo è nettamente più lineare e stabile col rate. È la strada
  hardware, e sposta il limite invece di aggirarlo;
- **controllo HV attivo** in retroazione (il [[Metodo Target]]);
- **stabilizzazione via photon-counting** come nel paper del 51B51/2, che usa il rivelatore
  stesso come riferimento.

