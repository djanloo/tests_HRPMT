"""
Fit the filtered-Poisson simulator to the real data by METHOD OF SIMULATED
MOMENTS, optimized with Optuna.

We match summary statistics that isolate different physics (so the fit is
identifiable rather than a blind 5-D search):
  - normalized ensemble ACF   -> pulse shape h (tau_rise, tau_fall) + noise_frac
  - PSD, Wasserstein distance  -> spectral shape + noise-floor position
                                  (normalized PSD as a distribution over log-f)
  - per-record power CV        -> occupancy  (rate x pulse-energy statistics)
  - excess kurtosis            -> SER width (ser_cv) / occupancy

Absolute gain is DEGENERATE and drops out (every statistic above is scale-free);
it is recovered afterwards as the variance-matching factor. Likewise in deep
pileup (anode) the rate saturates -> reported as a lower bound (see notes).

Fitted per file: lam, tau_rise, tau_fall, ser_cv, noise_frac.
Run:  python fit_simulator.py         (writes fit_results.json + fit_*.png)
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.stats import skew, kurtosis, wasserstein_distance
import optuna

from simulate_pmt import h_onepole, h_preamp, FS, DT

optuna.logging.set_verbosity(optuna.logging.WARNING)
MAXLAG = 500                      # lags used in the ACF match (= 5 us)
NPERSEG = 2000
_F = np.fft.rfftfreq(NPERSEG, DT)
_FM = _F > 0
_LOGF = np.log10(_F[_FM])         # Wasserstein support = log10(frequency)
_MID = (_F[_FM] >= 3e5) & (_F[_FM] <= 8e6)   # mid band: pins the RISE / roughness


# ---------------------------------------------------------------- statistics
def norm_acf(x, ml=MAXLAG):
    N, L = x.shape
    nf = 1 << int(np.ceil(np.log2(2 * L)))
    X = np.fft.rfft(x, n=nf, axis=1)
    ac = np.fft.irfft((X * np.conj(X)).real, n=nf, axis=1)[:, :ml].mean(0)
    ac /= (L - np.arange(ml))
    return ac / ac[0]


def psd_pmf(x):
    """Mean Welch PSD, normalized to a probability mass over frequency (gain-free)."""
    _, p = welch(x, fs=FS, nperseg=NPERSEG, axis=-1)
    p = p.mean(0)[_FM]
    return p / p.sum()


def summary(x):
    p = (x ** 2).mean(1)
    return dict(acf=norm_acf(x), cv=p.std() / p.mean(),
                skew=skew(x, axis=None), kurt=kurtosis(x, axis=None), psd=psd_pmf(x))


# ---------------------------------------------------------------- simulator
def simulate(kind, lam, tau_rise, tau_fall, ser_cv, noise_frac, N, L=2000, seed=0):
    rng = np.random.default_rng(seed)
    n = int(min(4000, max(800, 10 * tau_fall / DT)))      # kernel long enough
    h = (h_onepole(n=n, tau_rise=tau_rise, tau_fall=tau_fall) if kind == "anode"
         else h_preamp(n=n, tau_rise=tau_rise, tau_fall=tau_fall))
    counts = rng.poisson(lam * DT, size=(N, L)).astype(float)
    if ser_cv > 0:
        k = 1.0 / ser_cv ** 2
        counts *= rng.gamma(k, 1.0 / k, size=(N, L))
    nf = 1 << int(np.ceil(np.log2(L + len(h))))
    H = np.fft.rfft(h, n=nf)
    y = np.fft.irfft(np.fft.rfft(counts, n=nf, axis=1) * H, n=nf, axis=1)[:, :L]
    y = -y                                                # PMT pulses negative
    if noise_frac > 0:
        y = y + rng.normal(0, noise_frac * y.std(), y.shape)
    return y - np.median(y, axis=1, keepdims=True)


def measure_noise_frac(y):
    """White-noise fraction from the high-f PSD plateau (median, robust to lines);
    FIXED, not fitted -- normalized ACF/PSD metrics are blind to the absolute floor,
    so leaving noise free lets the sim get too rough (wrong small-scale morphology)."""
    f, p = welch(y, fs=FS, nperseg=NPERSEG, axis=-1)
    p = p.mean(0)
    sig_n2 = np.median(p[f > 0.6 * f[-1]]) * f[-1]
    return float(np.sqrt(sig_n2) / y.std())


# ---------------------------------------------------------------- objective
def make_objective(kind, tgt, N, ranges, noise_frac, seed=0):
    def obj(trial):
        lam = trial.suggest_float("lam", *ranges["lam"], log=True)
        tau_rise = trial.suggest_float("tau_rise", *ranges["tau_rise"], log=True)
        fr = trial.suggest_float("fall_over_rise", *ranges["for"], log=True)
        tau_fall = tau_rise * fr
        ser_cv = trial.suggest_float("ser_cv", 0.05, 1.5)
        trial.set_user_attr("tau_fall", tau_fall)

        ss = summary(simulate(kind, lam, tau_rise, tau_fall, ser_cv, noise_frac, N, seed=seed))
        acf_mse = float(np.mean((ss["acf"][1:MAXLAG] - tgt["acf"][1:MAXLAG]) ** 2))
        cv_t = ((ss["cv"] - tgt["cv"]) / tgt["cv"]) ** 2
        ku_t = ((ss["kurt"] - tgt["kurt"]) / (abs(tgt["kurt"]) + 0.15)) ** 2
        psd_w = float(wasserstein_distance(_LOGF, _LOGF, ss["psd"], tgt["psd"]))  # in decades
        # mid-band power fraction (0.3-8 MHz): pins the RISE / small-scale morphology.
        # The equal-weighted ACF and the broad Wasserstein underweight this band, so
        # the rise came out too slow -> sim too smooth. This term fixes it directly.
        fm_s, fm_d = ss["psd"][_MID].sum(), tgt["psd"][_MID].sum()
        mid_t = ((fm_s - fm_d) / fm_d) ** 2
        # skewness dropped: near-symmetric here, MC-noisy, and polarity is known.
        trial.set_user_attr("breakdown", dict(acf=acf_mse, cv=float(cv_t),
                                              kurt=float(ku_t), psd_w=psd_w, mid=float(mid_t)))
        return 70 * acf_mse + 1.5 * cv_t + 0.1 * ku_t + 6.0 * psd_w + 4.0 * mid_t
    return obj


CFG = {
    "anodewaves.npy": dict(
        kind="anode",
        ranges=dict(lam=(1e6, 8e7), tau_rise=(5e-9, 150e-9), **{"for": (1.3, 40)},
                    noise=(0.02, 0.6)),
    ),
    "culoculo.npy": dict(
        kind="preamp",
        ranges=dict(lam=(1e5, 1e7), tau_rise=(0.1e-6, 2e-6), **{"for": (1.3, 15)},
                    noise=(1e-3, 0.1)),
    ),
}
N_SEARCH, N_VALID, N_TRIALS = 600, 1000, 500


def load(fname):
    d = np.load(fname).astype(float)
    return d - np.median(d, axis=1, keepdims=True)


def fit_one(fname, cfg):
    x = load(fname)
    tgt = summary(x)
    noise_frac = measure_noise_frac(x)               # FIXED from data (PSD plateau)
    study = optuna.create_study(direction="minimize",
                                sampler=optuna.samplers.TPESampler(seed=1))
    study.optimize(make_objective(cfg["kind"], tgt, N_SEARCH, cfg["ranges"], noise_frac),
                   n_trials=N_TRIALS)
    bp, bt = study.best_params, study.best_trial
    tau_rise = bp["tau_rise"]; tau_fall = bt.user_attrs["tau_fall"]
    best = dict(lam=bp["lam"], tau_rise=tau_rise, tau_fall=tau_fall,
                ser_cv=bp["ser_cv"], noise_frac=noise_frac)

    # validate with a FRESH seed (guards against fitting one MC realization)
    sv = simulate(cfg["kind"], best["lam"], tau_rise, tau_fall, best["ser_cv"],
                  best["noise_frac"], N_VALID, seed=999)
    svs = summary(sv)

    # degeneracy band: params among near-best trials (value < 1.3 x best)
    good = [t for t in study.trials if t.value is not None and t.value < 1.3 * bt.value]
    lam_g = [t.params["lam"] for t in good]
    ser_g = [t.params["ser_cv"] for t in good]

    print("=" * 66)
    print(f"{fname}   (best objective = {bt.value:.4f}, {len(good)} near-best trials)")
    print(f"  lambda      = {best['lam']:.3e} Hz")
    print(f"  tau_rise    = {tau_rise*1e9:.1f} ns")
    print(f"  tau_fall    = {tau_fall*1e9:.1f} ns")
    print(f"  ser_cv      = {best['ser_cv']:.3f}")
    print(f"  noise_frac  = {best['noise_frac']:.4f}")
    print(f"  breakdown   = {bt.user_attrs['breakdown']}")
    print(f"  stat match (data -> sim@fresh seed):")
    print(f"     CV    {tgt['cv']:.3f} -> {svs['cv']:.3f}")
    print(f"     skew  {tgt['skew']:+.3f} -> {svs['skew']:+.3f}")
    print(f"     kurt  {tgt['kurt']:+.3f} -> {svs['kurt']:+.3f}")
    print(f"     acf1e {np.argmax(tgt['acf']<np.exp(-1))*DT*1e9:.0f} -> "
          f"{np.argmax(svs['acf']<np.exp(-1))*DT*1e9:.0f} ns")
    print(f"  degeneracy band (near-best): lambda [{min(lam_g):.2e},{max(lam_g):.2e}]  "
          f"ser_cv [{min(ser_g):.2f},{max(ser_g):.2f}]")
    best["_band"] = dict(lam=[min(lam_g), max(lam_g)], ser_cv=[min(ser_g), max(ser_g)],
                         n_near_best=len(good), best_obj=float(bt.value))
    return x, tgt, best, sv, svs


def main():
    results = {}
    fig, ax = plt.subplots(2, 3, figsize=(15, 8))
    for row, (fname, cfg) in enumerate(CFG.items()):
        x, tgt, best, sv, svs = fit_one(fname, cfg)
        results[fname] = {k: v for k, v in best.items()}
        # scale sim to data variance for the plot (recover the arbitrary gain)
        sv_p = sv * np.sqrt(x.var() / sv.var())
        lags = np.arange(MAXLAG) * DT * 1e6
        ax[row, 0].plot(lags, tgt["acf"], "k", lw=1.4, label="data")
        ax[row, 0].plot(lags, svs["acf"], "r--", label="fit")
        ax[row, 0].axhline(0, color="gray", lw=.4)
        ax[row, 0].set_title(f"{fname}  ACF"); ax[row, 0].set_xlabel("lag [us]"); ax[row, 0].legend()
        fd, pd = welch(x, fs=FS, nperseg=2000, axis=-1); pd = pd.mean(0)
        fs2, ps = welch(sv_p, fs=FS, nperseg=2000, axis=-1); ps = ps.mean(0)
        ax[row, 1].loglog(fd[1:], pd[1:], "k", lw=1.1, label="data")
        ax[row, 1].loglog(fs2[1:], ps[1:], "r--", label="fit")
        ax[row, 1].set_title("PSD"); ax[row, 1].set_xlabel("Hz"); ax[row, 1].legend()
        ax[row, 2].hist((x ** 2).mean(1), bins=50, density=True, alpha=.55, label="data")
        ax[row, 2].hist((sv_p ** 2).mean(1), bins=50, density=True, alpha=.55, label="fit")
        ax[row, 2].set_title("per-record power"); ax[row, 2].legend()
    fig.suptitle("Optuna MSM fit (red) vs data (black)")
    fig.tight_layout(); fig.savefig("fit_validation.png", dpi=100)
    with open("fit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nsaved fit_validation.png and fit_results.json")


if __name__ == "__main__":
    main()
