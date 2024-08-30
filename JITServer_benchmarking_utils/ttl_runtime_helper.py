import seaborn
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from constants import font_size
from constants import figure_size
plt.rcParams.update({
    "figure.constrained_layout.use": True,
    "figure.figsize": figure_size,
    "font.size": font_size,
    "hatch.linewidth": 0.5,
    "legend.fontsize": font_size,
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
parser.add_argument('-p', '--percentiles', type=str, required=False, help='The percentiles to calculate')

# Parse the arguments
args = parser.parse_args()
percentiles = [float(p) for p in args.percentiles.split(',')]

INPUT = open(args.input_file, 'r')
num_clients = args.num_clients

algos = ('FCFS', 'ALDCF', 'RR')
clients = (str(i) for i in range(num_clients))

client_runtime = {algo: [0 for _ in range(num_clients)] for algo in algos}
client_percentiles = {algo: [0 for _ in range(len(percentiles))] for algo in algos}

for line in INPUT:
    line_spl = line.split(',')
    if 'ildf_server' == line_spl[0]:
        client_runtime['ALDCF'][int(line_spl[1]) - 1] += float(line_spl[3])
    elif 'fcfs_server' == line_spl[0]:
        client_runtime['FCFS'][int(line_spl[1]) - 1] += float(line_spl[3])
    elif 'round_robin_server' == line_spl[0]:
        client_runtime['RR'][int(line_spl[1]) - 1] += float(line_spl[3])

print(client_runtime)
for percentile in percentiles:
    for algo in algos:
        client_percentiles[algo][percentiles.index(percentile)] = pd.Series(client_runtime[algo]).quantile(percentile / 100)

print(client_percentiles)

data_frames = []
df = pd.DataFrame(client_runtime)
data_frames.append(df)
both = pd.concat(data_frames, axis=1)
plot = seaborn.ecdfplot(data=both)
#plt.title("Akka-Uct (100s S.T)")
plt.xlabel("Completion time (s)")

for percentile in percentiles:
    # plt.axhline(y=percentile / 100, color='grey', linestyle='--')
    max_x = 0
    for algo in algos:
        x_value = client_percentiles[algo][percentiles.index(percentile)]
        if x_value > max_x:
            max_x = x_value
        plt.vlines(x=x_value, ymin=0, ymax=percentile / 100, color='red', linestyle=(5, (10, 3)))
    
    plt.hlines(y=percentile / 100, xmin=0, xmax=max_x, color='red', linestyle=(5, (8, 3)))

plt.xlim(0, max([max(client_runtime[algo]) for algo in algos]))
plt.ylim(0, 1)
#plt.legend(loc="upper left", ncol=3)
plt.legend(["RR","ALDCF","FCFS"],loc="upper left", ncol=3)
fig = plot.get_figure()
fig.savefig(f'{args.save_fig_path}.pdf', format="pdf", bbox_inches="tight")

#fig.savefig(f'{args.save_fig_path}.svg', format='svg', dpi=300)

