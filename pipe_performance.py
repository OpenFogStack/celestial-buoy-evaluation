"""
pipe_performance.py
"""
import threading as td
import queue
import multiprocessing as mp
import multiprocessing.connection as mp_connection
import time
import typing

def reader_pipe(p_out: mp_connection.Connection) -> None:
    while True:
        msg = p_out.recv()
        if msg=='DONE':
            break

def reader_queue(p_queue: queue.Queue[typing.Union[str, int]]) -> None:
    while True:
        msg = p_queue.get()
        if msg=='DONE':
            break

if __name__=='__main__':
    # first: mp.pipe
    for count in [10**4, 10**5, 10**6, 10**7]:
        p_mppipe_out, p_mppipe_in = mp.Pipe()
        reader_p = td.Thread(target=reader_pipe, args=((p_mppipe_out),))
        reader_p.start()
        _start = time.time()
        for ii in range(0, count):
            p_mppipe_in.send(ii)
        p_mppipe_in.send('DONE')
        reader_p.join()
        print(f"Sending {count} numbers to mp.Pipe() took {(time.time() - _start)*1e3:.3f} ms")

    # second: mp.Queue
        p_mpqueue  = mp.Queue()
        reader_p = td.Thread(target=reader_queue, args=((p_mpqueue),))
        reader_p.start()
        _start = time.time()
        for ii in range(0, count):
            p_mpqueue.put(ii)
        p_mpqueue.put('DONE')
        reader_p.join()
        print(f"Sending {count} numbers to mp.Queue() took {(time.time() - _start)*1e3:.3f} ms")

    # third: queue.Queue
        p_queue = queue.Queue()
        reader_p = td.Thread(target=reader_queue, args=((p_queue),))
        reader_p.start()
        _start = time.time()
        for ii in range(0, count):
            p_queue.put(ii)
        p_queue.put('DONE')
        reader_p.join()
        print(f"Sending {count} numbers to queue.Queue() took {(time.time() - _start)*1e3:.3f} ms")

    # fourth: queue.SimpleQueue
        p_squeue = queue.SimpleQueue()
        reader_p = td.Thread(target=reader_queue, args=((p_squeue),))
        reader_p.start()
        _start = time.time()
        for ii in range(0, count):
            p_squeue.put(ii)
        p_squeue.put('DONE')
        reader_p.join()
        print(f"Sending {count} numbers to queue.SimpleQueue() took {(time.time() - _start)*1e3:.3f} ms")