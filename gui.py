#!/usr/bin/env python3
from opcua import Opcua

from window import *
import nest_asyncio
from asset import *

nest_asyncio.apply()

# Assets.init()

window = Window((1600, 1000), 'hello world')

# opcua = Opcua()

# # scene1 = scenes.AirPScene(window, 'AP1', 41, 1, opcua)
# # scene1.createUi()
# # scene2 = scenes.AirPScene(window, 'AP2', 42, 2, opcua)
# # scene2.createUi()
# # scene3 = scenes.CamScene(window, 'Cam1')
# # scene3.createUi()

# # window.scenes.append(scene1)
# # window.scenes.append(scene2)
# # window.scenes.append(scene3)

window.run()