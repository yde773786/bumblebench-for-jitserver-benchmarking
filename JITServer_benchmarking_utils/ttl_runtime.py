import matplotlib.pyplot as plt
import numpy as np
import argparse
# DOTTY: {'FCFS': 182313.33, 'ALDF': 160133.14, 'RR': 187458.07}
# FUTURE-GENETIC: {'FCFS': 59214.090000000004, 'ALDF': 59337.02, 'RR': 61898.71999999999}
plt.rcParams.update({
    "figure.constrained_layout.use": True,
    "figure.figsize": (12.0, 10.25),
    "font.size": 12,
    "hatch.linewidth": 0.5,
    "legend.fontsize": 12,
    "legend.framealpha": 0.5,
    "lines.linewidth": 1.0,
    "lines.markersize": 4.0,
    "savefig.dpi": 300,
})

# Create the parser
parser = argparse.ArgumentParser(description='Plot the runtime per client')

# Add the arguments
parser.add_argument('-i', '--input_file', type=str, required=True, help='The input file')
parser.add_argument('-s1', '--save_fig_path_per_client', type=str, required=True, help='The path to save the figure for runtime per client')
parser.add_argument('-s2', '--save_fig_path_total', type=str, required=True, help='The path to save the figure for total runtime')
parser.add_argument('-n', '--num_clients', type=int, required=True, help='The number of clients')

# Parse the arguments
args = parser.parse_args()

INPUT = open(args.input_file, 'r')
num_clients = args.num_clients

algos = ('FCFS', 'ALDF', 'RR')
clients = (str(i) for i in range(num_clients))

client_runtime = {algo: [0 for _ in range(num_clients)] for algo in algos}

x = np.arange(num_clients)  # the label locations
width = 0.25  # the width of the bars
multiplier = 0

# Each client runtime plot

for line in INPUT:
    line_spl = line.split(',')
    if 'ildf_server' == line_spl[0]:
        client_runtime['ALDF'][int(line_spl[1]) - 1] += float(line_spl[3])
    elif 'fcfs_server' == line_spl[0]:
        client_runtime['FCFS'][int(line_spl[1]) - 1] += float(line_spl[3])
    elif 'round_robin_server' == line_spl[0]:
        client_runtime['RR'][int(line_spl[1]) - 1] += float(line_spl[3])

fig, ax = plt.subplots(layout='constrained')

for algo, runtimes in client_runtime.items():
    offset = multiplier * width
    rects = ax.bar(x + offset, runtimes, width, label=algo)
    multiplier += 1

print(client_runtime)

ax.set_ylabel('Runtime (ms)')
ax.set_title('Runtime per Client')
ax.set_xticks(x)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, max(max(client_runtime.values())) + 1000)

plt.savefig(args.save_fig_path_per_client)

# Total runtime plot
fig, ax = plt.subplots(layout='constrained')

total_runtime = {algo: sum(runtimes) for algo, runtimes in client_runtime.items()}
print(total_runtime)
ax.bar(total_runtime.keys(), total_runtime.values())
ax.set_ylabel('Total Runtime (ms)')
ax.set_title('Total Runtime')
ax.set_ylim(0, max(total_runtime.values()) + 1000)

plt.savefig(args.save_fig_path_total)