---
type: nota
project: frankenchiara
updated: 2026-08-03
tags: [tipo/nota, progetto/frankenchiara]
---

# Lo spettro di ampiezza P(A)

La distribuzione delle ampiezze di singolo evento — la SER (*single-electron response*,
strumentale) o lo spettro di energia per evento. È il **sistematico dominante di tutto
il progetto**, ed è l'unica cosa che non si riesce a misurare da questi dati.

## Perché conta

Gli $A_k$ sono le cariche/ampiezze di singolo evento. Da [[Cumulanti e Campbell]], ogni
cumulante è un momento: $\kappa_n = \lambda\langle A^n\rangle I_n$. I rapporti cancellano
λ e il guadagno → i **momenti normalizzati** $m_n = \langle A^n\rangle/\langle A\rangle^n$
sono la *forma* di $P(A)$.

Questi momenti entrano **direttamente** nelle stime di rate:
$\lambda = (\kappa_2^2/\kappa_4)(m_4 S_4)/(m_2^2 S_2^2)$ — cioè $m_4$ **linearmente**.
Non li misuriamo: li assumiamo. Da qui il **sistematico ~×6** dichiarato in
[[Limiti]], che è $m_2$ = l'*excess noise factor* $F = \langle A^2\rangle/\langle A\rangle^2$
di Personick.

## Il tentativo fallito: estrarre P(A) dai cumulanti

`amplitude_ser.py`. Esiste una combinazione λ-indipendente che dà la larghezza SER:

$$ \frac{\kappa_2\kappa_4}{\kappa_3^2}=\frac{\langle A^2\rangle\langle A^4\rangle}{\langle A^3\rangle^2}\cdot\frac{I_2I_4}{I_3^2},\qquad \text{Gamma: }\frac{\langle A^2\rangle\langle A^4\rangle}{\langle A^3\rangle^2}=\frac{1+3\,\mathrm{CV}^2}{1+2\,\mathrm{CV}^2} $$

**In pratica la forma di P(A) NON è estraibile da dati in pileup.** Serve il cumulante
*dispari* $\kappa_3$, che in pileup è

(a) piccolo — il segnale gaussianizza, $\kappa_3 \to 0$ come $\sim 1/\sqrt{\lambda\tau}$;
(b) con varianza di stima enorme.

E stando **al quadrato al denominatore**, l'errore esplode.

**Dimostrato, non supposto:** anche una simulazione pulita con $10^4$ record e CV nota
recupera male (`CV=0.8→1.1, 0.5→0.42, 0.3→fallisce`); sui dati veri è inutilizzabile.
il FAST (gaussiano) non dà nulla sulla forma; il CSP neppure
($N_\text{eff}\sim 7$ + artefatti).

È un risultato negativo che vale la pena aver dimostrato: chiude una strada che
sembrava aperta.

## Cosa resta misurabile

- $\lambda$ (cumulanti pari, [[Stima del rate dai cumulanti]]);
- $\lambda\langle A^2\rangle$ (la varianza);
- con un pedestal, l'**energia media per evento** $\langle A^2\rangle/\langle A\rangle$
  (Campbelling, rate-indipendente) — è η di [[Statistiche gain-free]].

L'**energia assoluta** (keV) richiede calibrazione di guadagno; lo **spettro P(A)
completo** richiede **eventi risolti** (run a basso rate/dark → istogramma delle aree
dei singoli impulsi).

Nota: il λ~10⁸ Hz dell'anode suggerisce che lì gli "eventi" siano **fotoelettroni
singoli** (P(A)=SER), mentre il CSP (preamp, ~1 MHz) è più a livello di
evento/energia.

## La via d'uscita: assumere uno spettro vero invece di una Gamma

Se P(A) non si estrae dai dati, tanto vale assumerne uno **realistico** anziché una
Gamma. Da agosto 2026 il simulatore accetta uno spettro di ampiezza empirico
(`energy_spectrum.py`): spettri misurati dal CAEN DDE, più Cs137/Am241 su NaI
modellati da fisica nota. Dettagli in [[Simulazione SDE]].

Il numero che giustifica il lavoro: $m_4$ vale **3.28** per una Gamma con CV 0.5 e
**117** per l'Eu152 su HPGe — un fattore **36** su una quantità che entra linearmente
nel rate. La scansione della sistematica in `mssd_cumulant_estimate` esplora
`cv ∈ {0, 0.3, 0.5, 1.0}`, cioè *dentro la famiglia Gamma*: non può contenere quel
fattore.

Il run **Am-241** è l'unico a impulsi risolti ([[Rivelatore e dati]]): è quindi l'unico
dato in mano da cui P(A) si può misurare **direttamente**. Fatto in
[[Misure a basso rate]] — con l'avvertenza che l'energia di un evento è la sua *carica*, non
l'altezza di un picco.
Vedi [[Backlog]].
