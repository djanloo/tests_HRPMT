"""
Welch / coerenza / filtri: gli sguardi di partenza sui due canali del rivelatore.

  FAST : il ramo d'anodo non sagomato. I primi 1000 record di
         data/anode_waveforms/run_Cs-137_28100.h5 (1000 su 10000, per stare alla
         stessa forma del canale CSP).
  CSP  : csp.npy, uscita del preamplificatore di carica. Tenuto solo come
         riferimento: filtra via l'informazione di conteggio.

Script esplorativo, non produce risultati citati: la coerenza spettrale e il test
allineati-vs-mescolati sono documentati nel vault (`Indipendenza dei due file`).
"""
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, coherence, butter, sosfiltfilt

fs = 100e6  # Hz
NREC = 1000

def load(ch):
    """Il canale `ch` come (NREC, 2000). FAST dal dataset ufficiale, CSP dal .npy."""
    if ch == "FAST":
        with h5py.File("data/anode_waveforms/run_Cs-137_28100.h5", "r") as f:
            return f["waveforms"][:NREC].astype(float)
    return np.load("csp.npy")[:NREC]

CHANNELS = ("CSP", "FAST")

figraw, axraw = plt.subplots(constrained_layout=True)
figpsd, axpsd = plt.subplots(constrained_layout=True)
figstats, axstats = plt.subplots(constrained_layout=True)

colors = plt.cm.rainbow(np.linspace(0,1,10))
for ch in CHANNELS:
    data = load(ch)
    for i in range(10):
        normdata = (data[i] - data[i].min())/(data[i].max() - data[i].min())
        axraw.plot(normdata + i, color=colors[i], ls=(":" if ch == "CSP" else "-"))
    freqs, psd = welch(data, fs=fs, nperseg=data.shape[1], axis=-1)  # psd: (1000, nfreqs)
    psd_mean = psd.mean(axis=0)
    # psd_norm = psd_mean / (psd_mean.sum() * (freqs[1] - freqs[0]))  # area unitaria

    axpsd.loglog(freqs, psd_mean, label=ch)

axpsd.set_xlabel("Frequenza [Hz]")
axpsd.set_ylabel("PSD")
axpsd.set_title("Welch PSD media su 1000 registrazioni")
axpsd.legend()

# --- coerenza spettrale media per run (scipy.signal.coherence) ---
# axis=1: scipy spezza ogni run (2000 campioni) in ~14 segmenti da 256 e ritorna
# coh (n_run, n_freq); .mean(0) media sui run.
# NB: con pochi segmenti la coerenza e' distorta verso ~1/n_seg anche per segnali
# indipendenti -> il floor NON e' 1/N. Lo stimo empiricamente mescolando i run
# (accoppiamento casuale = indipendenti per costruzione): se le due curve
# coincidono, non c'e' coerenza reale.
a = load("FAST")
c = load("CSP")
fcoh, coh   = coherence(a, c, fs=fs, axis=1, nperseg=500, noverlap=250, detrend="constant")        # (n_run, n_freq)
perm        = np.random.default_rng(0).permutation(a.shape[0])
_,    coh_sh = coherence(a, c[perm], fs=fs, axis=1, nperseg=500, noverlap=250, detrend="constant")

figcoh, axcoh = plt.subplots(constrained_layout=True)
axcoh.plot(fcoh, coh.mean(0),    label="run allineati")
axcoh.plot(fcoh, coh_sh.mean(0), ls=":", label="run mescolati (floor indipendenti)")
axcoh.set_ylim(0, 1)
axcoh.set_xlabel("Frequenza [Hz]")
axcoh.set_ylabel(r"$\gamma^2$")
axcoh.set_title("Coerenza spettrale media per run: CSP vs FAST")
axcoh.legend()

# --- serie temporali passa-alto (Butterworth zero-fase) a due tagli ---
figcut20, axcut20 = plt.subplots(constrained_layout=True)
figcut5,  axcut5  = plt.subplots(constrained_layout=True)
for cut, ax in ((20e6, axcut20), (5e6, axcut5)):
    sos = butter(4, cut, "high", fs=fs, output="sos")
    for ch in CHANNELS:
        data = load(ch)
        for i in range(10):
            y = sosfiltfilt(sos, data[i])
            y = (y - y.min()) / (y.max() - y.min())
            ax.plot(y + i, color=colors[i], ls=(":" if ch == "CSP" else "-"))
    ax.set_title(f"Serie temporale, passa-alto a {cut/1e6:.0f} MHz")
    ax.set_xlabel("campione")
    ax.set_ylabel("record (norm., offset)")

plt.show()