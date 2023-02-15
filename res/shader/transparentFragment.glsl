#version 400 core

// shader outputs
layout (location = 0) out vec4 accum;
layout (location = 1) out float reveal;

in vec4 objColor;

void main()
{
	// weight function
	float weight = clamp(pow(min(1.0, objColor.a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - gl_FragCoord.z * 0.9, 3.0), 1e-2, 3e3);
	
	// store pixel color accumulation
	accum = vec4(objColor.rgb * objColor.a, objColor.a) * weight;
	
	// store pixel revealage threshold
	reveal = objColor.a;
}