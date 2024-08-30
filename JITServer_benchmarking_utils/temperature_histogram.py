import sys

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({
    "figure.constrained_layout.use": True,
    "figure.figsize": (8, 4),
    "font.size": 14,
    "hatch.linewidth": 0.5,
    "legend.fontsize": 14,
    "legend.framealpha": 0.5,
    "lines.linewidth": 1.0,
    "lines.markersize": 4.0,
    "savefig.dpi": 300,
})
INPUT = open(sys.argv[1], 'r')
save_fig_path = sys.argv[2]
temperature = {'cold': 0, 'warm': 0, 'hot': 0, 'scorching': 0}
# read line by line
for line in INPUT:
    if 'is compilation' in line:
        spl = line.split()
        temperature[spl[3][:-1]] += int(spl[4])
plt.bar(temperature.keys(), temperature.values())
#plt.title('Temperature Histogram')
plt.xlabel('Temperature')
plt.ylabel('Number of Compilations')
plt.savefig(f'{save_fig_path}.pdf', format="pdf", bbox_inches="tight")