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

openj9_path = sys.argv[1]
bumblebench_jitserver_path = sys.argv[2]
xjit_flags = sys.argv[3]
xaot_flags = sys.argv[4]
other_flags = sys.argv[5]
time_to_run = sys.argv[6]
sp_directory = sys.argv[7]
loud_output = sys.argv[8]
num_clients = sys.argv[9]
staggering_time = sys.argv[10]


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