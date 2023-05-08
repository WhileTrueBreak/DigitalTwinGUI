#version 400 core

uniform sampler2D uTextures[%max_textures%];

in vec4 fColor;
in vec2 fTexCoords;
in float fTexID;
flat in uint fUiId;
// flat in vec2 nearestPos;
// in vec2 InterpNearestPos;

layout (location = 0) out vec4 color;
layout (location = 1) out uvec3 picking;

void main() {
	// float dist = distance(InterpNearestPos, nearestPos);
	// color = vec4(dist, 0, 0, 1);
	// if(dist < 0.1) discard;
	if(fTexID > -0.5){
		color = fColor * texture(uTextures[int(fTexID)], fTexCoords);
	}else{
		color = fColor;
	}
	picking = uvec3(fUiId+1,fUiId,gl_PrimitiveID);
}