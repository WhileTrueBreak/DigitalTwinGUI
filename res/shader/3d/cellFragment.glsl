#version 400 core

// shader outputs
layout (location = 0) out vec4 frag;

uniform vec2 texture_dim;
in vec2 texPos;

uniform sampler2D screen;
uniform usampler2D picking;

void main() {

	ivec2 coords = ivec2(gl_FragCoord.xy);

	uvec2 v = texelFetch(picking, coords, 0).xy;

	if(v.y == 0){
		frag = vec4(0,0,1,1);
	}
	if(v.y == 1){
		frag = vec4(0,1,0,1);
	}
	if(v.y == 2){
		frag = vec4(0,1,1,1);
	}
	if(v.y == 3){
		frag = vec4(1,0,0,1);
	}
	if(v.y == 4){
		frag = vec4(1,0,1,1);
	}

}