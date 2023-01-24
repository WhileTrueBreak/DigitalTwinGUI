from pathlib import Path
from py3d.core.base import Base
from py3d.core.utils import Utils
from py3d.core.attribute import Attribute

class Assets:
    GUI_FRAG = Path('./res/shader/guiFragment.glsl').read_text()
    GUI_VERT = Path('./res/shader/guiVertex.glsl').read_text()
    DEFAULT_FRAG = Path('./res/shader/defaultFragment.glsl').read_text()
    DEFAULT_VERT = Path('./res/shader/defaultVertex.glsl').read_text()
    TEST_FRAG = Path('./res/shader/testFragment.glsl').read_text()
    TEST_VERT = Path('./res/shader/testVertex.glsl').read_text()

    GUI_SHADER = None
    DEFAULT_SHADER = None
    TEST_SHADER = ''
    @staticmethod
    def init():
        # Assets.GUI_SHADER = Utils.initialize_program(Assets.GUI_VERT, Assets.GUI_FRAG)
        # Assets.DEFAULT_SHADER = Utils.initialize_program(Assets.DEFAULT_VERT, Assets.DEFAULT_FRAG)
        Assets.TEST_SHADER = Utils.initialize_program(Assets.TEST_VERT, Assets.TEST_FRAG)