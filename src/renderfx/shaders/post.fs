#version 330
#extension GL_ARB_shading_language_420pack: enable

layout(binding = 0) uniform sampler2D render_texture;
// layout(binding = 1) uniform sampler2D bloom_texture;

in vec2 texcoord;

out vec4 out_color;

void main()
{
	vec3 sample = texture(render_texture, texcoord).rgb;

 	// if (max(max(sample.r, sample.g), sample.b) < 1.0) {
		// vec3 bloom = textureLod(bloom_texture, texcoord, 0).rgb;
		// bloom += textureLod(bloom_texture, texcoord, 1).rgb;
		// bloom += textureLod(bloom_texture, texcoord, 2).rgb;
		// bloom += textureLod(bloom_texture, texcoord, 3).rgb;
		// // bloom += textureLod(bloom_texture, texcoord, 4).rgb;
		// bloom /= 4.0;
		// sample += bloom;
	// }
	sample = max(vec3(0), sample - vec3(0.004));
	sample = (sample * (vec3(6.2) * sample + vec3(0.5))) / (sample * (vec3(6.2) * sample + vec3(1.7)) + vec3(0.06));


	out_color.rgb = sample;
	out_color.a = 1.0;
	// out_color.a = dot(vec3(0.30, 0.59, 0.11), sample);
}