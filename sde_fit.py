"""
Fit the rise-time SDE simulator (sde_pulse_sim.py) to the real Cs-137 runs by
METHOD OF SIMULATED MOMENTS with Optuna.

Key differences from the deprecated fit_simulator.py:
  * the simulator INTEGRATES a second-order jump-SDE (finite rise time), it does
    NOT convolve with an analytic response;
  * every metric is extracted from SIMULATED WAVEFORMS, never from the response;
  * all parameters carry physical units (ADC, Hz, s); noise is a sigma in ADC
    passed by hand (here measured from the data high-f PSD plateau and fixed);
  * because units are physical, we also match the ABSOLUTE variance [ADC^2],
    which pins the amplitude scale (ser_mean) instead of throwing it away.

Targets: jeanluke/anode_waveforms/run_Cs-137_*.h5  (Am-241 excluded).
Fitted per run: lam [Hz], tau_rise [s], tau_fall [s], ser_mean [ADC], ser_cv.
Run:  python sde_fit.py    -> sde_fit_results.json + sde_fit_validation.png
"""
import glob
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.stats import kurtosis, skew, wasserstein_distance
import optuna

from sde_pulse_sim import simulate_sde, FS, DT

optuna.logging.set_verbosity(optuna.logging.WARNING)

WFDIR = "jeanluke/anode_waveforms"
NREC_DATA = 4000                 # records loaded from each run
N_SEARCH, N_VALID, N_TRIALS = 800, 2000, 250
MAXLAG = 500                     # ACF lags used in the match (= 5 us)
NPERSEG = 2000
_F = np.fft.rfftfreq(NPERSEG, DT)
_FM = _F > 0
_LOGF = np.log10(_F[_FM])                      # Wasserstein support = log10(freq)
_MID = (_F[_FM] >= 3e5) & (_F[_FM] <= 8e6)     # mid band: pins the RISE / roughness


# ---------------------------------------------------------------- statistics
def norm_acf(x, ml=MAXLAG):
    N, L = x.shape
    nf = 1 << int(np.ceil(np.log2(2 * L)))
    X = np.fft.rfft(x, n=nf, axis=1)
    ac = np.fft.irfft((X * np.conj(X)).real, n=nf, axis=1)[:, :ml].mean(0)
    ac /= (L - np.arange(ml))
    return ac / ac[0]


def psd_pmf(x):
    """Mean Welch PSD, normalized to a probability mass over frequency."""
    _, p = welch(x, fs=FS, nperseg=NPERSEG, axis=-1)
    p = p.mean(0)[_FM]
    return p / p.sum()


def summary(x):
    p = (x ** 2).mean(1)
    return dict(acf=norm_acf(x), var=float(x.var()), cv=float(p.std() / p.mean()),
                skew=float(skew(x, axis=None)), kurt=float(kurtosis(x, axis=None)),
                psd=psd_pmf(x))


def measure_noise_sigma(x):
    """White-noise RMS [ADC] from the high-f PSD plateau (median, robust to lines)."""
    f, p = welch(x, fs=FS, nperseg=NPERSEG, axis=-1)
    p = p.mean(0)
    return float(np.sqrt(np.median(p[f > 0.6 * f[-1]]) * f[-1]))


def load_h5(fn, nrec):
    import h5py
    f = h5py.File(fn, "r")
    md = dict(f["metadata"].attrs)
    w = f["waveforms"][:nrec].astype(float)
    f.close()
    x = w - w.mean(axis=1, keepdims=True)          # remove per-record DC (drift)
    return x, md


# ---------------------------------------------------------------- objective
def make_objective(tgt, noise_sigma, polarity, N, seed=0):
    def obj(trial):
        lam = trial.suggest_float("lam", 1e5, 1e8, log=True)
        tau_rise = trial.suggest_float("tau_rise", 5e-9, 500e-9, log=True)
        fr = trial.suggest_float("fall_over_rise", 1.05, 60.0, log=True)
        tau_fall = tau_rise * fr
        ser_mean = trial.suggest_float("ser_mean", 0.5, 3000.0, log=True)
        ser_cv = trial.suggest_float("ser_cv", 0.05, 1.5)
        trial.set_user_attr("tau_fall", tau_fall)

        y = simulate_sde(lam, tau_rise, tau_fall, ser_mean, ser_cv, noise_sigma,
                         n_rec=N, n_samp=2000, polarity=polarity, seed=seed)
        ss = summary(y)
        acf_mse = float(np.mean((ss["acf"][1:MAXLAG] - tgt["acf"][1:MAXLAG]) ** 2))
        var_t = ((ss["var"] - tgt["var"]) / tgt["var"]) ** 2          # ABSOLUTE scale (ADC^2)
        cv_t = ((ss["cv"] - tgt["cv"]) / tgt["cv"]) ** 2
        ku_t = ((ss["kurt"] - tgt["kurt"]) / (abs(tgt["kurt"]) + 0.15)) ** 2
        psd_w = float(wasserstein_distance(_LOGF, _LOGF, ss["psd"], tgt["psd"]))
        fm_s, fm_d = ss["psd"][_MID].sum(), tgt["psd"][_MID].sum()
        mid_t = ((fm_s - fm_d) / fm_d) ** 2
        trial.set_user_attr("breakdown", dict(acf=acf_mse, var=float(var_t), cv=float(cv_t),
                                              kurt=float(ku_t), psd_w=psd_w, mid=float(mid_t)))
        return 70 * acf_mse + 3.0 * var_t + 1.5 * cv_t + 0.1 * ku_t + 6.0 * psd_w + 4.0 * mid_t
    return obj


def polarity_of(x):
    """Detector polarity: positive-going pulses (+1) unless a clear negative tail.
    Deep-pileup runs are ~symmetric (skew ~ 0) -> default to the detector's
    physical polarity (+1, as seen in the resolved low-dose runs)."""
    return -1.0 if skew(x, axis=None) < -0.3 else 1.0


def fit_one(fn):
    x, md = load_h5(fn, NREC_DATA)
    tgt = summary(x)
    noise_sigma = measure_noise_sigma(x)               # FIXED, in ADC (passed to sim)
    pol = polarity_of(x)
    study = optuna.create_study(direction="minimize",
                                sampler=optuna.samplers.TPESampler(seed=1))
    study.optimize(make_objective(tgt, noise_sigma, pol, N_SEARCH), n_trials=N_TRIALS)
    bp, bt = study.best_params, study.best_trial
    tau_rise = bp["tau_rise"]; tau_fall = bt.user_attrs["tau_fall"]
    best = dict(lam=bp["lam"], tau_rise=tau_rise, tau_fall=tau_fall,
                ser_mean=bp["ser_mean"], ser_cv=bp["ser_cv"],
                noise_sigma=noise_sigma, polarity=pol,
                dose=float(md["dose"]), nuclide=str(md["nuclide"]))

    # validate with a FRESH seed (guards against fitting one MC realization)
    sv = simulate_sde(best["lam"], tau_rise, tau_fall, best["ser_mean"], best["ser_cv"],
                      noise_sigma, n_rec=N_VALID, n_samp=2000, polarity=pol, seed=999)
    svs = summary(sv)

    dose = best["dose"]
    print("=" * 70)
    print(f"{os.path.basename(fn)}   dose={dose:.0f} uSv/h   (best obj={bt.value:.4f})")
    print(f"  lambda      = {best['lam']:.3e} Hz")
    print(f"  tau_rise    = {tau_rise*1e9:.1f} ns")
    print(f"  tau_fall    = {tau_fall*1e9:.1f} ns")
    print(f"  ser_mean    = {best['ser_mean']:.1f} ADC")
    print(f"  ser_cv      = {best['ser_cv']:.3f}")
    print(f"  noise_sigma = {noise_sigma:.2f} ADC (measured, fixed)   polarity={pol:+.0f}")
    print(f"  breakdown   = {bt.user_attrs['breakdown']}")
    print(f"  match (data -> sim@fresh):  Var {tgt['var']:.1f} -> {svs['var']:.1f} ADC^2 | "
          f"CV {tgt['cv']:.3f}->{svs['cv']:.3f} | kurt {tgt['kurt']:+.2f}->{svs['kurt']:+.2f} | "
          f"skew {tgt['skew']:+.2f}->{svs['skew']:+.2f}")
    return x, tgt, best, sv, svs


def main():
    files = sorted(glob.glob(os.path.join(WFDIR, "run_Cs-137_*.h5")),
                   key=lambda f: float(os.path.basename(f).split("_")[-1][:-3]))
    results = {}
    nrow = len(files)
    fig, ax = plt.subplots(nrow, 3, figsize=(15, 3.1 * nrow))
    for row, fn in enumerate(files):
        x, tgt, best, sv, svs = fit_one(fn)
        results[os.path.basename(fn)] = best
        tag = f"Cs-137  {best['dose']:.0f} uSv/h"

        # (col 0) one sample record: data vs sim (different realizations, same scale)
        t = np.arange(1500) * DT * 1e6
        ax[row, 0].plot(t, x[0, :1500], "k", lw=0.6, label="data")
        ax[row, 0].plot(t, sv[0, :1500], "r", lw=0.6, alpha=0.8, label="sim")
        ax[row, 0].set_title(f"{tag}  -  record [ADC]")
        ax[row, 0].set_xlabel("t [us]"); ax[row, 0].legend(fontsize=7)

        # (col 1) normalized ACF
        lags = np.arange(MAXLAG) * DT * 1e6
        ax[row, 1].plot(lags, tgt["acf"], "k", lw=1.3, label="data")
        ax[row, 1].plot(lags, svs["acf"], "r--", label="sim")
        ax[row, 1].axhline(0, color="gray", lw=0.4)
        ax[row, 1].set_title("ACF (norm.)"); ax[row, 1].set_xlabel("lag [us]"); ax[row, 1].legend(fontsize=7)

        # (col 2) PSD (absolute)
        fd, pd = welch(x, fs=FS, nperseg=NPERSEG, axis=-1); pd = pd.mean(0)
        fss, ps = welch(sv, fs=FS, nperseg=NPERSEG, axis=-1); ps = ps.mean(0)
        ax[row, 2].loglog(fd[1:], pd[1:], "k", lw=1.0, label="data")
        ax[row, 2].loglog(fss[1:], ps[1:], "r--", label="sim")
        ax[row, 2].set_title("PSD [ADC^2/Hz]"); ax[row, 2].set_xlabel("Hz"); ax[row, 2].legend(fontsize=7)

    fig.suptitle("SDE rise-time simulator (red) vs Cs-137 data (black) - simulate then measure")
    fig.tight_layout()
    fig.savefig("sde_fit_validation.png", dpi=100)
    with open("sde_fit_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nsaved sde_fit_validation.png and sde_fit_results.json")


if __name__ == "__main__":
    main()
