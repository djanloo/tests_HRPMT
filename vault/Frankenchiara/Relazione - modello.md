---
type: nota
project: frankenchiara
updated: 2026-07-23
tags: [tipo/nota, progetto/frankenchiara]
---

# Relazione — il modello e i cumulanti

Parte di [[RELAZIONE]].

## 3. Il modello: rumore shot (Poisson filtrato)

Il modello di tutto il lavoro è uno solo, e va imparato bene perché è il
pavimento su cui poggia il resto. Il segnale è una **sovrapposizione di impulsi
identici, che arrivano a tempi casuali**:

$$ y(t) = \sum_k A_k\, h(t - t_k) + n(t) $$

I quattro pezzi:

- **$t_k$** — i tempi d'arrivo degli eventi. Sono un **processo di Poisson** di
  rate **λ**: in media λ eventi al secondo, ma con i tempi tra un evento e il
  successivo casuali (esponenziali). È l'ipotesi naturale per decadimenti
  radioattivi indipendenti.
- **$A_k$** — la "carica" del k-esimo evento (∝ all'energia depositata). È
  casuale: eventi diversi depositano energie diverse, e il PMT stesso ha una
  fluttuazione di gain. La sua distribuzione si chiama **SER** (*single-electron
  response*) o spettro di ampiezza.
- **$h(t)$** — la **forma del singolo impulso** (risposta del rivelatore +
  elettronica). Per l'anodo è ~esponenziale a un polo; per il preamp di carica è
  un bi-esponenziale (rise + fall).
- **$n(t)$** — il rumore elettronico additivo (piccolo, sottodominante).

Questo oggetto ha un nome in letteratura: **shot noise**, o **processo di
Poisson filtrato**, o **compound Poisson**. La parola "compound" ("composto")
indica proprio che a ogni arrivo di Poisson è associata una marca casuale $A_k$.

**Un punto che confonde spesso.** Il segnale sembra "rumore colorato /
autocorrelato". Verrebbe da pensare a un rumore additivo con struttura. **Non è
così**: la struttura temporale (l'autocorrelazione) nasce dal **filtro $h$**, non
da $n(t)$. Ogni impulso dura ~τ, quindi due campioni distanti meno di τ sono
correlati semplicemente perché appartengono spesso allo stesso impulso. La PSD
che si osserva (Lorentziana per l'anodo, più ripida per il preamp) è esattamente
$|H(f)|^2$ = il modulo quadro della trasformata di $h$. Il "rumore" *è il
processo stesso*.

---

## 4. I cumulanti e il teorema di Campbell

Qui introduciamo lo strumento matematico che fa girare tutto. Serve un minuto
di pazienza, poi diventa un martello universale.

### Cosa sono i cumulanti

Data una variabile casuale, i **cumulanti** $\kappa_n$ sono un modo alternativo
(ai momenti) di descriverne la distribuzione. I primi quattro sono facce note:

| cumulante | è | forma normalizzata |
|---|---|---|
| $\kappa_1$ | la **media** | — |
| $\kappa_2$ | la **varianza** | — |
| $\kappa_3$ | lega all'**asimmetria** (skewness) | $\gamma_1 = \kappa_3/\kappa_2^{3/2}$ |
| $\kappa_4$ | lega alla **"codosità"** (excess kurtosis) | $\gamma_2 = \kappa_4/\kappa_2^{2}$ |

Due proprietà rendono i cumulanti speciali, e sono le uniche due che useremo:

1. **Additività su somme indipendenti.** Il cumulante della somma di variabili
   indipendenti è la somma dei cumulanti. (I momenti no: la varianza sì, ma i
   momenti terzi/quarti si mescolano.)
2. **Una gaussiana ha $\kappa_n = 0$ per ogni $n \ge 3$.** Questo è cruciale:
   $\kappa_3, \kappa_4$ **misurano quanto una distribuzione è lontana dall'essere
   gaussiana**. Teniamolo a mente per il §6.

### Il teorema di Campbell

Applicando l'additività al nostro shot noise (una somma di tantissimi impulsi
indipendenti), si ottiene un risultato pulitissimo — il **teorema di Campbell**:

$$ \boxed{\;\kappa_n[y] = \lambda\,\langle A^n\rangle\, I_n\,,\qquad I_n = \int h(t)^n\,dt\;} $$

Ogni cumulante del segnale è il prodotto di tre fattori: il **rate λ**, il
**momento n-esimo dell'ampiezza** $\langle A^n\rangle$, e un **integrale di forma**
$I_n$ (una costante che dipende solo da $h$). Esplicitamente:

- $\kappa_1 = \lambda\langle A\rangle I_1$ → la **media** = corrente DC;
- $\kappa_2 = \lambda\langle A^2\rangle I_2$ → la **varianza** = potenza di fluttuazione;
- $\kappa_3 = \lambda\langle A^3\rangle I_3$, $\kappa_4 = \lambda\langle A^4\rangle I_4$, …

Un corollario che useremo: per $h$ esponenziale a un polo,
$h(t)=e^{-t/\tau}$, l'**autocovarianza** del processo è
$C(\Delta) = \lambda\langle A^2\rangle\frac{\tau}{2}e^{-|\Delta|/\tau}$ — cioè un
processo con ACF esponenziale, un **Ornstein–Uhlenbeck** guidato da Poisson. È
proprio ciò che si vede nell'anodo (τ ≈ 250 ns).

**Perché tutto questo è potente:** ogni statistica che sappiamo misurare (media,
varianza, skewness…) diventa una **equazione** in tre incognite fisiche (λ,
l'energia via $\langle A^n\rangle$, la forma via $I_n$). Misurando più
statistiche, mettiamo insieme un sistema e proviamo a invertirlo. Tutto il lavoro
è, in fondo, questo gioco di inversione — con l'accortezza di scegliere le
combinazioni giuste (§7).

---

