"""
DOSE-RATE ESTIMATION PIPELINE from PMT anode waveforms — signal statistics only.
No dark run, no pedestal, robust to the drifting/collapsing PMT gain.

  RATE (occupancy)  <-  skewness  γ1   (gain-free: ratio of cumulants)
  ENERGY (mean)     <-  η = Var/Msd    (gain-free)
  REGIME            <-  kurtosis  γ2   (gain-free)  + stability of γ1
  DOSE  Ḣ = k · rate · energy   ->  ln(Ḣ) = a + b·asinh(γ1) [+ c·ln(η) se energia ignota]

WHY gain-free features (and NOT Msd/Var/mean): the passive-divider gain drifts and
COLLAPSES with rate (../target_test/gain_model_proposal.md). Msd/Var/mean carry g or g²
and are non-monotonic in dose across HV -> the ladder model explains WHY we avoid them.
γ1 and η are cumulant RATIOS in which the gain cancels: no runtime gain correction.

Ground truth for calibration: `dose` metadata (µSv/h), verified ∝ activity/dist².
Validation: leave-one-out on the 5 Cs-137 runs (fixed energy, 2.5 decadi di dose).
Energia: η separa Am-241 (59.5 keV) da Cs-137 (662 keV).
Regime a bassissimo rate (occupancy λτ≲0.1, es. Am-241): impulsi risolti, i momenti
alti sono INSTABILI -> si CONTANO gli impulsi (fuori da questo stimatore statistico).
"""
import glob, json, os
import numpy as np
from scipy.stats import skew, kurtosis

FS = 100e6
DT = 1.0 / FS
WFDIR = os.path.join(os.path.dirname(__file__), "..", "jeanluke", "anode_waveforms")
E_LINE = {"Cs-137": 662.0, "Am-241": 59.5}          # keV (per la calibrazione energia)
CAL_MCPS_PER_USVH = 1.0 / 540.0                     # Cs-137 2x2" NaI (Target)


def features(w):
    """Gain-free, pedestal-free statistics from a (records, samples) array."""
    x = w - w.mean(axis=1, keepdims=True)
    var = float(x.var()); msd = 0.5 * float((np.diff(x, axis=1) ** 2).mean())
    # stabilità di γ1: split a metà (se instabile -> regime a bassissimo rate)
    n = len(x) // 2
    s1, s2 = float(skew(x[:n], axis=None)), float(skew(x[n:], axis=None))
    return dict(skew=float(skew(x, axis=None)), eta=var / msd,
                kurt=float(kurtosis(x, axis=None)),
                skew_unstable=abs(s1 - s2) > 0.5 * (abs(s1) + abs(s2) + 1e-9),
                var=var, msd=msd)


def regime(f):
    if f["skew_unstable"] or f["kurt"] > 20:
        return "bassissimo rate (impulsi risolti) → CONTA gli impulsi, non usare le statistiche"
    return "moderato rate (γ1 informativa)" if f["kurt"] > 1 else "alto rate (pileup gaussiano)"


# ---- calibrazioni (fittate sui run etichettati) ----
def fit_rate_dose(runs):                                    # Cs-137: energia fissa → dose ∝ rate
    cs = [r for r in runs if r["nuc"] == "Cs-137"]
    A = np.column_stack([np.arcsinh([r["skew"] for r in cs]), np.ones(len(cs))])
    b, *_ = np.linalg.lstsq(A, np.log([r["dose"] for r in cs]), rcond=None)
    return {"b": float(b[0]), "a": float(b[1])}

def fit_energy(runs):                                       # η → energia media (keV)
    et = np.log([r["eta"] for r in runs]); E = np.log([E_LINE[r["nuc"]] for r in runs])
    q, p = np.polyfit(et, E, 1)
    return {"p": float(p), "q": float(q)}

def dose_from_rate(f, cal):                                 # dose per energia nota (Cs)
    return float(np.exp(cal["a"] + cal["b"] * np.arcsinh(f["skew"])))
def energy_kev(f, cal):
    return float(np.exp(cal["p"] + cal["q"] * np.log(f["eta"])))
def rate_mcps(dose):                                        # rate assoluto (calib. Target, Cs)
    return dose * CAL_MCPS_PER_USVH


def load_runs():
    import h5py
    out = []
    for fn in sorted(glob.glob(os.path.join(WFDIR, "run_*.h5"))):
        f = h5py.File(fn, "r"); a = f["metadata"].attrs
        md = dict(nuc=str(a["nuclide"]), dose=float(a["dose"]))
        w = f["waveforms"][:].astype(float); f.close()
        md.update(features(w)); out.append(md)
    return sorted(out, key=lambda r: r["dose"])


def main():
    runs = load_runs()
    rc = fit_rate_dose(runs); ec = fit_energy(runs)
    json.dump({"rate_dose": rc, "energy": ec}, open(os.path.join(os.path.dirname(__file__), "calibration.json"), "w"), indent=2)

    # leave-one-out sui Cs-137 (dimensione RATE, energia fissa)
    cs = [r for r in runs if r["nuc"] == "Cs-137"]; dose = np.array([r["dose"] for r in cs])
    pred = np.empty(len(cs))
    for i in range(len(cs)):
        cal = fit_rate_dose([cs[j] for j in range(len(cs)) if j != i] +
                            [r for r in runs if r["nuc"] != "Cs-137"])  # (i non-Cs non entrano nel fit rate)
        pred[i] = dose_from_rate(cs[i], cal)
    fac = np.exp(np.abs(np.log(pred / dose)))

    print("CALIBRAZIONE  ln(dose)=%.3f%+.3f·asinh(γ1) [Cs]   ;   ln(E/keV)=%.2f%+.2f·ln(η)"
          % (rc["a"], rc["b"], ec["p"], ec["q"]))
    print("\n%-8s %7s | γ1(skew) %6s %6s | RATE  ENERGIA  DOSE→  vs vero" % ("nuclide", "dose", "η", "kurt"))
    for r in runs:
        d = dose_from_rate(r, rc); E = energy_kev(r, ec)
        print("%-8s %7.0f |  %+6.2f  %6.1f %6.1f | %5.2f Mcps  %5.0f keV  %7.0f  (vero %.0f, ×%.2f)  [%s]"
              % (r["nuc"], r["dose"], r["skew"], r["eta"], r["kurt"], rate_mcps(d), E, d, r["dose"],
                 np.exp(abs(np.log(d/r["dose"]))), "OK" if not r["skew_unstable"] else "conta impulsi"))
    print("\nVALIDAZIONE (leave-one-out, 5 run Cs-137, 2.5 decadi):")
    for r, p, fc in zip(cs, pred, fac):
        print("   dose %6.0f µSv/h → stima %6.0f  (×%.2f)" % (r["dose"], p, fc))
    print("   → fattore mediano ×%.2f, massimo ×%.2f" % (np.median(fac), fac.max()))

    # figura
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.4))
    ax[0].loglog(dose, pred, "o", ms=12, color="tab:blue")
    lo, hi = 400, 4e4
    ax[0].plot([lo, hi], [lo, hi], "k:", label="ideale")
    ax[0].fill_between([lo, hi], [lo/2, hi/2], [lo*2, hi*2], color="green", alpha=.12, label="±fattore 2")
    ax[0].set_xlabel("dose vera [µSv/h]"); ax[0].set_ylabel("dose stimata (LOO) [µSv/h]")
    ax[0].set_title("Dose dai segnali (solo skewness gain-free), Cs-137\nLOO mediano ×%.2f, max ×%.2f — no pedestal, no gain corr."
                    % (np.median(fac), fac.max())); ax[0].legend(fontsize=9)
    ax[1].semilogx([r["dose"] for r in runs], [r["skew"] for r in runs], "o", label="γ1 skew → rate")
    ax[1].semilogx([r["dose"] for r in runs], [r["eta"] for r in runs], "s", label="η=Var/Msd → energia")
    ax[1].semilogx([r["dose"] for r in runs], [min(r["kurt"], 12) for r in runs], "^", label="kurt (clip 12) → regime")
    ax[1].set_yscale("symlog"); ax[1].set_xlabel("dose [µSv/h]"); ax[1].set_ylabel("proxy (gain-free)")
    ax[1].set_title("I tre proxy gain-free"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(__file__), "dose_result.png"), dpi=100)
    print("saved calibration.json, dose_result.png")


if __name__ == "__main__":
    main()
