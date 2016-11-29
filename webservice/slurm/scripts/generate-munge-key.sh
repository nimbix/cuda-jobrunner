#!/bin/bash

dd if=/dev/urandom bs=1 count=1024 > /opt/munge-0.5.11/etc/munge/munge.key

chmod 400 /opt/munge-0.5.11/etc/munge/munge.key
chown -R root:root /opt/munge-0.5.11/etc/munge/munge.key

COUNT=$(cat /etc/JARVICE/nodes)
let NSLAVES=$COUNT-1

if [ -r /etc/JARVICE/nodes ]; then
    for i in `tail -n ${NSLAVES} /etc/JARVICE/nodes`; do
        scp /opt/munge-0.5.11/etc/munge/munge.key $i:/opt/munge-0.5.11/etc/munge/munge.key
    done
fi
