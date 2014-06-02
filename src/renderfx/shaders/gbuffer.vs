#version 120

varying vec4 vertex;
varying vec3 normal;
varying vec2 texcoord;

void main()
{
	gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
	vertex = gl_ModelViewMatrix * gl_Vertex;
	normal = gl_NormalMatrix * gl_Normal;
	texcoord = gl_MultiTexCoord0.xy;
}