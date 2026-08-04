"""
Test of the Target Systemelektronik high-dose-rate algorithm (patent US2021/0055429
A1, Stein; IEEE NSS 2018) on the real anode_waveforms/*.h5 runs.

Patent equations (i_Δ = digitized current samples, sampling period Δ):
    Msd(i_Δ) = λ·E(i_v) = λη            (Eq.2  MSSD = mean current)
    η ≈ E_γ  = Var(i_Δ) / Msd(i_Δ)      (Eq.3  mean energy)
    Ḣ = Z(η) · Msd(i_Δ)                 (Eq.4  compensated dose rate)
where λ = count rate, η = mean energy, Z = tissue-equivalence correction (unknown
here → we test the *uncompensated* pieces).

Gain-free rate proxy (derived):  λ̂ = Msd²/Var ∝ λ  (gain g cancels: Msd∝g, Var∝g²).
Energy proxy η = Var/Msd ∝ g  → NOT gain-free (tracks the rate-dependent PMT gain
drift described by the passive-divider sag; used here as a gain diagnostic).

We DON'T need the pedestal for Var/Msd/η/λ̂ (Var about per-record mean, Msd from
differences). Sampling: fs assumed 100 MS/s (Δ=10 ns ≈ 4% of NaI τ≈230 ns → within
the patent's Δ<5%τ requirement).  Ground truth in metadata: dose[µSv/h], activity,
distance[cm], nuclide.
"""
import glob, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import welch

FS = 100e6
DT = 1.0 / FS
TAU_NAI = 230e-9                       # NaI(Tl) scintillation decay
WFDIR = os.path.join(os.path.dirname(__file__), "..", "data", "anode_waveforms")
NREC = 6000                            # records per run (subset for speed)
CAL_MCPS_PER_USVH = 1.0 / 540.0        # Target slide7: 1 Mcps ~ 540 µSv/h (Cs-137, 2x2 NaI)


def msd(x, m):
    """m-th Mean Square successive Difference, von Neumann binomial-normalized,
    per record then averaged. Msd^1 = 1/2 <(Δx)^2>."""
    from math import comb
    d = x
    for _ in range(m):
        d = np.diff(d, axis=1)
    return (d ** 2).mean() / comb(2 * m, m)


def noise_var(w):
    """white-noise variance from high-f PSD plateau (robust to interference lines)."""
    f, p = welch(w, fs=FS, nperseg=w.shape[1], axis=-1)
    p = p.mean(0)
    return float(np.median(p[f > 0.6 * f[-1]]) * f[-1])


def analyze(fn):
    import h5py
    f = h5py.File(fn, "r")
    md = dict(f["metadata"].attrs)
    w = f["waveforms"][:NREC].astype(float)
    f.close()
    x = w - w.mean(axis=1, keepdims=True)          # remove per-record DC (drift)
    var = float(x.var())
    m1 = msd(x, 1); m2 = msd(x, 2); m3 = msd(x, 3)
    sig_n2 = noise_var(w)
    # noise-corrected (Gaussian noise: +σ² in Var, +2σ² in Msd^1)
    var_c = var - sig_n2
    m1_c = m1 - sig_n2                              # Msd^1 = 1/2<Δ²>=C0-C1; noise adds σ²
    from scipy.stats import skew, kurtosis
    dose = float(md["dose"]); dist = float(md["distance"]); act = float(md["activity"])
    lam_pred = dose * CAL_MCPS_PER_USVH * 1e6       # predicted count rate [cps] (Cs-137 calib)
    return dict(
        nuclide=str(md["nuclide"]), dose=dose, activity=act, distance=dist,
        inv_sq=act / dist**2, lam_pred=lam_pred, lamtau_pred=lam_pred * TAU_NAI,
        var=var, msd1=m1, msd2=m2, msd3=m3, sig_n=float(np.sqrt(sig_n2)),
        mean=float(w.mean()), base=float(np.median(w)),
        eta=var / m1, lam_hat=m1**2 / var,          # η=Var/Msd ; λ̂=Msd²/Var (∝ g²λ, gain-dip.)
        m2v=float(w.mean()**2 / var),               # mean²/Var (∝ λ, GAIN-FREE; ped=0 → solo direzione)
        eta_c=var_c / m1_c if m1_c > 0 else np.nan,
        lam_hat_c=m1_c**2 / var_c if (m1_c > 0 and var_c > 0) else np.nan,
        skew=float(skew(x, axis=None)), kurt=float(kurtosis(x, axis=None)),
        noise_frac_of_msd=sig_n2 / m1,
    )


def main():
    runs = [analyze(fn) for fn in sorted(glob.glob(os.path.join(WFDIR, "run_*.h5")))]
    cs = [r for r in runs if r["nuclide"] == "Cs-137"]
    cs.sort(key=lambda r: r["dose"])

    print("=" * 100)
    hdr = ("nuclide", "dose", "act", "dist", "lam_pred[Mcps]", "lamtau", "Var",
           "Msd1", "eta=V/M", "lamhat=M2/V", "kurt", "noise/Msd")
    print("%-9s %8s %6s %4s %10s %7s %9s %8s %8s %10s %7s %8s" % hdr)
    for r in sorted(runs, key=lambda r: (r["nuclide"], r["dose"])):
        print("%-9s %8.0f %6.1f %4.0f %10.2f %7.2f %9.1f %8.2f %8.1f %10.3f %7.2f %8.2f" % (
            r["nuclide"], r["dose"], r["activity"], r["distance"], r["lam_pred"]/1e6,
            r["lamtau_pred"], r["var"], r["msd1"], r["eta"], r["lam_hat"],
            r["kurt"], r["noise_frac_of_msd"]))

    print("\n--- Cs-137, sorted by dose: does lam_hat=Msd^2/Var track dose (~lambda)? ---")
    for r in cs:
        print("  dose=%8.0f  lam_pred=%6.2f Mcps  lam_hat=%8.3f  lam_hat_nc=%8.3f  eta=%6.1f  kurt=%+6.2f"
              % (r["dose"], r["lam_pred"]/1e6, r["lam_hat"], r["lam_hat_c"], r["eta"], r["kurt"]))

    with open(os.path.join(os.path.dirname(__file__), "target_results.json"), "w") as fp:
        json.dump(runs, fp, indent=2)

    # ---- figures ----
    fig, ax = plt.subplots(2, 2, figsize=(14, 10))
    csd = np.array([r["dose"] for r in cs])
    # 1: rate proxies vs dose — Msd²/Var (gain-dip, fallisce) vs mean²/Var (gain-free)
    hv = [r for r in cs if r["base"] < 500]        # solo Cs a stessa HV (esclude il 616)
    hvd = np.array([r["dose"] for r in hv])
    lh = np.array([r["lam_hat"] for r in hv]); lh /= lh[0]
    mv = np.array([r["m2v"] for r in hv]); mv /= mv[0]
    ax[0, 0].loglog(hvd, lh, "s-", label="Msd²/Var (∝g²λ, gain-DIP.) → giù ✗")
    ax[0, 0].loglog(hvd, mv, "o-", label="mean²/Var (∝λ, GAIN-FREE) → su ✓")
    ax[0, 0].loglog(hvd, hvd/hvd[0], "k:", label="∝ dose (atteso per il rate)")
    ax[0, 0].set_xlabel("dose [µSv/h]"); ax[0, 0].set_ylabel("proxy (norm. al 1° punto)")
    ax[0, 0].set_title("Rate: Msd²/Var anti-correla (gain crash); mean²/Var va nel verso\ngiusto (Cs stessa HV; ped=0 → solo direzione, il ∝ esatto serve il pedestal)")
    ax[0, 0].legend(fontsize=8)
    # 2: η vs predicted rate — η is GAIN-FREE (∝ energy); for Cs-137 should be CONSTANT
    ax[0, 1].semilogx([r["lam_pred"] for r in cs], [r["eta"] for r in cs], "o-")
    ax[0, 1].set_xlabel("λ_pred [cps]"); ax[0, 1].set_ylabel("η = Var/Msd  (gain-free, ∝ energy)")
    ax[0, 1].set_title("η: dovrebbe essere COSTANTE (Cs-137) → varia = metodo rotto (rumore/regime)")
    # 3: kurtosis vs λτ (pileup Gaussianization)
    for r in runs:
        mk = "o" if r["nuclide"] == "Cs-137" else "^"
        ax[1, 0].semilogx(r["lamtau_pred"], r["kurt"], mk, ms=9,
                          label=f"{r['nuclide']} {r['dose']:.0f}")
    ax[1, 0].axhline(0, color="gray", lw=.5)
    ax[1, 0].set_xlabel("λτ predetto (pileup)"); ax[1, 0].set_ylabel("eccesso kurtosi")
    ax[1, 0].set_title("Non-gaussianità vs pileup (→0 in pileup profondo)"); ax[1, 0].legend(fontsize=7)
    # 4: Msd (uncompensated dose proxy) vs dose
    ax[1, 1].loglog(csd, [r["msd1"] for r in cs], "o-", label="Msd¹ (∝ λη = dose non-comp.)")
    ax[1, 1].loglog(csd, [r["var"] for r in cs], "s--", label="Var (∝ λη²)")
    ax[1, 1].set_xlabel("dose [µSv/h]"); ax[1, 1].set_ylabel("statistica [ADC²]")
    ax[1, 1].set_title("Msd e Var vs dose (confusi dalla deriva di gain)"); ax[1, 1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(os.path.dirname(__file__), "target_test.png"), dpi=100)
    print("\nsaved target_results.json and target_test.png")


if __name__ == "__main__":
    main()
