#!/usr/bin/env python3

import socket
import time
import pickle
import typing
import http.server
import cgi
import argparse
import random
import multiprocessing as mp
from multiprocessing.connection import Connection as MultiprocessingConnection
import threading as td

target_address_pipe_in, target_address_pipe_out = mp.Pipe()

SERVER_RECV_BUFFER_SIZE = 2048

class Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers, # type: ignore
            environ={"REQUEST_METHOD": "POST"}
        )

        s = form.getvalue("server")

        target_address_pipe_in.send(s)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK\n")


class OneWayMeasurement():
    def __init__(self) -> None:
        self.target_address: typing.Optional[str] = None
        self.target_port: typing.Optional[int] = None

    def update_target(self, target_address_pipe: MultiprocessingConnection) -> None:
        while True:
            target_address = target_address_pipe.recv()
            if self.target_port is not None:
                print("Updating target address to %s:%d" % (target_address, self.target_port))
            if self.target_address != target_address:
                self.target_address = None

                if target_address != "none":
                    self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.sock_out.connect((target_address, self.target_port))
                    self.target_address = target_address

    def send_packets(self, sensor_id: int, n_packets: int, send_rate_kBps: float) -> None:
        """
        Send n_packets packets, each with a payload of packet_len bytes, to
        target_address, trying to maintain a constant send rate of
        send_rate_kbytes_per_s.
        """

        #send_rate_bytes_per_s = send_rate_kbytes_per_s * 1000
        n_bytes = 0
        #packet_rate = send_rate_bytes_per_s / packet_len
        #packet_interval = 1 / packet_rate

        #print("Sending %d %d-byte packets at about %d kB/s..." %(n_packets, packet_len, send_rate_kbytes_per_s))

        # find out how long to sleep between sending packets
        packet_interval = 128 / (send_rate_kBps * 1000)

        print("Waiting for a target address...")

        while self.target_address is None:
            pass

        print("Got a target address...")


        send_start_seconds = time.time()
        #inter_packet_sleep_times_ms = []

        for packet_n in range(n_packets):

            while self.target_address == None:
                pass

            tx_start_seconds = time.time()

            payload = self.get_packet_payload(sensor_id, packet_n)

            if self.target_address is not None:
                try:
                    self.sock_out.sendall(payload)
                    if packet_n % 200 == 0:
                        print("%d packets sent" % packet_n)
                except:
                    pass

            tx_end_seconds = time.time()

            # I don't know why, but this still doesn't yield exactly the desired
            # send rate. But eh, it's good enough.
            tx_time_seconds = tx_end_seconds - tx_start_seconds
            sleep_time_seconds = packet_interval - tx_time_seconds
            #inter_packet_sleep_times_ms.append("%.3f" % (sleep_time_seconds * 1000))
            if sleep_time_seconds > 0:
                time.sleep(sleep_time_seconds)
        send_end_seconds = time.time()

        print("Finished sending packets!")

        total_send_duration_seconds = send_end_seconds - send_start_seconds
        bytes_per_second = n_bytes / total_send_duration_seconds
        print("(Actually sent packets at %d kB/s: %d bytes for %.1f seconds)" % (bytes_per_second / 1e3, n_bytes, total_send_duration_seconds))

        self.sock_out.close()

    def run_client(self, sensor_id: int, listen_port: int, http_port: int, n_packets: int, send_rate_kBps: int) -> None:

        # self.workload_bytes: typing.List[int] = []
        # self.workload_deltas: typing.List[float] = []

        # with open(workload_file) as workload_csv:
        #     workload_reader = csv.DictReader(workload_csv)
        #     for row in workload_reader:
        #         delta = float(row["delta"]) / 1e9
        #         length = int(row["length"])

        #         self.workload_bytes.append(length)
        #         self.workload_deltas.append(delta)

        #         total_packet_len += length
        #         total_workload_duration += delta

        # assert len(self.workload_bytes) == len(self.workload_deltas)

        # self.workload_length = len(self.workload_bytes)

        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target_address = None
        self.target_port = listen_port

        httpd = http.server.HTTPServer(("", http_port), Handler)

        h = td.Thread(target=httpd.serve_forever)
        h.start()

        print("Started HTTP server on :%d" % (http_port))

        controlThread = td.Thread(target=self.update_target, args=[target_address_pipe_out])
        controlThread.start()

        print("Started control thread...")

        self.send_packets(sensor_id, n_packets, send_rate_kBps)

        h.join(0.0)
        controlThread.join(0.0)
        exit(0)

    def get_packet_payload(self, sensor_id: int, packet_n: int) -> bytes:
        """
        Return a packet payload consisting of:
        - The packet number
        - A random value
        - The timestamp of the packet
        """

        value = float(random.randint(0, 2**6))
        send_time_seconds = time.time()
        payload = pickle.dumps((sensor_id, packet_n, value, send_time_seconds))
        return payload

def start(Measurement: typing.Type[OneWayMeasurement]) -> None:
    """
    Process arguments and run the appropriate functions depending on whether
    we're in server mode or client mode.
    """

    args = parse_args()

    if args.payload_len > SERVER_RECV_BUFFER_SIZE:
        print("Warning: payload_len (%d) is greater than "
              "SERVER_RECV_BUFFER_SIZE (%d)" % (args.payload_len,
                                                SERVER_RECV_BUFFER_SIZE))

    tester = Measurement()

    sensor_id = args.name[len("sensor"):]

    tester.run_client(sensor_id, args.listen_port, args.http_port, args.n_packets, args.send_rate_kBps)

def parse_args() -> argparse.Namespace:
    """
    Parse arguments.
    """

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--n_packets", type=int, default=700000)
    parser.add_argument("--listen_port", type=int, default=8888)
    parser.add_argument("--payload_len", type=int, default=1227)
    parser.add_argument("--send_rate_kBps", type=float, default=1400.0)
    parser.add_argument("--name", type=str, required=True)
    parser.add_argument("--http_port", type=int, default=8000)
    # parser.add_argument("--workload_file", type=str, default="./workload.csv")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    start(OneWayMeasurement)