#version 330 core

in float shade;
in vec4 objColor;

void main() {
  float shadow = max(0.2, shade);

  gl_FragColor = vec4(objColor.xyz*shadow, objColor.w);
}