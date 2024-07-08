import argparse
import os

from JITServer_benchmarking_utils import constants

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that graphs a cdf function from data"
    )

    parser.add_argument('-d', '--data', required=True)
    parser.add_argument('-clw', '--continuous_load_wrapper', action='store_true')
    args = vars(parser.parse_args())
    total_data = args['data']
    continuous_load_wrapper = args['continuous_load_wrapper']
    per_client_report_file = open(total_data + '/report_per_client.csv', 'w')
    per_client_report_file.write("Server, Client, Run, Elapsed Time(s)\n")
    directories = constants.directories
    if not continuous_load_wrapper:
        files_in_dir = os.listdir(total_data + f'/{directories[0]}')
        clients_in_dir = [k for k in files_in_dir if "client" in k]
        for q in range(len(directories)):
            for i in range(int(len(clients_in_dir))):
                for j, output_file in enumerate(os.listdir(total_data + f'/{directories[q]}/client_{i}/Output')):
                    normal_file = open(total_data + f'/{directories[q]}/client_{i}/Output/output_file{j}.txt', 'r')
                    normal_elapsed_time = round(int(normal_file.readlines()[-2].split()[4]) / (10 ** 9), 2)
                    per_client_report_file.write(f"{directories[q]}, {i + 1}, {j + 1}, {normal_elapsed_time}\n")
    else:
        per_client_report_file = open(total_data + '/report_per_client.csv', 'w')

        header_string = "Run, Client"
        for i in range(len(directories)):
            header_string += f',{directories[i]} Elapsed Time (s)'
        header_string += "\n"

        per_client_report_file.write(header_string)

        completed_runs = []
        for i in range(len(directories)):
            files_in_dir = os.listdir(total_data + f'/{directories[i]}')
            runs_in_dir = [k for k in files_in_dir if "run" in k]
            completed_runs.append(len(runs_in_dir))
        num_runs = max(completed_runs)
        num_clients = 0
        if num_runs > 0:
            files_in_dir = os.listdir(total_data + f'/{directories[0]}/run_0')
            clients_in_dir = [k for k in files_in_dir if "client" in k]
            num_clients = len(clients_in_dir)

        for i in range(int(num_runs)):
            for j in range(int(num_clients)):
                times = []
                for q in range(len(directories)):
                    file = open(total_data + f'/{directories[q]}/run_{i}/client_{j}/output_file.txt', 'r')
                    times.append(round(int(file.readlines()[-2].split()[4]) / (10 ** 9), 2))

                middle_str = f"{i+2},{j+1}"
                for q in range(len(times)):
                    middle_str += f',{times[q]}'
                middle_str += '\n'
                per_client_report_file.write(middle_str)

    per_client_report_file.close()