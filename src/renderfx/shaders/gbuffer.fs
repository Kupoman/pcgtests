#version 330
#extension GL_ARB_shading_language_420pack: enable

in vec2 texcoord;
in vec3 normal;
in vec4 vertex;


layout(binding = 0) uniform sampler2D albedo_map;

layout(location = 0) out vec4 target0; // rgb: albedo a: UNUSED
layout(location = 1) out vec2 target1; // rg: normals
layout(location = 2) out vec4 target2; // rgb: fresnel a: roughness
layout(location = 3) out float target3; // r32: depth

void main()
{
	target0.rgb = texture(albedo_map, texcoord).rgb;

	// Encode normals with Lambert Azimuth Equal-Area Projection
	vec3 n = normalize(normal);
	float f = sqrt(8.0 * n.z + 8.0);
	target1.rg = n.xy / f + vec2(0.5);

	target2.rgba = vec4(vec3(0.04), 0.8);

	target3 = length(vertex.xyz);
}