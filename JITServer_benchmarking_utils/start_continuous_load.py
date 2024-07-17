import sys
import datetime as Date
from pathlib import Path
import argparse
import subprocess
import time
from multiprocessing import Process
import sys
from compiler_config import change_vlog_directory


def remove_empty_strings(lst) -> list:
    new_list = []
    for i in lst:
        if i.strip() != "":
            new_list.append(i)
    return new_list

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
            print(xjit_flags)

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

clients = []

if __name__ == '__main__':

    # print(sys.argv)
    arg = sys.argv[1]
    arg = arg.replace("자", " ")
    arg = arg.split('한')

    print(arg)
    openj9_path = arg[0]
    bumblebench_jitserver_path = arg[1]
    xjit_flags = arg[2]
    xaot_flags = arg[3]
    other_flags = arg[4]
    time_to_run = float(arg[5])
    sp_directory = arg[6]
    loud_output = True if arg[7] == "True" else False 
    num_clients = int(arg[8])
    staggering_time = float(arg[9])

    # print(openj9_path)
    # print(bumblebench_jitserver_path)
    # print(xjit_flags)
    # print(xaot_flags)
    # print(other_flags)
    # print(time_to_run)
    # print(sp_directory)
    # print(loud_output)
    # print(num_clients)
    # print(staggering_time)

    for q in range(int(num_clients)):
        Path(f"{sp_directory}/client_{q}").mkdir(parents=True, exist_ok=True)
        client_directory = f"{sp_directory}/client_{q}"
        command = Process(target=start_continuous_load, args=(
        openj9_path, bumblebench_jitserver_path, xjit_flags, xaot_flags, other_flags, time_to_run, client_directory,
        loud_output))
        command.start()
        clients.append(command)
        time.sleep(float(staggering_time))
    for client in clients:
        client.join()