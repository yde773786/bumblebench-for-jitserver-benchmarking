FROM ubuntu:22.04

# These directories must be mounted as volumes at runtime
RUN mkdir -p "/root/servers" "/root/vlogs"
RUN apt-get update -y
RUN apt-get install lshw -y
RUN apt-get install iproute2 -y
RUN apt-get install -y iputils-ping
EXPOSE 38400
