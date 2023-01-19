#!/usr/bin/env python3
from pygame_gui.elements.ui_text_box import UITextBox

import window
import scenes

window = window.Window((1000, 600), 'hello world')
window.setBGColor('#FF9999')

scene1 = scenes.AirPScene(window, 'AP1', 41, 1)
scene1.createUi()

window.scenes.append(scene1)
window.createUi()

window.run()