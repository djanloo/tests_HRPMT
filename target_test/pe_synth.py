"""
Photoelectron-level (doubly-stochastic / Cox) synthetic generator = the patent's
branching model, used to VALIDATE the Target estimators and their gain/rate/energy
scaling with KNOWN ground truth.

Generative model (per sample bin, dt=1/fs):
  gammas ~ Poisson(lambda*dt), each deposits eta photoelectrons (energy proxy)
  pe intensity envelope  mu = (gamma*eta) * h_scint,  h_scint=(1/tau)e^{-t/tau} (unit sum)
  pe counts  n ~ Poisson(mu)                 <- pe shot noise (the granularity)
  current sample  j = gain * n  + electronic noise
Then E[j] ~ gain*lambda*eta,  and we test Msd, Var, eta=Var/Msd, lam_hat=Msd^2/Var.

Key scaling to check (my report had it BACKWARDS):
  j -> g*j  =>  Var->g^2 Var, Msd->g^2 Msd  =>  eta=Var/Msd INVARIANT,  lam_hat ∝ g^2.
"""
import os
import numpy as np

FS = 100e6
DT = 1.0 / FS
TAU = 230e-9


def gen(lam, eta, gain, N=300, L=2000, noise_adc=0.0, eta_cv=0.0, seed=0):
    rng = np.random.default_rng(seed)
    gam = rng.poisson(lam * DT, (N, L)).astype(float)          # gamma arrivals
    marks = eta * (1 + eta_cv * rng.standard_normal((N, L))) if eta_cv else eta
    inj = gam * marks                                          # pe injected per sample
    n = int(10 * TAU / DT); t = np.arange(n) * DT
    h = np.exp(-t / TAU); h /= h.sum()                         # unit-sum scint kernel
    nf = 1 << int(np.ceil(np.log2(L + n)))
    mu = np.fft.irfft(np.fft.rfft(inj, n=nf, axis=1) * np.fft.rfft(h, n=nf), n=nf, axis=1)[:, :L]
    mu = np.clip(mu, 0, None)
    n_pe = rng.poisson(mu).astype(float)                       # pe shot noise (Cox)
    j = gain * n_pe
    if noise_adc > 0:
        j = j + rng.normal(0, noise_adc, (N, L))
    return j


def stats(j):
    x = j - j.mean(axis=1, keepdims=True)
    var = float(x.var())
    msd = 0.5 * float((np.diff(x, axis=1) ** 2).mean())
    from scipy.stats import kurtosis
    return dict(mean=float(j.mean()), var=var, msd=msd,
               eta=var / msd, lam_hat=msd ** 2 / var, kurt=float(kurtosis(x, axis=None)))


def line(tag, s):
    print("  %-22s mean=%10.2f  Var=%10.1f  Msd=%9.2f  eta=V/M=%8.2f  lamhat=M2/V=%10.3f  kurt=%+6.2f"
          % (tag, s["mean"], s["var"], s["msd"], s["eta"], s["lam_hat"], s["kurt"]))


if __name__ == "__main__":
    print("=== SCAN 1: gain (lam=5e6, eta=3500, no noise) -> eta invariant? lamhat ∝ g^2? ===")
    base = None
    for g in (0.5, 1.0, 2.0, 4.0):
        s = stats(gen(5e6, 3500, g, seed=1))
        line(f"gain={g}", s)
        if g == 1.0: base = s
    print("   expectation: eta constant; lamhat scales as g^2 (0.25,1,4,16 x); Var,Msd as g^2")

    print("\n=== SCAN 2: rate lambda (gain=1, eta=3500, no noise) -> lamhat ∝ lam? eta const? ===")
    for lam in (1e6, 3e6, 1e7, 3e7):
        s = stats(gen(lam, 3500, 1.0, seed=2))
        line(f"lam={lam:.0e}", s)
    print("   expectation (Target): mean,Var,Msd,lamhat all ∝ lam; eta=Var/Msd constant (=energy)")

    print("\n=== SCAN 3: energy eta (gain=1, lam=5e6, no noise) -> eta=Var/Msd ∝ energy? ===")
    for e in (500, 1500, 3500, 7000):
        s = stats(gen(5e6, e, 1.0, seed=3))
        line(f"eta_pe={e}", s)
    print("   expectation: eta=Var/Msd increases with the true pe/gamma (energy)")

    print("\n=== SCAN 4: electronic noise (lam=1e7, eta=3500, gain=1) -> corrupts eta & lamhat ===")
    for nz in (0.0, 5.0, 20.0, 50.0):
        s = stats(gen(1e7, 3500, 1.0, noise_adc=nz, seed=4))
        line(f"noise={nz} ADC", s)
    print("   expectation: white noise inflates Msd more than Var at high freq -> eta drops, lamhat rises")

    print("\n=== SCAN 5: INJECT gain crash g(lam)=g0/(1+lam/lc) -> which rate proxy survives? ===")
    print("   ground-truth lambda scan WITH gain collapsing; noise=10 ADC. Recover lambda?")
    g0, lc = 4.0, 5e6
    print("  %-12s %8s %10s %10s %12s %12s" % ("lam_true", "gain", "mean", "Msd", "lamhat=M2/V", "mean2/Var"))
    for lam in (1e6, 3e6, 1e7, 3e7, 6e7):
        g = g0 / (1 + lam / lc)                      # gain collapses with rate
        s = stats(gen(lam, 3500, g, noise_adc=10.0, seed=5))
        print("  %-12.0e %8.3f %10.1f %10.1f %12.2f %12.3e"
              % (lam, g, s["mean"], s["msd"], s["lam_hat"], s["mean"] ** 2 / s["var"]))
    print("   Msd, lamhat, mean all corrupted by g(lam); mean^2/Var cancels g EXACTLY -> proportional to lambda.")

    # ------------------------------------------------------------------ figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(14, 10))

    gains = np.array([0.5, 1, 2, 4]); S1 = [stats(gen(5e6, 3500, g, seed=1)) for g in gains]
    ax[0, 0].plot(gains, [s["eta"] for s in S1], "o-", label="η=Var/Msd (gain-free)")
    ax[0, 0].plot(gains, [s["lam_hat"] for s in S1], "s-", label="λ̂=Msd²/Var")
    ax[0, 0].plot(gains, S1[1]["lam_hat"] * gains**2, "k:", label="∝ gain²")
    ax[0, 0].set_xlabel("gain"); ax[0, 0].set_title("SCAN gain: η costante, λ̂ ∝ gain²")
    ax[0, 0].set_yscale("log"); ax[0, 0].legend(fontsize=8)

    lams = np.array([1e6, 3e6, 1e7, 3e7]); S2 = [stats(gen(l, 3500, 1.0, seed=2)) for l in lams]
    ax[0, 1].loglog(lams, [s["lam_hat"] for s in S2], "o-", label="λ̂=Msd²/Var")
    ax[0, 1].loglog(lams, [s["mean"]**2/s["var"] for s in S2], "^-", label="mean²/Var")
    ax[0, 1].loglog(lams, lams/lams[0]*S2[0]["lam_hat"], "k:", label="∝ λ")
    ax[0, 1].set_xlabel("λ vero [cps]"); ax[0, 1].set_title("SCAN λ (gain fisso): entrambi ∝ λ")
    ax[0, 1].legend(fontsize=8)

    etas = np.array([500, 1500, 3500, 7000]); S3 = [stats(gen(5e6, e, 1.0, seed=3)) for e in etas]
    ax[1, 0].plot(etas, [s["eta"] for s in S3], "o-")
    ax[1, 0].set_xlabel("η_pe vero (∝ energia)"); ax[1, 0].set_ylabel("η = Var/Msd")
    ax[1, 0].set_title("SCAN energia: η=Var/Msd cresce con l'energia")

    lam5 = np.array([1e6, 3e6, 1e7, 3e7, 6e7])
    S5 = [stats(gen(l, 3500, g0/(1+l/lc), noise_adc=10.0, seed=5)) for l in lam5]
    ax[1, 1].loglog(lam5, [s["mean"]**2/s["var"] for s in S5], "^-", lw=2, label="mean²/Var (RECUPERA)")
    ax[1, 1].loglog(lam5, [s["lam_hat"] for s in S5], "s--", label="λ̂=Msd²/Var (fallisce)")
    ax[1, 1].loglog(lam5, [s["msd"] for s in S5], "o--", label="Msd (fallisce)")
    ax[1, 1].loglog(lam5, lam5/lam5[0]*(S5[0]["mean"]**2/S5[0]["var"]), "k:", label="∝ λ")
    ax[1, 1].set_xlabel("λ vero [cps]")
    ax[1, 1].set_title("SCAN 5: gain crash iniettato → solo mean²/Var recupera λ"); ax[1, 1].legend(fontsize=8)

    fig.suptitle("Validazione sintetica pe-level (verità nota): scaling di gain, rate, energia, gain-crash")
    fig.tight_layout()
    fig.savefig(os.path.join(os.path.dirname(__file__), "pe_synth_validation.png"), dpi=100)
    print("\nsaved pe_synth_validation.png")
