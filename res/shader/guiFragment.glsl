#version 460 core

uniform sampler2D uTextures[8];

in vec4 fColor;
in vec2 fTexCoords;
in float fTexID;

out vec4 color;

void main() {
	if(fTexID > -1){
		color = fColor * texture(uTextures[int(fTexID)], fTexCoords);
	}else{
		color = fColor;
	}
	color = vec4(1,0,0,1);
}