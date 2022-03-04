# Notes.md

```sh
HOST=34.89.169.47
scp -ri gcloud.pem.pub sensor/sensor.img tp@$HOST:.
scp -ri gcloud.pem.pub service/service.img tp@$HOST:.
scp -ri gcloud.pem.pub sink/sink.img tp@$HOST:.
```

```sh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOiY5bT9f6NOcvzYGxFB8bb/c0dX0fpTKt3afyGA0H3V tp@mcc.tu-berlin.de" >> .ssh/authorized_keys
```

```sh
mkdir ./mnt_tmp

sudo mount -t ext4 -o loop /celestial/cesink1.ext4 ./mnt_tmp

cp ./mnt_tmp/root/udp_packetn_latency_pairs ./test-results.csv
sudo umount ./mnt_tmp
```

```sh
scp -ri gcloud.pem.pub tp@$HOST:./test-results.csv ./results/test/
```

```sh
# HOST1=35.234.113.127
HOST2=34.141.24.155
HOST3=34.141.80.97
HOST4=34.141.102.164
HOST5=35.242.254.102
HOSTC=34.89.169.47

# scp -ri gcloud.pem.pub sensor/sensor.img tp@$HOST1:.
# scp -ri gcloud.pem.pub service/service.img tp@$HOST1:.
# scp -ri gcloud.pem.pub sink/sink.img tp@$HOST1:.

scp -ri gcloud.pem.pub sensor/sensor.img tp@$HOST2:.
scp -ri gcloud.pem.pub service/service.img tp@$HOST2:.
scp -ri gcloud.pem.pub sink/sink.img tp@$HOST2:.

scp -ri gcloud.pem.pub sensor/sensor.img tp@$HOST3:.
scp -ri gcloud.pem.pub service/service.img tp@$HOST3:.
scp -ri gcloud.pem.pub sink/sink.img tp@$HOST3:.

scp -ri gcloud.pem.pub sensor/sensor.img tp@$HOST4:.
scp -ri gcloud.pem.pub service/service.img tp@$HOST4:.
scp -ri gcloud.pem.pub sink/sink.img tp@$HOST4:.

scp -ri gcloud.pem.pub sensor/sensor.img tp@$HOST5:.
scp -ri gcloud.pem.pub service/service.img tp@$HOST5:.
scp -ri gcloud.pem.pub sink/sink.img tp@$HOST5:.

scp -ri gcloud.pem.pub iridium-full.toml tp@$HOSTC:.


scp -ri gcloud.pem.pub tp@$HOST1:/celestial/vmlinux.bin .

scp -ri gcloud.pem.pub ./vmlinux.bin tp@$HOST2:.
scp -ri gcloud.pem.pub ./vmlinux.bin tp@$HOST3:.
scp -ri gcloud.pem.pub ./vmlinux.bin tp@$HOST4:.
scp -ri gcloud.pem.pub ./vmlinux.bin tp@$HOST5:.
```

```sh
sudo cp sensor.img /celestial/
sudo cp service.img /celestial/
sudo cp sink.img /celestial/
sudo cp vmlinux.bin /celestial/

sudo service systemd-resolved stop

sudo rm /celestial/out/*
sudo rm /celestial/ce*.ext4

echo "starting celestial..."

sudo ./celestial.bin
```

```sh

#!/bin/bash

# usage: run-cluster.sh <name> <number>
# check that we got the parameter we needed or exit the script with a usage message
[ $# -ne 2 ] && { echo "Usage: $0 name number"; exit 1; }

name=$1
number=$2

results_dir="./results2/results-$name-$number"

mkdir ./mnt_tmp

mkdir -p "$results_dir"

for d in /celestial/cesink*.ext4 ; do
    bname=$(basename "$d")
    echo "mounting $d"
    sudo mount -t ext4 -o loop "$d" ./mnt_tmp
    echo "mounting $d done"
    echo "copying results"
    cp -r ./mnt_tmp/root/udp_packetn_latency_pairs "$results_dir/$bname-results.csv"

    echo "copying results done"
    echo "unmounting $d"
    sudo umount ./mnt_tmp
    echo "unmounting $d done"
done

rm -rfd ./mnt_tmp
```

```sh
RUN_NAME=test
RUN_NUMBER=3
scp -ri gcloud.pem.pub tp@$HOST2:./results2/results-"$RUN_NAME"-"$RUN_NUMBER" ./results/ &
scp -ri gcloud.pem.pub tp@$HOST3:./results2/results-"$RUN_NAME"-"$RUN_NUMBER" ./results/ &
scp -ri gcloud.pem.pub tp@$HOST4:./results2/results-"$RUN_NAME"-"$RUN_NUMBER" ./results/ &
scp -ri gcloud.pem.pub tp@$HOST5:./results2/results-"$RUN_NAME"-"$RUN_NUMBER" ./results/ &
```
