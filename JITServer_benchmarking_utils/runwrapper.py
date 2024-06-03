import argparse
import os
import datetime as Date
import subprocess
from jitserver_benchmarker import main_function

def wait_for_server(cmd):
    TIMEOUT = 10
    current_time = Date.datetime.now()

    # Use exec to ensure the process is killed if the script is killed
    proc = subprocess.Popen('exec ' + cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)

    while True:
        line = proc.stdout.readline().strip()
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
    # parser.add_argument('-nsp', '--normal_server_path', required=True)
    # parser.add_argument('-ch', '--changed_server', action='store_true')
    # parser.add_argument('-csp', '--changed_server_path', required=True)


    args = vars(parser.parse_args())

    compiler_json_file = args['compiler_configuration']
    kernel_json_file = args['kernel_configuration']
    openj9_path = args['openj9_path']
    bumblebench_jitserver_path = args['bumblebench_jitserver_path']
    loud_output = args['loud_output']
    num_runs = args['number_of_runs']
    server_path = openj9_path + "/jitserver"
    openj9_path = openj9_path + "/java"
    #normal_server_path = args['normal_server_path']
    # changed_server_path = args['changed_server_path']
    cmd = ''

    # Run the normal server and the changed server in parallel
    # Each iteration has a warmup of the JITServer and then the actual benchmarking

    get_dir = ''
    for i in range(int(num_runs) * 2):
        if i % 2 == 0:
            print(f"Normal JITServer run {i}")
            os.environ['IsRandomJitServer'] = 'false'
            cmd = f'{server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}}'
            print("command: " + cmd)
            proc = wait_for_server(cmd)
            main_function(compiler_json_file,kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output,False)
            proc.kill()

            print(f"Normal JITServer run {i} done")
        else:
            print(f"Changed JITServer run {i}")
            os.environ['IsRandomJitServer'] = 'true'
            cmd = f'{server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose={{JITServer}}'
            print("command: " + cmd)
            proc = wait_for_server(cmd)
            get_dir = main_function(compiler_json_file,kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output,True)
            proc.kill()

            print(f"Changed JITServer run {i} done")


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