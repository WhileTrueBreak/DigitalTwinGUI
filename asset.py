from pathlib import Path
from py3d.core.base import Base
from py3d.core.utils import Utils
from py3d.core.attribute import Attribute
import OpenGL.GL as GL
import freetype

class Assets:
    INIT = False

    

    GUI_SHADER = None
    DEFAULT_SHADER = None
    TEST_SHADER = ''
    @staticmethod
    def init():
        if Assets.INIT: return
        Assets.TEXT_FRAG = Path('./res/shader/textFragment.glsl').read_text()
        Assets.TEXT_VERT = Path('./res/shader/textVertex.glsl').read_text()
        Assets.TEST_FRAG = Path('./res/shader/testFragment.glsl').read_text()
        Assets.TEST_VERT = Path('./res/shader/testVertex.glsl').read_text()
        Assets.STREAM_FRAG = Path('./res/shader/streamFragment.glsl').read_text()
        Assets.STREAM_VERT = Path('./res/shader/streamVertex.glsl').read_text()

        Assets.TEXT_SHADER = Utils.initialize_program(Assets.TEXT_VERT, Assets.TEXT_FRAG)
        Assets.TEST_SHADER = Utils.initialize_program(Assets.TEST_VERT, Assets.TEST_FRAG)
        Assets.STREAM_SHADER = Utils.initialize_program(Assets.STREAM_VERT, Assets.STREAM_FRAG)

        Assets.VERA_FONT = Assets.loadFont('fonts/Vera.ttf', 48*64)
        Assets.MONACO_FONT = Assets.loadFont('fonts/MONACO.TTF', 48*64)
        Assets.FIRACODE_FONT = Assets.loadFont('fonts/FiraCode-Retina.ttf', 48*64)
        Assets.INIT = True
    
    @staticmethod
    def loadFont(fontFile, size=48*64):
        print(f'Loading font: {fontFile}')
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        characters = {}
        face = freetype.Face(fontFile)
        face.set_char_size(size)
        for i in range(0,128):
            face.load_char(chr(i))
            glyph = face.glyph

            #generate texture
            texture = GL.glGenTextures(1)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RED, glyph.bitmap.width, glyph.bitmap.rows, 0,
                        GL.GL_RED, GL.GL_UNSIGNED_BYTE, glyph.bitmap.buffer)

            #texture options
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

            #now store character for later use
            characters[chr(i)] = CharacterSlot(texture,glyph)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        return characters

class CharacterSlot:
    def __init__(self, texture, glyph):
        self.texture = texture
        self.ascender  = max(0, glyph.bitmap_top)
        self.descender = max(0, glyph.bitmap.rows-glyph.bitmap_top)
        self.textureSize = (max(0, glyph.bitmap.width), self.ascender + self.descender)

        if isinstance(glyph, freetype.GlyphSlot):
            self.bearing = (glyph.bitmap_left, glyph.bitmap_top)
            self.advance = glyph.advance.x
        elif isinstance(glyph, freetype.BitmapGlyph):
            self.bearing = (glyph.left, glyph.top)
            self.advance = None
        else:
            raise RuntimeError('unknown glyph type')