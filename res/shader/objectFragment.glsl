#version 330 core

in float shade;
in vec3 color;

out vec4 fragColor;

void main() {
  float shadow = max(0.2, shade);
  fragColor = vec4(color.xyz*shadow, 1);
}