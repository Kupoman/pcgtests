#version 330
#extension GL_ARB_shading_language_420pack: enable

layout(binding = 0) uniform sampler2D render_texture;

in vec2 texcoord;

out vec3 out_color;

void main()
{
	vec3 sample = texture(render_texture, texcoord).rgb;
	float i = max(max(sample.x, sample.y), sample.z);

	if (i > 1.0) {
		out_color = sample;
	}
	else
		out_color = vec3(0.0);
}