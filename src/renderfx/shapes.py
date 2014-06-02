import ctypes

from OpenGL.GL import *


SPHERE_VERTICES = (ctypes.c_float * 126)(
	0.000000, 0.000000, -1.000000,
	0.723607, -0.525725, -0.447220,
	-0.276388, -0.850649, -0.447220,
	-0.894426, 0.000000, -0.447216,
	-0.276388, 0.850649, -0.447220,
	0.723607, 0.525725, -0.447220,
	0.276388, -0.850649, 0.447220,
	-0.723607, -0.525725, 0.447220,
	-0.723607, 0.525725, 0.447220,
	0.276388, 0.850649, 0.447220,
	0.894426, 0.000000, 0.447216,
	0.000000, 0.000000, 1.000000,
	-0.162456, -0.499995, -0.850654,
	0.425323, -0.309011, -0.850654,
	0.262869, -0.809012, -0.525738,
	0.850648, 0.000000, -0.525736,
	0.425323, 0.309011, -0.850654,
	-0.525730, 0.000000, -0.850652,
	-0.688189, -0.499997, -0.525736,
	-0.162456, 0.499995, -0.850654,
	-0.688189, 0.499997, -0.525736,
	0.262869, 0.809012, -0.525738,
	0.951058, -0.309013, 0.000000,
	0.951058, 0.309013, 0.000000,
	0.000000, -1.000000, 0.000000,
	0.587786, -0.809017, 0.000000,
	-0.951058, -0.309013, 0.000000,
	-0.587786, -0.809017, 0.000000,
	-0.587786, 0.809017, 0.000000,
	-0.951058, 0.309013, 0.000000,
	0.587786, 0.809017, 0.000000,
	0.000000, 1.000000, 0.000000,
	0.688189, -0.499997, 0.525736,
	-0.262869, -0.809012, 0.525738,
	-0.850648, 0.000000, 0.525736,
	-0.262869, 0.809012, 0.525738,
	0.688189, 0.499997, 0.525736,
	0.162456, -0.499995, 0.850654,
	0.525730, 0.000000, 0.850652,
	-0.425323, -0.309011, 0.850654,
	-0.425323, 0.309011, 0.850654,
	0.162456, 0.499995, 0.850654,
)

SPHERE_INDICES = (ctypes.c_ubyte * 240)(
	0, 13, 12,
	1, 13, 15,
	0, 12, 17,
	0, 17, 19,
	0, 19, 16,
	1, 15, 22,
	2, 14, 24,
	3, 18, 26,
	4, 20, 28,
	5, 21, 30,
	1, 22, 25,
	2, 24, 27,
	3, 26, 29,
	4, 28, 31,
	5, 30, 23,
	6, 32, 37,
	7, 33, 39,
	8, 34, 40,
	9, 35, 41,
	10, 36, 38,
	12, 14, 2,
	12, 13, 14,
	13, 1, 14,
	15, 16, 5,
	15, 13, 16,
	13, 0, 16,
	17, 18, 3,
	17, 12, 18,
	12, 2, 18,
	19, 20, 4,
	19, 17, 20,
	17, 3, 20,
	16, 21, 5,
	16, 19, 21,
	19, 4, 21,
	22, 23, 10,
	22, 15, 23,
	15, 5, 23,
	24, 25, 6,
	24, 14, 25,
	14, 1, 25,
	26, 27, 7,
	26, 18, 27,
	18, 2, 27,
	28, 29, 8,
	28, 20, 29,
	20, 3, 29,
	30, 31, 9,
	30, 21, 31,
	21, 4, 31,
	25, 32, 6,
	25, 22, 32,
	22, 10, 32,
	27, 33, 7,
	27, 24, 33,
	24, 6, 33,
	29, 34, 8,
	29, 26, 34,
	26, 7, 34,
	31, 35, 9,
	31, 28, 35,
	28, 8, 35,
	23, 36, 10,
	23, 30, 36,
	30, 9, 36,
	37, 38, 11,
	37, 32, 38,
	32, 10, 38,
	39, 37, 11,
	39, 33, 37,
	33, 6, 37,
	40, 39, 11,
	40, 34, 39,
	34, 7, 39,
	41, 40, 11,
	41, 35, 40,
	35, 8, 40,
	38, 41, 11,
	38, 36, 41,
	36, 9, 41,
)


class SphereData:
	def __init__(self):
		self.vao = glGenVertexArrays(1)
		glBindVertexArray(self.vao)

		self.vbo = glGenBuffers(1)
		glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
		size = len(SPHERE_VERTICES) * ctypes.sizeof(ctypes.c_float)
		glBufferData(GL_ARRAY_BUFFER, size, SPHERE_VERTICES, GL_STATIC_DRAW)

		glEnableVertexAttribArray(0)
		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

		self.ibo = glGenBuffers(1)
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
		size = len(SPHERE_INDICES) * ctypes.sizeof(ctypes.c_ubyte)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, size, SPHERE_INDICES, GL_STATIC_DRAW)

		glBindVertexArray(0)
		glBindBuffer(GL_ARRAY_BUFFER, 0)
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

		self._delete_buffers = glDeleteBuffers
		self._delete_vertexarrays = glDeleteVertexArrays

	def __del__(self):
		self._delete_buffers (1, self.vbo)
		self._delete_buffers (1, self.ibo)
		self._delete_vertexarrays(1, [self.vao])

	def draw(self):
		glBindVertexArray(self.vao)

		glDrawElements(GL_TRIANGLES, len(SPHERE_INDICES), GL_UNSIGNED_BYTE, None)

		glBindVertexArray(0)


G_SPHERE = None
def draw_sphere():
	global G_SPHERE
	if not G_SPHERE:
		G_SPHERE = SphereData()
	G_SPHERE.draw()

