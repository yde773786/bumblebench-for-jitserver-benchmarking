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
        counter = 0
        with open(data, "r") as file:
            for row in file:
                if "#INFO:  size:" in row:
                    splitted = row.split(":")
                    num = int(splitted[2])
                    x_data.append(counter)
                    y_data.append(num)
                    counter += 1
        x = np.array(x_data)
        y = np.array(y_data)
        plt.plot(x, y)
    plt.show()


