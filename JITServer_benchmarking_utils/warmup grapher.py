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
    parser.add_argument('-lc', '--longest_client', action='store_true')
    parser.add_argument('-gr', '--graph_all', action='store_true')
    parser.add_argument('-s', '--server', required=False)
    args = vars(parser.parse_args())
    total_data = args['data']
    particular_client = args['particular_client']
    graph_all = args['graph_all']
    server = args['server']
    longest_client = args['longest_client']

    if longest_client and particular_client is not None:
        print("these two options cannot be enabled at the same time, aborting...")
        exit(0)
    total_data = total_data.split(",")
    longest_start_client = -1
    longest_start_client_value = 0
    for data in total_data:
        x_data = []
        for i in range(int(args['num_runs'])):
            x_data.append([])
        recent_time = 0
        if longest_client:
            with open(data, "r") as file:
                reader = csv.reader(file)
                next(reader, None)

                for row in reader:
                    if server is None or server == row[0]:
                        if int(row[2]) == 1 and float(row[3]) > longest_start_client_value:
                            longest_start_client_value = float(row[3])
                            longest_start_client = int(row[1])
            print(f'Longest client is {longest_start_client},  with {longest_start_client_value} time')
        with open(data, "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if server is None or server == row[0]:
                    if particular_client is not None or longest_start_client != -1:
                        if particular_client is not None:
                            if int(row[1]) == int(particular_client):
                                x_data[int(row[2]) - 1].append(float(row[3]))
                        else:
                            if int(row[1]) == int(longest_start_client):
                                x_data[int(row[2]) - 1].append(float(row[3]))
                    else:
                        x_data[int(row[2]) - 1].append(float(row[3]))
        final_graph_data = []
        if not graph_all:
            for i in x_data:
                final_graph_data.append(sum(i)/len(i))
            x = np.array(range(1, int(args['num_runs']) + 1))
            y = np.array(final_graph_data)
            plt.plot(x, y)
        else:
            for z in range(len(x_data[0])):
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


