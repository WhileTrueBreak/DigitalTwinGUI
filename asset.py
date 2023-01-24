from pathlib import Path
from py3d.core.utils import Utils

GUI_FRAG = Path('./res/shader/guiFragment.glsl').read_text()
GUI_VERT = Path('./res/shader/guiVertex.glsl').read_text()
DEFAULT_FRAG = Path('./res/shader/defaultFragment.glsl').read_text()
DEFAULT_VERT = Path('./res/shader/defaultVertex.glsl').read_text()
TEST_FRAG = Path('./res/shader/testFragment.glsl').read_text()
TEST_VERT = Path('./res/shader/testVertex.glsl').read_text()

GUI_SHADER = Utils.initialize_program(GUI_VERT, GUI_FRAG)
DEFAULT_SHADER = Utils.initialize_program(DEFAULT_VERT, DEFAULT_FRAG)
TEST_SHADER = Utils.initialize_program(TEST_VERT, TEST_FRAG)