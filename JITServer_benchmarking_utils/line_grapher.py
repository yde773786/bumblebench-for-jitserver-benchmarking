import argparse
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that graphs a line graph of the size of the server queues"
    )

    parser.add_argument('-d', '--data', required=True)
    args = vars(parser.parse_args())
    total_data = args['data']
    total_data = total_data.split(",")
    for data in total_data:
        x_data = []
        y_data = []
        with open(data, "r") as file:
            for row in file:
                if "#INFO:  size:" in row:
                    splitted = row.split(":")
                    num = int(splitted[2])
                    other_num = float(splitted[4])
                    x_data.append(other_num)
                    y_data.append(num)
        x = np.array(x_data)
        y = np.array(y_data)
        plt.plot(x, y)
    plt.title("Server size vs time at the JITServer (100 clients)")
    plt.xlabel("Time (s)")
    plt.ylabel("Server size")
    plt.show()


