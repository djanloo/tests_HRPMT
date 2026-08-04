---
type: nota
project: frankenchiara
updated: 2026-07-23
tags: [tipo/nota, progetto/frankenchiara]
---

# I cumulanti e il teorema di Campbell

Lo strumento matematico che fa girare tutto. Serve un minuto di pazienza, poi
diventa un martello universale. Il modello a cui si applica è in [[Shot noise]].

## Cosa sono i cumulanti

Data una variabile casuale, i **cumulanti** $\kappa_n$ sono un modo alternativo (ai
momenti) di descriverne la distribuzione. I primi quattro sono facce note:

| cumulante | è | forma normalizzata |
|---|---|---|
| $\kappa_1$ | la **media** | — |
| $\kappa_2$ | la **varianza** | — |
| $\kappa_3$ | lega all'**asimmetria** (skewness) | $\gamma_1 = \kappa_3/\kappa_2^{3/2}$ |
| $\kappa_4$ | lega alla **"codosità"** (excess kurtosis) | $\gamma_2 = \kappa_4/\kappa_2^{2}$ |

Due proprietà rendono i cumulanti speciali, e sono le uniche due che useremo:

1. **Additività su somme indipendenti.** Il cumulante della somma di variabili
   indipendenti è la somma dei cumulanti. (I momenti no: la varianza sì, ma i momenti
   terzi/quarti si mescolano.)
2. **Una gaussiana ha $\kappa_n = 0$ per ogni $n \ge 3$.** Questo è cruciale:
   $\kappa_3, \kappa_4$ **misurano quanto una distribuzione è lontana dall'essere
   gaussiana**. È la chiave di [[Pile-up e occupancy]].

## Il teorema di Campbell

Applicando l'additività al nostro shot noise (una somma di tantissimi impulsi
indipendenti), si ottiene un risultato pulitissimo — il **teorema di Campbell**:

$$ \boxed{\;\kappa_n[y] = \lambda\,\langle A^n\rangle\, I_n\,,\qquad I_n = \int h(t)^n\,dt\;} $$

Ogni cumulante del segnale è il prodotto di tre fattori: il **rate λ**, il **momento
n-esimo dell'ampiezza** $\langle A^n\rangle$, e un **integrale di forma** $I_n$ (una
costante che dipende solo da $h$). Esplicitamente:

$$ \kappa_1 = \lambda\langle A\rangle I_1 + b,\quad
   \kappa_2 = \lambda\langle A^2\rangle I_2,\quad
   \kappa_3 = \lambda\langle A^3\rangle I_3,\quad
   \kappa_4 = \lambda\langle A^4\rangle I_4 $$

- $\kappa_1$ = la **media** = corrente DC (il $b$ è il pedestal, che sui nostri dati
  è perduto — vedi [[Limiti]]);
- $\kappa_2$ = la **varianza** = potenza di fluttuazione.

Un corollario che useremo: per $h$ esponenziale a un polo, $h(t)=e^{-t/\tau}$,
l'**autocovarianza** del processo è

$$ C(\Delta) = \lambda\langle A^2\rangle\frac{\tau}{2}e^{-|\Delta|/\tau} $$

cioè un processo con ACF esponenziale, un **Ornstein–Uhlenbeck** guidato da Poisson
composto. È proprio ciò che si vede nell'anodo (τ ≈ 250 ns), e la PSD corrispondente
è la Lorentziana osservata.

**Perché tutto questo è potente:** ogni statistica che sappiamo misurare (media,
varianza, skewness…) diventa una **equazione** in tre incognite fisiche (λ,
l'energia via $\langle A^n\rangle$, la forma via $I_n$). Misurando più statistiche,
mettiamo insieme un sistema e proviamo a invertirlo. Tutto il lavoro è, in fondo,
questo gioco di inversione — con l'accortezza di scegliere le combinazioni giuste
([[Statistiche gain-free]]).

## Come il gain entra nei cumulanti

Il gain $g$ del PMT **scala tutte le ampiezze**: $A_k \to g A_k$. Per Campbell,
$\kappa_n = \lambda\langle A^n\rangle I_n \to g^n\,\kappa_n$. Cioè:

$$ \text{media} \propto g,\quad \text{Var} \propto g^2,\quad \kappa_3 \propto g^3,\quad \kappa_4 \propto g^4 $$

Ogni cumulante porta una **potenza diversa** di $g$. Questo, lungi dall'essere un
problema, è la **chiave della soluzione**: basta costruire rapporti in cui le potenze
si elidono. Vedi [[Statistiche gain-free]].

## I momenti normalizzati $m_n$

Nelle formule di stima compare sempre la combinazione
$m_n = \langle A^n\rangle/\langle A\rangle^n$ — i **momenti normalizzati** della
distribuzione di ampiezza, cioè la sua *forma* a prescindere dalla scala. $m_2$ è
l'**excess noise factor** $F = \langle A^2\rangle/\langle A\rangle^2$ di Personick.

Questi numeri sono il sistematico dominante di tutto il lavoro: non li misuriamo, li
assumiamo. Storicamente da una Gamma con `ser_cv` fittato; da agosto 2026 anche da uno
spettro empirico ([[Simulazione SDE]]), dove $m_4$ può valere 36 volte tanto.
