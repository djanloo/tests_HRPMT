# Reading list — stima di rate/ampiezza da processi compound-Poisson (pile-up)

Recuperata dagli agenti di ricerca (la deep-research è morta per limite di spesa
API, non per merito). URL raccolti prima del blocco; titoli annotati a memoria/
riconoscimento, da verificare. Raggruppata per famiglia di metodo.

## Shot noise / Campbell / decompounding
- Lowen & Teich, *Power-Law Shot Noise*, IEEE IT 1990 — https://www3.nd.edu/~mhaenggi/ee87021/Lowen-1990-Information%20Theory.pdf
- *Non-Parametric Decompounding of Pulse Pile-Up Under Gaussian Noise With Finite Data Sets* (molto pertinente: recupero della distribuzione dei salti di un compound-Poisson dalla somma) — https://www.researchgate.net/publication/340014103
- *Poisson Process and Shot Noise* (rassegna) — https://www.researchgate.net/publication/335830450
- Variance-stabilizing transforms per intensity estimators di shot noise — https://www.researchgate.net/publication/372671705
- Cambridge, *Review on Poisson, Cox, Hawkes, shot-noise-Poisson and dynamic contagion processes* — https://www.cambridge.org/core/journals/annals-of-actuarial-science/article/abs/165DE537F3835621CA67311342BAA281

## Higher-order statistics / cumulanti / polispettri
- *Factorial cumulants reveal interactions in counting statistics* — https://arxiv.org/pdf/1507.04579
- Noise intensity-intensity correlations e 4° cumulante dello shot noise foto-assistito — https://www.researchgate.net/publication/257530079
- Signal processing with higher-order spectra (lecture CMU) — https://www.cs.cmu.edu/~pmuthuku/mlsp_page/lectures/Signal_proc_with_higher_order_spectra.pdf
- Rosenblatt, cumulant / higher-order / poly-spectra — https://www.researchgate.net/publication/241008888

## Fotoni / ottica / HBT / photon counting
- Shot-noise-intensity vs photon counting: equivalenza (Zmuidzinas vs Lieu) — https://arxiv.org/pdf/1501.03219
- Hanbury-Brown–Twiss con fotoni interagenti — https://www.researchgate.net/publication/45646555
- Shot noise in sistemi mesoscopici (rassegna) — https://www.researchgate.net/publication/355286101
- arXiv (photon statistics / flusso): 1609.01607, 1805.01262, 0711.0719, 1410.5930

## Neuroscienze — fluctuation/noise analysis, quantal & rate
- *A Method to Estimate Synaptic Conductances From Membrane Potential Fluctuations* — https://www.researchgate.net/publication/8568568 ; J.Neurophysiol https://journals.physiology.org/doi/full/10.1152/jn.00528.2012
- Quantal / variance-mean analysis del rilascio sinaptico — PMC: PMC3704362, PMC5122579, PMC2231069, PMC2278972, PMC1303444
- J.Neurosci (quantal/release): /content/24/10/2345 , /content/28/50/13563 , /content/30/4/1441
- Rate/spike inference & synaptic input — PubMed 14667542, 2426389, 1706951, 15136605

## Deconvoluzione (sparsa / FRI / calcium) & ML
- Sampling Signals with Finite Rate of Innovation (Vetterli/Blu/Dragotti) + caso rumoroso — https://www.researchgate.net/publication/3318328 , /37420678 , /220735296
- OASIS — *Fast online deconvolution of calcium imaging data* — https://www.researchgate.net/publication/315059491 ; PLoS Comput Biol https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005423
- SURE-LET deconvoluzione sotto rumore Poisson — https://www.researchgate.net/publication/300340138
- ML pile-up: *Deep Learning Based Pile-Up Correction ... High-Count-Rate* — https://www.researchgate.net/publication/389459277 ; *Pile-up correction by Genetic Algorithm & ANN* — https://www.researchgate.net/publication/245122859

## Point process / Hawkes / jump-diffusion (statistica, finanza)
- MLE per Hawkes (self-excitation/inhibition) — https://www.researchgate.net/publication/349943886
- Lévy models review — https://www.stat.purdue.edu/~figueroa/Papers/LevyModelsReview.pdf
- Inference/simulazione per spatial point process; marked point patterns bayesiani — RG 265716392, 24054052

## Pile-up nucleare (analisi-side, per confronto)
- Pile-up correction ad alto rate (gamma spectroscopy) — RG 337788711, 333636734 ; NIM S0168900218304455, S0168900220307051
- Frontiers Physics, modello pile-up con dead time & retrigger — https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2023.1205638/full
- Nuclear Sci & Tech (2024) — https://link.springer.com/article/10.1007/s41365-024-01606-y

*Nota: Roessl (Fourier/level-crossing) e Personick (excess noise factor) sono in
`findings_approaches.md` con le loro annotazioni.*
