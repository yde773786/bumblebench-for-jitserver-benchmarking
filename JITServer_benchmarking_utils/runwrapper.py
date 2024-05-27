
import argparse
import subprocess
from JITServer_benchmarking_utils.jitserver_benchmarker import main_function

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

    for i in range(num_runs * 2):
        if i % 2 == 0:
            cmd = f'./{normal_server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose=\\{{JITServer\\}}'
            print("command: " + cmd)
            proc = subprocess.Popen(cmd)
            main_function(compiler_json_file,kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output,False)
            proc.kill()
        else:
            cmd = f'./{changed_server_path} -XX:+JITServerLogConnections -XX:+JITServerMetrics -Xjit:verbose=\\{{JITServer\\}}'
            proc = subprocess.Popen(cmd)
            print("command: " + cmd)
            main_function(compiler_json_file,kernel_json_file,openj9_path,bumblebench_jitserver_path,loud_output,True)
            proc.kill()

