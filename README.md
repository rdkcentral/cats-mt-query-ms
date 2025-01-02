# MT Query MS
The MT-Query Microservice is used for querying the health of the network router. 

<br><br> 

## Development Setup 

* Download from source.
* Run `pip install -r requirements.txt` from the root directory to install required dependencies from [requirements.txt](requirements.txt) file
* Run `export ENVIRONMENT=development` to set up local development environment
* Run `python app.py` from the root directory
* Application should now be running at http://localhost:9647

<br><br> 

## Configuring Capabilities

The capability map for the MT Query Microservice holds the convention used for the IP Addresses of each capability. This file can be found at [capability_map.yml](mt_query/config/capability_map.yml) and is further explained in [capability_map.md](mt_query/config/capability_map.md). This file is used to map the IP addresses of the capabilities on the rack to the capability names. YAML file using YAML lookup variables is expected to reflect the following:

```
---
control_net: &control_net
  base_mac: 00:11:22:33:44
  base_ip: 192.168.100
  check_nat: false

capabilities:
  - name: SRV
    <<: *control_net
    start: 11
    end: 11
  - name: PWR
    <<: *control_net
    start: 21
    end: 30
  - name: IRR
    <<: *control_net
    start: 31
    end: 49
  - name: TCE
    <<: *control_net
    start: 61
    end: 68
  ...
```

<br><br>

## Building

Run the below command in root directory as required by the [Dockerfile](Dockerfile) to build application as a Docker container.
* `docker build -t="/mt-query-ms" .`

<br><br>


## Deploying on server

From the target server, pull Docker container onto server from hosting location. Run the following command to run the container as a service on the server:

* `sudo docker run --detach -p 9647:9647 /mt-query-ms`

Service will be found on the 9647 port of the target. 

<br><br>

## NGINX Configuration

NGINX is used to support a unified path for communication to the rack microservices as well as communication between the rack microservices. NGINX configuration for mt-query-ms can be found at [mt-query.conf](conf/mt-query.conf). This configuration file is used to route requests to the power microservice.


<br><br>


## Access the Swagger Documentation

The Swagger Documentation for the Power Microservice can be accessed at https://localhost:9647/docs when running locally. Default swagger path is **/docs**.


<br><br>
