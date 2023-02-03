#!/usr/bin/env python3
from opcua import Opcua
from window import *
from scenes.CamScene import *

import nest_asyncio
from asset import *

nest_asyncio.apply()

window = Window((1600, 1000), 'hello world')

scene3 = CamScene(window, 'Cam1')
scene3.createUi()

window.scenes.append(scene3)

window.createUi()
window.run()
