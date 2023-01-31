#version 330 core

uniform vec3 baseColor;
out vec4 fragColor;
void main(){
	fragColor = vec4(baseColor.r, baseColor.g, baseColor.b, 1.0);
}
