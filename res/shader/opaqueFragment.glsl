#version 400 core

// shader outputs
layout (location = 0) out vec4 frag;

in vec4 objColor;

void main() {
	frag = objColor;
}