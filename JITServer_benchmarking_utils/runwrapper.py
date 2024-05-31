import argparse
import os
import subprocess
from jitserver_benchmarker import main_function

def wait_for_server(splt):
    proc = subprocess.Popen(splt, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        strip = line.strip()
        if strip == "JITServer is ready to accept incoming requests":
            return proc

import time

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
    parser.add_argument('-nsp', '--normal_server_path', required=True)
    parser.add_argument('-csp', '--changed_server_path', required=True)

    args = vars(parser.parse_args())

    compiler_json_file = args['compiler_configuration']
    kernel_json_file = args['kernel_configuration']
    openj9_path = args['openj9_path']
    bumblebench_jitserver_path = args['bumblebench_jitserver_path']
    loud_output = args['loud_output']
    num_runs = args['number_of_runs']
    normal_server_path = args['normal_server_path']
    changed_server_path = args['changed_server_path']
    cmd = ''

    # Run the normal server and the changed server in parallel
    # Each iteration has a warmup of the JITServer and then the actual benchmarking

    get_dir = ''
    for i in range(int(num_runs) * 2):

        if i % 2 == 0:
            print("starting up normal jitserver")
            cmd = f'{normal_server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}}'
            print("command: " + cmd)
            splt = cmd.split(" ")
            proc = wait_for_server(splt)
            main_function(compiler_json_file, kernel_json_file, openj9_path, bumblebench_jitserver_path, loud_output,
                          False)
            proc.kill()
            print("killed the process")
            proc.wait()
        else:
            print("starting up altered jitserver")
            cmd = f'{changed_server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}}'
            splt = cmd.split(" ")
            print("command: " + cmd)
            proc = wait_for_server(splt)
            get_dir = main_function(compiler_json_file, kernel_json_file, openj9_path, bumblebench_jitserver_path, loud_output,
                          True)

            proc.kill()
            print("killed the process")
            proc.wait()


# Do a final analysis of the results
    print("_________________Final analysis of results_________________")
    print("Normal server results:")

    report_file = open(get_dir + '/report.csv', 'w')
    report_file.write("Run,Normal Server Time,Changed Server Time\n")

    files = [f for f in os.listdir(get_dir + '/normal_server/') if 'output_file' in f]
    files.sort(key=lambda x: os.path.getmtime(get_dir + '/normal_server/' + x))
    avg_normal = 0

    normal_report = []

    for i, f in enumerate(files):
        elapsedTime = open(get_dir + '/normal_server/' + f, 'r').readlines()[-2].split()[4]
        print(f"Run {i+1} Elapsed Time: {elapsedTime}")
        avg_normal += int(elapsedTime)
        normal_report.append(elapsedTime)

    avg_normal /= len(files)

    print("AVERAGE ELAPSED TIME FOR NORMAL SERVER: " + str(avg_normal))

    print("Changed server results:")

    altered_report = []

    files = [f for f in os.listdir(get_dir + '/altered_server/') if 'output_file' in f]
    files.sort(key=lambda x: os.path.getmtime(get_dir + '/altered_server/' + x))
    avg_changed = 0
    for i, f in enumerate(files):
        elapsedTime = open(get_dir + '/altered_server/' + f, 'r').readlines()[-2].split()[4]
        print(f"Run {i+1} Elapsed Time: {elapsedTime}")
        avg_changed += int(elapsedTime)
        altered_report.append(elapsedTime)

    avg_changed /= len(files)

    print("AVERAGE ELAPSED TIME FOR CHANGED SERVER: " + str(avg_changed))

    for i in range(len(normal_report)):
        report_file.write(f"{i+1},{normal_report[i]},{altered_report[i]}\n")