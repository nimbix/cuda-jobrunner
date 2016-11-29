#!/usr/bin/env python
import pika
import random
import subprocess


def submit_to_scheduler(command, files):

    job_id = int(random.random()*1000)
    #subprocess.call(['srun', '-J', job_id, command])
    return job_id


def callback(ch, method, properties, body):
    print(" [x] Received {body}".format(body=repr(body)))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def setup_connection(host='localhost'):

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host))
    channel = connection.channel()
    return channel


def main():
    channel = setup_connection()
    channel.queue_declare(queue='slurm_worker', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue='slurm_worker')
    channel.start_consuming()

if __name__ == '__main__':
    main()
