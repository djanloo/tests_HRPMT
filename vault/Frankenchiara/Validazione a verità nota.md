---
type: nota
project: frankenchiara
updated: 2026-08-04
tags: [tipo/nota, progetto/frankenchiara]
---

# Validazione a verità nota

Come abbiamo verificato di non star sognando. Ogni affermazione del progetto è stata
controllata contro **verità nota**, perché su dati reali non conosciamo λ, energia e
gain in modo indipendente. Quattro livelli.

## (a) Simulatore coerente del segnale

`simulate_pmt.py` genera lo shot noise in due modi equivalenti — somma esatta di
impulsi, e integrazione della SDE a salti $dY = -\frac{Y}{\tau}dt + dJ$. Confronto
modello-vs-dati su autocorrelazione, PSD e distribuzione di potenza per record:

![[model_validation.png]]
*Modello (rosso) vs dati (nero): ACF, PSD e distribuzione di potenza per record
combaciano.*

Il FAST combacia su tutti e tre i piani, il CSP bene su potenza e
corner. Dettagli in [[Simulazione SDE]].

## (b) Fit quantitativo dei parametri

`fit_simulator.py`: invece di tarare a mano, i parametri (τ_rise, τ_fall, rate,
larghezza SER, rumore) sono fittati ai dati con *method of simulated moments*
(ottimizzatore Optuna, 500 trial/file). Il gain assoluto è degenere e esce dal conto
(tutte le metriche sono scale-free — di nuovo il tema gain-free).

![[fit_validation.png]]
*Fit Optuna vs dati: ACF, PSD (distanza di Wasserstein) e distribuzione di potenza.*

*(La "distanza di Wasserstein" è una misura di quanto due distribuzioni differiscono —
intuitivamente, il "lavoro" per spostare una nell'altra; qui confronta la PSD misurata
con quella simulata.)*

Una lezione tecnica utile: per far combaciare la **forma d'onda** (non solo gli spettri
integrati) è servita una metrica sensibile alla **scala fine** (la frazione di potenza
in banda media 0.3–8 MHz), altrimenti il fit smussava troppo il rise-time. Il racconto
completo è in [[Fit dei parametri]].

## (c) Simulatore a livello di fotoelettrone

`target_test/pe_synth.py` — **il più importante per validare le stime**: un processo di
Cox/branching (Poisson di eventi → η fotoelettroni ciascuno → decadimento di
scintillazione → shot pe → gain + rumore), con **λ, energia e gain imposti da noi**.

Qui abbiamo smontato e verificato ogni affermazione su cosa è gain-free e cosa no:

![[pe_synth_validation.png]]
*η è costante sotto scansione di gain, λ̂ scala come g², mean²/Var recupera λ anche col
gain-crash iniettato.*

- scansione di **gain** (λ, η fissi): **η costante**, $\hat\lambda \propto g^2$ →
  conferma cosa è gain-free e cosa no ([[Metodo Target]]);
- scansione di **λ** (gain fisso): mean, Var, Msd, λ̂ tutti ∝ λ → il metodo Target
  funziona *quando il gain è fisso*;
- **gain-crash iniettato** $g(\lambda) = g_0/(1+\lambda/\lambda_c)$: Msd, λ̂, media
  diventano **non-monotoni** (salgono e poi scendono, *come i dati reali!*), ma
  **`mean²/Var` recupera λ** perché il gain si cancella esattamente.

> Questa è la prova regina che la strada gain-free è quella giusta.

## (d) Validazione sintetica della pipeline di dose

`dose_estimation/synth_validation.py`: rigenerando forme d'onda a λ noto su tutto il
range e applicando la calibrazione fittata sul reale, la dose stimata segue la vera
entro **×1.35 mediano (×1.60 max)** — coerente con l'LOO reale (×1.24/×1.98). Conferma
che la calibrazione non sta solo interpolando 5 punti fortunati.

![[synth_validation.png]]
*La stima segue la verità nota su tutto il range; in basso le timeseries dai ~1.2 Mcps
(impulsi quasi risolti) ai ~50 Mcps (fuzz gaussiano).*

Vedi [[Stima della dose]] per il risultato che questo valida.

## (e) Il quinto livello: il dato reale risolto

Gli altri quattro validano contro verità *imposta da noi*. Il PHA sull'Am-241
([[Misure a basso rate]]) è l'unico confronto contro una verità **fisica esterna**: il
fotopicco a 59.541 keV e il decadimento del NaI a 230 ns non li abbiamo scelti noi. È lì che
il modello di risoluzione si è confermato (9.1% implicito contro 8% assunto) e che il modello
di continuo si è rotto.

## Il livello che manca

Tutte e quattro le validazioni assumono la distribuzione di ampiezza — storicamente una
Gamma. Quella assunzione **non è validata contro una misura**, ed è il sistematico
dominante. Vedi [[Spettro di ampiezza]] e [[Backlog]].
