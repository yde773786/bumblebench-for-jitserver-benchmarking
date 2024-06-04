import json

# def change_vlog_directory(xjit_flags, directory):
#     xjit_flags = xjit_flags.replace("vlog=", "verbose={JITServer}")
#
def get_compiler_args(json_file, sp_directory):
    config = json.load(open(json_file, 'r'))

    xjit_flags = '-Xjit:'
    xaot_flags = '-Xaot:'
    other_flags = ''
    for key in config.keys():
        if key.startswith("JIT"):
            strings = key.split(":")
            strings[1] = strings[1].strip()
            if strings[1] == "global_invocation_count_till_compiled":
                xjit_flags += "count=" + str(config[key]) + ","
            elif strings[1] == "method_configs":
                for kernel_conf in config[key]:
                    xjit_flags += "'{" + kernel_conf["method_signature"] + "}("
                    if "temperature" in kernel_conf.keys():
                        xjit_flags += "optLevel=" + kernel_conf["temperature"] + ","
                    if "invocation_count_till_compiled" in kernel_conf.keys():
                        xjit_flags += "count=" + str(kernel_conf["invocation_count_till_compiled"])
                    xjit_flags += ")',"
            elif strings[1] == "log_file":
                if xjit_flags.find("verbose") == -1:
                    xjit_flags += "verbose,vlog" + '=' + sp_directory + "/" + str(config[key]) + ","
                else:
                    xjit_flags += "vlog" + '=' + sp_directory + "/" + str(config[key]) + ","
            elif strings[1] == "enable_JIT":
                if not config[key]:
                    other_flags += "-Xnojit "
            elif strings[1] == "JIT_server_log":
                if config[key]:
                    if xjit_flags.find("verbose") == -1:
                        xjit_flags += "verbose,"

                    xjit_flags = xjit_flags.replace("verbose", "verbose={JITServer}")
            elif strings[1] == "active_thread_heuristic":     
                if not config[key]:
                    xjit_flags += "highActiveThreadThreshold=1000000000,veryHighActiveThreadThreshold=1000000000"   
        elif key.startswith("AOT"):
            strings = key.split(":")
            strings[1] = strings[1].strip()
            if strings[1] == "enable_AOT":
                if not config[key]:
                    xaot_flags = "-Xnoaot -Xshareclasses:none"
            if xaot_flags != "-Xnoaot":
                if strings[1] == "AOT_count":
                    xaot_flags += "count" + '=' + str(config[key]) + ","
        elif key.startswith("VM"):
            strings = key.split(":")
            strings[1] = strings[1].strip()
            if strings[1] == "use_JIT_server":
                if config[key]:
                    other_flags += "-XX:+UseJITServer "
            elif strings[1] == "JIT_server_port":
                other_flags += "-XX:JITServerPort=" + str(config[key]) + " "
            elif strings[1] == "JIT_server_address":
                other_flags += "-XX:JITServerAddress=" + str(config[key]) + " "
            elif strings[1] == "number_of_compilation_threads":
                other_flags += "-XcompilationThreads" + str(config[key]) + " "

    xjit_flags = xjit_flags if xjit_flags.strip() != '-Xjit:' else ""
    xaot_flags = xaot_flags if xaot_flags != '-Xaot:' else ""

    return xjit_flags, xaot_flags, other_flags