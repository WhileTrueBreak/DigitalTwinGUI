#!/usr/bin/env python3
import nest_asyncio

from window import *

from scenes.KukaScene import *
from scenes.AMWExpo import *
from scenes.AMWExpo_R3 import *
from scenes.LimitTest import *

from asset import *

nest_asyncio.apply()

window = Window((1200, 800), 'Digital Twin GUI', fullscreen=False, resizeable=True, vsync=False)

scene0 = KukaScene(window, 'Digital Twin')
scene0.createUi()
# scene1 = AMWExpo(window, 'AMW Expo')
# scene1.createUi()
scene2 = AMWExpo_R3(window, 'AMW Expo')
scene2.createUi()
# scene3 = LimitScene(window, 'Cube World')
# scene3.createUi()

window.addScene(scene0)
# window.addScene(scene1)
window.addScene(scene2)
# window.addScene(scene3)

window.createUi()
window.run()
