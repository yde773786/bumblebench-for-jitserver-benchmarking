import argparse
import pandas as pd
import csv
import seaborn
import matplotlib.pyplot as plt
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that graphs a cdf function from data"
    )

    parser.add_argument('-d', '--data', required=True)

    args = vars(parser.parse_args())

    data = args['data']

    run = 0
    data_1 = []
    data_2 = []

    normal_data = []
    random_data = []
    with open(data, "r") as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            if int(row[0]) != run:
                run = int(row[0])
                if data_1 != []:
                    normal_data.append(sum(data_1)/len(data_1))
                    random_data.append(sum(data_2)/len(data_2))
                    data_1 = []
                    data_2 = []
            data_1.append(float(row[2]))
            data_2.append(float(row[3]))
    df = pd.DataFrame({"normal_data:": normal_data})
    df2 = pd.DataFrame({"random_data:": random_data})

    both = pd.concat([df, df2], axis=1)
    print(both)
    seaborn.ecdfplot(data=both)

    plt.show()

