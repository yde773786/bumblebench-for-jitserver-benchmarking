import sys
import matplotlib.pyplot as plt
INPUT = open(sys.argv[1], 'r')
save_fig_path = sys.argv[2]
temperature = {'cold': 0, 'warm': 0, 'hot': 0, 'scorching': 0}
# read line by line
for line in INPUT:
    if 'is compilation' in line:
        spl = line.split()
        temperature[spl[3][:-1]] += int(spl[4])
plt.bar(temperature.keys(), temperature.values())
plt.title('Temperature Histogram')
plt.xlabel('Temperature')
plt.ylabel('Number of Compilations')
plt.savefig(save_fig_path)