from model import *
from mathHelper import *

from pathlib import Path
import OpenGL.GL as GL
import freetype

from queue import Queue
from threading import Thread

class Assets:
    INIT = False
    GUI_SHADER = None
    DEFAULT_SHADER = None
    TEST_SHADER = ''
    @staticmethod
    def init():
        if Assets.INIT: return
        Assets.TEXT_SHADER = Assets.linkShaders('res/shader/textureVertex.glsl', 'res/shader/textFragment.glsl')
        Assets.STREAM_SHADER = Assets.linkShaders('res/shader/textureVertex.glsl', 'res/shader/streamFragment.glsl')
        Assets.SOLID_SHADER = Assets.linkShaders('res/shader/solidVertex.glsl', 'res/shader/solidFragment.glsl')
        Assets.OBJECT_SHADER = Assets.linkShaders('res/shader/objectVertex.glsl', 'res/shader/objectFragment.glsl')

        Assets.VERA_FONT = Assets.loadFont('res/fonts/Vera.ttf', 48*64)
        Assets.MONACO_FONT = Assets.loadFont('res/fonts/MONACO.TTF', 48*64)
        Assets.FIRACODE_FONT = Assets.loadFont('res/fonts/FiraCode-Retina.ttf', 48*64)
        
        modelQueues = []
        modelQueues.append(Assets.loadModel('res/models/link_0.stl', Assets.OBJECT_SHADER, createTransformationMatrix(0, 0, 0, 0, 0, 0)))
        modelQueues.append(Assets.loadModel('res/models/link_1.stl', Assets.OBJECT_SHADER, createTransformationMatrix(0,0,-(0.36-0.1575), 0, 0, 0)))
        modelQueues.append(Assets.loadModel('res/models/link_2.stl', Assets.OBJECT_SHADER, createTransformationMatrix(0, 0, 0, 0, 0, 180)))
        modelQueues.append(Assets.loadModel('res/models/link_3.stl', Assets.OBJECT_SHADER, createTransformationMatrix(0,0,0.2045-0.42, 0, 0, 0)))
        modelQueues.append(Assets.loadModel('res/models/link_4.stl', Assets.OBJECT_SHADER, createTransformationMatrix(0, 0, 0, 0, 0, 0)))
        modelQueues.append(Assets.loadModel('res/models/link_5.stl', Assets.OBJECT_SHADER, createTransformationMatrix(0,0,0.1845-0.4, 0, 0, 180)))
        modelQueues.append(Assets.loadModel('res/models/link_6.stl', Assets.OBJECT_SHADER, createTransformationMatrix(0, 0, 0, 0, 0, 180)))
        modelQueues.append(Assets.loadModel('res/models/link_7.stl', Assets.OBJECT_SHADER, createTransformationMatrix(0, 0, 0, 0, 0, 0)))

        Assets.KUKA_MODEL = []
        Assets.KUKA_MODEL.append(modelQueues[0].get())
        Assets.KUKA_MODEL.append(modelQueues[1].get())
        Assets.KUKA_MODEL.append(modelQueues[2].get())
        Assets.KUKA_MODEL.append(modelQueues[3].get())
        Assets.KUKA_MODEL.append(modelQueues[4].get())
        Assets.KUKA_MODEL.append(modelQueues[5].get())
        Assets.KUKA_MODEL.append(modelQueues[6].get())
        Assets.KUKA_MODEL.append(modelQueues[7].get())

        floorVertices = [
            [-1.5,-1.5, 0.0],
            [ 1.5,-1.5, 0.0],
            [-1.5, 1.5, 0.0],
            [-1.5, 1.5, 0.0],
            [ 1.5,-1.5, 0.0],
            [ 1.5, 1.5, 0.0],
        ]
        Assets.FLOOR = Model(Assets.OBJECT_SHADER, vertices=floorVertices)

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
    @staticmethod
    def complieShader(shaderFile, shaderType):
        print(f'Compiling shader: {shaderFile}')
        shaderCode = Path(shaderFile).read_text()
        shaderRef = GL.glCreateShader(shaderType)
        GL.glShaderSource(shaderRef, shaderCode)
        GL.glCompileShader(shaderRef)
        compile_success = GL.glGetShaderiv(shaderRef, GL.GL_COMPILE_STATUS)
        if not compile_success:
            error_message = GL.glGetShaderInfoLog(shaderRef)
            GL.glDeleteShader(shaderRef)
            error_message = '\n' + error_message.decode('utf-8')
            raise Exception(error_message)
        return shaderRef
    @staticmethod
    def linkShaders(vertexShaderFile, fragmentShaderFile):
        vertRef = Assets.complieShader(vertexShaderFile, GL.GL_VERTEX_SHADER)
        fragRef = Assets.complieShader(fragmentShaderFile, GL.GL_FRAGMENT_SHADER)
        print(f'Linking shader: {vertexShaderFile} & {fragmentShaderFile}')
        programRef = GL.glCreateProgram()
        GL.glAttachShader(programRef, vertRef)
        GL.glAttachShader(programRef, fragRef)
        GL.glLinkProgram(programRef)
        link_success = GL.glGetProgramiv(programRef, GL.GL_LINK_STATUS)
        if not link_success:
            error_message = GL.glGetProgramInfoLog(programRef)
            GL.glDeleteProgram(programRef)
            error_message = '\n' + error_message.decode('utf-8')
            raise Exception(error_message)
            return
        return programRef
    @staticmethod
    def loadModel(file, shader, tmat):
        q = Queue()
        t = Thread(target = Assets.modelLoader, args =(q, file, shader, tmat))
        t.start()
        return q
    @staticmethod
    def modelLoader(q, file, shader, tmat):
        print(f'Loading model: {file}')
        q.put(Model(shader, file=file, transform=tmat))

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





