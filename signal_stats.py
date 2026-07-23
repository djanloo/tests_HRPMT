"""Statistiche utili dei segnali d'anodo, in un dict. Gestisce 1D o 2D (record, campioni)."""
import numpy as np
from scipy.stats import skew, kurtosis


def signal_stats(w, fs=100e6):
    """Ritorna un dict di statistiche. La media per-record e' tolta (i dati sono
    AC-coupled: la media non porta informazione sul rate).

    Gain-free (rapporti di cumulanti, robusti alla deriva/collasso del gain del PMT):
      skew  -> proxy del RATE   (occupancy: grande a basso rate, ->0 in pileup)
      eta=Var/Msd -> proxy dell'ENERGIA media (=1 per rumore bianco, >1 se correlato)
      kurt  -> proxy del REGIME (>>0 impulsi risolti, ~0 pileup gaussiano)
    Gain-dipendenti (scala assoluta, NON confrontabili tra run a HV diversa):
      var, std, msd
    """
    w = np.atleast_2d(np.asarray(w, float))
    x = w - w.mean(axis=1, keepdims=True)
    var = float(x.var())
    msd = 0.5 * float((np.diff(x, axis=1) ** 2).mean())    # von Neumann MSSD = C(0)-C(1)
    return dict(
        mean=float(w.mean()), std=float(np.sqrt(var)), var=var, msd=msd,
        eta=var / msd,                                     # gain-free -> energia
        skew=float(skew(x, axis=None)),                    # gain-free -> rate
        kurt=float(kurtosis(x, axis=None)),                # gain-free -> regime
        n_records=len(w), n_samples=w.shape[1],
    )


def signal_stats_err(w, n_boot=200, seed=0, fs=100e6):
    """Come signal_stats ma con l'INCERTEZZA di ogni metrica, stimata per bootstrap
    sui record (ricampionati con rimpiazzo). Ritorna {nome: (valore, std)}.

    L'incertezza e' la deviazione standard della metrica sui resample: cattura la
    variabilita' dovuta al numero finito di record (sono i record gli oggetti iid,
    non i campioni). Richiede un 2D (record, campioni). n_records/n_samples esclusi.
    """
    w = np.atleast_2d(np.asarray(w, float))
    if len(w) < 2:
        raise ValueError("serve un 2D con >=2 record per stimare l'incertezza")
    val = signal_stats(w, fs)
    keys = [k for k in val if k not in ("n_records", "n_samples")]
    rng = np.random.default_rng(seed)
    n = len(w)
    boot = [signal_stats(w[rng.integers(0, n, n)], fs) for _ in range(n_boot)]
    return {k: (float(val[k]), float(np.std([b[k] for b in boot]))) for k in keys}


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    s = signal_stats(rng.standard_normal((200, 2000)))     # rumore bianco: skew~kurt~0, eta~1
    assert abs(s["skew"]) < 0.05 and abs(s["kurt"]) < 0.1 and abs(s["eta"] - 1) < 0.05, s
    print("self-check OK (rumore bianco):", {k: round(v, 3) for k, v in s.items()})

    se = signal_stats_err(rng.standard_normal((200, 2000)), n_boot=100)
    assert all(e > 0 for _, e in se.values()), se           # ogni metrica ha un'incertezza >0
    assert abs(se["eta"][0] - 1) < 0.05, se                 # valore coerente con signal_stats
    print("self-check OK (con errori):", {k: (round(v, 3), round(e, 4)) for k, (v, e) in se.items()})
