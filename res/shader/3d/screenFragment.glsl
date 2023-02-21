#version 400 core

uniform vec2 texture_dim;

// shader inputs
in vec2 texture_coords;

// shader outputs
layout (location = 0) out vec4 frag;

// screen image
uniform sampler2D screen;

void main(){

	frag = texture2D(screen, texture_coords);
	return;

	float step_u = 0.5 / texture_dim[0];
	float step_v = 0.5 / texture_dim[1];

	// read current pixel
	vec4 centerPixel = texture2D(screen, texture_coords);
	frag = centerPixel;

	// read nearest right pixel & nearest bottom pixel
	vec4 rightPixel  = texture2D(screen, texture_coords + vec2(step_u, 0.0));
	vec4 bottomPixel = texture2D(screen, texture_coords + vec2(0.0, step_v));

	// now manually compute the derivatives
	float _dFdX = length(rightPixel - centerPixel) / step_u;
	float _dFdY = length(bottomPixel - centerPixel) / step_v;
	float d = max(_dFdX, _dFdY);

	if(d > 110){
		frag = vec4(0,0,0,1);
	}

}