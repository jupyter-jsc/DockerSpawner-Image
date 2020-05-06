'''
Created on Feb 12, 2020

@author: Tim Kreuzer
'''

import os
from pathlib import Path

def get_mounts(app_logger, uuidcode, serverfolder, userfolder):
    ret = []
    ret.append("--mount")
    ret.append("type=bind,src={},dst=/home/jovyan".format(serverfolder))
    ret.append("--mount")
    ret.append("type=bind,src={},dst=/home/jovyan/work".format(os.path.join(userfolder, "work")))
    ret.append("--mount")
    ret.append("type=bind,src={},dst=/home/jovyan/Projects/MyProjects".format(os.path.join(userfolder, "Projects", "MyProjects")))
    ret.append("--mount")
    ret.append("type=bind,src={},dst=/home/jovyan/Projects/.share".format(os.path.join(userfolder, "Projects", ".share")))
    ret.append("--mount")
    ret.append("type=bind,src={},dst=/home/jovyan/Projects/.share_result".format(os.path.join(userfolder, "Projects", ".share_result")))
    
    with open(os.path.join(userfolder.replace("@", "_at_"), "projects.txt"), 'r') as f:
        projects = f.read()
    projects_list = projects.strip().split()
    for project in projects_list:
        p = Path(project)
        owner =  p.parent.parent.parent.name.replace("_at_", "@")
        if os.path.isdir(project):
            ret.append("--mount")
            ret.append("type=bind,src={project},dst=/home/jovyan/Projects/SharedProjects/{owner}_{name}".format(project=project, owner=owner, name=p.name))
    return ret
