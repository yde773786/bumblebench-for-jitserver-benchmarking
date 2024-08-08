import argparse
import pandas as pd
import seaborn
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
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
    print(maxim)
    if histogram:
        for frame in data_frames:
            plot = seaborn.displot(data=frame)
            plt.title("Histogram of compilation times on the JITServer")
            plt.xlabel("Completion time (s)")
        if len(data_frames) > 1:
            plot = seaborn.displot(data=both)
            plt.title("Histogram of compilation times on the JITServer")
            plt.xlabel("Completion time (s)")
        fig = plot.fig
        # fig.set_size_inches(3,3)
        # fig.set_dpi(100)
        plt.xlim(0, maxim)
        if figure_export_name is not None:
            fig.savefig(f'{figure_export_name}.png')

    else:
        plot = seaborn.ecdfplot(data=both)
        fig = plot.get_figure()
        plt.xlabel("Compilation time (s)")
        plt.xlim(0, maxim)
        if figure_export_name is not None:
            fig.savefig(f'{figure_export_name}.png')
    if figure_export_name is None:
        plt.show()
