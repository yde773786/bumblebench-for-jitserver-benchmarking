import argparse
import pandas as pd
import csv
import seaborn
import matplotlib
import constants
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
    parser.add_argument('-his', '--histogram', action='store_true')
    args = vars(parser.parse_args())
    total_data = args['data']
    figure_export_name = args['figure_export_name']
    continuous_load_wrapper = args['continuous_load_wrapper']
    histogram = args['histogram']
    total_data = total_data.split(",")

    data_frames = []
    directories = constants.directories
    if continuous_load_wrapper:
        for data in total_data:
            run = 0
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

            temp_data_wrapper = []
            temp_data_wrapper.clear()
            for i in directories:
                temp_data_wrapper.append([])

            data_wrapper = []
            for i in directories:
                data_wrapper.append([])

            file_name = data.split('/')[-1]
            file_name = file_name.replace(".csv","")

            with open(data, "r") as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if int(row[0]) != run:
                        run = int(row[0])
                        if temp_data_wrapper[0]:
                            # for q in range(len(temp_data_wrapper)):
                            #     data_wrapper[q].append(sum(temp_data_wrapper[q])/len(temp_data_wrapper[q]))
                            for q in range(len(temp_data_wrapper)):
                                data_wrapper[q].append(max(temp_data_wrapper[q]))
                            temp_data_wrapper.clear()
                            for i in directories:
                                temp_data_wrapper.append([])
                    for q in range(len(temp_data_wrapper)):
                        temp_data_wrapper[q].append(float(row[2 + q]))
            for i in range(len(directories)):
                df = pd.DataFrame({f'{file_name}_{directories[i]}:': data_wrapper[i]})
                data_frames.append(df)

    both = pd.concat(data_frames, axis=1)
    print(both)
    if histogram:
        for frame in data_frames:
            plot = seaborn.displot(data=frame)
            plt.title("Histogram of completion times for clients using different JITServers")
            plt.xlabel("Completion time (s)")
        plot = seaborn.displot(data=both)
        plt.title("Histogram of completion times for clients using different JITServers")
        plt.xlabel("Completion time (s)")
        fig = plot.fig
        if figure_export_name is not None:
            fig.savefig(f'{figure_export_name}.png')
    else:
        plot = seaborn.ecdfplot(data=both)
        fig = plot.get_figure()
        plot.set_axis_labels("label!!!")
        if figure_export_name is not None:
            fig.savefig(f'{figure_export_name}.png')
    plt.show()

