import os

STAGGER = [2, 3]

for stagger in STAGGER:
    os.system(f'python3 continuous_load_wrapper.py  -o ~/openj9-openjdk-jdk17/build/linux-x86_64-server-release/jdk/bin -c compiler_config.json -k kernel_config.json -b .. -n 2 -s {stagger} -t 10')

    for directory in os.listdir("."):
        if os.path.isdir(directory) and "__pycache__" not in directory and "cw" not in directory:
            os.system(f"mv {directory} cw_{stagger}")
