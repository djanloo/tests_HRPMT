"""
Validazione della pipeline di dose su DATI SINTETICI a verità nota.

Fit grossolano del simulatore pe-level (../target_test/pe_synth.py) ai run reali:
  tau_scint = 230 ns (NaI),  eta_pe = 3500 (Cs-137 662 keV),  rumore ~ reale.
Con questi, lo skew sintetico segue quello reale ai λ noti (vedi figura, pannello A).

Test: genero forme d'onda a λ NOTO (→ dose vera = λ·540 µSv/h·Mcps⁻¹), applico la
calibrazione di dose (dai dati reali) e verifico che recuperi la dose vera.
"""
import os, sys, json
import numpy as np
from scipy.stats import skew, kurtosis
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "target_test"))
import pe_synth as pe                                  # generatore pe-level (Cox)

CAL = json.load(open(os.path.join(os.path.dirname(__file__), "calibration.json")))["rate_dose"]
DT = pe.DT
ETA_PE, NOISE = 3500, 2.0
MCPS2USVH = 540.0                                       # 1 Mcps ↔ 540 µSv/h (Cs, 2x2" NaI)

def sk(j):
    x = j - j.mean(1, keepdims=True); return float(skew(x, axis=None))
def dose_est(s):
    return float(np.exp(CAL["a"] + CAL["b"] * np.arcsinh(s)))

# --- run reali (per overlay) ---
real = [(616, 2.17), (889, 1.83), (7900, 0.10), (17990, 0.02), (28100, -0.13)]

# --- sintetico su una griglia di λ noti ---
lam_grid = np.logspace(np.log10(0.6e6), np.log10(6e7), 12)
sks, dose_true, dose_hat = [], [], []
for lam in lam_grid:
    j = pe.gen(lam, ETA_PE, gain=1.0, N=1200, L=2000, noise_adc=NOISE, seed=1)
    s = sk(j); sks.append(s)
    dose_true.append(lam / 1e6 * MCPS2USVH); dose_hat.append(dose_est(s))
sks = np.array(sks); dose_true = np.array(dose_true); dose_hat = np.array(dose_hat)
fac = np.exp(np.abs(np.log(dose_hat / dose_true)))

# --- timeseries sintetiche low/high rate ---
j_lo = pe.gen(1.2e6, ETA_PE, gain=1.0, N=5, L=2000, noise_adc=NOISE, seed=3)
j_hi = pe.gen(5.0e7, ETA_PE, gain=1.0, N=5, L=2000, noise_adc=NOISE, seed=4)
t = np.arange(2000) * DT * 1e6

fig, ax = plt.subplots(2, 2, figsize=(14, 9))
# A: skew(dose) sim vs real
ax[0, 0].semilogx(dose_true, sks, "o-", label="sintetico (λ noto)")
ax[0, 0].semilogx([d for d, _ in real], [s for _, s in real], "s", ms=11, label="run reali")
ax[0, 0].axhline(0, color="gray", lw=.5)
ax[0, 0].set_xlabel("dose [µSv/h]"); ax[0, 0].set_ylabel("skewness γ1")
ax[0, 0].set_title("Fit grossolano: skew sintetico ≈ reale"); ax[0, 0].legend(fontsize=8)
# B: dose stimata vs vera (sintetico)
ax[0, 1].loglog(dose_true, dose_hat, "o", ms=9)
lo, hi = dose_true.min() * .6, dose_true.max() * 1.6
ax[0, 1].plot([lo, hi], [lo, hi], "k:", label="ideale")
ax[0, 1].fill_between([lo, hi], [lo/2, hi/2], [lo*2, hi*2], color="green", alpha=.12, label="±fattore 2")
ax[0, 1].set_xlabel("dose vera (sintetica) [µSv/h]"); ax[0, 1].set_ylabel("dose stimata [µSv/h]")
ax[0, 1].set_title("Validazione: recupero della dose\nmediano ×%.2f, max ×%.2f" % (np.median(fac), fac.max()))
ax[0, 1].legend(fontsize=8)
# C, D: timeseries
for k in range(4):
    ax[1, 0].plot(t, j_lo[k] + k * 1.2 * j_lo.std(), lw=0.6)
    ax[1, 1].plot(t, j_hi[k] + k * 1.2 * j_hi.std(), lw=0.6)
ax[1, 0].set_title("Sintetico ~1.2 Mcps (basso rate, γ1 grande)"); ax[1, 0].set_xlabel("t [µs]"); ax[1, 0].set_yticks([])
ax[1, 1].set_title("Sintetico ~50 Mcps (alto rate, pileup gaussiano)"); ax[1, 1].set_xlabel("t [µs]"); ax[1, 1].set_yticks([])
fig.suptitle("Validazione su dati sintetici (verità nota): fit, recupero dose, timeseries")
fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(__file__), "synth_validation.png"), dpi=100)

print("skew sintetico:", np.round(sks, 2))
print("dose vera :", np.round(dose_true, 0))
print("dose stim :", np.round(dose_hat, 0))
print("recupero dose sintetica: mediano ×%.2f, max ×%.2f" % (np.median(fac), fac.max()))
print("saved synth_validation.png")
