#version 330 core

in float shade;
in vec4 objColor;

layout(location = 0) out vec4 accum;
layout(location = 1) out float reveal;

float wFunc(vec4 color, float z){
    float weight = max(min(1.0, max(max(color.r, color.g), color.b) * color.a), color.a) * clamp(0.03 / (1e-5 + pow(z / 200, 4.0)), 1e-2, 3e3);
    return weight;
}

void main() {
    float z = gl_FragCoord.z / gl_FragCoord.w;
    vec4 color = vec4(objColor.rgb*shade, objColor.a);
    float weight = wFunc(color, z);
    accum = vec4(color.rgb * color.a, color.a) * weight;
    reveal = color.a;
}