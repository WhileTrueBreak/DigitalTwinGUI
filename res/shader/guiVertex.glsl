#version 400 core
layout (location=0) in vec2 aPos;
layout (location=1) in vec4 aColor;
layout (location=2) in vec2 aTexCoords;
layout (location=3) in float aTexID;

out vec4 fColor;
out vec2 fTexCoords;
out float fTexID;

void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
    fColor = aColor;
    fTexCoords = aTexCoords;
    fTexID = aTexID;
}