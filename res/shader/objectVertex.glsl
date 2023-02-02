#version 330 core

uniform mat4 transformationMatrix;
uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;

layout (location = 0) in vec3 vertexPos;
layout (location = 1) in vec3 vertexNormal;
layout (location = 2) in vec3 vertexColor;

out float shade;
out vec3 color;

void main() {
  vec3 lightVec = normalize(vec3(1, 1, 1));
  shade = dot(lightVec, vertexNormal)/2+0.5;
  color = vertexColor;

  vec4 worldPos = transformationMatrix * vec4(vertexPos, 1.0);
  vec4 relPos = viewMatrix * worldPos;
  vec4 screenPos = projectionMatrix*relPos;
  gl_Position = screenPos;
}