

def setup_kernel_args(json_file):
    jit_server_args = open('./JITServerArgs.txt', 'w')
    jit_server_args.write('BumbleBench.jsonFile=' + json_file)
    jit_server_args.close()
