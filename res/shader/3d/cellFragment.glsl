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

	if(v.x%7==0){
		frag = vec4(float(v.x)/80,0,0,1);
	}
	if(v.x%7==1){
		frag = vec4(0,float(v.x)/80,0,1);
	}
	if(v.x%7==2){
		frag = vec4(float(v.x)/80,float(v.x)/80,0,1);
	}
	if(v.x%7==3){
		frag = vec4(0,0,float(v.x)/80,1);
	}
	if(v.x%7==4){
		frag = vec4(float(v.x)/80,0,float(v.x)/80,1);
	}
	if(v.x%7==5){
		frag = vec4(0,float(v.x)/80,float(v.x)/80,1);
	}
	if(v.x%7==6){
		frag = vec4(float(v.x)/80,float(v.x)/80,float(v.x)/80,1);
	}
}