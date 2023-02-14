from threading import Thread
from mjpeg.client import MJPEGClient
from io import BytesIO

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
    try:
        client = MJPEGClient(url)
        bufs = client.request_buffers(65536, 50)
        for b in bufs:
            client.enqueue_buffer(b)
        client.start()
    except:
        pass
    
    while not stop():
        buf = client.dequeue_buffer()
        stream = BytesIO(buf.data)
        container.setStream(stream)
        client.enqueue_buffer(buf)
    client.stop()
    print(f'mjpeg thread stopped: {url}')
