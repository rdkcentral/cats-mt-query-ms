# Capability Map Overview

The [capability_map.yml](capability_map.yml) file holds the convention for the IP addresses for each capability on a rack. YAML lookup is used to define base values used in configuration of each capability. Expected values for capability_map file are defined below.

<br>

## Defining Expected Values

### The capability_map.yml file is a YAML file that contains the following fields: 
- **control_net** - Defines the convention used for configuring all capabilities
- **capabilities** - Defines the capabilities to configure and the IP address range to configure for

<br>

### The control_net section contains the following fields: 

- **control_net**
  - base_mac 
    - Defines base MAC address for capabilities
  - base_ip 
    - IP address prefix to be used for each capability IP definition
  - check_nat 
    - Boolean to define if NAT rules should be checked

<br>

### The capabilities section contains the following fields:

- **capabilities**
  - name 
    - Capability Shorthand (i.e. PWR, IRR, TCE, etc)
  - <<: *control_net
    - Defines YAML lookup tag to use for applying base values
  - start
    - Defines starting point for IP Address Host ID to use for a given capability. This will be appended to base_ip pulled from control_net YAML lookup and incremented for given number of hardware devices for a capability.
  - end
    - Defines ending point for IP Address Host ID to use for a given capability. This will be appended to base_ip pulled from control_net YAML lookup and incremented for given number of hardware devices for a capability.

<br> 

### Capabilities Shorthands Meanings:

- SRV = Server (Router)
- PWR = Power 
- IRR = IR
- TCE = Serial Trace
- VID = Video