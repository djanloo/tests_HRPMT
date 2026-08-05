---
type: nota
project: frankenchiara
updated: 2026-08-05
tags: [tipo/nota, progetto/frankenchiara]
---

# Hardware: il rivelatore

Com'è fatto il rivelatore che produce il segnale: cristallo, PMT, partitore. Cosa facciamo
poi di quel segnale sta in [[Catena di lettura]]. Nota **da popolare
gradualmente**: quello che c'è sotto è verificato, il resto va aggiunto quando si sa —
meglio una sezione vuota che una riempita a intuizione.

## Il rivelatore, dai datasheet

Documenti in `hardware/`. Il rivelatore è uno **Scionix 51B51/1.5M-E1-L-T-X-NEG**
(`NaI51x51_Led_temp_neg 2.pdf`), con testsheet del pezzo vero.

| | |
|---|---|
| cristallo | NaI(Tl) Ø51 × 51 mm — cioè il 2×2″ |
| PMT | **Ø38 mm, 10 stadi, Hamamatsu R10601-100** (il `-100` = fotocatodo super-bialkali) |
| polarità HV | **negativa** |
| catena di resistori | **5.85 MΩ** |
| HV tipica | −600 … −1000 V |
| risoluzione | spec < 7.5 % FWHM @ 662 keV; **misurata 6.6 %** (s/n S1AB5195, a −570 V) |
| stabilità di gain | < 1 % su 24 h a 20 °C |
| range in energia | 20 keV – 3 MeV |
| connessioni | HV: RG174 rosso; **segnale d'anodo: RG174 giallo** (20 cm) |
| extra | sensore di temperatura DS18B20, LED blu SSL LX 3044 (impulso 3–3.5 V, 200–250 ns → picco di riferimento a 2.5–3 MeV) |

**La polarità negativa è confermata dal costruttore**, quindi lo schema sopra (catodo a
$-V_{HV}$, anodo a massa) è quello giusto e non una deduzione.

### La sigla, decodificata

`51B51 / 1.5M - E1 - L - T - X - NEG`

| | |
|---|---|
| `51B51` | cristallo Ø51 × 51 mm |
| **`1.5M`** | **PMT da 1.5" = 38 mm** — non 2" |
| `E1` | opzione elettronica 1 = il partitore letto sotto |
| `L` | LED |
| `T` | sensore di temperatura |
| `X` | opzione connettori/cavi |
| `NEG` | HV negativa |

⚠️ **Il `1.5M` conta.** In letteratura si trova un `51B51/**2**` (PMT da 2", cioè della
stessa faccia del cristallo) su cui sono misurati **10 pe/keV**. Noi abbiamo un PMT da 38 mm
con area utile di fotocatodo Ø34 mm su un cristallo Ø51 mm: rapporto d'area nudo
$(34/51)^2 = 0.44$. Non è proporzionale (c'è interfaccia ottica e riflettore) ma la perdita
di raccolta è reale, quindi **10 pe/keV è un limite superiore per noi, non una misura**. Vedi
[[Stato dell'arte]].

### Il partitore è TARATO, non omogeneo

Dal disegno del divider, dal catodo verso l'anodo:

```
180K → 850K → 1M → 1M → 470K ×6      +  R_L = 100 kΩ  (carico d'anodo, verso massa)
```

Somma: $180+850+1000+1000+6\times470 = 5850$ kΩ = **5.85 MΩ**, che coincide esattamente col
valore di targa — quindi la lettura dei valori è verificata, non stimata.

Ci sono anche i **condensatori di disaccoppiamento** sugli ultimi stadi (C1 = 1000 pF/2 kV,
C2 = 10 nF/1 kV): sono quelli che forniscono la corrente d'impulso che i resistori non
riescono a seguire, e che il modello stazionario ignora.

$I_b = V_{HV}/\Sigma R$: **97 µA a −570 V**, 171 µA a −1000 V.

## Schema del partitore (per disegnarlo)

### Sì, il catodo sta a −V_HV

Con **HV negativa**: catodo a $-V_{HV}$, anodo a ~massa. È **l'unico schema compatibile
con questa misura**, e il motivo è la lettura: se vuoi il segnale d'anodo su una
resistenza di shunt verso massa e **DC-coupled**, l'anodo *deve* stare a potenziale di
massa. Con HV positiva (catodo a massa, anodo a $+V_{HV}$) l'anodo è a mille volt e devi
accoppiarlo in AC con un condensatore — e lì perdi il livello continuo, che è
esattamente l'informazione che questa catena conserva.

Prezzo dell'HV negativa: il fotocatodo è a potenziale alto rispetto all'involucro, quindi
lo schermo di mu-metal va trattato con cura (se è a massa e vicino al vetro può dare
rumore).

**Nota sul codice, che sembra dire il contrario.** `gain_ladder.py` usa $U_0=0$ (catodo) e
$U_{N+1}=V_{HV}$ (anodo), cioè la convenzione HV *positiva*. Non è un errore: il modello
dipende solo dalle **differenze** $V_i = U_i - U_{i-1}$ e dal vincolo
$\sum_i V_i = V_{HV}$, quindi traslare tutti i potenziali di una costante non cambia nulla
— è una scelta di gauge, presa perché così i numeri restano positivi. Per il **disegno**
usa la convenzione fisica (catodo a $-V_{HV}$): è quella del banco.

### Lo shunt va nel ramo d'anodo, verso massa

$R_s$ sta fra l'anodo e massa; il digitizer misura la tensione ai suoi capi. È in serie
con l'anello del partitore, ma **non lo perturba**, e si vede dai numeri: con
$\Sigma R = 10$ MΩ, $R_s/\Sigma R \approx 5\cdot10^{-6}$ per uno shunt da 50 Ω
($10^{-4}$ per 1 kΩ). La caduta dovuta alla sola corrente di bias è 5 µV (50 Ω) o 100 µV
(1 kΩ): irrilevante. **È per questo che il modello ladder può ignorare lo shunt.**

### Lo schemino

```
        massa (riferimento del digitizer)
          │                    │
          │                    ├───► DIGITIZER (V ai capi di R_s)
          │                    │
          │                   R_s  ~50 Ω … 1 kΩ
          │                    │
          │              ┌─────┴──── ANODO  (raccoglie, non moltiplica)
          │              │
      ┌───┴───┐         R11 = 909 kΩ
      │  HV   │          │
      │   +   ├──────────┘   ┌──── D10 ──┐
      │       │              │           R10
      │   −   │              │    ..    │        11 resistori uguali,
      └───┬───┘              │           │        ΣR = 10 MΩ, I_b = 0.1 mA
          │                  │    D2 ────┤
          │                  │     │     R2
          │                  │    D1 ────┤
          │                  │     │     R1
          └──────────────────┴─── CATODO ┘   a −V_HV = −1000 V
```

Dentro il tubo, gli elettroni vanno **catodo → D1 → … → D10 → anodo**, moltiplicandosi di
$\delta_i$ a ogni dinodo. Fuori, la corrente di bias $I_b$ scorre nella catena di
resistori nello stesso verso. I due flussi si contendono la catena: è quello il
meccanismo di [[Gain ladder]].

### Pseudocodice di connessione (netlist)

Con $N=10$ dinodi. Nodi: `K` (catodo), `D1.D10`, `A` (anodo), `GND`.

```
HV     K    GND     -1000 V        # alimentatore, morsetto + a massa
R1     K    D1      909k
R2     D1   D2      909k
R3     D2   D3      909k
R4     D3   D4      909k
R5     D4   D5      909k
R6     D5   D6      909k
R7     D6   D7      909k
R8     D7   D8      909k
R9     D8   D9      909k
R10    D9   D10     909k
R11    D10  A       909k           # gap di collezione: nessuna moltiplicazione
Rs     A    GND     50             # shunt: il segnale e' la V ai suoi capi
SCOPE  A    GND                    # digitizer, 100 MS/s, DC-coupled
```

**11 resistori per 10 dinodi**: i gap sono $N+1$ (catodo→D1, i nove fra dinodi, D10→anodo),
e a vuoto ciascuno prende $V_{HV}/(N+1) = 90.9$ V — è il "V₁ = 91 V" che compare in
[[Gain ladder]]. Nel codice l'undicesimo gap è escluso dal prodotto del gain
(`diff(Uf)[:N]`), perché l'anodo raccoglie e non moltiplica.

### Simboli da usare

Dalla libreria installata (`Shift+Ctrl+Y`, set *Electric Symbols*): `Resistor` per la
catena (IEC, rettangolare) o `Resistor_US` (zigzag) — scegline uno e sii coerente; `GND`
per la massa; `Voltage_source` per l'HV. Il tubo non c'è nella libreria: disegnalo come un
involucro con il catodo e i dinodi come segmenti obliqui alternati, che è la convenzione.

### Tre cose che il disegno onesto deve dire

1. **I condensatori di disaccoppiamento sugli ultimi stadi.** Un partitore reale li ha
   (forniscono la corrente d'impulso che i resistori non riescono a seguire). Il modello è
   in **regime stazionario DC** e li ignora: va bene per la curva gain-vs-rate, non per i
   transitori. Se li disegni, marcali come "non nel modello".
2. **Il primo stadio potrebbe essere protetto** (zener o $R_1$ maggiore). Non lo sappiamo,
   ed è una delle voci qui sotto — cambia le conclusioni di [[Gain ladder]], perché è
   proprio l'ingrediente che rompe il teorema AM-GM e permetterebbe il *bump*.
3. **La polarità misurata non torna con lo schema, e va confermata.** Con HV negativa e
   shunt verso massa gli impulsi d'anodo sono **negativi**. Ma i dati sono positivi
   (skewness +1.7 sull'Am-241) su una baseline di ~193 ADC. Quindi c'è un'inversione da
   qualche parte, o un offset del digitizer con ingresso invertente. Che la baseline sia
   un offset e non la corrente media si vede dal fatto che **non è monotona nella dose**
   (193, 167, 195, 194, 195 ADC su dosi crescenti): se fosse $\lambda\langle A\rangle$
   crescerebbe. Da verificare sul banco, non da indovinare.

## Cosa questo cambia nel modello

Tre cose non banali, tutte da [[Gain ladder]]:

1. **$N = 10$ dinodi: confermato.** Il modello lo assumeva e ci ha preso.
2. **$\Sigma R$ = 5.85 MΩ, non 10 MΩ** come nel codice — fattore 1.71. Sposta il ginocchio da
   ~180 a ~175 kcps a −570 V (o ~308 kcps a −1000 V): il run più basso del dataset resta
   comunque **5× oltre il ginocchio**, quindi la conclusione "tutti i run sono in collasso"
   **sopravvive**.
3. **Il partitore è tarato, e questo rompe la premessa del teorema AM-GM.** Il modello
   assume tutti i resistori uguali, e su quella base dimostra che il gain può solo scendere.
   Ma i primi stadi hanno resistori **più grandi** (850 K, 1 M, 1 M contro 470 K) — cioè
   esattamente l'ingrediente "primo stadio protetto" che la nota indicava come necessario per
   un eventuale *bump*. **Il teorema vale per resistori uguali; questo tubo non li ha.**.

E una reinterpretazione di $h(t)$:

4. **Il τ ≈ 250 ns che misuriamo è la scintillazione, non l'elettronica.** Il NaI(Tl) decade
   con 230 ns, e l'ACF 1/e misurata è 250–260 ns. Con $R_L = 100$ kΩ un RC da 250 ns
   richiederebbe $C = 2.5$ pF, mentre i soli 20 cm di RG174 ne portano ~20. Quindi la forma
   d'impulso è dominata dal cristallo — coerente con il fatto che a basso rate un evento si
   vede come un **burst** di fotoelettroni lungo ~1 µs ([[Misure a basso rate]]).

## Da riempire

- **quale board** ha preso i dati: GammaStream o Handheld/FRANKENSTEIN? Cambia l'ADC e
  quindi il sampling rate — il `100 MS/s` usato in tutto il progetto è dichiarato "assunto",
  e sulla motherboard GammaStream l'ADC è un **65 MSPS**. Se fosse 65 e non 100, ogni τ in ns
  e ogni λ in Hz va riscalato di 1.54;
- come è fatto il ramo **FAST** a valle di `DET IN` (è davvero un solo shunt, o c'è un
  buffer?);
- **HV per run**: il **CAEN DT5780** fornisce anche l'alta tensione (2 canali, ±5 kV, uscite
  SHV — vedi [[Catena di lettura]]), quindi il valore **è impostato e leggibile dal software**,
  non da indovinare. Oggi si usa la mediana ADC come proxy (i 4 run a ~195 a stessa HV, il run
  616 a 3764 no). Il testsheet dice −570 V, ma è la HV di collaudo Scionix, non dei run;
- impedenza d'ingresso del digitizer, che insieme a $R_L = 100$ kΩ fissa il carico vero;
- geometria sorgente-rivelatore e schermo, che fissano `photofrac`/`backscatter` del modello
  NaI.

