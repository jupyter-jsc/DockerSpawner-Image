'''
Created on 12 Feb, 2020

@author: Tim Kreuzer
'''

import subprocess

from flask import request
from flask_restful import Resource
from flask import current_app as app

from app import utils_common, utils_file_loads, jlab_utils
import os
from pathlib import Path

class JupyterLabHandler(Resource):
    def get(self):
        try:
            """
            Headers:
                Intern-Authorization: spawner_token
                uuidcode
                Containername: uuidcode_from_spawn                
            """
            # Track actions through different webservices.
            uuidcode = request.headers.get('uuidcode', '<no uuidcode>')
            app.log.info("uuidcode={} - Get JupyterLab Status".format(uuidcode))
            app.log.trace("uuidcode={} - Headers: {}".format(uuidcode, request.headers))
    
            # Check for the J4J intern token
            utils_common.validate_auth(app.log,
                                       uuidcode,
                                       request.headers.get('intern-authorization', None))
    
            request_headers = {}
            for key, value in request.headers.items():
                if 'Token' in key: # refresh, jhub, access
                    key = key.replace('-', '_')
                request_headers[key.lower()] = value
            containername = request_headers.get("containername")
            cmd1 = ["docker", "ps", "-q", "-f", "name={}".format(containername)]
            try:
                app.log.trace("uuidcode={} - Cmd: {}".format(uuidcode, cmd1))
                ret = subprocess.check_output(cmd1, stderr=subprocess.STDOUT, timeout=5)
                ret = ret.strip().decode("utf-8")
                app.log.trace("uuidcode={} - Output: {}".format(uuidcode, ret))
            except:
                app.log.exception("uuidcode={} - Could not check docker status. Return True".format(uuidcode))
                return "True", 200
            if ret == "":
                return "False", 200
            else:
                cmd2 = ["docker", "ps", "-aq", "-f", "status=exited", "-f", "name={}".format(containername)]
                try:
                    app.log.trace("uuidcode={} - Cmd: {}".format(uuidcode, cmd2))
                    ret = subprocess.check_output(cmd2, stderr=subprocess.STDOUT, timeout=5)
                    ret = ret.strip().decode("utf-8")
                    app.log.trace("uuidcode={} - Output: {}".format(uuidcode, ret))
                except:
                    app.log.exception("uuidcode={} - Could not check docker status. Return True".format(uuidcode))
                    return "True", 200
                if ret == "":
                    # it's running
                    return "True", 200
                else:
                    # cleanup. Container status=exited
                    cmd3 = ["docker", "rm", containername]
                    try:
                        app.log.trace("uuidcode={} - Cmd: {}".format(uuidcode, cmd3))
                        ret = subprocess.check_output(cmd3, stderr=subprocess.STDOUT, timeout=5)
                        ret = ret.strip().decode("utf-8")
                        app.log.trace("uuidcode={} - Output: {}".format(uuidcode, ret))
                    except:
                        app.log.exception("uuidcode={} - Could not cleanup non running container. Return False".format(uuidcode))
                        return "False", 200
                    return "False", 200
        except:
            app.log.exception("JLab.get failed. Bugfix required")
        return '', 500

    def post(self):
        try:
            """
            Headers:
                Intern-Authorization: spawner_token
                uuidcode
            Body:
                email
                environments
                image
                port
                servername
                jupyterhub_api_url
            Config:
                basefolder # /etc/j4j/j4j_hdfcloud
                network
                cap-add
                memory
                memory-swap
                device
                storage-opt                
            """
            # Track actions through different webservices.
            uuidcode = request.headers.get('uuidcode', '<no uuidcode>')
            app.log.info("uuidcode={} - Start JupyterLab".format(uuidcode))
            app.log.trace("uuidcode={} - Headers: {}".format(uuidcode, request.headers))
            app.log.trace("uuidcode={} - Json: {}".format(uuidcode, request.json))
    
            # Check for the J4J intern token
            utils_common.validate_auth(app.log,
                                       uuidcode,
                                       request.headers.get('intern-authorization', None))
    
            request_headers = {}
            for key, value in request.headers.items():
                if 'Token' in key: # refresh, jhub, access
                    key = key.replace('-', '_')
                request_headers[key.lower()] = value
            request_json = {}
            for key, value in request.json.items():
                if 'Token' in key: # refresh, jhub, access
                    key = key.replace('-', '_')
                request_json[key.lower()] = value
            app.log.trace("uuidcode={} - New Headers: {}".format(uuidcode, request_headers))
            app.log.trace("uuidcode={} - New Json: {}".format(uuidcode, request_json))
            
            config = utils_file_loads.get_general_config()
            basefolder = config.get('basefolder', '<no basefolder defined>')
            userfolder = os.path.join(basefolder, request_json.get('email').replace("@", "_at_"))
            serverfolder = Path(os.path.join(userfolder, '.{}'.format(uuidcode)))
            mounts = jlab_utils.get_mounts(app.log, uuidcode, serverfolder, userfolder)
            
            cmd = ["docker", "run"]
            cmd.append("--network")
            cmd.append(config.get("network"))
            cmd.append("--cap-add")
            cmd.append(config.get("cap-add"))
            cmd.append("--memory")
            cmd.append(config.get("memory"))
            cmd.append("--memory-swap")
            cmd.append(config.get("memory-swap"))
            cmd.append("--device")
            cmd.append(config.get("device"))
            cmd.append("--restart")
            cmd.append(config.get("restart"))
            #cmd.append("--storage-opt")
            #cmd.append(config.get("storage-opt"))
            cmd.append("--name")
            cmd.append(uuidcode)
            cmd.append("-e")
            cmd.append("{}={}".format("HPCACCOUNTS", request_json.get("environments",{}).get("HPCACCOUNTS", "")))
            cmd.append("-e")
            cmd.append("{}={}".format("JUPYTERHUB_API_URL", request_json.get("environments",{}).get("JUPYTERHUB_API_URL", "")))
            cmd.append("-e")
            cmd.append("{}={}".format("JUPYTERHUB_CLIENT_ID", request_json.get("environments",{}).get("JUPYTERHUB_CLIENT_ID", "")))
            cmd.append("-e")
            cmd.append("{}={}".format("JUPYTERHUB_API_TOKEN", request_json.get("environments",{}).get("JUPYTERHUB_API_TOKEN", "")))
            cmd.append("-e")
            cmd.append("{}={}".format("JUPYTERHUB_USER", request_json.get("environments",{}).get("JUPYTERHUB_USER", "")))
            cmd.append("-e")
            cmd.append("{}={}".format("JUPYTERHUB_SERVICE_PREFIX", request_json.get("environments",{}).get("JUPYTERHUB_SERVICE_PREFIX", "")))
            cmd.append("-e")
            cmd.append("{}={}".format("JUPYTERHUB_BASE_URL", request_json.get("environments",{}).get("JUPYTERHUB_BASE_URL", "")))
            cmd.extend(mounts)
            cmd.append(request_json.get("image"))
            cmd.append("/home/jovyan/.start.sh")
            cmd.append(str(request_json.get("port")))
            cmd.append(request_json.get("servername"))
            cmd.append(request_json.get("jupyterhub_api_url"))
            cmd.append("&")
            app.log.debug("uuidcode={} - Run Command: {}".format(uuidcode, cmd))
            subprocess.Popen(cmd)
        except:
            app.log.exception("JLab.post failed. Bugfix required")
            return "", 500
        return "", 202

    def delete(self):
        """
            Headers:
                Intern-Authorization: spawner_token
                uuidcode
                containername: uuidcode from spawn
        """
        try:
            # Track actions through different webservices.
            uuidcode = request.headers.get('uuidcode', '<no uuidcode>')
            app.log.info("uuidcode={} - Delete JupyterLab".format(uuidcode))
            app.log.trace("uuidcode={} - Headers: {}".format(uuidcode, request.headers))
    
            # Check for the J4J intern token
            utils_common.validate_auth(app.log,
                                       uuidcode,
                                       request.headers.get('intern-authorization', None))
            request_headers = {}
            for key, value in request.headers.items():
                if 'Token' in key: # refresh, jhub, access
                    key = key.replace('-', '_')
                request_headers[key.lower()] = value           
            containername = request_headers.get('containername')
            cmd1 = ["docker", "container", "exec", containername, "/bin/umount", "/home/jovyan/B2DROP"]
            cmd2 = ["docker", "container", "exec", containername, "/bin/fusermount", "-u", "/home/jovyan/HPCMOUNT"]
            cmd3 = ["docker", "container", "rm", "--force", containername]
            try:
                app.log.trace("uuidcode={} - Cmd: {}".format(uuidcode, cmd1))
                ret = subprocess.check_output(cmd1, stderr=subprocess.STDOUT, timeout=5)
                ret = ret.strip().decode("utf-8")
                app.log.trace("uuidcode={} - Output: {}".format(uuidcode, ret))
            except:
                app.log.warning("uuidcode={} - Could not unmount B2DROP".format(uuidcode))
            try:
                app.log.trace("uuidcode={} - Cmd: {}".format(uuidcode, cmd2))
                ret = subprocess.check_output(cmd2, stderr=subprocess.STDOUT, timeout=5)
                ret = ret.strip().decode("utf-8")
                app.log.trace("uuidcode={} - Output: {}".format(uuidcode, ret))
            except:
                app.log.warning("uuidcode={} - Could not unmount HPCMOUNT".format(uuidcode))
            try:
                app.log.trace("uuidcode={} - Cmd: {}".format(uuidcode, cmd3))
                ret = subprocess.check_output(cmd3, stderr=subprocess.STDOUT, timeout=5)
                ret = ret.strip().decode("utf-8")
                app.log.trace("uuidcode={} - Output: {}".format(uuidcode, ret))
            except:
                app.log.exception("uuidcode={} - Could not stop container".format(uuidcode))
            
        except:
            app.log.exception("JLabs.delete failed. Bugfix required")
            return '', 500
        return '', 202
