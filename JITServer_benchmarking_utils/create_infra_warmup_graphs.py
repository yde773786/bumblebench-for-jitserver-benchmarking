from warmup_grapher import create_graphs
import matplotlib.pyplot as plt
if __name__ == "__main__":
    #total_data = "work0816/future_genetic.csv"
    total_data = "../work0816/future1.csv"
    particular_client = None
    graph_all = False
    server = "baseline_server"
    longest_client = True
    num_clients = 50
    num_runs= 100
    create_graphs(total_data, particular_client, graph_all, server, longest_client, num_clients, num_runs)

    # total_data = "work0816/future_genetic.csv"
    # particular_client = None
    # graph_all = False
    # server = "ildf_server"
    # longest_client = True
    # num_clients = 50
    # num_runs= 100
    # create_graphs(total_data, particular_client, graph_all, server, longest_client, num_clients, num_runs)

    #total_data = "work0816/dotty50.csv"
    total_data = "../work0816/dotty1.csv"
    particular_client = None
    graph_all = False
    server = "baseline_server"
    longest_client = True
    num_clients = 50
    num_runs= 100
    create_graphs(total_data, particular_client, graph_all, server, longest_client, num_clients, num_runs)
    #
    # total_data = "work0816/dotty50.csv"
    # particular_client = None
    # graph_all = False
    # server = "ildf_server"
    # longest_client = True
    # num_clients = 50
    # num_runs= 100
    # create_graphs(total_data, particular_client, graph_all, server, longest_client, num_clients, num_runs)
    plt.legend(['Future-Genetic', 'Dotty'])
    # plt.legend(['future-genetic', 'future-genetic (ildf)', 'dotty', 'dotty (ildf)'])
    import matplotlib.transforms as mtransforms
    # import numpy as np
    # x = np.array(range(1, int(num_runs) + 1 ))
    # plt.fill_between(x,0,400, where=x>65, facecolor='red', alpha=0.2)
    # plt.fill_between(x,0,400, where= x<=65, facecolor='green', alpha=0.2)
    #fig, ax = plt.subplots()
    # fig.patch.set_facecolor('green')
    # fig.patch.set_alpha(0.2)
    # trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    #
    # x = np.array(range(1, int(num_runs)))
    # ax.fill_between(x, -1, 1, facecolor='green', alpha=0.2, transform=trans)
    # #ax.fill_between(x, -1, 1, where=x<=65, facecolor='red', alpha=0.2, transform=trans)
    # # # plt.fill_between(x,0,400, where=x>65, facecolor='red')
    # plt.axhspan(15,30, alpha=.2, color='red')
    #plt.plot(x, y)
    plt.savefig(f'dotty_vs_future_warmup.pdf', format="pdf")
    #plt.show()

