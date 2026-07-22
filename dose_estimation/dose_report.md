# Stima della dose dai segnali PMT — pipeline finale

**Il dato finale.** Dalla sola forma statistica del segnale digitizzato (nessun
pedestal, nessun dark run, nessuna correzione di gain) si stima la **dose rate**
entro un **fattore ×1.24 mediano (×1.98 massimo)** su **2.5 decadi** (616→28100 µSv/h,
Cs-137), in **leave-one-out**. Lo stimatore usa **una sola statistica gain-free**, la
**skewness**; l'energia si legge da un secondo rapporto gain-free, $\eta=\text{Var}/\text{Msd}$.

| dose vera [µSv/h] | dose stimata (LOO) | fattore |
|---|---|---|
| 616 | 602 | ×1.02 |
| 889 | 812 | ×1.09 |
| 7900 | 15680 | ×1.98 |
| 17990 | 14490 | ×1.24 |
| 28100 | 17650 | ×1.59 |

![risultato](dose_result.png)

### Come va letto il ×1.24 — il principio del leave-one-out (LOO)

La calibrazione ha 2 parametri ($a,b$) e i run Cs-137 sono solo 5. Se fittassi $a,b$
su tutti e 5 e poi misurassi l'errore *sugli stessi 5*, il numero sarebbe
**ottimistico e circolare**: sto misurando quanto bene una retta ci passa in mezzo,
non quanto bene predice una misura *nuova*.

Il **leave-one-out** evita questo. Per ogni run $i$ (dei 5):

1. **butto via** il run $i$;
2. **ri-fitto** la calibrazione $\ln\dot H=a+b\,\text{asinh}(\gamma_1)$ sui **4 run rimasti**;
3. **predìco** la dose del run $i$ con quella calibrazione — che **non ha mai visto** $i$;
4. confronto stima vs dose vera → fattore d'errore.

Ripetuto per tutti e 5 (5 ri-fit indipendenti), dà il **fattore ×1.24 mediano /
×1.98 massimo**. È un errore **fuori-campione**: la stima onesta di quanto sbaglierei
su una **misura mai usata per tarare**. È il numero che conta per l'uso reale, ed è
per questo che lo metto come risultato principale invece dell'errore di fit in-sample
(che sarebbe più basso ma bugiardo).

Note: (i) solo la calibrazione del **rate** è in LOO (Cs-137, energia fissa, 5 punti su
2.5 decadi); l'Am-241 sta fuori (regime a impulsi risolti, §5). (ii) 5 punti sono pochi:
l'LOO su così pochi dati è la cosa più onesta possibile *con questi dati*, ma resta un
campione piccolo — per questo lo affianco alla validazione sintetica a verità nota (§7),
dove i punti sono tanti e la dose vera è imposta da me, non misurata.

---

## 1. Idea (rate × energia → dose), con statistiche gain-free

$\dot H = k\,\lambda\,\langle E\rangle$ (dose = rate × energia media × conversione).
Il PMT ha **gain che deriva e collassa col rate** (partitore passivo, vedi
`../target_test/gain_model_proposal.md`): quindi **media, Var, Msd sono inutilizzabili**
(portano $g$ o $g^2$, non-monotòne nella dose). Si usano **solo rapporti di cumulanti
in cui il gain si cancella**:

| ingrediente | proxy (gain-free) | teoria |
|---|---|---|
| **rate** $\lambda$ | skewness $\gamma_1$ | $\gamma_1=\kappa_3/\kappa_2^{3/2}\propto 1/\sqrt{\lambda\tau}$ (occupancy) |
| **energia** $\langle E\rangle$ | $\eta=\text{Var}/\text{Msd}$ | $\propto \langle A^2\rangle/\langle A\rangle$ |
| **regime** | kurtosi $\gamma_2$ | $\propto 1/(\lambda\tau)$; + stabilità di $\gamma_1$ |

Nessuna correzione di gain a runtime: il ladder model serve a **spiegare perché**
evitare le statistiche gain-dipendenti, non come correzione.

## 2. La pipeline (deployabile)

1. **Feature** dal blocco di forme d'onda (media per-record tolta): $\gamma_1$ (skew),
   $\eta=\text{Var}/\text{Msd}$, $\gamma_2$ (kurt). Tutte **gain-free e senza pedestal**.
2. **Regime** dalla kurtosi + stabilità di $\gamma_1$ (split a metà dei record):
   - $\gamma_1$ instabile / $\gamma_2\!\gg\!1$ → **bassissimo rate, impulsi risolti → CONTA gli impulsi** (fuori dallo stimatore statistico; è il caso Am-241 qui).
   - $\gamma_2\gtrsim1$ → rate moderato; $\gamma_2\approx0$ → alto rate (pileup gaussiano).
3. **Rate**: $\lambda$ da $\gamma_1$ via calibrazione.
4. **Energia**: $\langle E\rangle$ da $\eta$.
5. **Dose**: $\ln\dot H = a + b\,\text{asinh}(\gamma_1)\;[+\,c\ln\eta$ se l'energia è ignota$]$.

**Calibrazione (questi dati):**
$$\ln(\dot H[\mu\text{Sv/h}]) = 9.685 - 2.158\,\text{asinh}(\gamma_1)\qquad(\text{Cs-137})$$
$$\ln(\langle E\rangle[\text{keV}]) = 1.38 + 1.17\,\ln(\eta)$$
(in `calibration.json`; codice in `dose_pipeline.py`).

## 3. Rate ed energia estratti

| nuclide | dose | $\gamma_1$ | $\eta$ | rate stimato | energia stimata (vera) |
|---|---|---|---|---|---|
| Am-241 | 94 | +14.4* | 13.2 | *conta impulsi* | 81 keV (59.5) |
| Cs-137 | 616 | +2.17 | 65.8 | 1.1 Mcps | 531 keV (662) |
| Cs-137 | 889 | +1.83 | 96.1 | 1.6 Mcps | 826 keV (662) |
| Cs-137 | 7900 | +0.10 | 110 | 24 Mcps | 967 keV (662) |
| Cs-137 | 17990 | +0.02 | 76 | 29 Mcps | 629 keV (662) |
| Cs-137 | 28100 | −0.13 | 46 | 39 Mcps | 350 keV (662) |

\*γ1 di Am-241 instabile (h1 +1.6 vs h2 +24.8) → regime a impulsi risolti. Rate
assoluto da calibrazione Target (1 Mcps ↔ 540 µSv/h, Cs-137 2×2″ NaI).

## 4. Perché è robusto (e "commercializzabile")

- **Gain-free by design**: skewness ed $\eta$ sono rapporti di cumulanti → il gain
  (che deriva/collassa) **si cancella**. Funziona anche sul run 616 a **HV diversa**.
- **Niente dark run / pedestal / correzione di gain**: una sola statistica per la dose.
- **Stabile** nel regime continuo (Cs: $\gamma_1,\eta$ coincidono tra metà dei record).
- **Autodiagnosi del regime**: la stessa pipeline sa quando è a bassissimo rate
  (γ1 instabile) e dice "conta gli impulsi".

## 5. Limiti onesti

- **Energia rozza** (~×1.5): $\eta$ dà l'ordine di grandezza (Am≈81 vs 59.5; Cs
  350–967 vs 662), sufficiente per il fattore di conversione, non per spettroscopia.
- **Saturazione ad alto rate**: $\gamma_1\to0$ in pileup profondo → il punto peggiore
  (7900, ×1.98) è alla transizione; oltre ~50 Mcps la sensibilità cala.
- **Calibrazione per tubo/HV**: i coefficienti $a,b$ dipendono da forma d'impulso
  ($\tau$) e SER, quindi vanno ri-tarati per un altro rivelatore; ma la **struttura
  gain-free è trasferibile** (una singola sorgente nota a 2–3 rate basta a tararli).
- **Validazione**: rate su 1 energia (Cs, 2.5 decadi, LOO); energia su 2 nuclidi.
- **Bassissimo rate**: fuori regime → pulse counting (già segnalato dalla pipeline).

## 6. Un solo miglioramento "gratis" (non richiede altri dati fisici, solo un dark run)

Con un **dark/pedestal run** (una volta sola, non è "altro segnale") si sbloccherebbe
$\lambda\propto\text{mean}^2/\text{Var}$ (gain-free, DC): un rate assoluto che **non
satura** in pileup profondo, dove la skewness invece si appiattisce. Migliorerebbe
solo l'estremo alto-rate; per il range qui coperto **la skewness basta**.

## 7. Validazione su dati sintetici (verità nota)

L'LOO sui 5 run reali dice che la pipeline è consistente, ma la dose vera lì è
misurata, non imposta. Per un test a **verità perfettamente nota** genero forme
d'onda col simulatore pe-level (`../target_test/pe_synth.py`, processo di Cox
γ→pe con decadimento di scintillazione), a λ **imposto da me**.

**Fit grossolano ai dati nuovi.** Con i soli parametri fisici $\tau_{\text{scint}}=230$ ns
(NaI) ed $\eta_{pe}=3500$ (Cs-137 662 keV), lo **skew sintetico riproduce quello reale**
ai λ noti dei run (pannello A: i quadrati reali cadono sulla curva sintetica):

| dose | skew reale | skew sintetico |
|---|---|---|
| 616 | 2.17 | 1.86 |
| 889 | 1.83 | 1.54 |
| 7900 | 0.10 | 0.46 |
| 17990 | 0.02 | 0.16 |
| 28100 | −0.13 | −0.06 |

(L'$\eta$ assoluto — dimensione energia — non è finemente tarato: sim ~18 vs reale
~66. Per la dose Cs l'energia è fissa e conta lo skew, che invece combacia. Vedi §5.)

**Recupero della dose.** Applicando la calibrazione (fittata sul reale) a forme d'onda
sintetiche a λ noto su tutto il range, la dose stimata segue quella vera entro
**×1.35 mediano (×1.60 max)** — coerente con l'LOO reale (×1.24/×1.98):

![validazione sintetica](synth_validation.png)

I pannelli in basso mostrano le timeseries sintetiche: a **~1.2 Mcps** impulsi
esponenziali quasi risolti (skew grande, coda positiva); a **~50 Mcps** fuzz
gaussiano da pileup (skew→0) — la stessa transizione dei dati reali.

**Cosa conferma:** (i) il modello a shot-noise filtrato riproduce la statistica reale
col solo occupancy $\lambda\tau$; (ii) la relazione skew↔rate↔dose regge su verità
nota, quindi la calibrazione non sta solo interpolando i 5 punti reali;
(iii) skew→0 in pileup profondo è reale, non un artefatto → conferma il limite di §5.
Riproducibile: `python synth_validation.py`.

---
**File:** `dose_pipeline.py` (pipeline + calibrazione + LOO + figura), `calibration.json`,
`dose_result.png`, `synth_validation.py`, `synth_validation.png`.
