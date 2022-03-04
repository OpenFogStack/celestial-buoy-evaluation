#!/usr/bin/env python3

import csv
import socket
import time
import pickle
import typing
import argparse
import queue
import threading as td

import tflite_runtime.interpreter as tflite
import numpy as np

SERVER_RECV_BUFFER_SIZE = 2048
MODEL_INPUT_LENGTH = 10

class OneWayMeasurement():

    def __init__(self, target_port: int, id: str, group_list: str, affinity_list: str) -> None:
        self.sockets: typing.Dict[str, socket.socket] = {}

        self.target_port = target_port

        self.id = id

        self.sensor_groups: typing.Dict[str, str] = {}

        self.group_buffers: typing.Dict[str, np.ndarray] = {}
        self.group_buffer_point: typing.Dict[str, int] = {}

        with open(group_list, "r") as f:
            for line in csv.DictReader(f):
                group = line["GROUP"]
                self.sensor_groups[line["SENSOR_ID"]] = group

                if group not in self.group_buffers:
                    self.group_buffers[group] = np.zeros(MODEL_INPUT_LENGTH, dtype=np.float32)
                    self.group_buffer_point[group] = 0

        self.targets: typing.Dict[str, typing.List[str]] = {}

        with open(affinity_list, "r") as f:
            for line in csv.DictReader(f):
                if line["GROUP"] not in self.targets:
                    self.targets[line["GROUP"]] = []
                self.targets[line["GROUP"]].append("sink%s.gst.celestial" % line["STATION_ID"])

        self.queue = queue.SimpleQueue()

        # https://www.tensorflow.org/lite/api_docs/python/tf/lite/Interpreter#used-in-the-notebooks
        interpreter = tflite.Interpreter(model_path="./model.tflite")
        interpreter.allocate_tensors()

        self.fn = interpreter.get_signature_runner('serving_default')

        self.min_v = 7.8
        self.max_v = 36.0

    def scale(self, x: float) -> np.float32:
        if x < self.min_v:
            return np.float32(0)
        if x > self.max_v:
            return np.float32(1)
        return np.float32((x - self.min_v) / (self.max_v - self.min_v))

    def predict(self, value: float, group: str) -> float:

        self.group_buffers[group][self.group_buffer_point[group]] = self.scale(value)
        self.group_buffer_point[group] += 1
        self.group_buffer_point[group] %= MODEL_INPUT_LENGTH

        return float(self.fn(x=np.array([[ self.group_buffers[group] ]]))["output_0"][0][0])

    def get_socket(self, target: str) -> socket.socket:
        if target in self.sockets:
            return self.sockets[target]

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((target, self.target_port))
        self.sockets[target] = sock
        return sock

    def send_packet(self, target: str, ids: int, packet_n: int, value: float, send_time: float, recv_time: float) -> None:
        """
        Send a packet to the target.
        """

        send_time_seconds2 = time.time()
        payload = pickle.dumps((ids, self.id, packet_n, value, send_time, recv_time, send_time_seconds2))
        payload = bytes(payload)

        try:
            self.get_socket(target).sendall(payload)
        except Exception as e:
            print("Exception sending packet to %s: %s" % (target, e))

    def run_server(self, server_listen_port: int, payload_len: int, timeout: int=15) -> None:
        """
        Receive packets sent from the client. Calculate the latency for each
        packet by comparing the counter value from the packet (the counter value
        at time of transmission) to the current counter value.
        """
        sock_in = \
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock_in.bind(("0.0.0.0", server_listen_port))

        print("UDP server running with %ds timeout..." % timeout)

        td.Thread(target=self.run_sender).start()

        # wait for the first packet before setting timeout
        sock_in.settimeout(10000)

        sock_in.recv(payload_len)

        sock_in.settimeout(timeout)

        packet_c = 0

        try:
            while True:
                payload = sock_in.recv(payload_len)

                recv_time = time.time()

                self.queue.put((payload, packet_c, recv_time))

                if packet_c % 200 == 0:
                    print("%d packets received" % packet_c)

                packet_c += 1

        except socket.timeout:
            print("Note: timed out waiting to receive packets")
            print("So far, had received %d packets" % packet_c)
        except KeyboardInterrupt:
            print("Interrupted")

        sock_in.close()

        print("Received %d packets" % packet_c)

    def run_sender(self) -> None:
        while True:
            payload, packet_c, recv_time = self.queue.get()

            (ids, packet_n, value, send_time) = pickle.loads(payload)

            group = self.sensor_groups[ids]

            vals = self.predict(value, group)

            for target in self.targets[group]:
                self.send_packet(target, ids, packet_n, vals, send_time, recv_time)

            if packet_c % 200 == 0:
                print("%d packets sent (%d backpressure)" % (packet_c, self.queue.qsize()))

def start(Measurement: typing.Type[OneWayMeasurement]) -> None:
    """
    Process arguments and run the appropriate functions depending on whether
    we're in server mode or client mode.
    """

    args = parse_args()

    tester = Measurement(args.target_port, args.id, args.group_list, args.afinity_list)

    tester.run_server(args.listen_port, SERVER_RECV_BUFFER_SIZE, args.timeout)

def parse_args() -> argparse.Namespace:
    """
    Parse arguments.
    """

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--id", type=str, required=True)
    parser.add_argument("--group_list", type=str, required=True)
    parser.add_argument("--afinity_list", type=str, required=True)
    parser.add_argument("--target_port", type=int, default=8000)
    parser.add_argument("--n_packets", type=int, default=700000)
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument(
        "--output_filename", default='udp_packetn_latency_pairs')
    parser.add_argument("--listen_port", type=int, default=8888)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    start(OneWayMeasurement)