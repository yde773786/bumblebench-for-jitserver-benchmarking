import argparse
import os
import datetime as Date
import shutil
from multiprocessing import Process
from compiler_config import get_compiler_args, change_vlog_directory
from kernel_config import setup_kernel_args
import time
import subprocess
from pathlib import Path
import config_comparer


def remove_empty_strings(lst) -> list:
    new_list = []
    for i in lst:
        if i.strip() != "":
            new_list.append(i)
    return new_list


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

def start_continuous_load(openj9_path, bumblebench_jitserver_path, xjit_flags, xaot_flags, other_flags, time_to_run,
                          log_directory, loud_output):
    limit = Date.datetime.now() + Date.timedelta(seconds=int(time_to_run))

    d_err = Path(f'{log_directory}/Error').mkdir(parents=True, exist_ok=True)
    d_err = f'{log_directory}/Error'
    d_out = Path(f'{log_directory}/Output').mkdir(parents=True, exist_ok=True)
    d_out = f'{log_directory}/Output'
    d_ver = Path(f'{log_directory}/Vlog').mkdir(parents=True, exist_ok=True)
    d_ver = f'{log_directory}/Vlog'

    i = 0

    while Date.datetime.now() < limit:

        now = str(Date.datetime.now())
        now = now.replace(" ", ".").replace(":", "").replace("-", "")

        if loud_output:
            command = f'{openj9_path} {xjit_flags} {xaot_flags} {other_flags} -jar {bumblebench_jitserver_path}/BumbleBench.jar JITserver'
            print("client command" + command)
            command = command.replace("'", "")
            command_splt = command.split(" ")
            command_splt = remove_empty_strings(command_splt)
            client_process = subprocess.Popen(command_splt)
            client_process.wait()
        else:
            xjit_flags = change_vlog_directory(xjit_flags, d_ver)

            f_err = open(f'{d_err}/error_file{i}.txt', "w")
            f = open(f'{d_out}/output_file{i}.txt', "w")
            command = f'{openj9_path} {xjit_flags} {xaot_flags} {other_flags} -jar {bumblebench_jitserver_path}/BumbleBench.jar JITserver'
            print("client command" + command)
            command = command.replace("'", "")
            command_splt = command.split(" ")
            command_splt = remove_empty_strings(command_splt)
            client_process = subprocess.Popen(command_splt, stdout=f, stderr=f_err)
            client_process.wait()

        i += 1


if __name__ == "__main__":
    os.environ['TR_Seed'] = str(0)
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that runs the individual continuous loads concurrently"
    )

    parser.add_argument('-o', '--openj9_path', required=True)
    parser.add_argument('-c', '--compiler_configuration', required=True)
    parser.add_argument('-b', '--bumblebench_jitserver_path', required=True)
    parser.add_argument('-l', '--loud_output', action='store_true')
    parser.add_argument('-k', '--kernel_configuration', required=True)
    parser.add_argument('-t', '--time_to_run', required=True)

    parser.add_argument('-n', '--number_of_clients', required=True)
    parser.add_argument('-s', '--staggering_time_between_loads', required=True)
    parser.add_argument('-f', '--figure_name', required=False)

    args = vars(parser.parse_args())

    compiler_json_file = args['compiler_configuration']
    kernel_json_file = args['kernel_configuration']
    openj9_path = args['openj9_path']
    bumblebench_jitserver_path = args['bumblebench_jitserver_path']
    loud_output = args['loud_output']
    time_to_run = args['time_to_run']
    num_clients = args['number_of_clients']
    staggering_time = args['staggering_time_between_loads']
    figure_name = args['figure_name']
    server_path = openj9_path + "/jitserver"
    openj9_path = openj9_path + "/java"
    cmd = ''

    compiler_hash = config_comparer.create_unique_hash_from_path(compiler_json_file, False, loud_output)
    kernel_hash = config_comparer.create_unique_hash_from_path(kernel_json_file, True, loud_output)
    log_hash = compiler_hash + kernel_hash
    log_hash_plus_info = log_hash + str(time_to_run) + str(num_clients) + str(staggering_time)
    log_directory = config_comparer.create_hash_from_str(log_hash_plus_info)

    base_path = f'clw_clients_{num_clients}_stagger_{staggering_time}_run_time_{time_to_run}'
    Path(base_path).mkdir(parents=True, exist_ok=True)
    log_directory = f'{base_path}/{log_directory}'

    Path(log_directory).mkdir(parents=True, exist_ok=True)

    cmd_options = open(f'{log_directory}/command_line_options.txt', "w")
    cmd_options.write(f'time clients run: {time_to_run}\n')
    cmd_options.write(f'number of clients: {num_clients}\n')
    cmd_options.write(f'initial staggering time between loads: {staggering_time}\n')
    cmd_options.write(f'config hash: {config_comparer.create_hash_from_str(log_hash)}\n')
    cmd_options.close()

    # Run the normal server and the changed server in parallel
    # Each iteration has a warmup of the JITServer and then the actual benchmarking

    get_dir = ''
    clients = []

    xjit_flags, xaot_flags, other_flags = get_compiler_args(compiler_json_file, log_directory)
    setup_kernel_args(kernel_json_file)

    run_env_vars = [None,'IsRoundRobinJitServer','IsLeastDoneFirstJitServer']
    directories = ['normal_server', 'round_robin_server', 'least_done_first_server']

    for i in range(len(run_env_vars)):
        print(f'{directories[i]} run')
        os.environ['IsRoundRobinJitServer'] = 'false'
        os.environ['IsLeastDoneFirstJitServer'] = 'false'
        if run_env_vars[i] is not None:
            os.environ[run_env_vars[i]] = 'true'

        cmd = f'{server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}},highActiveThreadThreshold=1000000000,veryHighActiveThreadThreshold=1000000000 -XcompilationThreads1'
        print("server command: " + cmd)
        server = wait_for_server(cmd)
        sp_directory = log_directory + f'/{directories[i]}'
        Path(sp_directory).mkdir(parents=True, exist_ok=True)
        shutil.copy(compiler_json_file, sp_directory + "/compiler_config.json")
        shutil.copy(kernel_json_file, sp_directory + "/kernel_config.json")
        now = str(Date.datetime.now())
        now = now.replace(" ", ".").replace(":", "").replace("-", "")

        for i in range(int(num_clients)):
            Path(f"{sp_directory}/client_{i}").mkdir(parents=True, exist_ok=True)
            client_directory = f"{sp_directory}/client_{i}"
            command = Process(target=start_continuous_load, args=(
            openj9_path, bumblebench_jitserver_path, xjit_flags, xaot_flags, other_flags, time_to_run, client_directory,
            loud_output))
            command.start()
            clients.append(command)
            time.sleep(int(staggering_time))
        for client in clients:
            client.join()

        shutil.copy('servervlog.txt', sp_directory + f'/servervlog_file.{now}')
        server.kill()

        print(f"{directories[i]} run done")

    # Do a final analysis of the results
    get_dir = log_directory
    print(f'Final analysis of results in {get_dir + "/report.csv"}')

    print("Normal server results:")

    per_client_report_file = open(get_dir + '/report_per_client.csv', 'w')
    per_client_report_file.write("Server, Client, Run, Elapsed Time(s)\n")

    for q in range(len(directories)):
        for i in range(int(num_clients)):
            for j, output_file in enumerate(os.listdir(get_dir + f'/{directories[q]}/client_{i}/Output')):
                normal_file = open(get_dir + f'/{directories[q]}/client_{i}/Output/output_file{j}.txt', 'r')
                normal_elapsed_time = round(int(normal_file.readlines()[-2].split()[4]) / (10 ** 9), 2)
                per_client_report_file.write(f"{directories[q]}, {i + 1}, {j + 1}, {normal_elapsed_time}\n")

    per_client_report_file.close()
    cmd = ''
    if figure_name is not None:
        cmd = f'python3 cdf_grapher.py -d {get_dir}/report_per_client.csv -f {figure_name} -clw'
    else:
        cmd = f'python3 cdf_grapher.py -d {get_dir}/report_per_client.csv -clw'
    proc = subprocess.Popen(cmd, shell=True)
