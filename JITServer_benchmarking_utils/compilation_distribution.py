import argparse
import pandas as pd
import seaborn
import matplotlib
try:
    matplotlib.use('TkAgg')
except:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
from constants import legend_size
from constants import font_size
from constants import COLUMN_HEIGHT
from constants import COLUMN_WIDTH

plt.rcParams.update({
    "figure.constrained_layout.use": True,
    "figure.figsize": (COLUMN_WIDTH,COLUMN_HEIGHT),
    "font.size": font_size,
    "hatch.linewidth": 0.5,
    "legend.fontsize": legend_size,
    "legend.framealpha": 0.5,
    "lines.linewidth": 1.0,
    "lines.markersize": 4.0,
    "savefig.dpi": 300,
})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that graphs a cdf function from data"
    )

    parser.add_argument('-d', '--data', required=True)
    parser.add_argument('-f', '--figure_export_name', required=False)
    parser.add_argument('-his', '--histogram', action='store_true')
    args = vars(parser.parse_args())
    total_data = args['data']
    figure_export_name = args['figure_export_name']
    histogram = args['histogram']
    total_data = total_data.split(",")
    maxim = 0
    data_frames = []
    for data in total_data:
        run = 0
        data_wrapper = []
        file_name = data.split('/')[-1]
        file_name = file_name.replace(".csv", "")

        with open(data, "r") as file:
            for row in file:
                if "Elapsed Time processing entry from client" in row:
                    #print(row)
                    a = row.split('<')[2]
                    b = a.split('>')[0]
                    if float(b) > maxim:
                        maxim = float(b)
                    data_wrapper.append(float(b))
        for i in range(len(total_data)):
            df = pd.DataFrame({f'{data}:': data_wrapper})
            data_frames.append(df)

    both = pd.concat(data_frames, axis=1)
    print(both)
    if histogram:
        palette = ["#f00202" ]

        #seaborn.set_style("whitegrid")
        # for frame in data_frames:
        #     plot = seaborn.displot(data=frame, legend=False, palette=seaborn.color_palette(palette, len(palette)))
        #     #plt.title("Histogram of compilation times on the JITServer")
        #     plt.xlabel("Compilation time (s)")
        # if len(data_frames) > 1:
        #     plot = seaborn.displot(data=both, legend=False, palette=seaborn.color_palette(palette, len(palette)))
        #     #plt.title("Histogram of compilation times on the JITServer")
        #     plt.xlabel("Compilation time (s)")
        # fig = plot.fig

        # fig.set_size_inches(3,3)
        # fig.set_dpi(100)
        plt.xlim(0, 0.5)
        # import numpy as np
        # logbins = np.geomspace(both.min(), both.max(), 8)


        # stuff to cut the tail
        new_wrapper = [x for x in data_wrapper if x <=0.5]
        df = pd.DataFrame({f'1:': new_wrapper})
        bad = [df]
        sad = pd.concat(bad, axis=1)



        #plt.ylim((0, 1000))
       # space = (np.logspace(start=-5, stop=3, num=1000).flatten()).tolist()
       #  print(space)
       #  plt.hist(both,bins=space, color="red")
        #print(new_wrapper)
        plt.hist(sad,bins=50, color="red")
        #plt.xscale('log')
        plt.xlabel("Compilation time (s)")
        plt.ylabel("Count")
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        #fig, ax = plt.subplots()
        if figure_export_name is not None:
            plt.savefig(f'{figure_export_name}.pdf', format="pdf", bbox_inches="tight")
            #fig.savefig(f'{figure_export_name}.pdf', format="pdf", bbox_inches="tight")

    else:
        plot = seaborn.ecdfplot(data=both)
        fig = plot.get_figure()
        plt.xlabel("Compilation time (s)")
        plt.yscale('log',base=10)
        plt.xlim(0, maxim)
        if figure_export_name is not None:
            fig.savefig(f'{figure_export_name}.pdf', format="pdf", bbox_inches="tight")
    if figure_export_name is None:
        plt.show()
