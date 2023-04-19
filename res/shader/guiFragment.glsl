#version 400 core

uniform sampler2D uTextures[8];

in vec4 fColor;
in vec2 fTexCoords;
in float fTexID;
flat in uint uiId;

layout (location = 0) out vec4 color;
layout (location = 1) out uvec3 picking;

void main() {
	if(fTexID >= -0.5){
		color = fColor * texture(uTextures[int(fTexID)], fTexCoords);
	}else{
		color = fColor;
	}
	picking = uvec3(uiId+1,0,gl_PrimitiveID);
}