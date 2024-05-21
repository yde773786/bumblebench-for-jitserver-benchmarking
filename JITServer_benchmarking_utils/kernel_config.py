import json


def setup_kernel_args(json_file):
    jit_server_args = open('./JITServerArgs.txt', 'w')
    config = json.load(open(json_file, 'r'))

    for key in config.keys():
        if key == "threads":
            jit_server_args.write('BumbleBench.classesToInvoc=')
            for thread in config[key]:
                for kernel_config in thread["kernels"]:
                    jit_server_args.write(f'{kernel_config["kernel_name"]} {kernel_config["invoc_count"]} ')
                jit_server_args.write(f'/ ')
            jit_server_args.write('\n')

    jit_server_args.close()
