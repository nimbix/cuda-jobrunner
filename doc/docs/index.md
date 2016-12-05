# Overview
This is a turn-key REST-driven job scheduler for custom applications. The application has been tested on Ubuntu 14.04 and Ubuntu 16.04 base images on Nimbix. Any Ubuntu 14.04 or Ubuntu 16.04 operating system should support the installation. If you are interested in running on another flavor of Linux such as CentOS, please feel free to open an issue on Github or send a pull request.

## Use Cases

*   Embarassingly parallel machine-learning processing on big data sets
*   Accelerated machine-learning inference cluster using NVIDIA GPUs, IBM POWER8, or Xilinx FPGAs
*   Turn-key REST API for latency-critical command-line applications
*   Parallelizing a GPU-driven application that respects CUDA_VISIBLE_DEVICES to assign work to a GPU, but doesn't inherently support multi-GPU usage

## Installation

**Operating System**: Ubuntu 14.04 or Ubuntu 16.04 Docker base images

### Method 1: Inherit your pre-built application image in the **template** Dockerfile on Github

```
# Dockerfile

FROM {your-application}

... github.com/nimbix/base-jobrunner.git:Dockerfile.tpl ...
```


```bash

docker build .

```

### Method 2: Inherit from one of the pre-enabled Nimbix Dockerfiles

For example, you can prepare your code like this:
```
# Dockerfile

FROM jarvice/cuda-jobrunner

ADD ./yourcode /usr/local/yourcode
RUN /usr/local/yourcode/install.sh
```

Use the command, `launch` in `/etc/NAE/AppDef.json`, which will invoke `/usr/local/scripts/start.sh`. You can customize `/usr/local/scripts/start.sh`. The core services are started using [supervisord](http://supervisord.org/).

### Method 3: Manual installation

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
