url = 'http://172.31.1.225:8080/?action=stream'

import io
import pygame
from urllib.request import urlopen
from mjpeg.client import MJPEGClient

from PIL import Image
from io import BytesIO

def pilImageToSurface(pilImage):
    return pygame.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode).convert()

pygame.init()

white = (255, 255, 255)
screen = pygame.display.set_mode((1600,400),  pygame.RESIZABLE )

client = MJPEGClient(url)
bufs = client.request_buffers(65536, 50)
for b in bufs:
    client.enqueue_buffer(b)
client.start()


while True:

    screen.fill(white)
    buf = client.dequeue_buffer()
    # print(buf.used)
    stream = BytesIO(buf.data)
    client.enqueue_buffer(buf)
    image = Image.open(stream).convert("RGB")
    stream.close()

    # image = pygame.image.load(image)
    image = pilImageToSurface(image)
    screen.blit(image, (0, 0))
    pygame.display.flip()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
