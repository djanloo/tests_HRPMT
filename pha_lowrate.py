"""
Pulse-height analysis on a RESOLVED-event run -- the classic offline measurement the
statistical pipeline gives up on, and the only way to measure P(A) directly (see
`Spettro di ampiezza` / `Backlog` in the vault).

WHAT AN EVENT LOOKS LIKE HERE, because it decides the whole method. On this detector
at this gain, one gamma is NOT a smooth pulse: it is a BURST of single-photoelectron
spikes spread over the scintillation decay, with dozens of local maxima inside it.
Measured on the Am-241 run: ACF 1/e = 260 ns, decayed to r=0.06 by ~1 µs.

So peak-finding on the raw trace counts PHOTOELECTRONS, not events -- it reported 113
"events" per 20 µs record against ~3 expected, and no amount of pile-up rejection
fixes that because the extra counts are inside one event, not between two. The energy
of an event is its CHARGE, so PHA here means integrating over a gate matched to the
scintillation decay, exactly like a QDC.

Applicable only at low occupancy: the Am-241 run sits at lambda*tau ~ 0.03, so bursts
are separated. On any Cs-137 run here it is meaningless by construction -- the module
refuses above OCC_MAX.

Run directly to measure the Am-241 run against the modeled NaI spectrum of
energy_spectrum.nai().
"""
import numpy as np
from scipy.signal import find_peaks

from mssd_cumulant_estimate import noise_var          # high-f PSD plateau, validated ~1%

DT = 1e-8                       # 100 MS/s
OCC_MAX = 0.15                  # refuse PHA above this occupancy
AM241_KEV = 59.541              # the line we calibrate on


def event_charges(y, gate, n_sigma=5.0, veto_gates=2.0):
    """Charges [ADC*samples] of the resolved events in y (n_rec, n_samp).

    gate         integration window in samples; size it at ~4x the ACF 1/e time so it
                 contains the scintillation burst without collecting extra baseline
    n_sigma      threshold in units of the INTEGRATED noise, sigma*sqrt(gate)
    veto_gates   pile-up veto: drop an event if another is within veto_gates*gate

    Pile-up, and why the veto is on the integral rather than on the peaks: two bursts
    closer than the gate share charge, so their integrals are both wrong -- one high by
    what it borrowed, the other high by what it kept. Vetoing both is the only honest
    move; `prominence` cannot separate them because the summed integral has no feature
    to be prominent against. The veto is symmetric for the same reason.

    Returns (charges, sigma, n_rejected).
    """
    y = y - np.median(y, axis=1, keepdims=True)        # DC-coupled: baseline is real
    sigma = np.sqrt(noise_var(y))
    thr = n_sigma * sigma * np.sqrt(gate)              # noise on a sum of `gate` samples

    # running sum over the gate: its local maxima are where the gate best frames a burst
    c = np.cumsum(y, axis=1)
    s = c[:, gate:] - c[:, :-gate]
    veto = max(gate, int(round(veto_gates * gate)))
    q, rej = [], 0
    for row in s:
        pk, props = find_peaks(row, prominence=thr, distance=gate)
        amp = props["prominences"]                     # charge above the local level
        if len(pk) > 1:
            far = np.diff(pk) > veto
            keep = np.r_[True, far] & np.r_[far, True]
            rej += int((~keep).sum())
            amp = amp[keep]
        q.append(amp)
    return np.concatenate(q), sigma, rej


def photopeak(q, bins=140, search_from=0.30):
    """(centroid, FWHM/centroid, (mid, counts)) of the highest peak in the histogram.

    search_from ignores the low end, where the L X-ray line and the threshold pile-up
    live. Centroid is the counts-weighted mean inside the half-maximum window, so it
    does not sit on whichever single bin happened to win.
    """
    cnt, edges = np.histogram(q, bins=bins, range=(0, np.percentile(q, 99.8)))
    mid = 0.5 * (edges[1:] + edges[:-1])
    lo = int(search_from * bins)
    i = lo + int(np.argmax(cnt[lo:]))
    over = np.where(cnt >= 0.5 * cnt[i])[0]
    over = over[over >= lo]
    # contiguous run containing the mode, so a second line cannot widen the FWHM
    lft = i
    while lft - 1 in over:
        lft -= 1
    rgt = i
    while rgt + 1 in over:
        rgt += 1
    band = slice(lft, rgt + 1)
    centroid = float(np.average(mid[band], weights=cnt[band]))
    return centroid, float(mid[rgt] - mid[lft]) / centroid, (mid, cnt)


# --------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import h5py
    from energy_spectrum import load
    from simulate_pmt import acf_tau_1e

    RUN = "data/anode_waveforms/run_Am-241_93.56.h5"
    with h5py.File(RUN, "r") as f:
        y = f["waveforms"][:].astype(float)
    y -= np.median(y, axis=1, keepdims=True)

    tau = acf_tau_1e(y, ml=400)
    GATE = int(round(4 * tau / DT))                    # 4 tau contains the burst
    print(f"{RUN}   {y.shape[0]} record x {y.shape[1]} campioni")
    print(f"ACF 1/e = {tau*1e9:.0f} ns  ->  gate = {GATE} campioni ({GATE*DT*1e9:.0f} ns)")

    q, sigma, rej = event_charges(y, GATE)
    n_ev = len(q) + rej
    lam = n_ev / (y.shape[0] * y.shape[1] * DT)
    occ = lam * tau
    print(f"rumore sigma = {sigma:.2f} ADC  ->  soglia sull'integrale "
          f"{5*sigma*np.sqrt(GATE):.0f} ADC*campioni")
    print(f"eventi trovati = {n_ev} ({n_ev/y.shape[0]:.2f}/record)  -> lambda = "
          f"{lam/1e6:.2f} Mcps   occupancy lambda*tau = {occ:.3f}")
    print(f"scartati per pile-up = {rej} ({100*rej/n_ev:.1f}%)   accettati = {len(q)}")
    assert occ < OCC_MAX, f"occupancy {occ:.2f}: eventi non risolti, PHA senza senso"

    ctr, res, (mid, cnt) = photopeak(q)
    print(f"\nfotopicco: centroide {ctr:.0f} ADC*campioni  ->  "
          f"{AM241_KEV/ctr*1e3:.2f} keV per 1000 ADC*campioni")
    print(f"risoluzione FWHM/E = {100*res:.1f}%  a {AM241_KEV:.1f} keV")
    assert ctr > 5 * sigma * np.sqrt(GATE), (ctr, sigma)
    assert 0.05 < res < 0.70, res
    assert cnt[int(0.30*len(cnt)):].max() > 3 * cnt[-1], "nessun picco: coda monotona"

    # IL controllo sul pile-up: se il veto morde, il centroide smette di muoversi.
    print("\nveto (gate)  scartati  centroide   deriva")
    prev = None
    for vg in (0.0, 1.0, 2.0, 4.0):
        q2, _, r2 = event_charges(y, GATE, veto_gates=vg)
        c2 = photopeak(q2)[0]
        d = "" if prev is None else f"{100*(c2-prev)/prev:+6.1f}%"
        print(f"  {vg:4.1f}      {100*r2/(len(q2)+r2):5.1f}%   {c2:8.0f}   {d}")
        prev = c2
    assert abs(prev - ctr) / ctr < 0.03, (prev, ctr)   # convergente tra 2 e 4 gate

    # confronto col modello NaI
    spec = load("Am241")
    pred = 0.08 * np.sqrt(661.657 / AM241_KEV)
    print(f"\nmodello nai(res662=8%): FWHM/E predetta {100*pred:.1f}%  vs misurata "
          f"{100*res:.1f}%  ->  res662 implicito "
          f"{100*res/np.sqrt(661.657/AM241_KEV):.1f}%")
    print(f"CV: spettro modellato {spec.cv:.3f}   carica misurata {q.std()/q.mean():.3f}")

    if "--plot" in sys.argv:
        import matplotlib.pyplot as plt
        a = (np.arange(len(spec.w)) + 0.5) * spec.scale * ctr
        fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.3))
        t = np.arange(600) * DT * 1e6
        ax[0].plot(t, y[0, :600], lw=0.6, label="anodo (grezzo)")
        cs = np.cumsum(y[0])
        ax[0].plot(t[:600 - GATE], (cs[GATE:600] - cs[:600 - GATE]) / GATE, lw=1.4,
                   label=f"integrale su gate ({GATE*DT*1e9:.0f} ns)")
        ax[0].set_xlabel("t [µs]"); ax[0].set_ylabel("ADC"); ax[0].legend(fontsize=8)
        ax[0].set_title("Am-241: un evento è un burst di fotoelettroni")
        ax[1].step(mid, cnt / cnt.sum(), where="mid", label="PHA misurato (reale)")
        ax[1].step(a, spec.w * (mid[1] - mid[0]) / (spec.scale * ctr), where="mid",
                   lw=0.9, label="modello NaI (sim)")
        ax[1].axvline(ctr, color="k", ls=":", lw=0.9,
                      label=f"fotopicco = {AM241_KEV:.1f} keV")
        ax[1].set_yscale("log"); ax[1].set_xlabel("carica [ADC·campioni]")
        ax[1].set_title(f"spettro Am-241 misurato (FWHM/E {100*res:.0f}%)")
        ax[1].legend(fontsize=8)
        fig.tight_layout()
        fig.savefig("pha_am241.png", dpi=110)
        plt.show()
