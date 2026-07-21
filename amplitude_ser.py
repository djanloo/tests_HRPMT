"""
What can the piled-up data tell us about P(A), the jump-amplitude (SER / per-event
energy) distribution?

Each cumulant gives one moment:  kappa_n = lambda <A^n> I_n.  A lambda- and
gain-INDEPENDENT combination isolates the SER *shape*:
    kappa_2 kappa_4 / kappa_3^2 = [<A2><A4>/<A3>^2] * [I2 I4 / I3^2]
and for a Gamma SER:   <A2><A4>/<A3>^2 = (1+3 cv^2)/(1+2 cv^2).
So in principle kappa_2,3,4 + pulse shape  ->  the SER width cv.

RESULT (demonstrated by the validation below): this DOES NOT WORK on piled-up data.
It needs the odd cumulant kappa_3, which in pileup is (a) small -- the signal
Gaussianizes, kappa_3 -> 0 as ~1/sqrt(lambda tau) -- and (b) has a huge estimator
variance; since kappa_3 sits SQUARED in the denominator, the error explodes.
Even a CLEAN simulation with 20000 records and KNOWN cv recovers it poorly
(cv=0.8->0.74, cv=0.5->0.32, cv=0.3->fails). On the real data it is unusable.

=> From piled-up shot noise you can measure the rate (even cumulants, see
   mssd_cumulant_estimate.py) and <A^2>*lambda (variance), and -- with a pedestal --
   the mean energy <A^2>/<A> (Campbelling). The SHAPE of P(A) is NOT recoverable;
   it requires RESOLVED single events (low-rate / dark run -> histogram pulse areas).
"""
import numpy as np
from simulate_pmt import h_onepole, h_preamp, DT

DIR = "c:/Users/gbecuzzi/Desktop/progetti_criminali/frankenchiara/"


def bulk_cumulants(y):
    v = (y - y.mean()).ravel()
    m2, m3, m4 = np.mean(v ** 2), np.mean(v ** 3), np.mean(v ** 4)
    return m2, m3, m4 - 3 * m2 ** 2                    # k2, k3, k4 (central)


def ser_cv(y, h):
    I2, I3, I4 = (np.sum(h ** n) * DT for n in (2, 3, 4))
    k2, k3, k4 = bulk_cumulants(y)
    if k3 == 0:
        return np.nan
    Rser = (k2 * k4 / k3 ** 2) / (I2 * I4 / I3 ** 2)   # = (1+3cv^2)/(1+2cv^2)
    cv2 = (Rser - 1) / (3 - 2 * Rser)
    return np.sqrt(cv2) if (1 < Rser < 1.5 and cv2 >= 0) else np.nan


def _clean_shotnoise(lam, cv, N, h, L=2000, seed=1):
    """Shot noise WITHOUT per-record baseline subtraction (which would corrupt k3)."""
    r = np.random.default_rng(seed)
    c = r.poisson(lam * DT, (N, L)).astype(float) * r.gamma(1 / cv ** 2, cv ** 2, (N, L))
    nf = 1 << int(np.ceil(np.log2(L + len(h))))
    return np.fft.irfft(np.fft.rfft(c, n=nf, axis=1) * np.fft.rfft(h, n=nf), n=nf, axis=1)[:, :L]


if __name__ == "__main__":
    h = h_preamp(tau_rise=0.5e-6, tau_fall=2.4e-6)
    print("VALIDATION on clean simulation (known cv) -- ideal, no baseline subtraction:")
    for cv in (0.3, 0.5, 0.8):
        rec = [ser_cv(_clean_shotnoise(1e6, cv, 10000, h, seed=s), h) for s in (1, 2)]
        ok = [x for x in rec if np.isfinite(x)]
        got = f"{np.mean(ok):.2f}" if ok else "FAILED"
        print(f"  true cv={cv}:  recovered {got}  (fails: {len(rec)-len(ok)}/{len(rec)})"
              f"  -> biased/ill-conditioned")
    print("\n=> The SER shape is NOT reliably recoverable even in the ideal case;")
    print("   on the real piled-up data it is unusable. Measure P(A) with a")
    print("   low-rate/dark run (resolved single pulses), not from pileup.")
