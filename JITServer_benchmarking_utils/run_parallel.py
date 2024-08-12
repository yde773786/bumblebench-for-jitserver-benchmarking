from multiprocessing import Process
import os
import subprocess
from pathlib import Path
from constants import directories
MACHINES = ['mel-19', 'mel-20', 'mel-22', 'mel-25', 'mel-26']
COMMANDS = []

class Runner:

    def __init__(self):
        self.machines = []
        self.commands = []

    @staticmethod
    def run_on_machine(machine, command):
        print(f"Running: ssh {machine} '{command}'")
        file_name = f'server_vlog_{machine}.txt'
        server_vlog_file = open(file_name, "w")
        subprocess.call(f"ssh {machine} '{command}'", stdout=server_vlog_file, stderr=subprocess.STDOUT, text=True, shell=True)
        server_vlog_file.close()

    def run(self):
        processes = []
        for i in range(len(self.machines)):
            p = Process(target=self.run_on_machine, args=(self.machines[i], self.commands[i]))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()
    
class KillAllProcesses(Runner):

    def __init__(self, user, machines=MACHINES):
        super().__init__()
        self.machines = machines
        self.commands = [f"pkill -u {user}"] * len(machines)

class MakeOpenJ9(Runner):

    def __init__(self, branch, machines=MACHINES):
        super().__init__()
        self.machines = machines
        self.commands = [f"cd ~/openj9-openjdk-jdk17/; cd openj9; git stash; git fetch; git checkout {branch}; git pull origin {branch}; cd ..; make clean; make all"] * len(machines)

class MakeBaselineOpenJ9(Runner):

    def __init__(self, machines=MACHINES):
        super().__init__()
        self.machines = machines
        self.commands = [f"cd ~/baseline_openj9; cd openj9-openjdk-jdk17/; cd openj9; git stash; git fetch; git checkout pure_fcfs; git pull origin pure_fcfs; cd ..; make clean; make all"] * len(machines)

class UpdateBenchmarkingUtils(Runner):

    def __init__(self, branch, machines=MACHINES):
        super().__init__()
        self.machines = machines
        self.commands = [f"cd ~/bumblebench-for-jitserver-benchmarking; git stash; git fetch; git checkout {branch}; git pull origin {branch}"] * len(machines)


class RunRenaissanceDockerSweep(Runner):

    def __init__(self, num_clients, stagger_time, run_time, num_threads, renaisance_args, machines=MACHINES, get_analytics=False):
        super().__init__()
        self.machines = machines
        self.get_analytics = get_analytics
        self.commands = [f'cd ~/bumblebench-for-jitserver-benchmarking/JITServer_benchmarking_utils; python3 continuous_load_wrapper.py -oa ~/openj9-openjdk-jdk17/build/linux-x86_64-server-release/jdk/bin -oo ~/baseline_openj9/openj9-openjdk-jdk17/build/linux-x86_64-server-release/jdk/bin -c compiler_config.json -k kernel_config.json -b .. -n {num_clients[i]} -s {stagger_time[i]} -ti {run_time[i]} -th {num_threads[i]} -ren "{renaisance_args[i]}" -d' for i in range(len(machines))]

    def run(self):
        super().run()
        Path('analytics').mkdir(parents=True, exist_ok=True)
        if self.get_analytics:
            Path("~/bumblebench-for-jitserver-benchmarking/JITServer_benchmarking_utils/analytics").mkdir(parents=True, exist_ok=True)
            num_files = str(len(os.listdir('analytics')))
            parallel_run_dir = f'analytics/{num_files}'
            Path(parallel_run_dir).mkdir(parents=True, exist_ok=True)
            for machine in self.machines:
                file = open(f'server_vlog_{machine}.txt', "r")
                for line in file:
                    if "LOCATION OF DIRECTORY" in line:
                        split = line.split("<")[1]
                        split = split.split(">")[0]
                        machine_dir = split.replace("/", "_")
                        machine_dir = f'{parallel_run_dir}/{machine_dir}'
                        Path(machine_dir).mkdir(parents=True, exist_ok=True)
                        graph_dir = f'{machine_dir}/graphs'
                        Path(graph_dir).mkdir(parents=True, exist_ok=True)
                        subprocess.call(f"scp {machine}:~/bumblebench-for-jitserver-benchmarking/JITServer_benchmarking_utils/{split}/report_per_client.csv {machine_dir}", text=True, shell=True)
                        for server_folder in directories:
                            subprocess.call(f"scp {machine}:~/bumblebench-for-jitserver-benchmarking/JITServer_benchmarking_utils/{split}/{server_folder}/servervlog* {machine_dir}/{server_folder}_servervlog", text=True, shell=True)

                        subprocess.call(f"python3 ../../../cdf_grapher.py -d report_per_client.csv -clw -f graphs/cdf_comp_times", text=True, shell=True, cwd=machine_dir)
                        subprocess.call(f"python3 ../../../temperature_histogram.py fcfs_server_servervlog graphs/temperature_histogram", text=True, shell=True, cwd=machine_dir)
                        subprocess.call(f"python3 ../../../compilation_distribution.py -d fcfs_server_servervlog -f graphs/cdf_comp_dist", text=True, shell=True, cwd=machine_dir)
                        subprocess.call(f"python3 ../../../compilation_distribution.py -d fcfs_server_servervlog -f graphs/histogram_comp_dist -his", text=True, shell=True, cwd=machine_dir)

class ClearContainers(Runner):

    def __init__(self, machines=MACHINES):
        super().__init__()
        self.machines = machines
        self.commands = [f"docker kill $(docker ps -q); docker remove $(docker ps -q -a)"] * len(machines)

############# DEFINE YOUR PERSONAL RUNNERS HERE. DO NOT COMMIT #############

#######################################################################

if __name__ == '__main__':

    # Enter your configuration here. Below is an example
    machines = ['mel-19', 'mel-20', 'mel-22', 'mel-25']
    runner = KillAllProcesses('richardkha', machines=machines)
    runner.run()
    # runner = ClearContainers(machines=machines)
    # runner.run()
    # runner = MakeOpenJ9('quickInfoGetterThreaded')
    # runner.run()
    # runner = MakeBaselineOpenJ9()
    # runner.run()
    runner = UpdateBenchmarkingUtils('dockertools', machines=machines)
    runner.run()
    runner = RunRenaissanceDockerSweep([50,50,50,50,50], [50,100,200,400,600], [2,2,2,2,2], [63,63,63,63,63], ['-r 100 finagle-chirper','-r 100 finagle-chirper','-r 100 finagle-chirper','-r 100 finagle-chirper','-r 100 finagle-chirper'], machines=machines, get_analytics=True)
    runner.run()

    ############# RUN YOUR PERSONAL RUNNER CONFIGURATION HERE. DO NOT COMMIT #############
    ...
    #######################################################################
