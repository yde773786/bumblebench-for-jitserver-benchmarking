import os

STAGGER = [4, 6, 8, 10, 12]

for stagger in STAGGER:
    os.system(f'python3 continuous_load_wrapper.py  -o ~/openj9-openjdk-jdk17/build/linux-x86_64-server-release/jdk/bin -c compiler_config.json -k kernel_config.json -b .. -n 10 -s {stagger} -t 600')

    for directory in os.listdir("."):
        if os.path.isdir(directory) and "__pycache__" not in directory and "cw" not in directory:
            os.system(f"mv {directory} cw_{stagger}")
