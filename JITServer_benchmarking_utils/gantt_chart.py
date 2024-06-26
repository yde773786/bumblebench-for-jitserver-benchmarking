import argparse
import random

import pandas as pd
import plotly.figure_factory as ff
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that graphs a line graph of the size of the server queues"
    )

    parser.add_argument('-d', '--data', required=True)
    args = vars(parser.parse_args())
    total_data = args['data']

    data = []
    start_time = 0
    client_set = set()
    with open(total_data, "r") as file:
        for row in file:
            if "#INFO:  Elapsed Time processing entry from client" in row:
                splitted = row.split("<")
                client_id = splitted[1].split(">")[0]
                end_time = float(splitted[2].split(">")[0])
                bar = dict(Task=f'{client_id}', Start=start_time, Finish=start_time+end_time, Resource=f'{client_id}')
                if client_id not in client_set:
                    client_set.add(client_id)
                start_time += end_time
                data.append(bar)
    r = lambda: random.randint(0,255)
    colors = ['#%02X%02X%02X' % (r(),r(),r())]
    for i in range(1, len(client_set)):
        colors.append('#%02X%02X%02X' % (r(),r(),r()))

    df = pd.DataFrame(data)
    fig = ff.create_gantt(df, index_col='Resource',colors=colors, bar_width=0.4, show_colorbar=True, group_tasks=True)
    fig.update_layout(xaxis_type='linear', autosize=False, width=1600, height=800)
    fig.show()