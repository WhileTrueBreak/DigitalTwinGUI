#version 400 core

// shader outputs
layout (location = 0) out vec4 accum;
layout (location = 1) out float reveal;
layout (location = 2) out uvec3 picking;

uniform sampler2D uTextures[32];
uniform uint batchId;

flat in uint objIndex;
in float shade;
in float texId;
in vec2 texCoord;
in vec4 color;

void main(){
	picking = uvec3(objIndex, batchId, gl_PrimitiveID+1);
	vec4 objColor = vec4(0,0,0,0);
	if(texId >= 0){
		vec4 textureColor = texture(uTextures[int(texId)], texCoord);
		vec4 baseColor = vec4(color.rgb*shade, color.a);
		objColor = vec4(textureColor.r*baseColor.r, textureColor.g*baseColor.r, textureColor.b*baseColor.b, baseColor.a);
	}else {
		objColor = vec4(color.rgb*shade, color.a);
	}

	// weight function
	float weight = clamp(pow(min(1.0, objColor.a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - gl_FragCoord.z * 0.9, 3.0), 1e-2, 3e3);
	
	// store pixel color accumulation
	accum = vec4(objColor.rgb * objColor.a, objColor.a) * weight;
	
	// store pixel revealage threshold
	reveal = objColor.a;
}