import argparse
import os
import datetime as Date
import shutil
from multiprocessing import Process

import constants
from compiler_config import get_compiler_args, change_vlog_directory
from kernel_config import setup_kernel_args
import time
import subprocess
from pathlib import Path
import config_comparer
import git

PATH_ON_MACHINE = "~/bumblebench-for-jitserver-benchmarking/JITServer_benchmarking_utils"

def remove_empty_strings(lst) -> list:
    new_list = []
    for i in lst:
        if i.strip() != "":
            new_list.append(i)
    return new_list

def per_machine_run(machine_name, arg_passed):
    os.system(f'ssh -o "StrictHostKeyChecking no" {machine_name} "cd {PATH_ON_MACHINE} ; python3 start_continuous_load.py {arg_passed}"')
    print(f'ssh -o "StrictHostKeyChecking no" {machine_name} "cd {PATH_ON_MACHINE} ; python3 start_continuous_load.py {arg_passed}"')

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
    os.environ['TR_Seed'] = str(0)
    parser = argparse.ArgumentParser(
        prog='runwrapper',
        description="A Script that runs the individual continuous loads concurrently"
    )

    parser.add_argument('-oa', '--openj9_path', required=True)
    parser.add_argument('-c', '--compiler_configuration', required=True)
    parser.add_argument('-b', '--bumblebench_jitserver_path', required=True)
    parser.add_argument('-l', '--loud_output', action='store_true')
    parser.add_argument('-k', '--kernel_configuration', required=True)
    parser.add_argument('-ti', '--time_to_run', required=True)
    parser.add_argument('-rc', '--run_clients_on_machines', nargs='+', required=False)
    parser.add_argument('-n', '--number_of_clients', required=True)
    parser.add_argument('-s', '--staggering_time_between_loads', required=True)
    parser.add_argument('-f', '--figure_name', required=False)
    parser.add_argument('-oo', '--original_openj9_path', required=True)
    parser.add_argument('-th', '--thread_count', required=True)

    args = vars(parser.parse_args())

    compiler_json_file = args['compiler_configuration']
    kernel_json_file = args['kernel_configuration']
    openj9_path = args['openj9_path']
    original_openj9_path = args['original_openj9_path']
    bumblebench_jitserver_path = args['bumblebench_jitserver_path']
    loud_output = args['loud_output']
    time_to_run = args['time_to_run']
    num_clients = args['number_of_clients']
    staggering_time = args['staggering_time_between_loads']
    figure_name = args['figure_name']
    thread_count = args['thread_count']
    server_path = openj9_path + "/jitserver"
    openj9_path = openj9_path + "/java"
    baseline_server_path = original_openj9_path + "/jitserver"
    baseline_openj9_path = original_openj9_path + "/java"
    cmd = ''
    rc = args['run_clients_on_machines']

    num_clients_per_machine = 0

    if rc is not None and len(rc) > 0:
        num_clients_per_machine = int(num_clients) // len(rc)


    compiler_hash = config_comparer.create_unique_hash_from_path(compiler_json_file, False, loud_output)
    kernel_hash = config_comparer.create_unique_hash_from_path(kernel_json_file, True, loud_output)
    log_hash = compiler_hash + kernel_hash
    log_hash_plus_info = log_hash + str(time_to_run) + str(num_clients) + str(staggering_time) + str(thread_count)

    staggering_time_str = str(staggering_time)
    staggering_time_str = staggering_time_str.replace(".","p")

    openj9_repo_path = f'{openj9_path.split("build/linux-x86_64-server-release/jdk/bin")[0]}openj9'
    git_branch = git.Repo(openj9_repo_path).active_branch.name
    git_commit = git.Repo(openj9_repo_path).git.rev_parse("HEAD")
    base_path = f'clw_cli_{num_clients}_sta_{staggering_time_str}_rt_{time_to_run}_b_{git_branch}_com_{git_commit[:7]}_tc_{thread_count}'
    Path(base_path).mkdir(parents=True, exist_ok=True)
    num_files = len(os.listdir(base_path))
    log_hash_plus_info += str(num_files) + git_commit

    log_directory = config_comparer.create_hash_from_str(log_hash_plus_info)
    log_directory = f'{base_path}/{log_directory}'

    Path(log_directory).mkdir(parents=True, exist_ok=True)

    cmd_options = open(f'{log_directory}/command_line_options.txt', "w")
    cmd_options.write(f'time clients run: {time_to_run}\n')
    cmd_options.write(f'number of clients: {num_clients}\n')
    cmd_options.write(f'initial staggering time between loads: {staggering_time}\n')
    cmd_options.write(f'thread_count: {thread_count}\n')
    cmd_options.write(f'config hash: {config_comparer.create_hash_from_str(log_hash)}\n')
    cmd_options.write(f'git branch: {git_branch}\n')
    cmd_options.write(f'git commit: {git_commit}\n')
    cmd_options.close()

    # Run the normal server and the changed server in parallel
    # Each iteration has a warmup of the JITServer and then the actual benchmarking

    get_dir = ''
    clients = []

    xjit_flags, xaot_flags, other_flags = get_compiler_args(compiler_json_file, log_directory)
    setup_kernel_args(kernel_json_file)

    run_env_vars = constants.run_env_vars
    directories = constants.directories

    for i in range(len(run_env_vars)):
        print(f'{directories[i]} run')
        for var in run_env_vars:
            if var is not None:
                os.environ[var] = 'false'
        if run_env_vars[i] is not None:
            os.environ[run_env_vars[i]] = 'true'

        cmd = f'{server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}},highActiveThreadThreshold=1000000000,veryHighActiveThreadThreshold=1000000000 -XcompilationThreads{thread_count}'
        print("server command: " + cmd)
        server = wait_for_server(cmd)
        sp_directory = log_directory + f'/{directories[i]}'
        Path(sp_directory).mkdir(parents=True, exist_ok=True)
        shutil.copy(compiler_json_file, sp_directory + "/compiler_config.json")
        shutil.copy(kernel_json_file, sp_directory + "/kernel_config.json")
        now = str(Date.datetime.now())
        now = now.replace(" ", ".").replace(":", "").replace("-", "")

        # Shenanigans to pass the arguments to start_continuous_load.py
        arg = '한'.join([openj9_path, bumblebench_jitserver_path, xjit_flags, xaot_flags, other_flags, str(time_to_run), sp_directory, str(loud_output), str(num_clients_per_machine), str(staggering_time)])
        arg = arg.replace(" ", "자")

        if num_clients_per_machine > 0:
            runs = []
            # Run the clients on the machines, distriubted evenly
            for machine in rc:
                p = Process(target=per_machine_run, args=(machine, arg))
                runs.append(p)
                p.start()

            for p in runs:
                p.join()
        else:
            os.system(f'python3 start_continuous_load.py {arg}')

        shutil.copy('servervlog.txt', sp_directory + f'/servervlog_file.{now}')
        server.kill()
        server.wait()

        print(f"{directories[i]} run done")
    directories.append("baseline_server")

    cmd = f'{baseline_server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}},highActiveThreadThreshold=1000000000,veryHighActiveThreadThreshold=1000000000 -XcompilationThreads{thread_count}'
    print("server command: " + cmd)
    server = wait_for_server(cmd)
    sp_directory = log_directory + f'/baseline_server'
    Path(sp_directory).mkdir(parents=True, exist_ok=True)
    shutil.copy(compiler_json_file, sp_directory + "/compiler_config.json")
    shutil.copy(kernel_json_file, sp_directory + "/kernel_config.json")
    now = str(Date.datetime.now())
    now = now.replace(" ", ".").replace(":", "").replace("-", "")

    # Shenanigans to pass the arguments to start_continuous_load.py
    arg = '한'.join([baseline_openj9_path, bumblebench_jitserver_path, xjit_flags, xaot_flags, other_flags, str(time_to_run), sp_directory, str(loud_output), str(num_clients_per_machine), str(staggering_time)])
    arg = arg.replace(" ", "자")

    if num_clients_per_machine > 0:
        # Run the clients on the machines, distriubted evenly
        for machine in rc:
            os.system(f'ssh {machine} "cd {PATH_ON_MACHINE} ; python3 start_continuous_load.py {arg}"')
    else:
        # Run the clients on the local machine
        os.system(f'python3 start_continuous_load.py {arg}')

    shutil.copy('servervlog.txt', sp_directory + f'/servervlog_file.{now}')
    server.kill()
    server.wait()

    print(f"baseline_server run done")


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
