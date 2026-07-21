# Cosa ho scoperto — revisione letteratura (`possible_approaches.md`) + test

Riepilogo di: (a) cosa danno davvero i riferimenti citati per il nostro problema,
(b) l'origine del "segnale troppo liscio" di culoculo (spoiler: **non è rumore**),
(c) test dell'idea più promettente della lista (level-crossing di Rice/Roessl).

---

## 1. La letteratura: opinione, riferimento per riferimento

**Roessl & Daerr, *A Fourier approach to pulse pile-up in photon-counting X-ray
detectors* (Med. Phys. 2016)** — il più rilevante. Identifica il pile-up con il
**problema del level-crossing di un processo shot-noise** e dà una formula di
Fourier esatta per il numero atteso di conteggi in funzione del flusso, per forma
d'impulso e risposta arbitrarie. C'è anche il companion SPIE *"On the analogy
between pulse-pile-up and level-crossing of shot noise"*. **Utile** come modello
forward per un rivelatore a *soglia/conteggio*; per il nostro caso (forma d'onda
continua, no soglia) l'idea del level-crossing è testabile ma ha un limite (§3).
→ https://pubmed.ncbi.nlm.nih.gov/26936714/ ,
https://www.spiedigitallibrary.org/conference-proceedings-of-spie/9783/97831H

**Personick, *Statistics of a General Class of Avalanche Detectors* (BSTJ 1971)**
— dà la distribuzione del guadagno di valanga e l'**excess noise factor**
`F=⟨G²⟩/⟨G⟩²`. È **esattamente** il momento SER `m₂=⟨A²⟩/⟨A⟩²` che domina i nostri
sistematici (il "fattore ~6" su rate/energia). Confronta anche modo-corrente vs
photon-counting = la nostra distinzione Campbelling vs pulse-counting. **Utile**
per mettere un prior fisico sulla larghezza SER (invece di scansionarla alla
cieca). Open access su archive.org. → https://archive.org/details/bstj50-10-3075

**Rice, *Mathematical Analysis of Random Noise* (1944)** — la sorgente della
teoria del level-crossing. Formula chiave (processo gaussiano stazionario):
`N(u) = (1/2π)·√(λ₂/λ₀)·exp(−u²/2λ₀)`, con `λ₀=Var`, `λ₂=Var(derivata)`.
**Utile** ma vedi §3 (in pileup gaussiano il crossing dà la *forma*, non λ).

**Lowen & Teich, *Power-Law Shot Noise* (IEEE IT 1990)** — shot noise con risposta
a legge di potenza `h(t)∝t^{-α}` → spettri `1/f^β` / frattali. **Non è il nostro
caso:** le nostre PSD sono Lorentziane / 2-poli con floor bianco, τ finito, non
1/f. La *macchina* (cumulanti di Campbell) è la stessa, ma il regime power-law
non si applica. Da tenere solo se emergesse struttura 1/f (non c'è).

**Cox & Isham *Point Processes* / Papoulis** — testi di riferimento, framework
generale (processi puntuali, cumulanti). Nessun risultato specifico nuovo per noi.

**Giudizio d'insieme.** La direzione del documento è giusta e già implementata:
trattiamo il segnale come **Poisson filtrato / Campbell** e stimiamo λ dalle
statistiche del continuo, senza pulse-finding (§3–7 del REPORT). Il valore aggiunto
della letteratura è: (i) Personick → prior sulla SER; (ii) Roessl/Rice →
level-crossing come stima/cross-check; (iii) conferma che **tutti** questi metodi
sbattono contro lo stesso muro in pileup gaussiano profondo (anode): la forma
d'onda perde la granularità e resta solo `λ⟨A²⟩`.

---

## 2. Scoperta: culoculo "troppo liscio" = **rise-time**, non rumore

Ipotesi iniziale: aggiungere rumore post-preamp. **Test → è sbagliata.**
Confronto della PSD reale/simulata per bande (rapporto reale/sim, dovrebbe →1):

| banda | fit (rise 528 ns) | + rumore bianco ×3 | rise 200 ns |
|---|---|---|---|
| 0.5–2 MHz | 2.95 | 2.95 | 0.62 |
| 2–8 MHz | 2.19 | 0.94 | 0.43 |
| 30–50 MHz (floor) | 1.01 | **0.18** ✗ | 1.00 |
| dy-std (reale 8.3) | 7.0 | 14.7 | 8.5 |

Al segnale reale manca potenza **nella banda media 0.5–8 MHz** (fino a ~3×), ma al
floor (30–50 MHz) combacia già. Il **rumore bianco** riempie la banda *sbagliata*
(alta-f) e rovina il floor (0.18 = 5× troppo). Un **rise più veloce** (~250–350 ns
invece dei 528 ns fittati) riempie esattamente la banda giusta e porta la
roughness (`dy`-std) da 7.0 a ~8.3.

**Perché il fit aveva sbagliato il rise:** le metriche ACF (pesata uniforme su 500
lag) e PSD-Wasserstein (su spettro *normalizzato*, distanza broad) **sotto-pesano
la banda media / i lag corti** → il rise era mal vincolato e usciva troppo lento.
Stesso identico meccanismo per cui prima usciva troppo rumore (§6 REPORT).

**Fix implementato:** aggiunto all'obiettivo un termine sulla **frazione di potenza
nella banda 0.3–8 MHz** (`_MID` in `fit_simulator.py`), che vincola direttamente il
rise. Rifit completo → **rise 528 → 322 ns**, `dy`-std 7.0 → 7.4 vs 8.3 reale,
ACF-1e ancora ✓. La morfologia delle serie temporali ora combacia. *(Un tentativo
col rapporto di von Neumann lag-1 non funziona: la MSSD di culoculo è dominata dal
rumore, che confonde il termine — la frazione di potenza in banda è più pulita.)*

**Lezione generale:** per matchare la **forma d'onda** (non solo gli spettri
integrati) serve una metrica sensibile alla scala fine. Qui: potenza in banda media.

---

## 3. Test dell'idea migliore: level-crossing (Rice/Roessl) come stima di λ

Rate di attraversamenti verso l'alto della soglia `u`, su dati simulati (forma
preamp), vs λ vero:

| λ vero | N(0)/λ | N(0) [Hz] |
|---|---|---|
| 5×10⁴ | 54 | 2.7×10⁶ |
| 2×10⁵ | 5.4 | 1.1×10⁶ |
| 1×10⁶ | 0.22 | 2.2×10⁵ |
| 5×10⁶ | 0.05 | 2.4×10⁵ |
| 2×10⁷ | 0.01 | 2.2×10⁵ |

**Risultato:** a **basso** rate `N(u)≈λ` (ogni impulso attraversa la soglia una
volta → conta gli eventi). In **pileup** il mean-crossing rate **satura** a ~2.2×10⁵
Hz *indipendente da λ*: è la **frequenza RMS della forma** `(1/2π)√(λ₂/λ₀)`, cioè
misura la *forma d'impulso*, non il rate. Stesso muro del pileup dei cumulanti.

**Conclusione onesta:** il level-crossing **non è un proiettile d'argento** per il
nostro regime (anode pileup profondo). MA:
- è una **misura di forma indipendente e robusta** (la freq RMS ≈ 220 kHz per
  culoculo cross-controlla il rise+fall fittati) — cheap e vale la pena aggiungerla;
- in pileup *moderato* (culoculo) lo **spettro dei crossing** (rate vs soglia)
  contiene informazione di λ oltre alla varianza — è la parte del forward-model di
  Roessl che potrebbe battere i cumulanti (κ₃ rumoroso). Vale un test dedicato se
  serve spingere culoculo.

---

## 4. Cosa vale la pena fare (priorità)

1. **[fatto]** metrica banda-media nel fit → morfologia corretta (rise ~360 ns).
2. **Prior SER da Personick** invece della scansione cieca: mettere `F=⟨A²⟩/⟨A⟩²`
   nel range fisico di un PMT (F≈1.1–1.5, cioè CV≈0.3–0.7) → stringe il fattore ~6
   sul rate a ~×1.5.
3. **Forward-model di level-crossing alla Roessl** per culoculo (pileup moderato):
   fit dello *spettro dei crossing* N(u) vs soglia — informazione di λ non-varianza,
   non contaminata da κ₃. Da testare se il rate di culoculo deve essere pinnato meglio.
4. Il muro del pileup dell'anode (λ~10⁸, gaussiano) **non si supera** con nessuna di
   queste: serve un run a rate più basso o un pedestal/dark (REPORT §9).
