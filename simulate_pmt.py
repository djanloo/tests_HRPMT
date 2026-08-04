"""
Coherent simulation of the PMT detector signal as a *marked filtered Poisson
process* (shot noise):

        y(t) = sum_k  A_k * h(t - t_k)  +  n(t)

    t_k   arrival times, Poisson process of rate lambda   (the "rate")
    A_k   pulse charges, iid ~ SER distribution           (the "mean energy")
    h(t)  single-event impulse response (detector+electronics)
    n(t)  electronic noise (white and/or colored OU)

Two equivalent generators are provided:
  * simulate_events()  -- exact superposition of pulses (recommended, any h)
  * simulate_ou_sde()  -- Euler-Maruyama integration of the jump-SDE
                          dY = -(Y/tau) dt + dJ(t),  J = compound Poisson
                          (valid for the single-pole exponential h; this is the
                           "stochastic differential equation" form)

Parameters below reproduce the two measured datasets (fs = 100 MS/s):
  FAST : the anode read across the ~50 ohm termination (V = R*I, no shaping)
         -- one-pole, tau_fall ~ 250 ns, deep pileup (lambda*tau >> 1). This is
         the signal the whole project works on; the reference dataset is
         data/anode_waveforms/run_Cs-137_*.h5.
  CSP  : charge-sensitive preamp downstream of the same anode (UNIPOLAR), rise
         ~0.7 us, fall ~2.4 us -- csp.npy. Kept for reference only: the CSP
         integrates and filters, so at high rate its bandwidth is gone long
         before the interesting statistics are.

Run directly for a self-check that the generated ACF time-constant and the
per-record power CV match the measured values.
"""
import numpy as np

FS = 100e6            # sampling rate [Hz]
DT = 1.0 / FS


# --------------------------------------------------------------------------
# single-event impulse responses  h(t)  (peak-normalized)
# --------------------------------------------------------------------------
def h_onepole(n=800, tau_fall=250e-9, tau_rise=22e-9):
    """Anode: bi-exponential (fast rise, exp fall). ~one-pole, unipolar."""
    t = np.arange(n) * DT
    h = np.exp(-t / tau_fall) - np.exp(-t / tau_rise)
    return h / h.max()


def h_preamp(n=1500, tau_rise=0.7e-6, tau_fall=2.4e-6):
    """Charge-sensitive preamp: it INTEGRATES the detector current, so the
    single-event response is UNIPOLAR -- fast rise (current integration) + slow
    exp fall (feedback RC). Bi-exponential, positive area (carries a DC term).
    (The 'bipolar' ACF zero-crossing was an artifact of per-record
    baseline subtraction on a signal whose tau_corr is a large fraction of the
    window, not a real bipolar shape.)"""
    t = np.arange(n) * DT
    h = np.exp(-t / tau_fall) - np.exp(-t / tau_rise)
    return h / h.max()


# --------------------------------------------------------------------------
# generator 1: exact event superposition
# --------------------------------------------------------------------------
def simulate_events(lam, h, n_rec=1000, n_samp=2000,
                    ser_mean=1.0, ser_cv=0.5, noise_sigma=0.0,
                    noise_tau=0.0, spectrum=None, seed=0):
    """
    lam         event rate [Hz]
    h           impulse response array (peak-normalized)
    ser_cv      coeff. of variation of the single-event charge (Gamma marks);
                0 = fixed charge, 1 = exponential (typical PMT SER ~ 0.3-0.5)
    spectrum    energy_spectrum.Spectrum with MEASURED pulse heights (CAEN DDE);
                overrides ser_cv, `ser_mean` still sets the mean charge
    noise_sigma electronic noise RMS [ADC]; white if noise_tau==0,
                else Ornstein-Uhlenbeck colored with correlation time noise_tau
    returns     (n_rec, n_samp) array, per-record baseline removed
    """
    rng = np.random.default_rng(seed)
    if spectrum is not None:
        from energy_spectrum import poisson_marks
        counts = poisson_marks(lam, DT, (n_rec, n_samp), ser_mean, spectrum, rng)
    else:
        counts = rng.poisson(lam * DT, size=(n_rec, n_samp)).astype(float)
        if ser_cv > 0:                               # Gamma-distributed charges
            k = 1.0 / ser_cv ** 2
            counts *= rng.gamma(k, ser_mean / k, size=(n_rec, n_samp))
        else:
            counts *= ser_mean

    nfft = 1 << int(np.ceil(np.log2(n_samp + len(h))))
    H = np.fft.rfft(h, n=nfft)
    y = np.fft.irfft(np.fft.rfft(counts, n=nfft, axis=1) * H, n=nfft, axis=1)[:, :n_samp]

    if noise_sigma > 0:
        if noise_tau > 0:                            # OU colored noise
            a = np.exp(-DT / noise_tau)
            w = rng.normal(0, noise_sigma * np.sqrt(1 - a * a), size=(n_rec, n_samp))
            nse = np.empty_like(w)
            nse[:, 0] = rng.normal(0, noise_sigma, n_rec)
            for i in range(1, n_samp):
                nse[:, i] = a * nse[:, i - 1] + w[:, i]
        else:
            nse = rng.normal(0, noise_sigma, size=(n_rec, n_samp))
        y = y + nse

    y -= np.median(y, axis=1, keepdims=True)
    return y


# --------------------------------------------------------------------------
# generator 2: jump-SDE (Euler-Maruyama), single-pole exponential response
#   dY = -(Y/tau) dt + dJ(t),   J = sum of A_k at Poisson times
# --------------------------------------------------------------------------
def simulate_ou_sde(lam, tau_fall, n_rec=1000, n_samp=2000,
                    ser_mean=1.0, ser_cv=0.5, noise_sigma=0.0, seed=0):
    """Exact for the one-pole anode. Between events Y decays as exp(-t/tau);
    each Poisson arrival adds a charge A_k. (Colored-h cases need the
    state-space form / use simulate_events instead.)"""
    rng = np.random.default_rng(seed)
    decay = np.exp(-DT / tau_fall)
    counts = rng.poisson(lam * DT, size=(n_rec, n_samp)).astype(float)
    if ser_cv > 0:
        k = 1.0 / ser_cv ** 2
        jumps = counts * rng.gamma(k, ser_mean / k, size=(n_rec, n_samp))
    else:
        jumps = counts * ser_mean

    y = np.empty((n_rec, n_samp))
    y[:, 0] = jumps[:, 0]
    for i in range(1, n_samp):                        # Euler-Maruyama recursion
        y[:, i] = decay * y[:, i - 1] + jumps[:, i]
    if noise_sigma > 0:
        y = y + rng.normal(0, noise_sigma, size=(n_rec, n_samp))
    y -= np.median(y, axis=1, keepdims=True)
    return y


# --------------------------------------------------------------------------
# quick estimators (same ones used to characterize the real data)
# --------------------------------------------------------------------------
def acf_tau_1e(x, ml=800):
    """1/e lag of the normalized ensemble ACF [s]."""
    n, L = x.shape
    nf = 1 << int(np.ceil(np.log2(2 * L)))
    X = np.fft.rfft(x, n=nf, axis=1)
    ac = np.fft.irfft((X * np.conj(X)).real, n=nf, axis=1)[:, :ml].mean(0)
    ac /= (L - np.arange(ml))
    r = ac / ac[0]
    below = np.where(r < np.exp(-1))[0]
    return (below[0] * DT) if len(below) else np.nan


def power_cv(x):
    p = (x ** 2).mean(1)
    return p.std() / p.mean()


def _with_noise(gen, noise_frac, **kw):
    """Generate noiseless, then add electronic noise at a fixed fraction of the
    signal RMS (absolute gain is arbitrary, so calibrate noise to the signal)."""
    y = gen(noise_sigma=0.0, **kw)
    return y + np.random.default_rng(9).normal(0, noise_frac * y.std(), y.shape)


def plot_demo(anode, shaper, h_a, h_s, source="default"):
    """Show a few simulated records of each config + their impulse responses."""
    import matplotlib.pyplot as plt
    t = np.arange(anode.shape[1]) * DT * 1e6
    fig, ax = plt.subplots(2, 2, figsize=(13, 7), gridspec_kw={"width_ratios": [3, 1]})
    for k in range(4):
        ax[0, 0].plot(t, anode[k] + k * 6 * anode.std(), lw=0.6)
        ax[1, 0].plot(t, shaper[k] + k * 6 * shaper.std(), lw=0.6)
    ax[0, 0].set_title("FAST sim (1-pole anode)")
    ax[1, 0].set_title("CSP sim (charge preamp)")
    for a_ in ax[:, 0]:
        a_.set_xlabel("t [us]"); a_.set_yticks([])
    ax[0, 1].plot(np.arange(len(h_a)) * DT * 1e6, h_a)
    ax[0, 1].set_title("h(t) anode"); ax[0, 1].set_xlabel("t [us]")
    ax[1, 1].plot(np.arange(len(h_s)) * DT * 1e6, h_s)
    ax[1, 1].set_title("h(t) preamp"); ax[1, 1].set_xlabel("t [us]")
    fig.suptitle(f"simulate_pmt — parametri: {source}")
    fig.tight_layout()
    plt.show()


def _fitted_params():
    """Load optimized parameters from fit_results.json (next to this file); None if absent."""
    import json, os
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit_results.json")
    if not os.path.exists(fp):
        return None
    with open(fp) as f:
        return json.load(f)


if __name__ == "__main__":
    # self-check: generated signals must reproduce the measured summary stats.
    # Gain is arbitrary -> noise given as a fraction of signal RMS (see report).

    # FAST: tau_fall=250ns, deep pileup -> CV at the Gaussian floor ~0.17
    a = _with_noise(simulate_events, 0.23, lam=3e7, h=h_onepole(), ser_cv=0.5, seed=1)
    tau_a, cv_a = acf_tau_1e(a) * 1e9, power_cv(a)
    print(f"anode-like : ACF 1/e = {tau_a:6.1f} ns (meas ~250)   CV = {cv_a:.3f} (meas 0.170)")
    assert 150 < tau_a < 400, tau_a
    assert 0.12 < cv_a < 0.24, cv_a

    # CSP: unipolar charge preamp, lambda~1.5MHz -> CV ~0.6 (above Gaussian floor)
    c = simulate_events(lam=1.5e6, h=h_preamp(), ser_cv=0.5, noise_sigma=0.0, seed=2)
    cv_c = power_cv(c)
    print(f"shaper-like: CV = {cv_c:.3f} (meas 0.635)")
    assert 0.5 < cv_c < 0.8, cv_c

    # OU-SDE form must agree with the event-sum for the one-pole case
    b = _with_noise(simulate_ou_sde, 0.23, lam=3e7, tau_fall=250e-9, ser_cv=0.5, seed=1)
    tau_b = acf_tau_1e(b) * 1e9
    print(f"OU-SDE     : ACF 1/e = {tau_b:6.1f} ns (should match event-sum)")
    assert 150 < tau_b < 400, tau_b
    print("self-check OK")

    # plot using the OPTIMIZED parameters from fit_results.json when available
    fit = _fitted_params()
    if fit:
        pa, pc = fit["FAST"], fit["CSP"]
        h_a = h_onepole(tau_rise=pa["tau_rise"], tau_fall=pa["tau_fall"])
        h_s = h_preamp(tau_rise=pc["tau_rise"], tau_fall=pc["tau_fall"])
        a = _with_noise(simulate_events, pa["noise_frac"], lam=pa["lam"], h=h_a, ser_cv=pa["ser_cv"], seed=1)
        c = _with_noise(simulate_events, pc["noise_frac"], lam=pc["lam"], h=h_s, ser_cv=pc["ser_cv"], seed=2)
        plot_demo(a, c, h_a, h_s, source="ottimizzati (fit_results.json)")
    else:
        plot_demo(a, c, h_onepole(), h_preamp(), source="default (nessun fit_results.json)")
