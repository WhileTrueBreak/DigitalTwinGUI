#version 330 compatibility
#include <compatibility.glsl>

uniform sampler2D accumTexture;

uniform sampler2D revealageTexture;

void main() {
    float  revealage = texelFetch(revealageTexture, gl_FragCoord.xy, 0).r;
    if (revealage == 1.0) {
        // Save the blending and color texture fetch cost
        discard; 
    }

    vec4 accum     = texelFetch(accumTexture, gl_FragCoord.xy, 0);

    vec3 averageColor = accum.rgb / max(accum.a, 0.00001);


    // dst' =  (accum.rgb / accum.a) * (1 - revealage) + dst * revealage
    gl_FragColor = float4(averageColor, 1.0 - revealage);
}
