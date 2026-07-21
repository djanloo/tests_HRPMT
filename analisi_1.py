import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch, coherence, butter, sosfiltfilt

fs = 100e6  # Hz

figraw, axraw = plt.subplots(constrained_layout=True)
figpsd, axpsd = plt.subplots(constrained_layout=True)
figstats, axstats = plt.subplots(constrained_layout=True)

colors = plt.cm.rainbow(np.linspace(0,1,10))
for fname in ("culoculo.npy", "anodewaves.npy"):
    data = np.load(fname)  # (1000 registrazioni, 2000 punti)
    for i in range(10):
        normdata = (data[i] - data[i].min())/(data[i].max() - data[i].min())
        axraw.plot(normdata + i, color=colors[i], ls=(":" if fname.find("culo") >-1 else "-"))
    freqs, psd = welch(data, fs=fs, nperseg=data.shape[1], axis=-1)  # psd: (1000, nfreqs)
    psd_mean = psd.mean(axis=0)
    # psd_norm = psd_mean / (psd_mean.sum() * (freqs[1] - freqs[0]))  # area unitaria

    axpsd.loglog(freqs, psd_mean, label=fname)

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
a = np.load("anodewaves.npy")
c = np.load("culoculo.npy")
fcoh, coh   = coherence(a, c, fs=fs, axis=1, nperseg=500, noverlap=250, detrend="constant")        # (n_run, n_freq)
perm        = np.random.default_rng(0).permutation(a.shape[0])
_,    coh_sh = coherence(a, c[perm], fs=fs, axis=1, nperseg=500, noverlap=250, detrend="constant")

figcoh, axcoh = plt.subplots(constrained_layout=True)
axcoh.plot(fcoh, coh.mean(0),    label="run allineati")
axcoh.plot(fcoh, coh_sh.mean(0), ls=":", label="run mescolati (floor indipendenti)")
axcoh.set_ylim(0, 1)
axcoh.set_xlabel("Frequenza [Hz]")
axcoh.set_ylabel(r"$\gamma^2$")
axcoh.set_title("Coerenza spettrale media per run: culoculo vs anodewaves")
axcoh.legend()

# --- serie temporali passa-alto (Butterworth zero-fase) a due tagli ---
figcut20, axcut20 = plt.subplots(constrained_layout=True)
figcut5,  axcut5  = plt.subplots(constrained_layout=True)
for cut, ax in ((20e6, axcut20), (5e6, axcut5)):
    sos = butter(4, cut, "high", fs=fs, output="sos")
    for fname in ("culoculo.npy", "anodewaves.npy"):
        data = np.load(fname)
        for i in range(10):
            y = sosfiltfilt(sos, data[i])
            y = (y - y.min()) / (y.max() - y.min())
            ax.plot(y + i, color=colors[i], ls=(":" if "culo" in fname else "-"))
    ax.set_title(f"Serie temporale, passa-alto a {cut/1e6:.0f} MHz")
    ax.set_xlabel("campione")
    ax.set_ylabel("record (norm., offset)")

plt.show()