#!/bin/sh

#
# This file is part of Celestial's Buoy Evaluation
# (https://github.com/OpenFogStack/celestial-buoy-evaluation).
# Copyright (c) 2022 Tobias Pfandzelter, The OpenFogStack Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

rc-service chronyd start

IP=$(/sbin/ip route | awk '/default/ { print $3 }')

echo nameserver "$IP" > /etc/resolv.conf

rc-status --servicelist
rc-service chronyd start
rc-status --servicelist
touch /run/openrc/softlevel
rc-service chronyd start
rc-status chronyd

chronyc tracking

chronyc -a makestep

sleep 10

chronyc tracking

chronyc -a makestep

chronyc tracking

sleep 10

chronyc tracking

while ! curl -m 5 -f "$IP/self" ; do
    echo "cannot curl $IP/self"
    sleep 5
done

echo "STARTING SINK"

NAME=$(curl -s "$IP"/self | python3 -c 'import sys, json; print(json.load(sys.stdin)["name"])')

echo "$NAME"

./data_read.py --listen_port 3000 --n_packets 25000 --timeout 60

sleep 20
