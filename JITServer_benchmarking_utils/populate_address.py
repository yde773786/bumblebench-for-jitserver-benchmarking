"""
This script is used to populate the JITServer address in the compiler_config.json file.
"""

import socket
import json

CONFIG_ = open('compiler_config.json', "r")
CONFIG_ADDR = open('compiler_config_addr.json', "w")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))

ip_address = s.getsockname()[0]

lines = []

js = json.load(CONFIG_)
js['-XX:JITServerAddress'] = ip_address

json.dump(js, CONFIG_ADDR, indent=4)
