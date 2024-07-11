from multiprocessing import Process
import os

import sys

MACHINES = ['mel-19', 'mel-20', 'mel-22', 'mel-25', 'mel-26']
COMMAND = sys.argv[1]

def run_on_machine(machine):
    print(f"Running: ssh {machine} '{COMMAND}'")
    os.system(f"ssh {machine} '{COMMAND}'")

if __name__ == '__main__':

    processes = []

    for machine in MACHINES:
        p = Process(target=run_on_machine, args=(machine,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    
    print("DONE")