from threading import Thread
from mjpeg.client import MJPEGClient
from urllib.request import urlopen
from io import BytesIO

import time

def handler(signum, frame):
    raise Exception("Time is up")

class StreamContainer:
    def __init__(self):
        self.stream = None
    
    def getStream(self):
        stream = self.stream
        self.stream = None
        return stream
    
    def setStream(self, stream):
        self.stream = stream

def createMjpegThread(container, url, stop):
    t = Thread(target = MjpegConnection, args =(container, url, stop))
    t.start()
    return t

def MjpegConnection(container, url, stop):
    print(f'mjpeg thread started: {url}')
    connectionOpen = True
    try:
        urlopen(url, timeout=3)
    except:
        connectionOpen = False
        print('url timeout')
        stop = lambda:True
    
    if connectionOpen:
        try:
            client = MJPEGClient(url)
            bufs = client.request_buffers(1048576, 2)
            for b in bufs:
                client.enqueue_buffer(b)
            client.start()
        except:
            stop = lambda:True
    running = False
    start = time.time_ns()
    while not stop():
        if not running:
            if client.reconnects > 1:
                stop = lambda:True
            if client.frames == 0:
                time.sleep(0.1)
                continue
            else:
                running = True
        try:
            time.sleep(0.01)
            buf = client.dequeue_buffer(timeout=1)
            stream = BytesIO(buf.data)
            container.setStream(stream)
            client.enqueue_buffer(buf)
        except Exception as e:
            print('buffer error')
            stop = lambda:True
    if connectionOpen:
        client.stop()
    
    print(f'mjpeg thread stopped: {url}')
