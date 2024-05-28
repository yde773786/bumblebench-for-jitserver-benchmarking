
import argparse
import os
import subprocess
from pathlib import Path

from jitserver_benchmarker import main_function
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
    for i in range(int(num_runs) * 2):

        if i % 2 == 0:
            paths = list(Path('.').glob('**/normal*'))
            cmd = f'{normal_server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}}'
            print("command: " + cmd)
            splt = cmd.split(" ")
            proc = subprocess.Popen(splt, stdout=subprocess.PIPE)
            msg = proc.stdout.readline()
            while True:
                print(msg)
                if msg.strip() == "JITServer is ready to accept incoming requests":
                    break
            main_function(compiler_json_file,kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output,False)
            proc.kill()
            print("killed the process")
            time.sleep(10)
        else:
            paths = list(Path('.').glob('**/altered*'))
            cmd = f'{changed_server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}},vlog=serverlogs/altered'
            splt = cmd.split(" ")
            proc = subprocess.Popen(splt, stdout=subprocess.PIPE)
            print("command: " + cmd)
            msg = proc.stdout.readline()
            while True:
                print(msg)
                if msg.strip() == "JITServer is ready to accept incoming requests":
                    break
            main_function(compiler_json_file,kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output,True)
            proc.kill()
            print("killed the process")
            time.sleep(10)

    # Do a final analysis of the results
    print("_________________Final analysis of results_________________")
    print("Normal server results:")
    files = [f for f in os.listdir(normal_server_path) if 'output_file' in f]
    files.sort(key=lambda x: os.path.getmtime(x))
    avg_normal = 0
    for i, f in enumerate(files):
        elapsedTime = f.readlines()[-2].split()[4]
        print(f"Run {i+1} Elapsed Time: {elapsedTime}")
        avg_normal += elapsedTime

    avg_normal /= len(files)

    print("AVERAGE ELAPSED TIME FOR NORMAL SERVER: " + str(avg_normal))

    print("Changed server results:")
    files = [f for f in os.listdir(changed_server_path) if 'output_file' in f]
    files.sort(key=lambda x: os.path.getmtime(x))
    avg_changed = 0
    for i, f in enumerate(files):
        elapsedTime = f.readlines()[-2].split()[4]
        print(f"Run {i+1} Elapsed Time: {elapsedTime}")
        avg_changed += elapsedTime

    avg_changed /= len(files)

    print("AVERAGE ELAPSED TIME FOR CHANGED SERVER: " + str(avg_changed))