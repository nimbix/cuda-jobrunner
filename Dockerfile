FROM nimbix/ubuntu-cuda:trusty

# Upstart hack
USER root
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -s /bin/true /sbin/initctl

RUN apt-get update && \
    apt-get install -y \
            python \
            python-dev \
            python-virtualenv \
            wget \
            curl \
            gdebi

WORKDIR /tmp
RUN apt-get update && wget https://www.rabbitmq.com/releases/rabbitmq-server/v3.6.6/rabbitmq-server_3.6.6-1_all.deb && \
    gdebi -n rabbitmq-server_3.6.6-1_all.deb

RUN sudo dpkg-divert --remove --local /sbin/initctl
RUN sudo apt-get install --reinstall -y --force-yes upstart

WORKDIR /code
USER nimbix

# Install SLURM
ADD ./slurm ./slurm
RUN /bin/bash -x ./slurm/scripts/install-munge.sh
RUN /bin/bash -x ./slurm/scripts/install-slurm.sh


ADD ./scripts /usr/local/scripts
ADD ./slurm/conf /opt/conf

RUN sudo apt-get install -y supervisor
ADD ./web/conf/web.conf /etc/supervisor/conf.d/web.conf

USER root
RUN mkdir -p /code/web
ADD ./web /code/web
RUN chown -R nimbix:nimbix /code/web
RUN echo 'OPTIONS="--force"' >> /etc/default/munge

# Clean up any existing state
USER nimbix
RUN rm -rf /code/web/.venv
RUN virtualenv /code/web/.venv
WORKDIR /code/web
RUN /bin/bash -c ". /code/web/.venv/bin/activate; pip install -r requirements.txt"
RUN /bin/bash -x /code/web/setup.sh

ADD ./rabbitmq /code/rabbitmq

USER nimbix

# Build examples
ADD ./examples /code/examples
#RUN /bin/bash /code/examples/install-torch.sh
#RUN /bin/bash -x /code/examples/install-neural-style.sh
RUN sudo pip install pika requests

USER root
RUN sudo apt-get install -y nginx
ADD ./nginx/conf/default /etc/nginx/sites-available/webservice
RUN ln -sf /etc/nginx/sites-available/webservice /etc/nginx/sites-enabled/webservice
ADD ./doc/site /code/web/
