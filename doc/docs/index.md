# Overview
This is a turn-key REST-driven job scheduler for custom applications.

# Example Usage

### Client
```python
# Launch Cluster
job = ...
c = AuthenticatedClient(username='username', apikey='apikey')
c.submit(job)

# Launch short-running HPC tasks
...

```

# Use Cases

*   Embarassingly parallel machine-learning processing on big data sets
*   Accelerated machine-learning inference cluster using NVIDIA GPUs, IBM POWER8, or Xilinx FPGAs
*   Turn-key REST API for latency-critical command-line applications

## Installation

### Method 1: Inherit from one of the pre-enabled Nimbix Dockerfiles (recommended)

For example, you can prepare your code like this:
```
# Dockerfile

FROM jarvice/cuda-jobrunner

ADD ./yourcode /usr/local/yourcode
RUN /usr/local/yourcode/install.sh
```

Use the command, `launch` in `/etc/NAE/AppDef.json`, which will invoke `/usr/local/scripts/start.sh`. You can customize `/usr/local/scripts/start.sh`. The core services are started using [supervisord](http://supervisord.org/).

### Method 2: Auto-install inside of Dockerfile


### Method 3: Manual installation



## API Documentation

## Job Status Documentation

Jobs are submitted asynchronously as a POST request to **/submission**. In order to obtain the job status of that task, you have two options:

1.  Poll /submission/{job_id} for status
2.  Subscribe to the **response queue using a RabbitMQ Client**
