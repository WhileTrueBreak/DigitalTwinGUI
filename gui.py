#!/usr/bin/env python3
from opcua import Opcua

import window
import scenes
import nest_asyncio

nest_asyncio.apply()

window = window.Window((1600, 1000), 'hello world')

opcua = Opcua()

scene1 = scenes.AirPScene(window, 'AP1', 41, 1, opcua)
scene1.createUi()
scene2 = scenes.AirPScene(window, 'AP2', 42, 2, opcua)
scene2.createUi()

window.scenes.append(scene1)
window.scenes.append(scene2)
window.createUi()

window.run()