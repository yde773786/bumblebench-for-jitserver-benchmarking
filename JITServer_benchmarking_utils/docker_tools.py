import docker


def start_container():
    #TODO Assert basic jitserver in client.images.list()
    #TODO assert openj9_volume is valid
    client = docker.from_env()

    volumes = {'openj9_volume': {'bind': '/root/servers', 'mode': 'rw'},
               'vlog_volume': {'bind': '/root/vlogs', 'mode': 'rw'}}

    container = client.containers.run("basic_jitserver", name="jitserver_host", volumes=volumes,
                                      cpuset_cpus="1", detach=True, tty=True)
    return container


def view_container_logs(container):
    for line in container.logs(stream=True):
        print(line.strip())


def execute_container_commmand(container, command):
    return container.exec_run(command, socket=True)


if __name__ == "__main__":
    client = docker.from_env()
    print(client.images.list())