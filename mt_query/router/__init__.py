# Copyright 2024 Comcast Cable Communications Management, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0


import os
import glob
from librouteros import connect
from librouteros.exceptions import ConnectionClosed, TrapError
from werkzeug.exceptions import abort
from mt_query.config import AppConf
from paramiko import SSHClient, AutoAddPolicy
from os import path
import datetime as dt
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Semaphore


class Router:

    # Minimal object for logging into the router
    def __init__(self, credentials):
        conf = AppConf.config('credentials')
        self.backup_path = AppConf.config('backup_path')
        self.host = credentials.get('host') or conf.get('host')
        self.user = conf.get('username')
        self.password = conf.get('password')
        self.backup_interval = conf.get('backup_interval')
        self.connection = None
        self.backup_semaphore = Semaphore(1)

        # schedule background job
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.scheduler.add_job(self.backup_config, 'interval', minutes=2, 
                               name=f"{self.host}-backup")

    # Try to login, raise exception if unsuccessful
    def login(self, host):
        try:
            self.connection = connect(username=self.user, password=self.password, host=host or self.host)
        except TrapError:
            abort(400, "Username or password not valid")
        except ConnectionClosed:
            abort(404, "Could not connect to host: {}".format(self.host))

    def logout(self):
        self.connection.close()

    # Return the output of a command
    def command(self, command):
        return self.connection(cmd=command)

    def make_call(self, command, host):
        self.login(host)
        data = [data for data in self.command(command)]
        self.logout()
        return data

    def get_identity(self, host):
        command = '/system/identity/print'
        return self.make_call(command, host)

    def get_leases(self, host):
        command = '/ip/dhcp-server/lease/print'
        return self.make_call(command, host)

    def get_nat(self, host):
        command = '/ip/firewall/nat/print'
        return self.make_call(command, host)

    def get_firmware(self, host):
        command = '/system/routerboard/print'
        return self.make_call(command, host)

    def get_netwatch(self, host):
        command = '/tool/netwatch/print'
        return self.make_call(command, host)
    
    def _ssh_command_exec(self, host, command, port=22):
        ssh_client = SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy)

        try:
            # needs "allow_agent=False" for MikroTik
            ssh_client.connect(hostname=self.host, username=self.user, 
                               password=self.password, port=port, allow_agent=False)
        except Exception as e:
            logging.error(f"SSH connection to {self.host}:{port} failed with {str(e)}")
            abort(401, f"SSH connection to {self.host}:{port} failed.")
        try:
            stdin, stdout, stderr = ssh_client.exec_command(command=command)
        except Exception as e:
            logging.error(f"SSH command execution on {self.host}:{port} for {command} failed with {str(e)}")

            abort(404, f"Execution of '{command}' on {self.host}:{port} failed.")

        output = stdout.read()
        return output
    
    def backup_config(self):
        command = '/export compact'
        logging.info(f"creating config backup for host: {self.host}")

        # avoid scheduled jobs stepping on API initiated calls.
        self.backup_semaphore.acquire(timeout=60)
        config_file = self._ssh_command_exec(host=self.host, command=command)

        config_file_name = f"{self.host}.rsc"
        try: 
            with open(os.path.join(self.backup_path, config_file_name), "wb") as f:
                f.write(config_file)
        except Exception as e:
            logging.error(f"writing config backup for host: {self.host} to {config_file} failed with {str(e)}")
            self.backup_semaphore.release()
            abort(500, "Failed to write config backup to disk.")
        self.backup_semaphore.release()
        return config_file_name
    
    def get_config_info(self):
        output = {"backups": [], "backup_interval": self.backup_interval, "jobs": []} 
        try:
            for filename in glob.iglob(f"{self.backup_path}/*.rsc"):
                file_epoch_time = path.getmtime(filename)
                output["backups"].append({"name": os.path.basename(filename), 
                               "last_modified": 
                                dt.datetime.utcfromtimestamp(file_epoch_time).isoformat(),
                                "size": os.path.getsize(filename=filename)}
                               )
        except OSError as e:
            abort(404, "No backup file found!")

        for j in self.scheduler.get_jobs():
            output["jobs"].append({"id": j.id, "name": j.name, 
                                   "next_run": j.next_run_time.astimezone(
                                       dt.timezone.utc).isoformat()})
        return output

