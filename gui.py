#!/usr/bin/env python3
import nest_asyncio

from window import *
from scenes.CamScene import *
from scenes.KukaScene import *
from scenes.BadApple import *
from asset import *

nest_asyncio.apply()

window = Window((1200, 800), 'Digital Twin GUI', fullscreen=False, resizeable=True, vsync=False)

scene3 = CamScene(window, '3D Printers')
scene3.createUi()
scene4 = KukaScene(window, 'Digital Twin')
scene4.createUi()
# scene5 = BadApple(window, 'bad apple')
# scene5.createUi()

window.scenes.append(scene3)
window.scenes.append(scene4)
# window.scenes.append(scene5)

window.createUi()
window.run()
