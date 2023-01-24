#!/usr/bin/python3
import OpenGL.GL as GL
import pathlib
import sys

# Get the package directory
package_dir = str(pathlib.Path(__file__).resolve().parents[2])
# Add the package directory into sys.path if necessary
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from py3d.core.base import Base
from py3d.core.utils import Utils
from py3d.core.attribute import Attribute
from py3d.core.uniform import Uniform
from asset import *

class Example(Base):
    """ Enables the user to move a triangle using the arrow keys """
    def initialize(self):
        print("Initializing program...")
        # Initialize program #
        self.shaderRef = TEST_SHADER
        # render settings (optional) #
        # Specify color used when clearly
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        # Set up vertex array object #
        vao_ref = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(vao_ref)
        # Set up vertex attribute #
        position_data = [[ 0.0,  0.0,  1.0],
                         [ 0.1,  0.0,  -1.0],
                         [ 0.0,  0.1,  0.0]]
        self.vertex_count = len(position_data)
        position_attribute = Attribute('vec3', position_data)
        position_attribute.associate_variable(self.shaderRef, 'position')
        # Set up uniforms #
        self.translation = Uniform('vec3', [0.0, 0.0, 0.0])
        self.translation.locate_variable(self.shaderRef, 'translation')
        self.base_color = Uniform('vec3', [1.0, 1.0, 0.0])
        self.base_color.locate_variable(self.shaderRef, 'baseColor')
        # triangle speed, units per second
        self.speed = 0.5

    def update(self):
        """ Update data """
        distance = self.speed * self.delta_time
        if self.input.is_key_pressed('left'):
            self.translation.data[0] -= distance
        if self.input.is_key_pressed('right'):
            self.translation.data[0] += distance
        if self.input.is_key_pressed('down'):
            self.translation.data[1] -= distance
        if self.input.is_key_pressed('up'):
            self.translation.data[1] += distance
        # Reset color buffer with specified color
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glUseProgram(self.shaderRef)
        self.translation.upload_data()
        self.base_color.upload_data()
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.vertex_count)


# Instantiate this class and run the program
Example((800, 600), 'hello world').run()