import argparse
import os
import datetime as Date
import random
import subprocess
from pathlib import Path

import config_comparer
from jitserver_benchmarker import main_function

def wait_for_server(cmd):
    TIMEOUT = 10
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

    compiler_hash = config_comparer.create_unique_hash_from_path(compiler_json_file, False)
    kernel_hash = config_comparer.create_unique_hash_from_path(kernel_json_file, True)
    log_hash = compiler_hash + kernel_hash
    log_directory = config_comparer.create_hash_from_str(log_hash)

    Path(log_directory).mkdir(parents=True, exist_ok=True)

    # Run the normal server and the changed server in parallel
    # Each iteration has a warmup of the JITServer and then the actual benchmarking

    get_dir = ''
    for i in range(int(num_runs)):
        num = random.randint(0, 10000000)
        os.environ['TR_Seed'] = str(num)

        print(f"Normal JITServer run {i}")
        os.environ['IsRandomJitServer'] = 'false'
        cmd = f'{server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}},highActiveThreadThreshold=1000000000,veryHighActiveThreadThreshold=1000000000 -XcompilationThreads1'
        print("command: " + cmd)
        proc = wait_for_server(cmd)
        main_function(log_directory,compiler_json_file, kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output,False, int(num_clients), i)
        proc.kill()

        print(f"Normal JITServer run {i} done")

        print(f"Changed JITServer run {i}")
        os.environ['IsRandomJitServer'] = 'true'
        cmd = f'{server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}},highActiveThreadThreshold=1000000000,veryHighActiveThreadThreshold=1000000000 -XcompilationThreads1'
        print("command: " + cmd)
        proc = wait_for_server(cmd)
        get_dir = main_function(log_directory,compiler_json_file, kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output,True, int(num_clients), i)
        proc.kill()

        print(f"Changed JITServer run {i} done")


    # Do a final analysis of the results
    print(f'Final analysis of results in {get_dir + "/report.csv"}')

    print("Normal server results:")

    report_file = open(get_dir + '/report.csv', 'w')
    report_file.write("Run, Client, FCFS Elapsed Time, Random Elapsed Time\n")

    for i in range(int(num_runs)):
        for j in range(int(num_clients)):
            normal_file = open(get_dir + f'/normal_server/run_{i}/client_{j}/output_file.txt', 'r')
            changed_file = open(get_dir + f'/altered_server/run_{i}/client_{j}/output_file.txt', 'r')

            report_file.write(f"{i+1},{j+1},{normal_file.readlines()[-2].split()[4]},{changed_file.readlines()[-2].split()[4]}\n")

    report_file.close()