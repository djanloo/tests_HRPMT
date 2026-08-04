"""
Rise-time shot-noise simulator via a SECOND-ORDER jump-SDE (two coupled
first-order SDEs), integrated by explicit time-stepping -- NO convolution with
an analytic response kernel.

Physical picture: each event is the impulse response of a two-pole linear
system, i.e. a double-exponential pulse  exp(-t/tau_f) - exp(-t/tau_r)  with a
FINITE rise (tau_r) and fall (tau_f). When tau_r -> tau_f it becomes the alpha
function t*exp(-t/tau) (a genuine double pole). In state space:

    dx1 = -(x1/tau_r) dt + dJ(t)              x1 = fast stage, receives the jumps
    dx2 = (-(x2/tau_f) + x1/tau_r) dt          x2 = slow stage, driven by x1
    y   = polarity * x2  +  white noise        (output)

    J(t) = sum_k A_k delta(t - t_k)   compound Poisson: arrivals ~ Poisson(lam),
                                      marks A_k ~ Gamma(mean=ser_mean, cv=ser_cv)

Everything carries PHYSICAL UNITS (no gain-relative fudge factors):
    lam         [Hz]      event rate
    tau_rise    [s]       rise time      (fast pole)
    tau_fall    [s]       fall time      (slow pole)
    ser_mean    [ADC]     mean PEAK amplitude of a single-event pulse
    ser_cv      [-]       coeff. of variation of the single-event amplitude
    noise_sigma [ADC]     white-noise RMS per sample  (passed in by hand)

The two-pole linear part is advanced with the EXACT discretization
Phi = expm(M*dt), which is stable even when tau_rise ~ dt (the anode rise is
~1.7 samples at 100 MS/s) where Euler-Maruyama would be inaccurate. It is still
an SDE integrator (exact solution of the linear segment between jumps), not a
kernel convolution: the waveform emerges from stepping the state.

Run directly for a self-check (rise/fall recovered, noise sigma recovered,
variance ~ ser_mean^2).
"""
import numpy as np
from scipy.linalg import expm

FS = 100e6                 # sampling rate [Hz]
DT = 1.0 / FS              # sample period [s]


def _state_matrix(tau_rise, tau_fall):
    """Continuous-time state matrix M of the two-pole cascade (x1 -> x2)."""
    return np.array([[-1.0 / tau_rise, 0.0],
                     [1.0 / tau_rise, -1.0 / tau_fall]])


def single_event_response(tau_rise, tau_fall, n=None):
    """Discrete impulse response y[n] (peak-normalized to 1) of the two-pole
    system to ONE unit jump into x1, using the same recursion as the simulator.
    Returns the array and its (un-normalized) peak value `gpk` -- the factor that
    maps an injected jump to the resulting pulse peak."""
    Phi = expm(_state_matrix(tau_rise, tau_fall) * DT)
    if n is None:
        n = int(np.clip(12 * tau_fall / DT, 200, 20000))
    x = np.array([1.0, 0.0])          # unit jump into x1 at sample 0
    y = np.empty(n)
    for i in range(n):
        y[i] = x[1]                   # record x2 (output) before propagating
        x = Phi @ x
    gpk = y.max()
    return y / gpk, gpk


def simulate_sde(lam, tau_rise, tau_fall, ser_mean, ser_cv, noise_sigma,
                 n_rec=1000, n_samp=2000, polarity=1.0, spectrum=None, seed=0):
    """Generate (n_rec, n_samp) waveforms in ADC units. Per-record mean removed
    at the end (matches how the real DC-coupled runs are pre-processed).

    spectrum: an energy_spectrum.Spectrum (a MEASURED pulse-height histogram from
    the CAEN DDE) to draw the marks from; `ser_mean` then sets the mean peak and
    `ser_cv` is ignored (the spectrum carries its own width). Default None keeps
    the Gamma marks -- adequate in deep pileup, wrong at low rate where the
    individual pulse heights are resolved and must show the photopeaks."""
    rng = np.random.default_rng(seed)
    Phi = expm(_state_matrix(tau_rise, tau_fall) * DT)
    _, gpk = single_event_response(tau_rise, tau_fall)   # peak of a unit-jump pulse

    # per-bin injected charge into x1, scaled so a mark of value m -> pulse peak m.
    if spectrum is not None:
        from energy_spectrum import poisson_marks
        marks = poisson_marks(lam, DT, (n_rec, n_samp), ser_mean, spectrum, rng)
    else:
        # counts ~ Poisson(lam*dt); the summed mark of c iid Gamma(k, theta) is
        # exactly Gamma(c*k, theta), so draw the aggregate per bin in one shot.
        counts = rng.poisson(lam * DT, size=(n_rec, n_samp))
        if ser_cv > 0:
            k = 1.0 / ser_cv ** 2
            theta = ser_mean * ser_cv ** 2               # mean = k*theta = ser_mean
            shape = counts * k
            marks = rng.standard_gamma(np.where(shape > 0, shape, 1.0)) * theta
            marks[shape == 0] = 0.0
        else:
            marks = counts * ser_mean
    inject = marks / gpk                                 # (n_rec, n_samp) jumps into x1

    X = np.zeros((n_rec, 2))
    y = np.empty((n_rec, n_samp))
    PhiT = Phi.T
    for n in range(n_samp):
        X[:, 0] += inject[:, n]                          # jumps at sample n
        y[:, n] = X[:, 1]                                # output = x2
        X = X @ PhiT                                     # exact propagation to n+1

    y *= polarity
    if noise_sigma > 0:
        y += rng.normal(0.0, noise_sigma, size=(n_rec, n_samp))
    y -= y.mean(axis=1, keepdims=True)
    return y


# --------------------------------------------------------------------------
if __name__ == "__main__":
    from scipy.signal import welch
    tr, tf = 40e-9, 300e-9

    # (1) rise/fall recovered from the single-event response
    resp, gpk = single_event_response(tr, tf)
    pk = resp.argmax()
    t10 = np.argmax(resp >= 0.1)
    t90 = np.argmax(resp >= 0.9)
    rise_1090 = (t90 - t10) * DT
    tail = resp[pk:]
    fall_1e = (np.argmax(tail < np.exp(-1))) * DT        # 1/e from peak
    print(f"single-event: peak@{pk*DT*1e9:.0f} ns  rise(10-90)={rise_1090*1e9:.0f} ns  "
          f"fall(1/e from peak)={fall_1e*1e9:.0f} ns  (tau_r={tr*1e9:.0f}, tau_f={tf*1e9:.0f})")
    # 10-90 rise of a bi-exponential is ~2.2*tau_r when tau_f>>tau_r; fall 1/e ~ tau_f
    assert 1.2 * tr < rise_1090 < 3.5 * tr, rise_1090
    assert 0.7 * tf < fall_1e < 1.5 * tf, fall_1e

    # (2) white-noise sigma is recovered from the high-f PSD plateau
    NS = 20.0
    y = simulate_sde(lam=1e5, tau_rise=tr, tau_fall=tf, ser_mean=50.0, ser_cv=0.4,
                     noise_sigma=NS, n_rec=400, n_samp=2000, seed=1)
    f, p = welch(y, fs=FS, nperseg=2000, axis=-1); p = p.mean(0)
    sig_meas = np.sqrt(np.median(p[f > 0.6 * f[-1]]) * f[-1])
    print(f"noise sigma: set {NS:.1f} ADC -> measured (high-f) {sig_meas:.1f} ADC")
    assert 0.85 * NS < sig_meas < 1.15 * NS, sig_meas

    # (3) variance scales as ser_mean^2 (gain^2), at fixed rate, noise off
    v1 = simulate_sde(3e6, tr, tf, ser_mean=50.0, ser_cv=0.4, noise_sigma=0.0,
                      n_rec=400, seed=2).var()
    v2 = simulate_sde(3e6, tr, tf, ser_mean=100.0, ser_cv=0.4, noise_sigma=0.0,
                      n_rec=400, seed=2).var()
    print(f"variance: ser_mean x2 -> var x{v2/v1:.2f} (expect ~4)")
    assert 3.5 < v2 / v1 < 4.5, v2 / v1
    print("self-check OK")
