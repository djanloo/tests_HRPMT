"""
Full coupled nonlinear divider model with PER-STAGE voltages (no uniform-drop
assumption). Homogeneous R and dynode law, but each stage solved self-consistently.

Resistor ladder across a FIXED supply (total voltage conserved):
  nodes U_0=0 (cathode) ... U_{N+1}=V_HV (anode); resistor R between neighbours.
  stage gap V_i = U_i - U_{i-1};  dynode gain δ_i = a·V_i^κ.
  beam current entering dynode i:  J_i = I0·∏_{j<i} δ_j,  I0 = q·n0·λ (cathode current).
  tube pulls from node i the resupply current  t_i = (δ_i−1)·J_i.
  KCL at each dynode node i=1..N:
     (U_{i-1}-U_i)/R + (U_{i+1}-U_i)/R − t_i = 0.
Solve U_1..U_N self-consistently (δ depends on U). Total gain G = ∏ δ_i.
Because ΣV=V_HV is fixed, loading REDISTRIBUTES the gaps (some rise, some fall).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

N = 10; KAPPA = 0.75; VHV = 1000.0
delta0 = 4.0                                   # nominal per-stage gain -> a
V0 = VHV / (N + 1)
a = delta0 / V0 ** KAPPA                        # so δ(V0)=delta0, G0=delta0^N
q, n0 = 1.6e-19, 3500.0
Ib = 1e-4                                       # bias current 0.1 mA
R = VHV / ((N + 1) * Ib)                         # divider resistor

def residual(U, I0):
    Ufull = np.concatenate(([0.0], U, [VHV]))
    V = np.diff(Ufull)                           # N+1 gaps
    Vd = np.clip(V[:N], 1e-6, None)              # dynode gaps
    delta = a * Vd ** KAPPA
    J = I0 * np.concatenate(([1.0], np.cumprod(delta)[:-1]))   # J_i, i=1..N
    t = (delta - 1) * J                          # tube extraction at each node
    res = np.empty(N)
    for i in range(N):                           # KCL at node i+1 (0-indexed i)
        res[i] = (Ufull[i] - Ufull[i + 1]) / R + (Ufull[i + 2] - Ufull[i + 1]) / R - t[i]
    return res

def solve(lam, guess):
    I0 = q * n0 * lam
    U = fsolve(residual, guess, args=(I0,), full_output=False)
    Ufull = np.concatenate(([0.0], U, [VHV]))
    V = np.diff(Ufull)[:N]
    delta = a * np.clip(V, 1e-6, None) ** KAPPA
    G = np.prod(delta)
    Ia = q * n0 * lam * G
    return U, V, G, Ia

lams = np.logspace(4, 7.5, 60)
guess = np.linspace(0, VHV, N + 2)[1:-1]
Gs, Ias, Vprof = [], [], []
for lam in lams:
    U, V, G, Ia = solve(lam, guess); guess = U      # continuation
    Gs.append(G); Ias.append(Ia); Vprof.append(V)
Gs = np.array(Gs); Ias = np.array(Ias); Vprof = np.array(Vprof)
G0 = delta0 ** N

fig, ax = plt.subplots(1, 3, figsize=(16, 5))
# (1) per-stage voltage profile at a few rates
sel = [0, 25, 40, 50, 59]
for j in sel:
    ax[0].plot(range(1, N + 1), Vprof[j], "o-", label=f"λ={lams[j]:.1e} (I_a/I_b={Ias[j]/Ib:.2f})")
ax[0].axhline(V0, color="gray", ls=":", label="V0 (a vuoto)")
ax[0].set_xlabel("stadio i"); ax[0].set_ylabel("V_i [V]")
ax[0].set_title("Profilo tensioni per stadio (redistribuzione)"); ax[0].legend(fontsize=7)
# (2) G(λ): full ladder vs uniform-drop
ax[1].loglog(lams, Gs / G0, "-", lw=2, label="ladder (drop per-stadio)")
# uniform-drop reference g=(1-r g)^{Nk}, r=q n0 λ G0/Ib
from scipy.optimize import brentq
p = N * KAPPA
def g_unif(lam):
    r = q * n0 * lam * G0 / Ib
    hi = min(1.0, 1.0 / r) * (1 - 1e-12) if r > 0 else 1.0
    return brentq(lambda g: g - (1 - r * g) ** p, 1e-14, hi) if r > 0 else 1.0
ax[1].loglog(lams, [g_unif(l) for l in lams], "--", label="uniform-drop (1−rg)^{Nk}")
ax[1].set_xlabel("λ [cps]"); ax[1].set_ylabel("G/G0")
ax[1].set_title("Gain: ladder vs uniform-drop"); ax[1].legend(fontsize=8)
# (3) anode current saturation + which stages rise/fall
ax[2].loglog(lams, Ias / Ib, label="I_a/I_b (ladder)")
ax[2].axhline(1, color="crimson", ls="--", label="I_a=I_b")
ax[2].set_xlabel("λ [cps]"); ax[2].set_ylabel("I_a/I_b")
ax[2].set_title("Corrente d'anodo (satura a I_b)"); ax[2].legend(fontsize=8)
fig.tight_layout(); fig.savefig("gain_ladder.png", dpi=100)

# diagnostics: does any stage voltage RISE above V0 (bump precursor)?
print(f"V0 (no load) = {V0:.1f} V ;  G0 = {G0:.3e}")
print("\nλ [cps]     I_a/I_b   G/G0     V_1(primo)  V_N(ultimo)  max stadio")
for j in [0, 25, 40, 50, 55, 59]:
    print("%9.2e  %7.3f  %7.4f   %8.1f   %9.1f   V%d=%.0f"
          % (lams[j], Ias[j]/Ib, Gs[j]/G0, Vprof[j][0], Vprof[j][-1],
             1+int(np.argmax(Vprof[j])), Vprof[j].max()))
rose = np.any(Vprof.max(1) > V0 * 1.001)
print(f"\nQualche stadio sale sopra V0?  {rose}  (se sì → bump emerge dal circuito)")
print("saved gain_ladder.png")
