#version 400 core

// shader inputs
layout (location = 0) in vec3 position;
layout (location = 1) in vec2 texCoord;

out vec2 texPos;

void main() {
	texPos = texCoord;
	gl_Position = vec4(position, 1.0f);
}