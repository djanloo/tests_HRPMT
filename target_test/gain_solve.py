"""
Solve & plot the minimal homogeneous PMT gain model (same fractional drop):
    g = (1 - r*g)^p ,   g = G/G0 ,  r = I_a^(0)/I_b = q n0 lambda G0 / I_b ,  p = N*k
F(g)=g-(1-rg)^p is strictly increasing (F'=1+pr(1-rg)^{p-1}>0) -> unique root.
As r->inf, I_a/I_b = r*g -> 1 (anode current saturates at the bias current).
Overlay: relative gain extracted from the same-config real runs (crash side),
gain ∝ sqrt(Msd/dose) since Msd ∝ gain^2 * lambda and lambda ∝ dose.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import brentq

def g_of_r(r, p):
    if r <= 0:
        return 1.0
    hi = min(1.0, 1.0 / r) * (1 - 1e-12)
    return brentq(lambda g: g - (1 - r * g) ** p, 1e-14, hi)

r = np.logspace(-2, 3, 400)

fig, ax = plt.subplots(1, 3, figsize=(16, 5))

# (1) universal gain g(r) for a few p=Nk
for p in (5, 7.5, 10, 15):
    ax[0].loglog(r, [g_of_r(x, p) for x in r], label=f"p=Nk={p}")
ax[0].axvline(1, color="gray", ls=":", lw=1)
ax[0].set_xlabel("r = I_a(0)/I_b  (carico a gain nominale)")
ax[0].set_ylabel("g = G/G0")
ax[0].set_title("Gain relativo vs carico (radice unica)")
ax[0].legend(fontsize=8)

# (2) anode current saturates at I_b
for p in (5, 7.5, 15):
    gg = np.array([g_of_r(x, p) for x in r])
    ax[1].semilogx(r, r * gg, label=f"p={p}")
ax[1].axhline(1, color="crimson", ls="--", label="I_a = I_b (tetto)")
ax[1].set_xlabel("r"); ax[1].set_ylabel("I_a/I_b = r·g")
ax[1].set_title("La corrente d'anodo si satura a I_b"); ax[1].legend(fontsize=8)

# (3) physical G(lambda) + real runs overlay (fit only the loading scale alpha)
p = 7.5                                   # N=10, k=0.75
dose = np.array([7900., 17990., 28100.])  # same-config Cs-137 series (∝ lambda)
Msd  = np.array([19.00, 8.65, 6.45])
g_data = np.sqrt(Msd / dose); g_data /= g_data[0]     # relative gain (crash side)
lam_rel = dose / dose[0]                               # relative rate

def model_ratio(alpha):
    gm = np.array([g_of_r(alpha * d, p) for d in dose])
    return gm / gm[0]
# fit alpha (log-least-squares on the 2 ratios)
alphas = np.logspace(-6, 0, 400)
err = [np.sum((np.log(model_ratio(a)) - np.log(g_data)) ** 2) for a in alphas]
alpha = alphas[int(np.argmin(err))]

r_grid = np.logspace(-2, 4, 400)
ax[2].loglog(r_grid, [g_of_r(x, p) for x in r_grid], label=f"modello p={p}")
r_data = alpha * dose
g_anchor = (g_data / g_data[0]) * g_of_r(r_data[0], p)   # ancora i dati al modello al 1° run
ax[2].loglog(r_data, g_anchor, "o", ms=11, label="run reali (gain ∝ √(Msd/dose))")
ax[2].axvline(1, color="gray", ls=":", label="ginocchio r=1 (I_a~I_b)")
ax[2].set_xlabel("r = alpha·dose  (∝ rate)"); ax[2].set_ylabel("g = G/G0")
ax[2].set_title(f"Modello vs dati sul lato crollo; alpha={alpha:.2e} /(µSv/h)")
ax[2].legend(fontsize=8)

fig.tight_layout(); fig.savefig("gain_solve.png", dpi=100)

# numbers
print("run (same config):  dose   lam_rel  gain_data(rel)  gain_model(rel)  r=alpha*dose")
gm = model_ratio(alpha)
for d, lr, gd, g in zip(dose, lam_rel, g_data, gm):
    print("  %8.0f  %6.2f   %8.3f       %8.3f        %8.2f" % (d, lr, gd, g, alpha*d))
print(f"\nfitted loading scale alpha = {alpha:.3e} per µSv/h")
print("interpretazione: tutti i run stanno a r>1 (oltre il ginocchio) -> regime di collasso.")
print("gain-drop misurato 7900->28100:", round(g_data[0]/g_data[-1],1), "x ; modello:", round(gm[0]/gm[-1],1), "x")
print("saved gain_solve.png")
