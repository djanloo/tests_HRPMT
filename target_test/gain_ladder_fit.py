"""
Fit the LADDER model to the real (same-config) gain-vs-rate points.

Data: same-HV Cs-137 series {7900,17990,28100} µSv/h. For Cs-137 dose ∝ λ, and
gain ∝ sqrt(Msd/dose) (since Msd ∝ gain^2 λ). All 3 points are on the CRASH side.

Free parameter of the fit: a single loading scale (I0 = c·λ, absorbing q·n0).
Fixed: N, κ, R, V_HV, a. We then scan (N,κ) to show what is / isn't identifiable.
"""
import numpy as np
from scipy.optimize import fsolve, brentq

VHV = 1000.0
Ib_target = 1e-4                # bias current (sets R via R=VHV/((N+1)Ib))

def build(N, kappa, delta0=4.0):
    V0 = VHV / (N + 1)
    a = delta0 / V0 ** kappa
    R = VHV / ((N + 1) * Ib_target)
    return a, R, V0

def solve_G(I0, N, kappa, a, R, guess):
    def resid(U):
        Uf = np.concatenate(([0.0], U, [VHV]))
        Vd = np.clip(np.diff(Uf)[:N], 1e-6, None)
        delta = a * Vd ** kappa
        J = I0 * np.concatenate(([1.0], np.cumprod(delta)[:-1]))
        t = (delta - 1) * J
        r = np.empty(N)
        for i in range(N):
            r[i] = (Uf[i] - Uf[i + 1]) / R + (Uf[i + 2] - Uf[i + 1]) / R - t[i]
        return r
    U = fsolve(resid, guess, full_output=False)
    Vd = np.clip(np.diff(np.concatenate(([0.0], U, [VHV])))[:N], 1e-6, None)
    return np.prod(a * Vd ** kappa), U

def gain_curve(lams, c, N, kappa):
    a, R, V0 = build(N, kappa)
    guess = np.linspace(0, VHV, N + 2)[1:-1]
    Gs = []
    for lam in lams:
        G, guess = solve_G(c * lam, N, kappa, a, R, guess)
        Gs.append(G)
    return np.array(Gs)

# ---- data: same-HV Cs-137 (baseline ~195), incl. the PRE-CRASH point 889 ----
dose = np.array([889., 7900., 17990., 28100.])
Msd = np.array([46.95, 19.00, 8.65, 6.45])
g_data = np.sqrt(Msd / dose); g_data /= g_data[0]          # relative gain (rif = 889)
lam = dose                                                 # ∝ λ (arbitrary units)

def fit_scale(N, kappa):
    # fit c (log-spaced) minimizing residual on the 2 relative-gain ratios
    def err(logc):
        G = gain_curve(lam, np.exp(logc), N, kappa)
        return np.sum((np.log(G / G[0]) - np.log(g_data)) ** 2)
    from scipy.optimize import minimize_scalar
    res = minimize_scalar(err, bounds=(np.log(1e-25), np.log(1e-10)), method="bounded")
    c = np.exp(res.x)
    G = gain_curve(lam, c, N, kappa)
    return c, G / G[0], res.fun

print("Fit del ladder ai 3 punti same-config (gain relativo).")
print("dati gain_rel:", np.round(g_data, 3), " λ_rel:", np.round(lam / lam[0], 2))
print("\n  N   kappa   Nk    loading c        gain_modello(rel)     residuo")
for N, kappa in [(10, 0.75), (8, 0.70), (12, 0.80), (10, 0.60), (14, 0.75)]:
    c, gm, res = fit_scale(N, kappa)
    print("  %2d  %.2f   %4.1f  %.3e   %s   %.2e"
          % (N, kappa, N * kappa, c, np.array2string(np.round(gm, 3)), res))
print("\n-> tutti fittano ~ugualmente bene: sul lato crollo (g∝1/λ) i punti vincolano")
print("   solo la SCALA di carico, non (N,κ,R) separatamente. Per pinnarli serve uno")
print("   scan a HV fisso che campioni il ginocchio (r~1) e la parte piatta.")

# ---- figura: ladder + dati veri ----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ref = lam[0]                                                # riferimento = run 889 (pre-crash)
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
lam_ext = np.logspace(np.log10(ref * 2e-3), np.log10(lam[-1] * 1.4), 70)
for N, kappa in [(10, 0.75), (8, 0.70), (14, 0.75)]:
    c, gmk, _ = fit_scale(N, kappa)
    G = gain_curve(lam_ext, c, N, kappa)
    G0 = gain_curve(np.array([ref]), c, N, kappa)[0]        # anchor al run 889
    ax[0].loglog(lam_ext / ref, G / G0, label=f"ladder N={N}, κ={kappa}")
ax[0].loglog(lam / ref, g_data, "ko", ms=12, label="dati veri (stessa HV)")
ax[0].axvspan(lam[0] / ref, (lam[-1] / ref) * 1.05, color="orange", alpha=0.12,
              label="regime coperto dai dati")
ax[0].set_xlabel("λ / λ(889)  (∝ dose)"); ax[0].set_ylabel("gain relativo G/G(889)")
ax[0].set_title("Estimated gain vs rate")
ax[0].legend(fontsize=8)

# zoom sul regime dei dati (fit N=10,κ=0.75)
c, gmk, res = fit_scale(10, 0.75)
drop_d, drop_m = g_data[0] / g_data[-1], gmk[0] / gmk[-1]
ax[1].semilogy(lam / ref, g_data, "ko", ms=12, label="dati veri")
ax[1].semilogy(lam / ref, gmk, "r^-", ms=9, label="ladder N=10, κ=0.75 (fit)")
for i in range(len(lam)):
    ax[1].annotate(f"{g_data[i]:.3f}", (lam[i]/ref, g_data[i]),
                   textcoords="offset points", xytext=(6, 6), fontsize=8)
ax[1].set_xlabel("λ / λ(889)  (∝ dose)"); ax[1].set_ylabel("gain relativo")
ax[1].set_title(f"Zoom of gain vs rate residuo={res:.1e}")
ax[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig("gain_ladder_fit.png", dpi=100)
print("saved gain_ladder_fit.png")
