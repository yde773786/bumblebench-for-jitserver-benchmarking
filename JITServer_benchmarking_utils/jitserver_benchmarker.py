import subprocess
from compiler_config import get_compiler_args, change_vlog_directory
from kernel_config import setup_kernel_args
import argparse
from pathlib import Path
import shutil
from datetime import datetime
import config_comparer

def remove_empty_strings(lst) -> list:
    new_list = []
    for i in lst:
        if i.strip() != "":
            new_list.append(i)
    return new_list

def main_function(log_directory, compiler_json_file, kernel_json_file, openj9_path, bumblebench_jitserver_path, loud_output, sp_directory, num_clients, run) -> str:
    clients = []

    sp_directory += f'/run_{run}'

    Path(sp_directory).mkdir(parents=True, exist_ok=True)

    xjit_flags, xaot_flags, other_flags = get_compiler_args(compiler_json_file, sp_directory)
    setup_kernel_args(kernel_json_file)

    now = str(datetime.now())
    now = now.replace(" ", ".").replace(":", "").replace("-", "")
    shutil.copy(compiler_json_file, sp_directory + "/compiler_config.json")
    shutil.copy(kernel_json_file, sp_directory + "/kernel_config.json")

    if loud_output:
        for i in range(num_clients):
            command = f'{openj9_path} {xjit_flags} {xaot_flags} {other_flags} -jar {bumblebench_jitserver_path}/BumbleBench.jar JITserver'
            print("client command" + command)
            command = command.replace("'","")
            command_splt = command.split(" ")
            command_splt = remove_empty_strings(command_splt)
            client_process = subprocess.Popen(command_splt)
            clients.append(client_process)
        for client in clients:
            client.wait()
        shutil.copy('servervlog.txt', sp_directory + f'/servervlog_file.{now}')
    else:
        for i in range(num_clients):
            client_directory = f'{sp_directory}/client_{i}'

            xjit_flags = change_vlog_directory(xjit_flags, client_directory)

            Path(client_directory).mkdir(parents=True, exist_ok=True)

            f_err = open(f'{client_directory}/error_file.txt', "w")
            f = open(f'{client_directory}/output_file.txt', "w")
            command = f'{openj9_path} {xjit_flags} {xaot_flags} {other_flags} -jar {bumblebench_jitserver_path}/BumbleBench.jar JITserver'
            print("client command" + command)
            command = command.replace("'","")
            command_splt = command.split(" ")
            command_splt = remove_empty_strings(command_splt)
            client_process = subprocess.Popen(command_splt, stdout=f, stderr=f_err)
            clients.append(client_process)
        for client in clients:
            client.wait()
        shutil.copy('servervlog.txt', sp_directory + f'/servervlog_file.{now}')
        f.close()

    return log_directory

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='jitserver_benchmarker',
        description="A Script that takes in a configuration of kernels and uses BumbleBench for JITServer to benchmark"
    )

    parser.add_argument('-o', '--openj9_path', required=True)
    parser.add_argument('-c', '--compiler_configuration', required=True)
    parser.add_argument('-b', '--bumblebench_jitserver_path', required=True)
    parser.add_argument('-l', '--loud_output', action='store_true')
    parser.add_argument('-k', '--kernel_configuration', required=True)

    args = vars(parser.parse_args())

    compiler_json_file = args['compiler_configuration']
    kernel_json_file = args['kernel_configuration']
    openj9_path = args['openj9_path']
    bumblebench_jitserver_path = args['bumblebench_jitserver_path']
    loud_output = args['loud_output']

    compiler_hash = config_comparer.create_unique_hash_from_path(compiler_json_file, False, loud_output)
    kernel_hash = config_comparer.create_unique_hash_from_path(kernel_json_file, True, loud_output)
    log_hash = compiler_hash + kernel_hash
    log_directory = config_comparer.create_hash_from_str(log_hash)

    Path(log_directory).mkdir(parents=True, exist_ok=True)
    
    main_function(log_directory, compiler_json_file, kernel_json_file, openj9_path,bumblebench_jitserver_path,loud_output, log_directory+"/normal_server", 1, 1)