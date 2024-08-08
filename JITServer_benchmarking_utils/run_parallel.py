from multiprocessing import Process
import os

MACHINES = ['mel-19', 'mel-20', 'mel-22', 'mel-25', 'mel-26']
COMMANDS = []

class Runner:

    def __init__(self):
        self.machines = []
        self.commands = []

    @staticmethod
    def run_on_machine(machine, command):
        print(f"Running: ssh {machine} '{command}'")
        os.system(f"ssh {machine} '{command}'")

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

class UpdateBenchmarkingUtils(Runner):

    def __init__(self, branch, machines=MACHINES):
        super().__init__()
        self.machines = machines
        self.commands = [f"cd ~/bumblebench-for-jitserver-benchmarking; git stash; git fetch; git checkout {branch}; git pull origin {branch}"] * len(machines)


class RunRenaissanceDockerSweep(Runner):

    def __init__(self, num_clients, stagger_time, run_time, num_threads, renaisance_args, machines=MACHINES, get_analytics=False):
        super().__init__()
        self.machines = machines
        self.run_analytics = get_analytics
        self.commands = [f'cd ~/bumblebench-for-jitserver-benchmarking/JITServer_benchmarking_utils; python3 continuous_load_wrapper.py -oa ~/openj9-openjdk-jdk17/build/linux-x86_64-server-release/jdk/bin -oo ~/baseline_openj9/openj9-openjdk-jdk17/build/linux-x86_64-server-release/jdk/bin -c compiler_config.json -k kernel_config.json -b .. -n {num_clients[i]} -s {stagger_time[i]} -ti {run_time[i]} -th {num_threads[i]} -ren "{renaisance_args[i]}" -d' for i in range(len(machines))]

    def run(self):
        super().run()

        if self.get_analytics:
            ...

############# DEFINE YOUR PERSONAL RUNNERS HERE. DO NOT COMMIT #############

#######################################################################

if __name__ == '__main__':

    # Enter your configuration here. Below is an example
    # runner = KillAllProcesses('user')
    # runner.run()
    # runner = MakeOpenJ9('master')
    # runner.run()
    # runner = UpdateBenchmarkingUtils('dockertools')
    # runner.run()
    # runner = RunRenaissanceDockerSweep([10, 10, 10, 10, 10], [0.5, 0.5, 0.5, 0.5, 0.5], [6000, 6000, 6000, 6000, 6000], [63, 63, 63, 63, 63], ['-r 10 als', '-r 10 als', '-r 10 als', '-r 10 als', '-r 10 als'])
    # runner.run()

    ############# RUN YOUR PERSONAL RUNNER CONFIGURATION HERE. DO NOT COMMIT #############
    ...
    #######################################################################
