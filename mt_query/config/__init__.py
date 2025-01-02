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

import yaml


class AppConf:
    __conf = {
        "capability_map": "",
        "credentials": "",
        "backup_path": "config_backup"
    }

    __valid_keys = ["capability_map", "credentials", "backup_path"]

    @staticmethod
    def get_capability_map_file_path():

        if 'ENVIRONMENT' in os.environ and os.environ['ENVIRONMENT'] == 'development':
            capability_map_path = "mt_query/config/capability_map.yml"
        else:
            capability_map_path = "/mt-query-ms/mt_query/config/capability_map.yml"

        return capability_map_path

    @staticmethod
    def get_config_file_path():

        if 'ENVIRONMENT' in os.environ and os.environ['ENVIRONMENT'] == 'development':
            config_path = "mt_query/resource/config.yml"
        else:
            config_path = "/mt-query-ms/mt_query/resource/config.yml"

        return config_path

    @staticmethod
    def config(key):
        return AppConf.__conf[key]

    @staticmethod
    def set(key, value):
        if key in AppConf.__valid_keys:
            AppConf.__conf[key] = value
        else:
            raise NameError("Invalid key: {}".format(key))

    @staticmethod
    def open(path, key=None):
        with open(path, 'r') as stream:
            try:
                obj = yaml.safe_load(stream)
                if key:
                    obj = obj.get(key)
                return obj
            except yaml.YAMLError as exc:
                print(exc)
