#version 330
#extension GL_ARB_shading_language_420pack: enable

layout(binding = 0) uniform sampler2D render_texture;

in vec2 texcoord;

out vec3 out_color;

uniform float strength = 1;

const float kernel[9] = float[9](
						1.0/16.0, 1.0/8.0, 1.0/16.0,
						1.0/8.0, 1.0/4.0, 1.0/8.0,
						1.0/16.0, 1.0/8.0, 1.0/16.0);

const vec2 offset[9] = vec2[9](
                        vec2(-1, 1), vec2(0, 1), vec2(1, 1),
                        vec2(-1, 0), vec2(0, 0), vec2(1, 0),
                        vec2(-1, -1), vec2(0, -1), vec2(1, -1)
                        );

void main(void)
{
	int i = 0;
	vec3 sum = vec3(0.0);
	vec2 size = textureSize(render_texture, 0);
    vec2 scale = vec2(strength) / size;
	for (; i < 9; i++) {
		sum += texture(render_texture, texcoord + scale*offset[i]).rgb * kernel[i];
	}
	
	out_color = sum;
}