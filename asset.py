import os
import cv2
from PIL import Image

from pathlib import Path
import OpenGL.GL as GL
import freetype

from queue import Queue
from threading import Thread

import time

from utils.model import *
from utils.mathHelper import *
from utils.sprite import Sprite
from utils.timing import *
from utils.characterSlot import CharacterSlot

from constants import Constants

import sys

from colorama import Fore, Back, Style

class Assets:
    
    INIT = False

    @staticmethod
    @timing
    def init():
        # require python 3.10+
        if sys.version_info < (3,10,0):
            raise Exception('Python 3.10.0+ required')

        if Assets.INIT: return

        Assets.KUKA_IIWA14_MODEL = [None]*8
        Assets.KUKA_IIWA14_MODEL[0] = Assets.loadModelFile('res/models/iiwa14/visual/link_0.stl', createTransformationMatrix(0, 0, 0, 0, 0, 0))
        Assets.KUKA_IIWA14_MODEL[1] = Assets.loadModelFile('res/models/iiwa14/visual/link_1.stl', createTransformationMatrix(0,0,-(0.36-0.1575), 0, 0, 0))
        Assets.KUKA_IIWA14_MODEL[2] = Assets.loadModelFile('res/models/iiwa14/visual/link_2.stl', createTransformationMatrix(0, 0, 0, 0, 0, 180))
        Assets.KUKA_IIWA14_MODEL[3] = Assets.loadModelFile('res/models/iiwa14/visual/link_3.stl', createTransformationMatrix(0,0,0.2045-0.42, 0, 0, 0))
        Assets.KUKA_IIWA14_MODEL[4] = Assets.loadModelFile('res/models/iiwa14/visual/link_4.stl', createTransformationMatrix(0, 0, 0, 0, 0, 0))
        Assets.KUKA_IIWA14_MODEL[5] = Assets.loadModelFile('res/models/iiwa14/visual/link_5.stl', createTransformationMatrix(0,0,0.1845-0.4, 0, 0, 180))
        Assets.KUKA_IIWA14_MODEL[6] = Assets.loadModelFile('res/models/iiwa14/visual/link_6.stl', createTransformationMatrix(0, 0, 0, 0, 0, 180))
        Assets.KUKA_IIWA14_MODEL[7] = Assets.loadModelFile('res/models/iiwa14/visual/link_7.stl', createTransformationMatrix(0, 0, 0, 0, 0, 0))

        Assets.GRIPPER = Assets.loadModelFile('res/models/gripper/2F140.stl', createTransformationMatrix(0, 0, 0, 0, 0, 90))
        Assets.KUKA_BASE = Assets.loadModelFile('res/models/Objects/FlexFellow.STL', createTransformationMatrix(0, 0, -0.926, 0, 0, 0))

        Assets.TABLE_CUSTOM = Assets.loadModelFile('res/models/Objects/Benchtop_Custom.stl')
        Assets.TABLE_RECT = Assets.loadModelFile('res/models/Objects/Benchtop_Rectangle.STL')
        Assets.TABLE_SQUARE = Assets.loadModelFile('res/models/Objects/Benchtop_Square.STL')

        Assets.TUBE_INSIDE = Assets.loadModelFile('res/models/tube/tube_inside.stl', createTransformationMatrix(0,0,0,0,90,0))
        Assets.TUBE_OUTSIDE = Assets.loadModelFile('res/models/tube/tube_outside.stl', createTransformationMatrix(0,0,0,0,90,0))
        Assets.TUBE_HOLDER = Assets.loadModelFile('res/models/tube/tube_holder.stl')

        Assets.BAR_STOOL = Assets.loadModelFile('res/models/Expo/BarStool.stl', createTransformationMatrix(0, 0, 0, 0, 0, 0))
        Assets.COUNTER = Assets.loadModelFile('res/models/Expo/Counter.stl', createTransformationMatrix(0, 0, 0, 0, 0, 0))
        Assets.TABLE = Assets.loadModelFile('res/models/Expo/RoundTable.stl', createTransformationMatrix(0, 0, 0, 0, 0, 0))
        Assets.TVSCREEN = Assets.loadModelFile('res/models/Expo/TvScreen.stl', createTransformationMatrix(0, 0, 0, 0, 0, 0))
        Assets.KUKA_FLEX = Assets.loadModelFile('res/models/Expo/KukaFlex.stl', np.matmul(createTransformationMatrix(9, -8.4075, -0.89, 0, 0, 0), createScaleMatrix(0.001, 0.001, 0.001)))

        Assets.AMW_LEFT_TEX = Assets.loadTexture('res/textures/AMW_LEFT.jpg', flipX=True, flipY=True)
        Assets.AMW_RIGHT_TEX = Assets.loadTexture('res/textures/AMW_RIGHT.jpg', flipX=False, flipY=True)
        Assets.AMW_MID_TEX = Assets.loadTexture('res/textures/AMW_MID.jpg', flipX=True, flipY=True)

        Assets.DRAGON = Assets.loadModelFile('res/models/dragon.obj', createScaleMatrix(0.01, 0.01, 0.01).dot(createTransformationMatrix(0,0,0,90,0,0)))
        Assets.POLE = Assets.loadModelFile('res/models/pole.stl', createScaleMatrix(10, 10, 10))

        Assets.ENDER3_3D_PRINTER = Assets.loadModelFile('res/models/Objects/Ender3-V2.STL')
        Assets.SHELF = Assets.loadModelFile('res/models/Objects/Shelving1.stl', createTransformationMatrix(0, 0, 0, 90, 0, 0))

        Assets.BAD_APPLE_VID = Assets.loadVideo('res/videos/badapple.mp4')
        Assets.HAMSTER = Assets.loadVideo('res/videos/hamster.gif')

        Assets.CUBE_TEX = Assets.loadTexture('res/textures/cube.jpg', flipY=True)
        
        Assets.LEFT_ARROW = Assets.loadTexture('res/textures/arrow.png')
        Assets.UP_ARROW = Assets.loadTexture('res/textures/arrow.png', rot=90)
        Assets.RIGHT_ARROW = Assets.loadTexture('res/textures/arrow.png', flipX=True)
        Assets.DOWN_ARROW = Assets.loadTexture('res/textures/arrow.png', rot=270)

        Assets.TEXT_SHADER = Assets.linkShaders('res/shaders/ui/textureVertex.glsl', 'res/shaders/ui/textFragment.glsl')
        Assets.GUI_SHADER = Assets.linkShaders('res/shaders/ui/guiVertex.glsl', 'res/shaders/ui/guiFragment.glsl')
        Assets.SCREEN_SHADER = Assets.linkShaders('res/shaders/ui/screenVertex.glsl', 'res/shaders/ui/screenFragment.glsl')

        Assets.OPAQUE_SHADER = Assets.linkShaders('res/shaders/3d/objectVertex.glsl', 'res/shaders/3d/opaqueFragment.glsl')
        Assets.TRANSPARENT_SHADER = Assets.linkShaders('res/shaders/3d/objectVertex.glsl', 'res/shaders/3d/transparentFragment.glsl')
        Assets.COMPOSITE_SHADER = Assets.linkShaders('res/shaders/3d/compositeVertex.glsl', 'res/shaders/3d/compositeFragment.glsl')
        Assets.CELL_SHADER = Assets.linkShaders('res/shaders/3d/compositeVertex.glsl', 'res/shaders/3d/cellFragment.glsl')

        Assets.VERA_FONT = Assets.loadFont('res/fonts/Vera.ttf')
        Assets.MONACO_FONT = Assets.loadFont('res/fonts/MONACO.TTF')
        Assets.FIRACODE_FONT = Assets.loadFont('res/fonts/FiraCode-Retina.ttf')
        Assets.ARIAL_FONT = Assets.loadFont('res/fonts/ARIALNB.TTF',48*64)

        Assets.OMNIMOVE = Assets.loadModelFile('res/models/omnimove/KMP200.stl', np.matmul(createTransformationMatrix(0, 0, -0.7, 0, 0, 0), createScaleMatrix(0.001, 0.001, 0.001)))
        Assets.OMNIMOVE_CHARGER = Assets.loadModelFile('res/models/omnimove/KMP200_Charger.stl')

        floorVertices = [
            [0,0,0],[1,0,0],[0,1,0],
            [0,1,0],[1,0,0],[1,1,0],
            # [0,0,0],[0,1,0],[1,0,0],
            # [1,0,0],[0,1,0],[1,1,0],
        ]
        Assets.UNIT_WALL = Assets.loadModelVertices(vertices=floorVertices)
        screenVertices = [
            [0, 0, 0.0, 1, 0],[ 2*3/4, 0, 0.0, 1, 1],[ 0, 2, 0.0, 0, 0],
            [0, 2, 0.0, 0, 0],[ 2*3/4, 0, 0.0, 1, 1],[ 2*3/4, 2, 0.0, 0, 1],
            [0, 0, 0.0, 1, 0],[ 0, 2, 0.0, 0, 0],[ 2*3/4, 0, 0.0, 1, 1],
            [0, 2, 0.0, 0, 0],[ 2*3/4, 2, 0.0, 0, 1],[ 2*3/4, 0, 0.0, 1, 1],
        ]
        Assets.SCREEN = Assets.loadModelVertices(vertices=screenVertices)
        screenVertices1 = [
            [0, 0, 0.0, 1, 0],[ 1, 0, 0.0, 1, 1],[ 0, 1, 0.0, 0, 0],
            [0, 1, 0.0, 0, 0],[ 1, 0, 0.0, 1, 1],[ 1, 1, 0.0, 0, 1],
            [0, 0, 0.0, 1, 0],[ 0, 1, 0.0, 0, 0],[ 1, 0, 0.0, 1, 1],
            [0, 1, 0.0, 0, 0],[ 1, 1, 0.0, 0, 1],[ 1, 0, 0.0, 1, 1],
        ]
        Assets.SCREENSQ = Assets.loadModelVertices(vertices=screenVertices1)

        Assets.INIT = True
    @staticmethod
    @timing
    def loadFont(fontFile, size=48*64):
        print(f'Loading font: {Fore.LIGHTMAGENTA_EX}{fontFile}{Style.RESET_ALL}')
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
    @timing
    def complieShader(shaderFile, shaderType):
        print(f'Compiling shader: {Fore.LIGHTMAGENTA_EX}{shaderFile}{Style.RESET_ALL}')
        shaderCode = Path(shaderFile).read_text()
        shaderCode = shaderCode.replace('%max_textures%', str(Constants.MAX_TEXTURE_SLOTS))
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
    @timing
    def linkShaders(vertexShaderFile, fragmentShaderFile):
        vertRef = Assets.complieShader(vertexShaderFile, GL.GL_VERTEX_SHADER)
        fragRef = Assets.complieShader(fragmentShaderFile, GL.GL_FRAGMENT_SHADER)
        print(f'Linking shader: {Fore.LIGHTMAGENTA_EX}{vertexShaderFile}{Style.RESET_ALL} & {Fore.LIGHTMAGENTA_EX}{fragmentShaderFile}{Style.RESET_ALL}')
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
    @timing
    def loadModelFile(file, tmat=np.identity(4)):
        print(f'Loading model: {Fore.LIGHTMAGENTA_EX}{file}{Style.RESET_ALL}')
        ext = os.path.splitext(file)[1].lower()
        models = None
        match ext:
            case '.stl':
                models = Model.fromSTL(file=file, transform=tmat)
            case '.obj':
                models = Model.fromOBJ(file=file, transform=tmat)
            case _:
                raise Exception(f'Unknown file type: {ext}')
        if len(models) > 1:
            return models
        return models[0]
    @staticmethod
    @timing
    def loadModelVertices(vertices):
        return Model.fromVertices(vertices)[0]
    @staticmethod
    @timing
    def loadTexture(file, flipX=False, flipY=False, rot=0):
        print(f'Loading texture: {Fore.LIGHTMAGENTA_EX}{file}{Style.RESET_ALL}')
        img = Image.open(file)
        if flipX:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if flipY:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        if rot == 90:
            img = img.transpose(Image.ROTATE_90)
        elif rot == 180:
            img = img.transpose(Image.ROTATE_180)
        elif rot == 270:
            img = img.transpose(Image.ROTATE_270)
        
        # imgData = np.array(list(img.getdata()), np.int8)
        imgData = np.asarray(img)

        texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
        GL.glTexEnvf(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_DECAL)
        if imgData.shape[2] == 3:
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, *img.size, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, imgData)
        elif imgData.shape[2] == 4:
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, *img.size, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, imgData)
        else:
            raise Exception(f'Unknown image shape: {imgData.shape}')

        sprite = Sprite.fromTexture(texture)
        return sprite
    @staticmethod
    @timing
    def loadVideo(file):
        print(f'Loading video: {Fore.LIGHTMAGENTA_EX}{file}{Style.RESET_ALL}')
        capture = cv2.VideoCapture(file)
        return capture
