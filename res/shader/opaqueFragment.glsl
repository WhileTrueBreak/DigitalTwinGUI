#version 400 core

// shader outputs
layout (location = 0) out vec4 frag;

uniform sampler2D uTextures[16];

in float shade;
in float texId;
in vec2 texCoord;
in vec4 color;

void main() {
	if(texId > -1){
		vec4 color = vec4(color.rgb*shade, color.a); 
		frag = color * vec4(texture(uTextures[int(texId)], texCoord).rgb, 1);
	}else {
		frag = vec4(color.rgb*shade, color.a);
	}
}