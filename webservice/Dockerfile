FROM nimbix/ubuntu-cuda:trusty

# Upstart hack
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -s /bin/true /sbin/initctl

RUN apt-get update && \
    apt-get install -y \
            python \
            python-dev \
            python-virtualenv \
            wget \
            curl \
            gdebi \
             && \
    rm -rf /var/lib/apt/*

WORKDIR /tmp
RUN sudo apt-get update
RUN wget https://www.rabbitmq.com/releases/rabbitmq-server/v3.6.6/rabbitmq-server_3.6.6-1_all.deb && \
    gdebi -n rabbitmq-server_3.6.6-1_all.deb

RUN sudo dpkg-divert --remove --local /sbin/initctl
RUN sudo apt-get install --reinstall -y --force-yes upstart

WORKDIR /code
USER nimbix

# Install SLURM
ADD ./slurm ./slurm
RUN /bin/bash -x ./slurm/scripts/install-munge.sh
RUN /bin/bash -x ./slurm/scripts/install-slurm.sh


# Build examples
ADD ./examples /code/examples
RUN /bin/bash -x /code/examples/install-neural-style.sh
ADD ./scripts /usr/local/scripts

ADD ./slurm/conf /opt/conf

RUN sudo apt-get install -y supervisor
ADD ./web/conf/web.conf /etc/supervisor/conf.d/web.conf

USER root
RUN mkdir -p /code/web
ADD ./web /code/web
RUN chown -R nimbix:nimbix /code/web

# Clean up any existing state
USER nimbix
RUN rm -rf /code/web/.venv
RUN virtualenv /code/web/.venv
WORKDIR /code/web
RUN /bin/bash -c ". /code/web/.venv/bin/activate; pip install -r requirements.txt"
RUN /bin/bash -x /code/web/setup.sh
