from warmup_grapher import create_graphs
import matplotlib.pyplot as plt
if __name__ == "__main__":
    total_data = "analytics/set_of_runs/11/clw_cli_50_sta_25_rt_2_b_quickInfoGetterThreaded_com_df11e8f_docker_tc_63_renaissance_0/report_per_client.csv"
    particular_client = None
    graph_all = False
    server = "baseline_server"
    longest_client = True
    num_clients = 50
    num_runs= 100
    create_graphs(total_data, particular_client, graph_all, server, longest_client, num_clients, num_runs)

    total_data = "analytics/set_of_runs/10/clw_cli_50_sta_50_rt_2_b_quickInfoGetterThreaded_com_31e96d2_docker_tc_63_renaissance_0/report_per_client.csv"
    particular_client = None
    graph_all = False
    server = "baseline_server"
    longest_client = True
    num_clients = 50
    num_runs= 100
    create_graphs(total_data, particular_client, graph_all, server, longest_client, num_clients, num_runs)
    plt.legend(['future-genetic', 'dotty'])
    plt.show()

