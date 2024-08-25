import argparse
import csv

import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that graphs a line graph of the client warmup"
    )

    parser.add_argument('-d', '--data', required=True)
    parser.add_argument('-nc', '--num_clients', required=True)
    parser.add_argument('-nr', '--num_runs', required=True)
    parser.add_argument('-pc', '--particular_client', required=False)
    parser.add_argument('-gr', '--graph_all', action='store_true')
    args = vars(parser.parse_args())
    total_data = args['data']
    particular_client = args['particular_client']
    graph_all = args['graph_all']
    total_data = total_data.split(",")
    for data in total_data:
        x_data = []
        for i in range(int(args['num_runs'])):
            x_data.append([])
        recent_time = 0
        with open(data, "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if particular_client is not None:
                    if int(row[1]) == int(particular_client):
                        x_data[int(row[2]) - 1].append(float(row[3]))
                else:
                    x_data[int(row[2]) - 1].append(float(row[3]))
        final_graph_data = []
        if not graph_all:
            for i in x_data:
                final_graph_data.append(sum(i)/len(i))
            x = np.array(range(1,int(args['num_runs']) + 1))
            y = np.array(final_graph_data)
            plt.plot(x, y)
        else:
            for z in range(len(x_data)):
                final_graph_data = []
                for i in x_data:
                    final_graph_data.append(i[z])
                x = np.array(range(1,int(args['num_runs']) + 1))
                y = np.array(final_graph_data)
                plt.plot(x, y)
    plt.title("Client runtime vs run when the JITServer is throttled")
    plt.xlabel("Run (s)")
    plt.ylabel("Client runtime")
    plt.show()


