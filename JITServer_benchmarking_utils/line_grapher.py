import argparse
import numpy as np
import matplotlib
import re
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
        x_data2 = []
        y_data2 = []
        recent_time = 0
        with open(data, "rb") as file:
            counter = 0
            counter2 = 0
            for row in file:
                row = row.decode('utf-8', 'ignore')
                # if "#INFO:  size:" in row:
                #     counter += 1
                #     if counter == 100:
                #         counter = 0
                #         import re
                #         row = re.findall(r"[\x20-\x7E]+", row)
                #         s = ''
                #         row = s.join(row)
                #         splitted = row.split("#INFO:")
                #         splitted = splitted[1].split(":")
                #         num = int(splitted[1])
                #         result = re.match(r"[\x20-\x7E]+", splitted[3]).group()
                #         other_num = result
                #         x_data.append(other_num)
                #         y_data.append(num)
                if "#INFO:  size:" in row:
                    row = re.findall(r"[\x20-\x7E]+", row)
                    s = ''
                    row = s.join(row)
                    splitted = row.split("#INFO:")
                    splitted = splitted[1].split(":")
                    num = int(splitted[1])
                    result = re.match(r"[\x20-\x7E]+", splitted[3]).group()
                    other_num = result
                    other_num = re.search(r"[0-9]+\.[0-9]+",other_num).group()
                    recent_time = round(float(other_num),2)
                if "#INFO:  num methods to process:" in row:
                    counter += 1
                    if counter == 100:
                        counter = 0
                        import re
                        row = re.findall(r"[\x20-\x7E]+", row)
                        s = ''
                        row = s.join(row)
                        splitted = row.split("#INFO:")
                        splitted = splitted[1].split(":")
                        num = int(re.search(r"[0-9]+",splitted[1]).group())
                        result = recent_time
                        other_num = result
                        x_data.append(other_num)
                        y_data.append(num)
                if "#INFO:  method queue 2 size:" in row:
                    counter2 += 1
                    if counter2 == 100:
                        counter2 = 0
                        import re
                        row = re.findall(r"[\x20-\x7E]+", row)
                        s = ''
                        row = s.join(row)
                        splitted = row.split("#INFO:")
                        splitted = splitted[1].split(":")
                        num = int(re.search(r"[0-9]+",splitted[1]).group())
                        result = recent_time
                        other_num = result
                        x_data2.append(other_num)
                        y_data2.append(num)
        print(len(x_data))
        x = np.array(x_data)
        y = np.array(y_data)
        plt.plot(x, y)
        x2 =  np.array(x_data2)
        y2 = np.array(y_data2)
        plt.plot(x2, y2)
    plt.title("Server size vs time at the JITServer (100 clients)")
    plt.xlabel("Time (s)")
    plt.ylabel("Server size")
    plt.show()


