#version 400 core

// shader outputs
layout (location = 0) out vec4 frag;

uniform vec2 texture_dim;
in vec2 texPos;

uniform sampler2D screen;
uniform sampler2D objects;

void main() {

	float step_u = 0.5 / texture_dim[0];
	float step_v = 0.5 / texture_dim[1];

    ivec2 iTexPos = ivec2(texPos[0]*texture_dim[0], texPos[1]*texture_dim[1]);

	vec4 centerPixel = texelFetch(objects, iTexPos, 0);

	vec4 rightPixel  = texelFetch(objects, iTexPos + ivec2(1, 0), 0);
	vec4 bottomPixel = texelFetch(objects, iTexPos + ivec2(0, 1), 0);
	vec4 leftPixel  = texelFetch(objects, iTexPos + ivec2(-1, 0), 0);
	vec4 topPixel = texelFetch(objects, iTexPos + ivec2(0, -1), 0);

	float _dFdXp = length(rightPixel.xy - centerPixel.xy);
	float _dFdYp = length(bottomPixel.xy - centerPixel.xy);
	float _dFdXn = length(leftPixel.xy - centerPixel.xy);
	float _dFdYn = length(topPixel.xy - centerPixel.xy);
	float d = _dFdXp + _dFdYp + _dFdXn + _dFdYn;
    
    vec4 sp = texture2D(screen, texPos);

    frag = vec4(centerPixel.x/10, centerPixel.y/10, 1, 1);

}