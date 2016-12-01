#!usr/bin/env python
import pika
import json
import os
import requests
import logging

SLURM_EPILOG_LOGFILE = os.getenv('SLURM_EPILOG_LOGFILE',
                                 '/code/web/slurm_epilog.log')

root = logging.getLogger()
root.setLevel(logging.DEBUG)
fh = logging.FileHandler('/code/web/slurm_epilog.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '[%(levelname)s] %(name)s %(asctime)s %(message)s')
fh.setFormatter(formatter)
root.addHandler(fh)

logger = logging.getLogger('slurm_epilog')


CALLBACK_QUEUE = 'job_results'


def publish_response(data):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost'))
    ch = connection.channel()
    message = '{message}\n'.format(message=json.dumps(data))
    ch.queue_declare(queue=data['id'],
                     auto_delete=True,
                     durable=True)
    ch.basic_publish(exchange='',
                     routing_key=CALLBACK_QUEUE,
                     body=message,
                     properties=pika.BasicProperties(
                         correlation_id=data['id']))


def main():

    job_name = os.getenv('SLURM_JOB_NAME', '')
    job_exit_code = os.getenv('SLURM_JOB_EXIT_CODE', '0')

    data = {'id': job_name,
            'exit_code': job_exit_code}

    publish_response(data)

    callback_url = os.getenv('JARVICE_CALLBACK_URL', '')
    if callback_url:
        requests.get(callback_url, data=data)


if __name__ == '__main__':
    main()
