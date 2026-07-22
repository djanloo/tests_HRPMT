import h5py
import numpy as np
import matplotlib.pyplot as plt 
import os
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

files = [f for f in os.listdir('signals') if f.find("Cs") > 0]
files = np.sort(files)

signals = []
metadata = []

for i, file in enumerate(files):
    with h5py.File(f"signals/{file}") as f:
        d = dict(f['metadata'].attrs)
        events = np.array(f['waveforms'])
        signals += [events]
        metadata += [d]

dose = [_["dose"] for _ in metadata]
signals = np.array(signals)[np.argsort(dose)]
metadata = np.array(metadata)[np.argsort(dose)]

mosaic = np.array([np.arange(5), 5*["c"]]).T
fig,ax = plt.subplot_mosaic(mosaic,constrained_layout=True, sharex=False, width_ratios=[1, 0.05])
cm = plt.cm.rainbow
norm = Normalize(vmin=0, vmax = 30000)
for i in range(len(signals)):
    ax[str(i)].plot(np.arange(len(signals[i][0])).astype(float)*10, signals[i][100], color=cm(norm(metadata[i]['dose'])))
    ax[str(i)].set_title(fr"{metadata[i]['dose']} $\mu S/h$ - activity={metadata[i]['activity']} Bq - ({metadata[i]['distance']} cm)")
    ax[str(i)].set_ylabel("ADC")
    ax['c'].axhline(metadata[i]['dose'], color='k', zorder=100)
    if i < 4:
        ax[str(i)].set_xticklabels([])
    else:
        ax[str(i)].set_xlabel("t [ns]")

ax['c'].set_ylim(0, 30000)
plt.colorbar(ScalarMappable(cmap=cm, norm=norm), cax = ax['c'], label=r"Dose [$\mu S/ h $]")
ax['c'].set_yticks(np.arange(0,5)*30000/5)

fig.savefig("anode_signals.png", dpi=200)
plt.show()

