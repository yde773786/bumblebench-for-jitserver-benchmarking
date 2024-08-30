import docker


if __name__ == "__main__":
    client = docker.from_env()
    logs = client.containers.run("hello-world")
    print(client.containers.list())
    image = client.images.get('hello-world')
    a = client.containers.create(image)
    a.start()
    for line in a.logs(stream=True):
        print(line.strip())

    print(client.images.list())