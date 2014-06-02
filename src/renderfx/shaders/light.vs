#version 330

uniform mat4 modelview_mat;
uniform mat4 proj_mat;
uniform mat4 inv_proj_mat;
uniform bool light_isdir;

layout(location=0) in vec4 in_vertex;
layout(location=1) in vec2 in_texcoord;

out vec2 texcoord;
out vec4 vertex;

void main()
{
	if (light_isdir) {
		gl_Position = in_vertex;
		texcoord = in_texcoord;
		vertex = inv_proj_mat * in_vertex;
	}
	else {
		vertex = modelview_mat * in_vertex;
		gl_Position = proj_mat * vertex;

		vec3 ndc = gl_Position.xyz/gl_Position.w;
		texcoord = ndc.xy * 0.5 + vec2(0.5);
	}
}