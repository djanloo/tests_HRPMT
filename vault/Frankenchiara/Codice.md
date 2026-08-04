---
type: nota
project: frankenchiara
updated: 2026-08-03
tags: [tipo/nota, progetto/frankenchiara]
---

# Il codice

Mappa file → cosa fa, per il repo `djanloo/tests_HRPMT`. Sostituisce la nota
*Architettura* del template, che descriveva un servizio e non un repo di script di
analisi.

## Modello e simulazione

| file | cosa fa |
|---|---|
| `simulate_pmt.py` | simulatore shot-noise a convoluzione (somma esatta di impulsi + jump-SDE a un polo) + self-check |
| `sde_pulse_sim.py` | simulatore SDE a due poli, discretizzazione esatta `expm`, unità fisiche (ADC) + self-check |
| `energy_spectrum.py` | spettro di ampiezza empirico: caricamento DDE (CSV + N42 XML), modello NaI per Cs137/Am241, aggregazione esatta delle marche + self-check |
| `spectra/` | gli istogrammi di ampiezza (CAEN DDE DT4800 `examples/spectra`) |

Vedi [[Simulazione SDE]].

## Fit dei parametri

| file | cosa fa |
|---|---|
| `fit_simulator.py` | fit Optuna MSM per `simulate_pmt` (ACF + PSD-Wasserstein + banda media + CV + kurtosi) → `fit_results.json` |
| `sde_fit.py` | fit Optuna per `sde_pulse_sim`, parametri in unità fisiche → `sde_fit_results.json` |
| `analisi_1.py` | Welch / coerenza / filtri di partenza |

Vedi [[Fit dei parametri]].

## Stima

| file | cosa fa |
|---|---|
| `mssd_cumulant_estimate.py` | stima rate/energia da MSSD + cumulanti pari, con validazione a verità nota |
| `amplitude_ser.py` | tentativo (fallito, e dimostrato tale) di estrarre P(A) dai cumulanti |
| `pha_lowrate.py` | PHA offline sui run a impulsi risolti: integrazione di carica su gate + veto di pile-up |
| `signal_stats.py`, `plot_signals.py` | statistiche e grafici di supporto |
| `target_test/target_method.py` | metodo Target sui 6 run reali |
| `target_test/pe_synth.py` | simulatore a livello di fotoelettrone (verità nota) |
| `dose_estimation/dose_pipeline.py` | pipeline di dose finale + calibrazione + LOO |
| `dose_estimation/synth_validation.py` | validazione della dose su verità nota |

Vedi [[Stima del rate dai cumulanti]], [[Metodo Target]], [[Stima della dose]],
[[Validazione a verità nota]], [[Misure a basso rate]].

## Modello del gain

| file | cosa fa |
|---|---|
| `target_test/gain_ladder.py` | modello ladder del partitore (KCL accoppiato, N equazioni) |
| `target_test/gain_ladder_fit.py` | fit del ladder ai 4 run a stessa HV |

Vedi [[Gain ladder]].

## Dipendenze non ovvie

`h5py` (per i run `.h5`), `optuna` (per i fit), `scipy`, `numpy`, `matplotlib`.

## Dati

| file | cosa contiene |
|---|---|
| `data/anode_waveforms/*.h5` | **il dataset ufficiale**: i 6 run a dose nota (Am-241 + 5× Cs-137), 10⁴×2000 a 100 MS/s, ramo FAST |
| `csp.npy` | caratterizzazione del ramo CSP (1000×2000) — solo riferimento, nessun risultato ci passa |
| `data/2847 High Dose Rate Rev. 2.pdf` | documentazione del setup |
| `US20210055429A1.pdf` | brevetto del metodo Target |

Vedi [[Rivelatore e dati]], [[Hardware]] e [[Catena di lettura]].

## Risultati salvati

`fit_results.json`, `sde_fit_results.json`, `target_test/target_results.json`,
`dose_estimation/calibration.json`.

## Le figure

Le figure nel vault stanno in `img/`, **copiate** dalla root del repo perché Obsidian non
renderizza immagini fuori dal vault. **Sono copie, non si aggiornano da sole**: dopo aver
rigenerato i grafici con gli script, ricopiale con

```sh
cp signals.png independence_test.png model_validation.png fit_validation.png \
   energy_spectrum.png pha_am241.png dose_estimation/*.png target_test/*.png \
   vault/Frankenchiara/img/
```

## Self-check

Gli script principali hanno un `__main__` che verifica la logica non banale e fallisce
con un assert se si rompe:

```sh
python simulate_pmt.py        # ACF e CV riproducono i valori misurati
python sde_pulse_sim.py       # rise/fall, sigma di rumore, scaling della varianza
python energy_spectrum.py     # momenti, spettro ricostruito a basso rate, Campbell
python pha_lowrate.py         # PHA Am-241: fotopicco, risoluzione, stabilita' al veto
```

**Nota**: `simulate_pmt.py` passa il self-check ma crasha nel blocco plot finale
(`KeyError: 'FAST'`) perché `fit_results.json` ora ha chiavi
`signals/run_Cs-137_*.h5`. Vedi [[Backlog]].
