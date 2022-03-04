#!/usr/bin/env python3
import socket
import time
import pickle
import typing
import argparse
import random

SERVER_RECV_BUFFER_SIZE = 2048

class OneWayMeasurement():

    def __init__(self, test_output_filename: str) -> None:
        self.test_output_filename = test_output_filename

    @staticmethod
    def save_packet_latencies(packetn_latency_tuples: typing.Tuple[typing.List[str], typing.List[str], typing.List[int], typing.List[int], typing.List[float], typing.List[float], typing.List[float], typing.List[float]], output_filename: str) -> None:
        """
        Save latencies of received packets to a file, along with the total
        number of packets send in the first place.
        """
        with open(output_filename, "w") as out_file:
            out_file.write("sensor_id,service_id,packet_n,packet_len,send_time1,recv_time1,send_time2,recv_time2\n")
            for i in range(len(packetn_latency_tuples[0])):
                sensor_id = packetn_latency_tuples[0][i]
                service_id = packetn_latency_tuples[1][i]
                packet_n = packetn_latency_tuples[2][i]
                packet_len = packetn_latency_tuples[3][i]
                send_time1 = (packetn_latency_tuples[4][i] * 1e9)
                recv_time1 = (packetn_latency_tuples[5][i] * 1e9)
                send_time2 = (packetn_latency_tuples[6][i] * 1e9)
                recv_time2 = (packetn_latency_tuples[7][i] * 1e9)
                out_file.write("%s,%s,%d,%d,%.0f,%.0f,%.0f,%.0f\n" % (sensor_id, service_id, packet_n, packet_len, send_time1, recv_time1, send_time2, recv_time2))


    def run_server(self, n_packets_expected: int, server_listen_port: int, payload_len: int, timeout: int=15) -> None:
        """
        Receive packets sent from the client. Calculate the latency for each
        packet by comparing the counter value from the packet (the counter value
        at time of transmission) to the current counter value.
        """
        sock_in = \
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock_in.bind(("0.0.0.0", server_listen_port))

        print("UDP server running...")

        # packets: typing.List[typing.Tuple[int, int, int, float, float, float]] = [(0, 0, 0, 0.0, 0.0, 0.0)] * n_packets_expected
        sensor_ids = [""] * n_packets_expected
        service_ids = [""] * n_packets_expected
        packet_ns = [0] * n_packets_expected
        packet_lens = [0] * n_packets_expected
        send_times1 = [0.0] * n_packets_expected
        recv_times1 = [0.0] * n_packets_expected
        send_times2 = [0.0] * n_packets_expected
        recv_times2 = [0.0] * n_packets_expected

        packet_c = 0

        a = bytes("a", "ascii")

        # wait for the first packet before setting timeout
        sock_in.settimeout(10000)

        sock_in.recv(payload_len)

        sock_in.settimeout(timeout)

        try:
            while packet_c < n_packets_expected:
                data = sock_in.recv(payload_len)
                recv_time2 = time.time()
                packet_lens[packet_c] = len(data)
                payload = data.rstrip(a)
                (sensor_ids[packet_c], service_ids[packet_c], packet_ns[packet_c], values, send_time1, recv_time1, send_time2) = pickle.loads(payload)
                #packets[packet_c] = (id, packet_n, packet_len, latency_ms, send_time, recv_time)
                send_times1[packet_c]  = send_time1
                recv_times1[packet_c]  = recv_time1
                send_times2[packet_c]  = send_time2
                recv_times2[packet_c]  = recv_time2

                packet_c += 1

                if packet_c % 2000 == 0:
                   print("%d packets received so far" % packet_c)

        except socket.timeout:
            print("Note: timed out waiting to receive packets")
            print("So far, had received %d packets" % packet_c)
        except KeyboardInterrupt:
            print("Interrupted")

        sock_in.close()

        print("Received %d packets" % packet_c)

        self.save_packet_latencies((sensor_ids[:packet_c], service_ids[:packet_c], packet_ns[:packet_c], packet_lens[:packet_c], send_times1[:packet_c], recv_times1[:packet_c], send_times2[:packet_c], recv_times2[:packet_c]), self.test_output_filename)


def start(Measurement: typing.Type[OneWayMeasurement]) -> None:
    """
    Process arguments and run the appropriate functions depending on whether
    we're in server mode or client mode.
    """

    args = parse_args()

    tester = Measurement(args.output_filename)

    tester.run_server(args.n_packets, args.listen_port, SERVER_RECV_BUFFER_SIZE, args.timeout)

def parse_args() -> argparse.Namespace:
    """
    Parse arguments.
    """

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--n_packets", type=int, default=700000)
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument(
        "--output_filename", default='udp_packetn_latency_pairs')
    parser.add_argument("--listen_port", type=int, default=8888)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    start(OneWayMeasurement)