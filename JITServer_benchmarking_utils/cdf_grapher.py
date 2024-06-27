import argparse
import pandas as pd
import csv
import seaborn
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that graphs a cdf function from data"
    )

    parser.add_argument('-d', '--data', required=True)
    parser.add_argument('-f', '--figure_export_name', required=False)
    parser.add_argument('-clw', '--continuous_load_wrapper', action='store_true')
    parser.add_argument('-his', '--histogram', required=False)
    args = vars(parser.parse_args())
    total_data = args['data']
    figure_export_name = args['figure_export_name']
    continuous_load_wrapper = args['continuous_load_wrapper']
    histogram = args['histogram']
    total_data = total_data.split(",")

    data_frames = []

    if continuous_load_wrapper:
        for data in total_data:
            run = 0
            directories = ['normal_server', 'round_robin_server', 'least_done_first_server']
            data_wrapper = []
            for i in directories:
                data_wrapper.append([])
            file_name = data.split('/')[-1]
            file_name = file_name.replace(".csv","")

            with open(data, "r") as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    for i in range(len(directories)):
                        if row[0] == directories[i]:
                            data_wrapper[i].append(float(row[3]))
            for i in range(len(directories)):
                df = pd.DataFrame({f'{file_name}_{directories[i]}:': data_wrapper[i]})
                data_frames.append(df)
    else:
        for data in total_data:
            run = 0
            data_1 = []
            data_2 = []

            normal_data = []
            random_data = []
            file_name = data.split('/')[-1]
            file_name = file_name.replace(".csv","")

            with open(data, "r") as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if int(row[0]) != run:
                        run = int(row[0])
                        if data_1 != []:
                            # normal_data.append(sum(data_1)/len(data_1))
                            # random_data.append(sum(data_2)/len(data_2))
                            normal_data.append(max(data_1))
                            random_data.append(max(data_2))
                            data_1 = []
                            data_2 = []
                    data_1.append(float(row[2]))
                    data_2.append(float(row[3]))
            df = pd.DataFrame({f'{file_name}_normal_server:': normal_data})
            df2 = pd.DataFrame({f'{file_name}_altered_server:': random_data})
            data_frames.extend([df, df2])

    both = pd.concat(data_frames, axis=1)
    print(both)
    if histogram is not None:
        for frame in data_frames:
            plot = seaborn.displot(data=frame)

        plot = seaborn.displot(data=both)
        fig = plot.fig
        if figure_export_name is not None:
            fig.savefig(f'{figure_export_name}.png')
    else:
        plot = seaborn.ecdfplot(data=both)
        fig = plot.get_figure()
        if figure_export_name is not None:
            fig.savefig(f'{figure_export_name}.png')

    plt.show()

