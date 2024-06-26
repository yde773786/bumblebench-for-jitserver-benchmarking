import argparse
import os
import datetime as Date
import random
import subprocess
from pathlib import Path

import config_comparer
from jitserver_benchmarker import main_function

def wait_for_server(cmd):
    TIMEOUT = 20
    current_time = Date.datetime.now()

    server_vlog_file = open("servervlog.txt", "w")

    # Use exec to ensure the process is killed if the script is killed
    proc = subprocess.Popen('exec ' + cmd, stdout=server_vlog_file, stderr=subprocess.STDOUT, text=True, shell=True)
    server_read = open("servervlog.txt", "r")
    while True:
        line = server_read.readline().strip()
        if line:
            print(line)
        if line == "JITServer is ready to accept incoming requests":
            return proc
        if Date.datetime.now() - current_time > Date.timedelta(seconds=TIMEOUT):
            proc.kill()  # Ensure the process is killed if it times out
            raise TimeoutError("JITServer did not start in time")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that takes in a configuration of kernels and uses BumbleBench for JITServer to benchmark"
    )

    parser.add_argument('-o', '--openj9_path', required=True)
    parser.add_argument('-c', '--compiler_configuration', required=True)
    parser.add_argument('-b', '--bumblebench_jitserver_path', required=True)
    parser.add_argument('-l', '--loud_output', action='store_true')
    parser.add_argument('-k', '--kernel_configuration', required=True)
    parser.add_argument('-n', '--number_of_runs', required=True)
    parser.add_argument('-m', '--number_of_clients', required=True)


    args = vars(parser.parse_args())

    compiler_json_file = args['compiler_configuration']
    kernel_json_file = args['kernel_configuration']
    openj9_path = args['openj9_path']
    bumblebench_jitserver_path = args['bumblebench_jitserver_path']
    loud_output = args['loud_output']
    num_runs = args['number_of_runs']
    num_clients = args['number_of_clients']
    server_path = openj9_path + "/jitserver"
    openj9_path = openj9_path + "/java"
    cmd = ''

    compiler_hash = config_comparer.create_unique_hash_from_path(compiler_json_file, False, loud_output)
    kernel_hash = config_comparer.create_unique_hash_from_path(kernel_json_file, True, loud_output)
    log_hash = compiler_hash + kernel_hash
    log_hash_plus_info = log_hash + str(num_runs) + str(num_clients)
    log_directory = config_comparer.create_hash_from_str(log_hash_plus_info)

    Path(log_directory).mkdir(parents=True, exist_ok=True)

    cmd_options = open(f'{log_directory}/command_line_options.txt', "w")
    cmd_options.write(f'number of runs: {num_runs}\n')
    cmd_options.write(f'number of clients: {num_clients}\n')
    cmd_options.write(f'config hash: {config_comparer.create_hash_from_str(log_hash)}\n')
    cmd_options.close()



    # Run the normal server and the changed server in parallel
    # Each iteration has a warmup of the JITServer and then the actual benchmarking

    get_dir = ''
    for i in range(int(num_runs)):
        num = random.randint(0, 10000000)
        os.environ['TR_Seed'] = str(num)

        print(f"Normal JITServer run {i}")
        os.environ['IsRandomJitServer'] = 'false'
        cmd = f'{server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}},highActiveThreadThreshold=1000000000,veryHighActiveThreadThreshold=1000000000 -XcompilationThreads1'
        print("server command: " + cmd)
        proc = wait_for_server(cmd)
        main_function(log_directory,compiler_json_file, kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output,False, int(num_clients), i)
        proc.kill()

        print(f"Normal JITServer run {i} done")

        os.environ['TR_Seed'] = str(num)
        print(f"Changed JITServer run {i}")
        os.environ['IsRandomJitServer'] = 'true'
        cmd = f'{server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}},highActiveThreadThreshold=1000000000,veryHighActiveThreadThreshold=1000000000 -XcompilationThreads1'
        print("server command: " + cmd)
        proc = wait_for_server(cmd)
        get_dir = main_function(log_directory,compiler_json_file, kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output,True, int(num_clients), i)
        proc.kill()

        print(f"Changed JITServer run {i} done")


    # Do a final analysis of the results
    print(f'Final analysis of results in {get_dir + "/report.csv"}')

    print("Normal server results:")

    per_client_report_file = open(get_dir + '/report_per_client.csv', 'w')
    per_run_report_file = open(get_dir + '/report_per_run.csv', 'w')
    per_client_report_file.write("Run, Client, FCFS Elapsed Time (s), Random Elapsed Time (s)\n")
    per_run_report_file.write("Run, Max FCFS Elapsed Time (s), Max Random Elapsed Time (s), Min FCFS Elapsed Time (s), Min Random Elapsed Time (s), Average FCFS Elapsed Time (s), Average Random Elapsed Time (s)\n")

    for i in range(int(num_runs)):
        fcfs_elapsed_times = []
        random_elapsed_times = []

        for j in range(int(num_clients)):
            normal_file = open(get_dir + f'/normal_server/run_{i}/client_{j}/output_file.txt', 'r')
            changed_file = open(get_dir + f'/altered_server/run_{i}/client_{j}/output_file.txt', 'r')

            normal_elapsed_time = round(int(normal_file.readlines()[-2].split()[4]) / (10 ** 9), 2)
            changed_elapsed_time = round(int(changed_file.readlines()[-2].split()[4]) / (10 ** 9), 2)

            per_client_report_file.write(f"{i+2},{j+1},{normal_elapsed_time},{changed_elapsed_time}\n")
            fcfs_elapsed_times.append(normal_elapsed_time)
            random_elapsed_times.append(changed_elapsed_time)

        per_run_report_file.write(f'{i+1},{max(fcfs_elapsed_times)},{max(random_elapsed_times)},{min(fcfs_elapsed_times)}, {min(random_elapsed_times)},{sum(fcfs_elapsed_times)/len(fcfs_elapsed_times)},{sum(random_elapsed_times)/len(random_elapsed_times)}\n')

    per_client_report_file.close()
    per_run_report_file.close()
