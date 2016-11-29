#!/bin/bash

dd if=/dev/urandom bs=1 count=1024 > /etc/munge/munge.key

chmod 440 /etc/munge/munge.key
chown -R munge:munge /etc/munge/munge.key

COUNT=$(cat /etc/JARVICE/nodes | wc -l)
let NSLAVES=$COUNT-1

if [ -r /etc/JARVICE/nodes ]; then
    for i in `tail -n ${NSLAVES} /etc/JARVICE/nodes`; do
        scp /etc/munge/munge.key $i:/tmp/munge.key
        ssh $i sudo mv /tmp/munge.key /etc/munge/munge.key
        ssh $i "sudo chmod 440 /etc/munge/munge.key && sudo chown -R munge:munge /etc/munge/munge.key"
    done
fi
