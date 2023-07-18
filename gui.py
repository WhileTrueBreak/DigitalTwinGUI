#!/usr/bin/env python3
import nest_asyncio

from window import *

from scenes.DigitalTwinLab import *
from scenes.testScene import *

from asset import *

from colorama import init as colorama_init

colorama_init(convert=True)

nest_asyncio.apply()

window = Window((1200, 800), 'Digital Twin GUI', fullscreen=False, resizeable=True, vsync=False)

labScene = DigitalTwinLab(window, 'Digital Twin Lab')
labScene.createUi()
testScene = TestScene(window, 'test')
testScene.createUi()

window.addScene(labScene)

window.createUi()
window.run()
