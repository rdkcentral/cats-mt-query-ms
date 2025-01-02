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


import logging
from mt_query.router import Router
from mt_query.router.common import make_camel_case
from mt_query.router.capability import is_valid, health_check

from packaging import version
from mt_query.config import AppConf

""" This file is used aggregate the data from the router and return it in a format that can be used by the API. """

# Load the configuration files
capability_file_path = AppConf.get_capability_map_file_path()
config_file_path = AppConf.get_config_file_path()

AppConf.set('capability_map', AppConf.open(capability_file_path, "capabilities"))
AppConf.set('credentials', AppConf.open(config_file_path))
router = Router({})


""" Start of v1 implementation """


def get_aggregate_v1(body):
    host = body.get('host')
    showDisabled = body.get('showDisabled')
    showDefault = body.get('showDefault')
    agg = get_aggregate(host, showDisabled, showDefault)

    agg.update({'capability': get_capability_v1(body)})
    return agg


def get_capability_v1(body):
    keys = body.get('capabilities')
    showDisabled = body.get('showDisabled')
    showDefault = body.get('showDefault')
    host = body.get('host')
    capabilities = get_capability(host, showDisabled, showDefault)
    return make_camel_case([capabilities], keys)


""" Start of v2 implementation """


def get_aggregate(host, showDisabled, showDefault):
    agg = {}
    agg.update({'identity': get_identity(host)})
    agg.update({'firmware': get_firmware(host)})
    agg.update({'capability': get_capability(host, showDisabled, showDefault)})
    agg.update({'leases': get_leases(host)})
    agg.update({'netwatch': get_netwatch(host)})
    return agg


def get_identity(host):
    call = router.get_identity(host)
    response = (make_camel_case(call))
    return response


def get_capability(host, showDisabled=False, showDefault=False, filter=None):
    options = {'showDisabled': showDisabled, 'showDefault': showDefault}
    leases = get_leases(host)
    cap_dict = {}
    capabilities_map = AppConf.config('capability_map')
    for capability in capabilities_map:
        cap_name = capability.get('name')
        cap_dict.update({cap_name: {}})
        matching_leases = []
        for lease in leases:
            if is_valid(lease, capability, options):
                matching_leases.append(lease)
        if matching_leases:
            obj_body = {'metadata': matching_leases, 'isHealthy': health_check(matching_leases)}
            cap_dict[cap_name].update(obj_body)

    return cap_dict


def get_firmware(host):
    response = {'metaData': None, 'isHealthy': None}
    keys = ('factory-firmware', 'current-firmware', 'upgrade-firmware')
    call = router.get_firmware(host)
    firmware_meta = make_camel_case(call, keys)
    current = version.parse(firmware_meta.get('currentFirmware'))
    response['metaData'] = firmware_meta
    target = version.parse("6.44.5")
    response.update({'isHealthy': current >= target})
    return response


def get_leases(host):
    keys = ('comment', 'address', 'mac-address', 'status', 'disabled', 'last-seen')
    call = router.get_leases(host)
    response = make_camel_case(call, keys)
    for lease in response:
        lease.update({'isHealthy': lease.get('status') == 'bound'})
        if not lease.get('address'):
            lease['address'] = ""
    return response


def get_netwatch(host):
    keys = ('comment', 'host', 'status', 'since')
    call = router.get_netwatch(host)
    response = make_camel_case(call, keys)
    return response


# v3

def get_aggregate_v3(host, showDisabled, showDefault):
    agg = {}
    agg.update({'identity': get_identity(host)})
    agg.update({'firmware': get_firmware(host)})
    agg.update({'capability': get_capability(host, showDisabled, showDefault)})
    agg.update({'leases': get_leases(host)})
    agg.update({'netwatch': get_netwatch(host)})
    return agg


def post_config_backup():
    config_file_name = router.backup_config()
    logging.info(f"Wrote config file {config_file_name}.")
    return {"response": "Wrote config."}


def get_config_backup():
    reply = router.get_config_info()
    logging.info(f"returned backup info size {len(reply)}.")
    logging.debug(f"File info: {reply}")
    return reply
