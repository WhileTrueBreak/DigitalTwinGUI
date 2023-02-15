#!/usr/bin/env python3

from window import *
from scenes.CamScene import *
from scenes.KukaScene import *

import nest_asyncio
from asset import *

nest_asyncio.apply()

window = Window((1600, 800), 'hello world', fullscreen=False)

scene3 = CamScene(window, 'Cam1')
scene3.createUi()
scene4 = KukaScene(window, '3d model')
scene4.createUi()

window.scenes.append(scene3)
window.scenes.append(scene4)

window.createUi()
window.run()
