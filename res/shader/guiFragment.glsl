#version 400 core

uniform sampler2D uTextures[8];

in vec4 fColor;
in vec2 fTexCoords;
in float fTexID;

out vec4 color;

void main() {
	if(fTexID >= 0){
		// color = fColor * texture(uTextures[int(fTexID)], fTexCoords);
		color = fColor;
	}else{
		color = fColor;
	}
}