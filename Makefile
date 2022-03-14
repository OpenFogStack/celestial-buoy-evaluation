#
# This file is part of Celestial's Videoconferencing Evaluation
# (https://github.com/OpenFogStack/celestial-videoconferencing-evaluation).
# Copyright (c) 2021 Tobias Pfandzelter, The OpenFogStack Team.
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

.PHONY: all

all: sensor/sensor.img sensor/sensor-sat.img service/service.img sink/sink.img

model/model.tflite: model/lstm.py model/data.csv model/train.sh
	cd model && sh train.sh

sensor/server_selection.bin: sensor/server_selection.go
	GOOS=linux GOARCH=amd64 go build -o $@ sensor/server_selection.go

sensor/sensor.img: sensor/sensor.sh sensor/sensor-base.sh sensor/data_gen.py sensor/server_selection.bin
	@docker run --rm -v $(PWD)/sensor/sensor.sh:/app.sh -v $(PWD)/sensor/sensor-base.sh:/base.sh -v $(PWD)/sensor/workload.csv:/files/workload.csv -v $(PWD)/sensor/data_gen.py:/files/data_gen.py -v $(PWD)/sensor/server_selection.bin:/files/server_selection.bin -v $(PWD):/opt/code --privileged rootfsbuilder $@

sensor/sensor-sat.img: sensor/sensor-sat.sh sensor/sensor-base.sh sensor/data_gen.py sensor/server_selection.bin
	@docker run --rm -v $(PWD)/sensor/sensor-sat.sh:/app.sh -v $(PWD)/sensor/sensor-base.sh:/base.sh -v $(PWD)/sensor/workload.csv:/files/workload.csv -v $(PWD)/sensor/data_gen.py:/files/data_gen.py -v $(PWD)/sensor/server_selection.bin:/files/server_selection.bin -v $(PWD):/opt/code --privileged rootfsbuilder $@

service/service.img: service/service.sh service/service-base.sh service/data_analyze.py model/model.tflite affinity.csv groups.csv
	@docker run --rm -v $(PWD)/service/service.sh:/app.sh -v $(PWD)/service/service-base.sh:/base.sh -v $(PWD)/service/data_analyze.py:/files/data_analyze.py -v $(PWD)/model/model.tflite:/files/model.tflite -v $(PWD)/wheels/tflite_runtime-2.8.0-cp39-cp39-linux_x86_64.whl:/files/tflite_runtime-2.8.0-cp39-cp39-linux_x86_64.whl  -v $(PWD)/wheels/numpy-1.22.2-cp39-cp39-linux_x86_64.whl:/files/numpy-1.22.2-cp39-cp39-linux_x86_64.whl -v $(PWD)/affinity.csv:/files/affinity.csv -v $(PWD)/groups.csv:/files/groups.csv -v $(PWD):/opt/code --privileged rootfsbuilder $@

sink/sink.img: sink/sink.sh sink/sink-base.sh sink/data_read.py
	@docker run --rm -v $(PWD)/sink/sink.sh:/app.sh -v $(PWD)/sink/sink-base.sh:/base.sh -v $(PWD)/sink/data_read.py:/files/data_read.py -v $(PWD):/opt/code --privileged rootfsbuilder $@
