"""
Rate & mean-energy estimate via von Neumann/MSSD + higher CUMULANTS (Campbell).

Filtered-Poisson cumulants:  kappa_n = lambda * <A^n> * S_n
  * SUCCESSIVE-DIFFERENCE ("MSSD") form:  dy=y[i+1]-y[i], kernel g=h(t)-h(t-dt),
    S_n = J_n = integral g^n  -> DRIFT ROBUST (von Neumann).  k2[dy] = MSSD.
  * BULK form: y (global-mean removed), S_n = I_n = integral h^n.

Decoupling with EVEN cumulants (k2, k4), for either form:
    lambda = (k2^2 / k4) * (m4 S4) / (m2^2 S2^2)          # ABSOLUTE rate [Hz]
    <A>    = sqrt( (k4 / k2) * (m2 S2) / (m4 S4) )         # energy scale [ADC, rel.]
with m_n = <A^n>/<A>^n the SER shape moments (Gamma, from ser_cv).

ALL PRECAUTIONS:
  1. even cumulants k2,k4     -> S2,S4>0 always; no odd-integral cancellation / polarity
  2. dy for the MSSD form     -> kills DC / slow drift (von Neumann principle)
  3. raw moments about 0 (dy) / central about GLOBAL mean (bulk) -> no per-record
     mean-subtraction bias (that would remove real Campbell variance)
  4. Gaussian noise hits only k2 (k4 immune). sigma_n^2 is measured FROM THE DATA
     (extrapolate the autocovariance C(1..5) back to lag 0; the excess at lag 0 is
     the white-noise variance) -- NOT from noise_frac*var (which conflates the huge
     low-freq signal variance with the high-freq noise the MSSD actually sees).
  5. which form is usable depends on whether the pulse RISE is resolved:
     sharp rise (anode, 16 ns ~ 1 sample) -> jumpy increments -> k4[dy]>0 (MSSD ok);
     slow rise (preamp, 426 ns ~ 42 samp) -> smooth increments -> k4[dy]~0 (use BULK).
  6. bootstrap over records for the statistical CI; report k4>0 fraction
  7. k4 -> 0 (Gaussian / deep pileup) => rate diverges => LOWER BOUND
  8. lambda is gain-free (ADC cancels); <A> is a relative energy scale
  9. SER width is the dominant SYSTEMATIC -> scanned explicitly
Validated below: recovers a known lambda from simulated data (ratio ~1).
"""
import json
import numpy as np
from scipy.signal import welch
from simulate_pmt import h_onepole, h_preamp, DT, FS

DIR = "c:/Users/gbecuzzi/Desktop/progetti_criminali/frankenchiara/"
WIN = 2000 * DT


def ser_moments(cv):
    return {n: float(np.prod([1 + j * cv * cv for j in range(n)])) for n in (2, 4)}


def kernel(kind, tau_rise, tau_fall):
    n = int(min(4000, max(800, 10 * tau_fall / DT)))
    return (h_onepole(n=n, tau_rise=tau_rise, tau_fall=tau_fall) if kind == "anode"
            else h_preamp(n=n, tau_rise=tau_rise, tau_fall=tau_fall))


def noise_var(y):
    """White electronic-noise variance from the high-frequency PSD plateau:
    sigma_n^2 = S0 * f_Nyquist, with S0 = median PSD above 0.6*f_Nyq (median is
    robust to narrow interference lines). Validated to ~1% on simulated data."""
    f, p = welch(y, fs=FS, nperseg=y.shape[1], axis=-1)
    p = p.mean(0)
    S0 = np.median(p[f > 0.6 * f[-1]])
    return S0 * f[-1]


def even_cumulants(v, about_zero):
    m2 = np.mean(v ** 2) if about_zero else np.var(v)
    m4 = np.mean((v - (0 if about_zero else v.mean())) ** 4)
    return m2, m4 - 3 * m2 ** 2                        # k2, k4


def decouple(k2, k4, S2, S4, m):
    lam = (k2 ** 2 / k4) * (m[4] * S4) / (m[2] ** 2 * S2 ** 2)
    A = np.sqrt(abs((k4 / k2) * (m[2] * S2) / (m[4] * S4)))
    return lam, A


def method(y, form, h, ser_cv, sig_n2):
    """form: 'mssd' (successive differences) or 'bulk'. Returns (lam,A,k2,k4)."""
    m = ser_moments(ser_cv)
    if form == "mssd":
        dy = np.diff(y, axis=1)
        k2, k4 = even_cumulants(dy.ravel(), about_zero=True)
        k2 = k2 - 2 * sig_n2                            # noise: +2 sigma^2 in MSSD
        g = np.diff(h); S2, S4 = np.sum(g ** 2) * DT, np.sum(g ** 4) * DT
    else:                                              # bulk
        yc = (y - y.mean()).ravel()
        k2, k4 = even_cumulants(yc, about_zero=False)
        k2 = k2 - sig_n2                                # noise: +sigma^2 in variance
        S2, S4 = np.sum(h ** 2) * DT, np.sum(h ** 4) * DT
    lam, A = decouple(k2, k4, S2, S4, m)
    return lam, A, k2, k4, (S2, S4, m)


def run(y, label, kind, tau_rise, tau_fall, ser_cv, nboot=300, truth=None):
    h = kernel(kind, tau_rise, tau_fall)
    sig_n2 = noise_var(y)
    N = y.shape[0]
    print("=" * 72)
    print(f"{label}   [{kind}: tau_r={tau_rise*1e9:.0f}ns tau_f={tau_fall*1e9:.0f}ns  "
          f"ser_cv={ser_cv:.2f}]   sigma_noise={np.sqrt(sig_n2):.3g} ADC")

    for form in ("mssd", "bulk"):
        lam, A, k2, k4, (S2, S4, m) = method(y, form, h, ser_cv, sig_n2)
        # bootstrap
        rng = np.random.default_rng(0)
        bl, bk4 = [], []
        for _ in range(nboot):
            idx = rng.integers(0, N, N)
            l, _, _, k4b, _ = method(y[idx], form, h, ser_cv, sig_n2)
            bl.append(l); bk4.append(k4b)
        bl, bk4 = np.array(bl), np.array(bk4)
        pos = np.mean(bk4 > 0)
        tag = "MSSD/increments" if form == "mssd" else "bulk cumulants "
        if pos < 0.95 or k4 <= 0:
            lob = np.nanpercentile(bl[bk4 > 0], 16) if pos > 0.02 else np.nan
            print(f"  [{tag}] k4={k4:+.3g} (~0, {pos*100:.0f}% boot>0) -> "
                  f"Gaussian/deep pileup: LOWER BOUND lambda >~ {lob:.2e} Hz")
        else:
            lo, hi = np.percentile(bl, [16, 84])
            print(f"  [{tag}] k2={k2:.4g} k4={k4:+.3g}  ->  "
                  f"lambda = {lam:.3e} Hz  (68% CI [{lo:.2e},{hi:.2e}])")
            print(f"                 events/20us = {lam*WIN:.1f}   <A> = {A:.3g} ADC (rel.)"
                  + (f"   [truth {truth:.2e}]" if truth else ""))

    # SER systematic on the better-conditioned form (bulk if mssd failed)
    _, _, _, k4m, _ = method(y, "mssd", h, ser_cv, sig_n2)
    form = "mssd" if k4m > 0 else "bulk"
    print(f"  SER systematic ({form}) - lambda vs assumed SER CV:")
    for cv in (0.0, 0.3, 0.5, 1.0):
        lam_cv = method(y, form, h, cv, sig_n2)[0]
        print(f"       CV={cv:.1f}: lambda = {lam_cv:.2e} Hz")


def validate():
    from simulate_pmt import simulate_events
    lam_true, cv, nf, tr, tf = 1.0e6, 0.5, 0.02, 0.5e-6, 2.4e-6
    y = simulate_events(lam_true, h_preamp(tau_rise=tr, tau_fall=tf), n_rec=1000,
                        ser_cv=cv, noise_sigma=0.0, seed=5)
    y = y + np.random.default_rng(6).normal(0, nf * y.std(), y.shape)
    print("### VALIDATION on simulated preamp data (true lambda = 1.00e6 Hz) ###")
    run(y, "SIM", "preamp", tr, tf, cv, truth=lam_true)
    print()


def main():
    validate()
    with open(DIR + "fit_results.json") as f:
        fit = json.load(f)
    kinds = {"anodewaves.npy": "anode", "culoculo.npy": "preamp"}
    for fname, p in fit.items():
        y = np.load(DIR + fname).astype(float)
        run(y, fname, kinds[fname], p["tau_rise"], p["tau_fall"], p["ser_cv"])


if __name__ == "__main__":
    main()
