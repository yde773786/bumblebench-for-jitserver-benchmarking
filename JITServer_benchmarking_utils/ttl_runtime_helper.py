import seaborn
import pandas as pd
import matplotlib.pyplot as plt
import argparse

plt.rcParams.update({
    "figure.constrained_layout.use": True,
    "figure.figsize": (5.0, 4),
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
parser.add_argument('-s1', '--save_fig_path', type=str, required=True, help='The path to save the figure for runtime per client')
parser.add_argument('-n', '--num_clients', type=int, required=True, help='The number of clients')

# Parse the arguments
args = parser.parse_args()

INPUT = open(args.input_file, 'r')
num_clients = args.num_clients

algos = ('First Come First Serve (Baseline)', 'Alternating Least Done Client First', 'Round Robin')
clients = (str(i) for i in range(num_clients))

client_runtime = {algo: [0 for _ in range(num_clients)] for algo in algos}

for line in INPUT:
    line_spl = line.split(',')
    if 'ildf_server' == line_spl[0]:
        client_runtime['Alternating Least Done Client First'][int(line_spl[1]) - 1] += float(line_spl[3])
    elif 'fcfs_server' == line_spl[0]:
        client_runtime['First Come First Serve (Baseline)'][int(line_spl[1]) - 1] += float(line_spl[3])
    elif 'round_robin_server' == line_spl[0]:
        client_runtime['Round Robin'][int(line_spl[1]) - 1] += float(line_spl[3])

print(client_runtime)

data_frames = []
df = pd.DataFrame(client_runtime)
data_frames.append(df)
both = pd.concat(data_frames, axis=1)
plot = seaborn.ecdfplot(data=both)
plt.title("Finagle (75s S.T)")
plt.xlabel("Completion time (s)")
fig = plot.get_figure()
fig.savefig(args.save_fig_path)

