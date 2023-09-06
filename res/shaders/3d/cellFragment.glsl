#version 400 core

// shader outputs
layout (location = 0) out vec4 frag;
layout (location = 1) out uvec3 oPicking;

uniform vec2 texture_dim;
in vec2 texPos;

uniform sampler2D screen;
uniform usampler2D picking;

void main() {

	ivec2 coords = ivec2(gl_FragCoord.xy);

	uvec3 v0 = texelFetch(picking, coords, 0).xyz;
	oPicking = v0;

	uvec2 v1 = texelFetch(picking, ivec2(coords.x+1, coords.y), 0).xy;
	uvec2 v2 = texelFetch(picking, ivec2(coords.x-1, coords.y), 0).xy;
	uvec2 v3 = texelFetch(picking, ivec2(coords.x, coords.y+1), 0).xy;
	uvec2 v4 = texelFetch(picking, ivec2(coords.x, coords.y-1), 0).xy;

	float dist = max(max(length(v0.xy-v1), length(v0.xy-v2)),max(length(v0.xy-v3), length(v0.xy-v4)));

	if(dist > 0.01){
		frag = vec4(0,0,0,1);
	}else{
		frag = texelFetch(screen, coords, 0);
	}

}