import docker


def start_container(env_vars):
    #TODO Assert basic jitserver in client.images.list()
    #TODO assert openj9_volume is valid
    client = docker.from_env()
    import os
    volumes = {os.environ['HOME']: {'bind': '/root', 'mode': 'rw'},
               'vlog_volume': {'bind': '/root/vlogs', 'mode': 'rw'}}

    container = client.containers.run("basic_jitserver", name="jitserver_host", volumes=volumes,
                                      cpuset_cpus="1", detach=True, tty=True, environment=env_vars,
                                      cap_add=["NET_ADMIN"])
    return container


def view_container_logs(container):
    for line in container.logs(stream=True):
        print(line.strip())


def execute_container_commmand(container, command):
    return container.exec_run(command, socket=True, privileged=True)


def lag_container(container, time):
    return container.exec_run(f'tc qdisc add dev eth0 root netem delay {time}ms', socket=True, privileged=True)


def verify_basic_jitserver_active():
    client = docker.from_env()
    print(client.images.list())
    try:
        image = client.images.get("basic_jitserver")
        print("image found")
        return True
    except docker.errors.ImageNotFound:
        print("image not found, building...")
        client.images.build(path="JITServer", tag="basic_jitserver")
        print("build complete")
        return False

def remake_basic_jitserver():
    client = docker.from_env()
    if verify_basic_jitserver_active():
        print("removing old image")
        client.images.remove("basic_jitserver")
    print("Building image...")
    client.images.build(path="JITServer", tag="basic_jitserver")
    print("build complete")
def read_from_file(file):
    file_read = open(file, "r")
    while True:
        line = file_read.readline().strip()
        print(line)
if __name__ == "__main__":
    remake_basic_jitserver()
    #container = start_container(dict())
    #lag_container(container, 100)
    #command_exec = execute_container_commmand(container, "ping 8.8.8.8 > /root/pingfile.txt")

    #read_from_file("/home/richardkha/pingfile.txt")
    # from pathlib import Path
    #
    # paths = list(Path('.').glob('temp/*'))
    # print(paths)
