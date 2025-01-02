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


from mt_query.router.common import get_last_octet


"""This file is used to define the capabilities of a router.
The capabilities are defined by the base IP, base MAC, and the range of IP addresses that the router can lease."""


def make_capabilities(cap_list):
    return dict((cap, {}) for cap in cap_list)


def is_valid(lease, capability, options):
    correct_ip = is_correct_ip(lease, capability['base_ip'])
    in_range = is_in_ip_range(lease, capability['start'], capability['end'])
    not_default = is_not_default_mac(lease, capability['base_mac'], options['showDisabled'])
    not_disabled = is_not_disabled(lease, options['showDefault'])
    validity = correct_ip and in_range and not_default and not_disabled
    return correct_ip and in_range and not_default and not_disabled


def is_correct_ip(lease, base_ip):
    return base_ip in lease.get('address')


def is_in_ip_range(lease, start, end):
    last_octet = get_last_octet(lease.get('address'))

    return start <= last_octet <= end


def is_not_default_mac(lease, default_mac, show_default):
    lease_mac = lease.get('macAddress') or ""
    return True if show_default else default_mac not in lease_mac


def is_not_disabled(lease, show_disabled):
    return True if show_disabled else not lease.get('disabled')


def health_check(leases):
    lease_health = False if any(not lease.get('isHealthy') for lease in leases) else True
    return lease_health
