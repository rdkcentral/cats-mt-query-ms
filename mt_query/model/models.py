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


from __future__ import annotations

from enum import Enum
from typing import List, Optional, Set

from pydantic import BaseModel, Field, RootModel


class Identity(BaseModel):
    name: Optional[str] = Field(None, example='example_router_name')


class NetwatchItem(BaseModel):
    since: Optional[str] = Field(
        None,
        description='Length of time since status change.',
        example='aug/02/2019 18:18:11',
    )
    status: Optional[str] = Field(None, description='Current status.', example='up')
    comment: Optional[str] = Field(
        None, description='Configuration comment.', example='system - TRS01'
    )
    address: Optional[str] = Field(
        None, description='Lease IP address.', example='192.168.100.61'
    )


class Netwatch(RootModel):
    root: List[NetwatchItem] = Field(
        ..., description='All of the netwatch entries on the router.'
    )


class FirmwareMeta(BaseModel):
    currentFirmware: Optional[str] = None
    upgradeFirmware: Optional[str] = None
    model: Optional[str] = None


class DhcpLease(BaseModel):
    comment: Optional[str] = Field(
        None, description='Configuration comment.', example='TRS01'
    )
    address: Optional[str] = Field(
        None, description='Lease IP address.', example='192.168.100.6'
    )
    isHealthy: Optional[bool] = Field(
        None,
        description='Health state of the lease. False if lease is unbound.',
        example=True,
    )
    macAddress: Optional[str] = Field(
        None,
        description='Mac address of the lease device.',
        example='93:FB:E5:3D:0E:BF',
    )
    status: Optional[str] = Field(
        None, description='Current status of lease.', example='bound'
    )
    disabled: Optional[bool] = Field(
        None,
        description='True if the lease has been disabled via configuration.',
        example=False,
    )


class CapabilityV2(BaseModel):
    isHealthy: Optional[bool] = Field(
        None,
        description='Health status of the capability. False if one or more child leases is not healthy.',
        example=True,
    )
    metadata: Optional[List[DhcpLease]] = Field(
        None, description='Detailed list of checked leases for a given capability'
    )


class Capability1(Enum):
    IRR = 'IRR'
    PWR = 'PWR'
    TCE = 'TCE'
    VID = 'VID'
    SRV = 'SRV'


class Capability(BaseModel):
    host: Optional[str] = Field(None, example='0.0.0.0.0')
    capabilities: Optional[Set[Capability1]] = Field(
        None,
        example=['IRR', 'TCE', 'PWR'],
        max_items=15,
        min_items=0,
    )
    showDefault: Optional[bool] = False
    showDisabled: Optional[bool] = False


class LeaseArray(RootModel):
    root: List[DhcpLease] = Field(
        ..., description='An array containing all of the leases on a router.'
    )


class Firmware(BaseModel):
    isHealthy: Optional[bool] = Field(
        None,
        description='Health status of the firmware. Returns false if the firmware is less than 6.44.5',
    )
    metaData: Optional[FirmwareMeta] = None


class Aggregate(BaseModel):
    identity: Optional[Identity] = None
    capability: Optional[CapabilityV2] = None
    leases: Optional[LeaseArray] = None
    netwatch: Optional[Netwatch] = None
    firmware: Optional[Firmware] = None
