#version 430 core

// uniform mat4 transformationMatrix;
uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;

layout (std430, binding = 0) buffer transformationMatrices {
  mat4 TMAT[];
};

layout (location = 0) in vec3 vertexPos;
layout (location = 1) in vec3 vertexNormal;
layout (location = 2) in vec3 vertexColor;
layout (location = 3) in float tmatIndex;

out float shade;
out vec3 color;

void main() {
  int index = int(tmatIndex);

  vec3 lightVec1 = normalize(vec3(-0.5, -2, 1));
  vec3 lightVec2 = normalize(vec3(0.5, 2, 1));
  vec4 tnormal = TMAT[index] * vec4(vertexNormal,0.0);

  float shade1 = dot(lightVec1, tnormal.xyz)/2+0.5;
  float shade2 = dot(lightVec2, tnormal.xyz)/2+0.5;
  shade = max(shade1, shade2);

  color = vertexColor;

  vec4 worldPos = TMAT[index] * vec4(vertexPos, 1.0);
  vec4 relPos = viewMatrix * worldPos;
  vec4 screenPos = projectionMatrix*relPos;
  gl_Position = screenPos;
}

