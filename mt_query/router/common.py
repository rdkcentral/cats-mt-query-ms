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


from re import split
import ipaddress

"""This file is used to define common functions that are used throughout the application."""


def make_camel_case(objects, keys=None):
    if keys:
        filter_objects(objects, keys)
    try:
        for obj in objects:
            for key in list(obj.keys()):
                key_arr = split('([^a-zA-Z0-9])', key)
                key_arr = [i for i in key_arr if i.isalnum()]
                new_key = ''.join([j.title() if i > 0 else j for i, j in enumerate(key_arr)])
                obj[new_key] = obj.pop(key)
        return objects if len(objects) > 1 else objects[0]
    except IndexError:
        return {}


def filter_objects(objects, keys=None, remove_list=False):
    if keys:
        formatted_object = []
        for obj in objects:
            response = dict((k, obj.get(k)) for k in keys)
            formatted_object.append(response)

        return formatted_object
    else:
        return objects


def get_last_octet(ip):
    try:
        ipaddr = ipaddress.ip_address(ip)
    except ValueError:
        return 11
    ip_arr = ip.split('.')
    last_octet = int(ip_arr[len(ip_arr) - 1])
    return last_octet
