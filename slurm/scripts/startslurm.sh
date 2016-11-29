#!/bin/bash

NCORES=`cat /etc/JARVICE/cores | wc -l`
NNODES=`cat /etc/JARVICE/nodes | wc -l`

let CORES_PER_NODE=$NCORES/$NNODES

NODES=

# Write the slurm.conf file
for i in `cat /etc/JARVICE/nodes`; do
    if [ -z $NODES ]; then
        NODES="$i"
        SUBMITNODE="$i"
    else
        NODES="$NODES,$i"
    fi
done

cp /opt/conf/slurm.conf.template /tmp/slurm.conf

sed -i "s/{{nodes}}/${NODES}/g" /tmp/slurm.conf
sed -i "s/{{hostname}}/${SUBMITNODE}/g" /tmp/slurm.conf
sed -i "s/{{cores_per_node}}/${CORES_PER_NODE}/g" /tmp/slurm.conf

sudo mkdir -p /opt/slurm/etc
sudo cp /tmp/slurm.conf /opt/slurm/etc

sudo /opt/slurm/sbin/slurmctld

for i in `cat /etc/JARVICE/nodes`; do
    ssh $i sudo mkdir -p /opt/slurm/etc
    scp /tmp/slurm.conf $i:/tmp/slurm.conf
    ssh $i sudo cp /tmp/slurm.conf /opt/slurm/etc/slurm.conf
    ssh $i sudo /etc/init.d/munge start
    ssh $i sudo /opt/slurm/sbin/slurmd
done
