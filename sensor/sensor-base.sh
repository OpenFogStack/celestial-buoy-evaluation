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

apk update
apk add -u chrony
echo "refclock PHC /dev/ptp0 poll -2 dpoll -2 offset 0 trust prefer" > /etc/chrony/chrony.conf
apk add python3 curl
chmod +x ./data_gen.py