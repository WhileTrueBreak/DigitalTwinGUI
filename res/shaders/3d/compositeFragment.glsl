#version 400 core

// shader outputs
layout (location = 0) out vec4 frag;
layout (location = 1) out uvec3 oPicking;

in vec2 texPos;

// color accumulation buffer
uniform sampler2D accum;

// revealage threshold buffer
uniform sampler2D reveal;


uniform usampler2D picking;

// epsilon number
const float EPSILON = 0.00001f;

// calculate floating point numbers equality accurately
bool isApproximatelyEqual(float a, float b)
{
	return abs(a - b) <= (abs(a) < abs(b) ? abs(b) : abs(a)) * EPSILON;
}

// get the max value between three values
float max3(vec3 v) 
{
	return max(max(v.x, v.y), v.z);
}

void main() {
	// fragment coordination
	ivec2 coords = ivec2(gl_FragCoord.xy);
	// frag = vec4(float(coords.x)/1000, float(coords.y)/1000, 0, 1);
	// return;
	uvec3 v = texelFetch(picking, coords, 0).xyz;
	oPicking = v;
	
	// fragment revealage
	float revealage = texelFetch(reveal, coords, 0).r;

	// save the blending and color texture fetch cost if there is not a transparent fragment
	if (isApproximatelyEqual(revealage, 1.0f)) 
		discard;
 
	// fragment color
	vec4 accumulation = texelFetch(accum, coords, 0);

	// suppress overflow
	if (isinf(max3(abs(accumulation.rgb)))) 
		accumulation.rgb = vec3(accumulation.a);

	// prevent floating point precision bug
	vec3 average_color = accumulation.rgb / max(accumulation.a, EPSILON);

	// blend pixels
	frag = vec4(average_color, 1.0f - revealage);
}