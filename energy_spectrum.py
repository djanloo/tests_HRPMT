"""
EMPIRICAL energy spectrum for the marks A_k of the shot-noise simulators.

Why: a Gamma is a single smooth bump. A real PMT amplitude spectrum has
photopeaks, a Compton continuum, escape peaks and a low-energy pile of
backscatter. At high rate deep pileup washes the difference out (CLT), but at
LOW rate the waveform is a train of RESOLVED pulses whose peak heights ARE the
spectrum -- and there a Gamma is simply the wrong picture.

Source of the spectra: the CAEN Digital Detector Emulator control software
(DT4800 Control Software, `examples/spectra/`) -- the histograms the DDE itself
samples from to synthesize pulses. Collected in `spectra/` next to this file so
the repo does not depend on the local install. Two formats, both 16384 channels
and both read by `load()`:

  *.csv   one integer count per line, one line per channel  (DDE export)
  *.xml   ANSI N42.42, counts in the <ChannelData> element  (MC2 / DT5780 export)

Collected here:

  Co57.csv        NaI-like, 122 keV line dominant + low-energy pile  CV 0.38
  Co60LowRes.csv  NaI, 1173+1332 keV merged, wide Compton continuum  CV 0.75
  Fe55.csv        5.9 keV, single narrow line                        CV 0.14
  complex.csv     multi-nuclide mixture, many peaks                 CV 0.72
  co60HPGE.xml    Co60 on HPGe: sharp lines, high resolution
  EU-HPGE.xml     Eu152 on HPGe: the busiest of the set, ~10 lines

Not collected: `cobalto.csv` (byte-identical to Co60LowRes.csv) and the
`*.spectrum` files (Type=Peaks -- a synthetic peak list, not a measured
histogram). Cs137 and Am241 are NOT among the DDE examples; drop any DDE- or
MC2-exported file into `spectra/` and it becomes loadable by name.

Normalization: every spectrum is scaled to  <A> = 1. So `ser_mean` in the
simulators keeps its physical meaning (mean single-event peak, ADC) and the
spectrum contributes only the SHAPE -- i.e. the normalized moments
m_n = <A^n>/<A>^n that Campbell's theorem needs (see mssd_cumulant_estimate).

Run directly for a self-check (moments reproduced, low-rate peak heights
recover the input spectrum, Campbell variance holds); `--plot` to look at it.
"""
import glob
import os

import numpy as np

DDE_DIR = "C:/Program Files (x86)/CAEN/DT4800/examples/spectra"
LOCAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spectra")


class Spectrum:
    """Measured pulse-height histogram, rescaled so that <A> = 1.

    lld: lower-level-discriminator channel. Channels below it are zeroed.
    Default 0 = use the histogram verbatim, which is what the DDE does; raise it
    to cut the MCA noise floor near channel 0 (Co57 has ~400k counts in the
    first 512 channels that are instrumental, not events).
    """

    synthetic = False       # True only for the modeled NaI spectra, see nai()

    def __init__(self, counts, name="?", lld=0):
        c = np.asarray(counts, dtype=float).copy()
        c[:lld] = 0.0
        if not c.sum() > 0:
            raise ValueError(f"{name}: empty spectrum (lld={lld} cut everything?)")
        self.name = name
        self.w = c / c.sum()                       # channel probabilities
        self.cdf = np.cumsum(self.w)
        ch = np.arange(len(c)) + 0.5               # bin centres
        self.scale = 1.0 / float((self.w * ch).sum())   # channel -> amplitude, <A>=1

    def sample(self, n, rng):
        """n iid marks with mean exactly 1. Inverse-CDF on the channel index plus
        uniform jitter inside the channel -- an MCA bin is a quantization of a
        continuous amplitude, not a delta, and U[i,i+1) has mean i+0.5, matching
        the bin centre used by `scale` and `moment`."""
        i = np.searchsorted(self.cdf, rng.random(n), side="right")
        return (np.minimum(i, len(self.cdf) - 1) + rng.random(n)) * self.scale

    def moment(self, n):
        """m_n = <A^n> with <A> = 1: the SER shape moment Campbell's theorem uses."""
        a = (np.arange(len(self.w)) + 0.5) * self.scale
        return float((self.w * a ** n).sum())

    @property
    def cv(self):
        return float(np.sqrt(self.moment(2) - 1.0))

    def __repr__(self):
        tag = " MODELLO" if self.synthetic else ""
        return f"<Spectrum {self.name}{tag}: {len(self.w)} ch, CV={self.cv:.3f}>"


def available():
    """{name: path} of every spectrum in `spectra/`, then the DDE install as
    fallback (a name present in both resolves to the local copy)."""
    seen = {}
    for d in (LOCAL_DIR, DDE_DIR):
        for f in sorted(glob.glob(os.path.join(d, "*.csv")) +
                        glob.glob(os.path.join(d, "*.xml"))):
            seen.setdefault(os.path.splitext(os.path.basename(f))[0], f)
    return seen


def _read(path):
    """Counts per channel from a DDE CSV or an ANSI N42.42 XML."""
    if path.lower().endswith(".xml"):
        import xml.etree.ElementTree as ET
        # match on the local tag name: N42 files carry a default namespace
        text = next(e.text for e in ET.parse(path).iter()
                    if e.tag.rpartition("}")[2] == "ChannelData")
        return np.fromstring(text, sep=" ")
    return np.loadtxt(path)


def load(name, lld=0, **kw):
    """`name` is a MEASURED spectrum -- a source name ('Co57', 'Co60', 'Fe55',
    'complex', 'EU'; substring, case-insensitive) or a path to a spectrum file --
    or one of the MODELED NaI ones ('Cs137', 'Am241', see `nai()`; those carry
    `.synthetic = True`, and `**kw` goes to `nai()`)."""
    if name in NUCLIDES:
        return nai(name, **kw)
    if os.path.exists(name):
        path = name
    else:
        hits = [p for k, p in available().items() if name.lower() in k.lower()]
        if not hits:
            raise FileNotFoundError(
                f"{name!r}: no spectrum in {LOCAL_DIR} or {DDE_DIR}. Have measured "
                f"{sorted(available())}, modeled {sorted(NUCLIDES)}")
        path = hits[0]
    return Spectrum(_read(path), os.path.splitext(os.path.basename(path))[0], lld)


# --------------------------------------------------------------------------
# Cs137 / Am241 on NaI: NOT measured, MODELED (the DDE ships neither, and these
# are the two sources of the real runs -- 2x2" NaI, see dose_estimation/dose_report.md)
# --------------------------------------------------------------------------
MEC2 = 510.999                                 # electron rest energy [keV]

# nuclide -> (gamma line [keV], photofraction, backscatter weight, X-ray line+weight)
# photofraction = peak/total for 2x2" NaI: ~0.30 at 662 keV, ~1 at 59.5 keV where
# the photoelectric effect dominates and there is no usable Compton continuum.
NUCLIDES = {
    "Cs137": dict(e0=661.657, photofrac=0.30, backscatter=0.06, xray=(32.0, 0.07)),
    "Am241": dict(e0=59.541, photofrac=0.97, backscatter=0.0, xray=(17.0, 0.10)),
}


def _kn_sample(e0, n, rng):
    """n Compton electron energies [keV] from the Klein-Nishina cross-section,
    by rejection on dsigma/dP.  P = E'/E0 in [1/(1+2a), 1],  a = E0/m_e c^2:

        dsigma/dP  ~  P + 1/P - sin^2(theta),   cos(theta) = 1 - (1-P)/(aP)

    The deposited energy is the electron recoil T = E0 (1 - P) -- i.e. the true
    Compton continuum, ending at the Compton edge T_max = E0 2a/(1+2a).
    """
    a = e0 / MEC2
    lo = 1.0 / (1.0 + 2.0 * a)

    def f(p):
        cos_t = 1.0 - (1.0 - p) / (a * p)
        return p + 1.0 / p - (1.0 - cos_t ** 2)

    fmax = f(np.linspace(lo, 1.0, 2000)).max()
    out = np.empty(0)
    while len(out) < n:                        # rejection sampling
        p = rng.uniform(lo, 1.0, 2 * (n - len(out)) + 64)
        out = np.concatenate([out, p[rng.random(len(p)) * fmax < f(p)]])
    return e0 * (1.0 - out[:n])


def nai(nuclide, res662=0.08, nch=16384, full_scale=None, n_mc=4_000_000, seed=0,
        **override):
    """Pulse-height spectrum of `nuclide` ('Cs137'|'Am241') on a NaI(Tl) scintillator.

    MODELED, not measured -- say so wherever a result depends on it. Built by
    Monte Carlo over the deposit channels (photopeak / Klein-Nishina Compton
    continuum / backscatter peak / K-X-ray escape), each sample smeared by the
    detector resolution, then histogrammed on the same 16384-channel grid as the
    DDE files so it is a drop-in `Spectrum`.

    res662   FWHM/E at 662 keV, scaled as 1/sqrt(E) for the photostatistics (so ~27%
             at 59.5 keV with the default). Three measured numbers for THIS detector,
             a Scionix 51B51 with a 10-stage Hamamatsu R10601-100 (hardware/):
               6.6%  the crystal's own testsheet, s/n S1AB5195 at -570 V -- the floor,
                     measured by Scionix on their electronics
               8.0%  the default here: a round number picked before any of this was known
               9.1%  implied by our own PHA on the Am-241 run (pha_lowrate.py), i.e. what
                     the whole chain actually delivers, noise and pileup included
             Use 9.1% to model OUR data, 6.6% for what the crystal could do.
    Every weight in NUCLIDES is overridable by keyword -- these are calibration
    knobs for a real crystal, geometry and shielding, not constants of nature.
    """
    p = dict(NUCLIDES[nuclide], **override)
    e0 = p["e0"]
    full_scale = full_scale if full_scale else 2.0 * e0
    rng = np.random.default_rng(seed)

    w_pk, w_bs, (e_x, w_x) = p["photofrac"], p["backscatter"], p["xray"]
    w_co = max(0.0, 1.0 - w_pk - w_bs - w_x)
    n = {k: int(n_mc * v) for k, v in
         dict(pk=w_pk, co=w_co, bs=w_bs, x=w_x).items()}

    e_bs = e0 / (1.0 + 2.0 * e0 / MEC2)        # 180-deg backscatter, 184 keV for Cs137
    dep = np.concatenate([
        np.full(n["pk"], e0),                  # full absorption
        _kn_sample(e0, n["co"], rng),          # Compton continuum
        np.full(n["bs"], e_bs),                # backscatter off shielding/source
        np.full(n["x"], e_x),                  # K-X-ray / L-X-ray line
    ])
    # detector resolution: FWHM/E = res662 * sqrt(662/E)  ->  sigma [keV]
    sigma = dep * res662 * np.sqrt(661.657 / np.maximum(dep, 1e-3)) / 2.355
    meas = dep + rng.normal(0.0, 1.0, dep.size) * sigma

    counts, _ = np.histogram(meas, bins=nch, range=(0.0, full_scale))
    s = Spectrum(counts, f"{nuclide}(NaI,sim)")
    s.synthetic = True
    s.kev_per_ch = full_scale / nch
    return s


def poisson_marks(lam, dt, shape, ser_mean, spec, rng):
    """Per-bin summed charge of a compound Poisson process with EMPIRICAL marks.

    Poisson counts per time bin, then that many iid draws from `spec`,
    scatter-added back into their bins. Exact at any rate. The Gamma shortcut the
    simulators use (sum of c iid Gamma(k,th) == Gamma(c*k,th), so the aggregate is
    one draw) has no analogue for an arbitrary spectrum, so the events are drawn
    individually -- ~lam*dt*shape.size of them, cheap while lam*dt << 1.
    """
    counts = rng.poisson(lam * dt, size=shape)
    tot = int(counts.sum())
    if tot == 0:
        return np.zeros(shape)
    a = spec.sample(tot, rng) * ser_mean
    idx = np.repeat(np.arange(counts.size), counts.ravel())
    return np.bincount(idx, weights=a, minlength=counts.size).reshape(shape)


# --------------------------------------------------------------------------
def _plot(spec, y, heights, dt):
    import matplotlib.pyplot as plt
    a = (np.arange(len(spec.w)) + 0.5) * spec.scale
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].step(a, spec.w, lw=0.7)
    ax[0].set_yscale("log"); ax[0].set_xlabel("A  (<A> = 1)")
    src = "modello NaI" if spec.synthetic else "DDE misurato"
    ax[0].set_title(f"{src}: {spec.name}  (CV={spec.cv:.2f})")
    t = np.arange(y.shape[1]) * dt * 1e6
    ax[1].plot(t, y[0], lw=0.6)
    ax[1].set_xlabel("t [us]"); ax[1].set_ylabel("ADC")
    ax[1].set_title("waveform a basso rate (impulsi risolti)")
    ax[2].hist(heights, bins=200, histtype="step", density=True, label="picchi misurati")
    ax[2].step(a * heights.mean(), spec.w / spec.scale / heights.mean(), lw=0.7,
               label="spettro in ingresso")
    ax[2].set_yscale("log"); ax[2].set_xlabel("altezza di picco [ADC]")
    ax[2].set_title("spettro ricostruito dalla waveform"); ax[2].legend()
    fig.tight_layout()
    fig.savefig("energy_spectrum.png", dpi=110)
    plt.show()


if __name__ == "__main__":
    import sys
    from scipy.signal import find_peaks
    from sde_pulse_sim import DT, simulate_sde, single_event_response

    # (0) every spectrum in the collection loads, in both formats
    for nm in sorted(available()):
        s = load(nm)
        print(f"  {nm:16s} {len(s.w):6d} ch  CV={s.cv:.3f}  m2={s.moment(2):.3f}  "
              f"m4={s.moment(4):.3f}")
        assert 0.05 < s.cv < 3.0, (nm, s.cv)

    # (0b) modeled NaI: photopeak on the right channel, Compton edge in the right place
    for nm, edge in (("Cs137", 477.3), ("Am241", None)):
        s = load(nm)
        ch_pk = int(np.argmax(s.w[len(s.w) // 4:]) + len(s.w) // 4)  # skip the X-ray line
        e_pk = (ch_pk + 0.5) * s.kev_per_ch
        print(f"  {s.name:16s} {len(s.w):6d} ch  CV={s.cv:.3f}  m2={s.moment(2):.3f}  "
              f"m4={s.moment(4):.3f}  fotopicco @ {e_pk:.1f} keV "
              f"({NUCLIDES[nm]['e0']:.1f})")
        assert abs(e_pk / NUCLIDES[nm]["e0"] - 1) < 0.03, (nm, e_pk)
        if edge:   # Compton edge: cumulative counts must roll off there, before the peak
            e = (np.arange(len(s.w)) + 0.5) * s.kev_per_ch
            band = s.w[(e > 0.75 * edge) & (e < edge)].sum()
            gap = s.w[(e > 1.05 * edge) & (e < 0.9 * NUCLIDES[nm]["e0"])].sum()
            print(f"  {'':16s} spalla Compton {edge:.0f} keV: peso sotto={band:.3f} "
                  f"valle sopra={gap:.3f}")
            assert band > 3 * gap, (band, gap)

    # Am241 at 94 uSv/h is the real resolved-pulse run (dose_report.md) -- the exact
    # case a Gamma gets wrong -- so the rest of the checks run on it.
    spec = load("Am241")
    assert 0.1 < spec.cv < 2.0, spec.cv

    # (1) sample() reproduces the histogram's own moments
    rng = np.random.default_rng(0)
    s = spec.sample(2_000_000, rng)
    print(f"sample: <A>={s.mean():.4f} (1)  m2={np.mean(s**2):.3f} ({spec.moment(2):.3f})  "
          f"m4={np.mean(s**4):.3f} ({spec.moment(4):.3f})")
    assert abs(s.mean() - 1.0) < 0.005, s.mean()
    assert abs(np.mean(s ** 2) / spec.moment(2) - 1) < 0.02
    assert abs(np.mean(s ** 4) / spec.moment(4) - 1) < 0.10

    # (2) LOW rate: pulses are resolved, so their peak heights must BE the spectrum.
    #     This is the case a Gamma gets qualitatively wrong.
    tr, tf, AMP, LAM = 40e-9, 300e-9, 100.0, 1.7e5    # LAM = Am241 94 uSv/h run
    y = simulate_sde(LAM, tr, tf, ser_mean=AMP, ser_cv=0.0, noise_sigma=0.0,
                     n_rec=400, n_samp=2000, spectrum=spec, seed=1)
    pk, _ = find_peaks(y.ravel(), height=0.02 * AMP, distance=int(4 * tf / DT))
    hh = y.ravel()[pk]
    print(f"picchi risolti: n={len(hh)}  <h>={hh.mean():.1f} ADC (atteso ~{AMP:.0f})  "
          f"CV={hh.std()/hh.mean():.3f} (spettro {spec.cv:.3f})")
    assert 0.85 * AMP < hh.mean() < 1.15 * AMP, hh.mean()
    assert abs(hh.std() / hh.mean() - spec.cv) < 0.10, hh.std() / hh.mean()

    #     ...and the STRUCTURE survives, which is the whole point: Am241 has the
    #     17 keV L-X-ray line, the 59.5 keV photopeak, and a deep valley between
    #     them. Any unimodal mark law (Gamma included) fills that valley in.
    xray = AMP * NUCLIDES["Am241"]["xray"][0] / NUCLIDES["Am241"]["e0"]
    dens, edges = np.histogram(hh, bins=120, range=(0, 2 * AMP), density=True)
    mid = 0.5 * (edges[1:] + edges[:-1])
    # floor the valley at 0.1% of the mode so the ratios below cannot pass on a 0
    valley = max(dens[(mid > 1.6 * xray) & (mid < 0.6 * AMP)].max(), 1e-3 * dens.max())
    print(f"struttura: picco X {dens[abs(mid-xray) < 0.15*xray].max():.2e}  "
          f"valle {valley:.2e}  fotopicco {dens[abs(mid-AMP) < 0.15*AMP].max():.2e}")
    assert dens[abs(mid - xray) < 0.15 * xray].max() > 5 * valley, "riga X persa"
    assert dens[abs(mid - AMP) < 0.15 * AMP].max() > 20 * valley, "fotopicco perso"

    # (3) Campbell:  var(y) = lam * <A^2> * I_2,  <A^2> from the spectrum.
    #     Measured runs ~8% low, as expected: simulate_sde removes the per-record
    #     mean, and pulses at the start of a record are truncated (state starts at 0).
    resp, _ = single_event_response(tr, tf)
    I2 = float(np.sum(resp ** 2) * DT)
    var_pred = LAM * (AMP ** 2 * spec.moment(2)) * I2
    print(f"Campbell: var misurata={y.var():.4g}  prevista={var_pred:.4g}  "
          f"rapporto={y.var()/var_pred:.3f}")
    assert 0.85 < y.var() / var_pred < 1.10, y.var() / var_pred
    print("self-check OK")

    if "--plot" in sys.argv:
        _plot(spec, y, hh, DT)
