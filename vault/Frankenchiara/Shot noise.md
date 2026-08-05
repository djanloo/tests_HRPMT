---
type: nota
project: frankenchiara
updated: 2026-08-04
tags: [tipo/nota, progetto/frankenchiara]
---

# Shot noise: il modello di tutto

Il modello di tutto il lavoro è uno solo, e va imparato bene perché è il pavimento
su cui poggia il resto. Il segnale è una **sovrapposizione di impulsi identici, che
arrivano a tempi casuali**:

$$ y(t) = \sum_k A_k\, h(t - t_k) + n(t) $$

I quattro pezzi:

- **$t_k$** — i tempi d'arrivo degli eventi. Sono un **processo di Poisson** di rate
  **λ**: in media λ eventi al secondo, ma con i tempi tra un evento e il successivo
  casuali (esponenziali). È l'ipotesi naturale per decadimenti radioattivi
  indipendenti.
- **$A_k$** — la "carica" del k-esimo evento (∝ all'energia depositata). È casuale:
  eventi diversi depositano energie diverse, e il PMT stesso ha una fluttuazione di
  gain. La sua distribuzione si chiama **SER** (*single-electron response*) o
  spettro di ampiezza — vedi [[Spettro di ampiezza]].
- **$h(t)$** — la **forma del singolo impulso**. Non è la risposta dell'elettronica: la
  catena di lettura è ~260× più veloce del τ osservato, quindi $h$ **è il decadimento della
  scintillazione del NaI** (230 ns) — vedi [[Catena di lettura]]. Per l'anodo si modella come
  ~esponenziale a un polo; per il preamp di carica è un bi-esponenziale (rise + fall). Gli
  integrali di forma $I_n = \int h^n dt$ compaiono in ogni cumulante.
- **$n(t)$** — il rumore elettronico additivo (piccolo, sottodominante).

Questo oggetto ha un nome in letteratura: **shot noise**, o **processo di Poisson
filtrato**, o **compound Poisson**. La parola "compound" ("composto") indica proprio
che a ogni arrivo di Poisson è associata una marca casuale $A_k$.

## I protagonisti, per nome

- **λ (lambda) — il rate.** Numero di eventi al secondo che arrivano al rivelatore.
  "Evento" = un decadimento della sorgente che deposita energia → scintillazione →
  fotoelettroni. È la grandezza che vogliamo perché, a energia fissa, **la dose è
  proporzionale a λ** (più eventi al secondo = più radiazione). Ordine di grandezza
  qui: da ~0.2 a ~50 milioni di conteggi al secondo (Mcps).

- **$A_k$ e l'energia.** L'ampiezza del singolo evento, proporzionale all'energia
  depositata. La distribuzione delle $A_k$ entra solo attraverso i suoi momenti
  $\langle A^n\rangle$. L'**energia media per evento** è ciò che, moltiplicato per λ,
  dà la dose.

- **dose** $\dot H = k\,\lambda\,\langle E\rangle$ — rate × energia media × fattore
  di conversione. L'obiettivo finale.

Manca un protagonista, il **gain g**, che è il guaio: sta in
[[Statistiche gain-free]] perché è lì che diventa un problema operativo.

## Un punto che confonde spesso

Il segnale sembra "rumore colorato / autocorrelato". Verrebbe da pensare a un rumore
additivo con struttura. **Non è così**: la struttura temporale (l'autocorrelazione)
nasce dal **filtro $h$**, non da $n(t)$. Ogni impulso dura ~τ, quindi due campioni
distanti meno di τ sono correlati semplicemente perché appartengono spesso allo
stesso impulso. La PSD che si osserva (Lorentziana per l'anodo, più ripida per il
preamp) è esattamente $|H(f)|^2$ = il modulo quadro della trasformata di $h$.

> Il "rumore" **è il processo stesso**. Il rumore elettronico additivo esiste, ma è
> sottodominante.

## Da qui in avanti

- [[Cumulanti e Campbell]] — lo strumento matematico che trasforma il modello in
  equazioni risolvibili
- [[Pile-up e occupancy]] — il numero adimensionale che decide quanta informazione
  sopravvive
- [[Simulazione SDE]] — il modello messo a generare forme d'onda
- [[Punto di partenza]] — il documento originale che proponeva questa direzione
