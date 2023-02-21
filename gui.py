#!/usr/bin/env python3
import nest_asyncio

from window import *
from scenes.CamScene import *
from scenes.KukaScene import *
from scenes.BadApple import *
from asset import *

nest_asyncio.apply()

window = Window((800, 800), 'hello world', fullscreen=False, resizeable=True)

scene3 = CamScene(window, 'Cam1')
scene3.createUi()
scene4 = KukaScene(window, '3d model')
scene4.createUi()
# scene5 = BadApple(window, 'bad apple')
# scene5.createUi()

window.scenes.append(scene3)
window.scenes.append(scene4)
# window.scenes.append(scene5)

window.createUi()
window.run()
