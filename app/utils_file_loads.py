'''
Created on Feb 12, 2020

@author: Tim Kreuzer
'''

import json

def get_j4j_dockerspawner_token():
    with open('/etc/j4j/j4j_mount/j4j_token/dockerspawner.token', 'r') as f:
        token = f.read().rstrip()
    return token

def get_general_config():
    with open('/etc/j4j/j4j_mount/j4j_docker/slave/config.json', 'r') as f:
        ret = json.load(f)
    return ret
