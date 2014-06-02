#version 330
#extension GL_ARB_shading_language_420pack: enable

uniform vec3 light_position;
uniform bool light_isdir = false;
uniform vec3 light_color;
uniform float light_dist;
uniform mat4 light_spersmat;
layout(binding = 4) uniform sampler2D light_shadowmap;

layout(binding = 0) uniform sampler2D target0; // rgb: albedo a: UNUSED
layout(binding = 1) uniform sampler2D target1; // rg: normals
layout(binding = 2) uniform sampler2D target2; // rgb: fresnel a: roughness
layout(binding = 3) uniform sampler2D target3; // r32: depth

in vec2 texcoord;
in vec4 vertex;

out vec3 out_color;

vec3 decode_normal(vec2 enorm)
{
	vec2 fenc = enorm * vec2(4.0) - vec2(2.0);
	float f = dot(fenc, fenc);
	float g = sqrt(1.0 - f / 4.0);
	vec3 n;
	n.xy = fenc * vec2(g);
	n.z = 1.0 - f / 2.0;
	return n;
}

vec3 decode_position(float depth)
{
	vec3 view_ray = normalize(vertex.xyz);
	return view_ray * depth;
}

vec3 fresnel(vec3 cspec, vec3 l, vec3 h)
{
	return cspec + (1.0 - cspec) * pow((1.0 - dot(l, h)), 5.0);
}

float distf(float a, vec3 n, vec3 h)
{
	// GGX
	float a2 = a*a;
	float NoH2 = pow(dot(n, h), 2.0);
	return a2 / (4.0 * pow((NoH2 *(a2 - 1.0) + 1.0), 2.0));
}

float visibility(float a, vec3 n, vec3 l, vec3 v)
{
	// Schlick with k = a/2
	float k = pow(a + 1.0, 2.0) / 8.0;
	float NoV = dot(n, v);
	float NoL = dot(n, l);
	float gv = NoV * (1.0 - k) + k;
	float gl = NoL * (1.0 - k) + k;
	return 1.0 / (4.0*gv*gl);
}

float test_shadowbuf_vsm(vec3 rco, float shadowbias, float bleedbias)
{
	float result = 1.0;
	vec4 co = light_spersmat*vec4(rco, 1.0);
	co = co * 0.5 + 0.5;

	if (co.w > 0.0 && co.x > 0.0 && co.x/co.w < 1.0 && co.y > 0.0 && co.y/co.w < 1.0) {
		vec2 moments = textureProj(light_shadowmap, co).rg;
		float dist = co.z/co.w;
		float p = 0.0;

		if(dist <= moments.x)
			p = 1.0;

		float variance = moments.y - (moments.x*moments.x);
		variance = max(variance, shadowbias/10.0);

		float d = moments.x - dist;
		float p_max = variance / (variance + d*d);

		// Now reduce light-bleeding by removing the [0, x] tail and linearly rescaling (x, 1]
		p_max = clamp((p_max-bleedbias)/(1.0-bleedbias), 0.0, 1.0);

		result = max(p, p_max);
	}

	return result;
}

void main()
{
	vec3 albedo = pow(texture(target0, texcoord).rgb, vec3(2.2));
	vec3 N = decode_normal(texture(target1, texcoord).rg);
	vec3 V = decode_position(texture(target3, texcoord).r);

	vec4 sdata = texture(target2, texcoord);
	vec3 c_spec = sdata.rgb;
	float roughness = sdata.a;
	vec3 E = normalize(-V);

	vec3 L;
	float attenuation;
	if (light_isdir) {
		L = -light_position;
		attenuation = 1.0;
		attenuation = test_shadowbuf_vsm(V, 0.001, 0.0);
	}
	else {
		L = light_position - V;
		float dist = length(L);
		attenuation = light_dist/(light_dist + dist*dist);
		attenuation *= max((light_dist - dist), 0.0)/light_dist;
	}

	L = normalize(L);

	vec3 H = normalize(L+E);

	float NoL = dot(N, L);

	if (light_isdir)
		NoL = pow(NoL * 0.5 + 0.5, 2.0);
	else
		NoL = max(NoL, 0.0);

	vec3 c_light = attenuation * NoL * light_color;

	vec3 specular = fresnel(c_spec, L, H);
	specular *= c_light;
	specular *= distf(roughness, N, H);
	specular *= visibility(roughness, N, L, E);

	vec3 diffuse = c_light;// * (vec3(1.0) - fresnel(c_spec, N, L));

	out_color = albedo * diffuse + specular;
}