#version 400 core

// shader outputs
layout (location = 0) out vec4 opaque;
layout (location = 1) out ivec3 picking;

uniform sampler2D uTextures[32];
uniform int batchId;

flat in int objIndex;
in float shade;
in float texId;
in vec2 texCoord;
in vec4 color;

void main() {
	// opaque = vec4(float(objIndex), float(batchId), float(gl_PrimitiveID), 1);
	// return;

	if(texId > -1){
		vec4 color = vec4(color.rgb*shade, color.a); 
		opaque = color * vec4(texture(uTextures[int(texId)], texCoord).rgb, 1);
	}else {
		opaque = vec4(color.rgb*shade, color.a);
	}
	picking = ivec3(objIndex, batchId, gl_PrimitiveID+1);
	// picking = uvec3(objIndex, batchId, 1);
}