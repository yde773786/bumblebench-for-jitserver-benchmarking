from constants import COLUMN_WIDTH, font_size, legend_size, COLUMN_HEIGHT
from ttl_runtime_helper import graph_ttl_helper
import matplotlib.pyplot as plt
plt.rcParams.update({
    "figure.constrained_layout.use": True,
    "figure.figsize": (COLUMN_WIDTH * 2, COLUMN_HEIGHT * 2),
    "font.size": font_size,
    "hatch.linewidth": 0.5,
    "legend.fontsize": legend_size,
    "legend.framealpha": 0.5,
    "lines.linewidth": 1.0,
    "lines.markersize": 4.0,
    "savefig.dpi": 300,
})
if __name__ == "__main__":
    plt.figure(0)
    ainput_file = "data/dotty50stag.csv"
    asave_fig_path = None
    anum_clients = 50
    apercentiles = "80"
    aldcf_plus = True
    amix_even = False
    amix_odd= False
    avertical_legend = False
    plt.subplot(2, 2, 1)
    graph_ttl_helper(ainput_file, asave_fig_path, anum_clients, apercentiles, aldcf_plus, amix_even, amix_odd, avertical_legend)
    plt.xlabel("Dotty: Completion time (s)")
    ax = plt.gca()
    ax.get_legend().remove()
    ainput_file = "data/future10stag.csv"
    asave_fig_path = None
    anum_clients = 50
    apercentiles = "80"
    aldcf_plus = True
    amix_even = False
    amix_odd= False
    avertical_legend = False
    plt.subplot(2, 2, 3)
    graph_ttl_helper(ainput_file, asave_fig_path, anum_clients, apercentiles, aldcf_plus, amix_even, amix_odd, avertical_legend)
    plt.xlabel("Future-Genetic: Completion time (s)")
    ax = plt.gca()
    ax.get_legend().remove()

    ainput_file = "data/mix30stag.csv"
    asave_fig_path = None
    anum_clients = 50
    apercentiles = "80"
    aldcf_plus = True
    amix_even = True
    amix_odd= False
    avertical_legend = False
    plt.subplot(2, 2, 2)
    graph_ttl_helper(ainput_file, asave_fig_path, anum_clients, apercentiles, aldcf_plus, amix_even, amix_odd, avertical_legend)
    plt.xlabel("Dotty: Completion time (s)")
    ax = plt.gca()
    ax.get_legend().remove()
    ainput_file = "data/mix30stag.csv"
    asave_fig_path = None
    anum_clients = 50
    apercentiles = "80"
    aldcf_plus = True
    amix_even = False
    amix_odd= True
    avertical_legend = False
    plt.subplot(2, 2, 4)
    graph_ttl_helper(ainput_file, asave_fig_path, anum_clients, apercentiles, aldcf_plus, amix_even, amix_odd, avertical_legend)
    plt.xlabel("Future-Genetic: Completion time (s)")
    ax = plt.gca()
    ax.get_legend().set_loc("lower left")
    plt.savefig(f'combined_workloads_cdf.pdf', format="pdf", bbox_inches="tight")