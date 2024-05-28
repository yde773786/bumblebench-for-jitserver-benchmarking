import subprocess
from compiler_config import get_compiler_args
from kernel_config import setup_kernel_args
import os
import argparse
from pathlib import Path
import shutil
from datetime import datetime
import config_comparer


def main_function(compiler_json_file, kernel_json_file, openj9_path, bumblebench_jitserver_path, loud_output, altered_JITserver) -> str:

    compiler_hash = config_comparer.create_unique_hash_from_path(compiler_json_file, False)
    kernel_hash = config_comparer.create_unique_hash_from_path(kernel_json_file, True)
    log_hash = compiler_hash + kernel_hash
    log_directory = config_comparer.create_hash_from_str(log_hash)
    sp_directory = log_directory

    Path(log_directory).mkdir(parents=True, exist_ok=True)

    if altered_JITserver:
        sp_directory += "/altered_server"
    else:
        sp_directory += "/normal_server"

    Path(sp_directory).mkdir(parents=True, exist_ok=True)

    xjit_flags, xaot_flags, other_flags = get_compiler_args(compiler_json_file, sp_directory)
    setup_kernel_args(kernel_json_file)

    now = str(datetime.now())
    now = now.replace(" ", ".").replace(":", "").replace("-", "")
    shutil.copy(compiler_json_file, sp_directory + "/compiler_config.json")
    shutil.copy(kernel_json_file, sp_directory + "/kernel_config.json")

    if loud_output:
        command = f"{openj9_path} -jar {xjit_flags} {xaot_flags} {other_flags} {bumblebench_jitserver_path}/BumbleBench.jar JITserver"
        subprocess.call(command, shell=True)
    else:
        command = f"{openj9_path} -jar {xjit_flags} {xaot_flags} {other_flags} {bumblebench_jitserver_path}/BumbleBench.jar JITserver > {sp_directory}/output_file.{now}"
        subprocess.call(command, shell=True)

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
    main_function(compiler_json_file,kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output, False)