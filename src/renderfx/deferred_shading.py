import os

from OpenGL.GL import *
from OpenGL.GL.ARB.texture_rg import *

import bge
import mathutils

from .shaders import Shader
from .shapes import draw_sphere


CLIP_SIZE = 40
CLIP_START = 15
CLIP_END= 80


AMBIENT_LIGHT = (0.0, 0.0, 0.0, 0.0)


class DeferredShader:
	def __init__(self):
		self.gbuffer_src = []
		with open("renderfx/shaders/gbuffer.vs") as vert:
			self.gbuffer_src.append(vert.read())
		with open("renderfx/shaders/gbuffer.fs") as frag:
			self.gbuffer_src.append(frag.read())
		self.gbuffer_src.append(True)

		self.fbo = glGenFramebuffers(1)
		self.textures = glGenTextures(4)
		self.depth_buffer = glGenRenderbuffers(1)
		self.width = bge.render.getWindowWidth()
		self.height = bge.render.getWindowHeight()
		self._resize_fbo()

		self.light_prog = Shader("light.vs", "light.fs")
		self.shadow_texture = 0

		self.mat_cache = {}

		self._delete_framebuffers = glDeleteFramebuffers
		self._delete_textures = glDeleteTextures

	def __del__(self):
		self._delete_framebuffers(1, [self.fbo])
		self._delete_textures(self.textures)

	def _resize_fbo(self):
		glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

		glBindRenderbuffer(GL_RENDERBUFFER, self.depth_buffer)
		glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT32, \
			self.width, self.height)
		glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, \
			GL_RENDERBUFFER, self.depth_buffer)
		glBindRenderbuffer(GL_RENDERBUFFER, 0)

		iformats = (GL_RGBA8, GL_RG16, GL_RGBA8, GL_R32F)
		formats = (GL_RGBA, GL_RG, GL_RGBA, GL_RED)
		types = (GL_UNSIGNED_BYTE, GL_UNSIGNED_SHORT, GL_UNSIGNED_BYTE, GL_FLOAT)

		for i in range(len(self.textures)):
			glBindTexture(GL_TEXTURE_2D, self.textures[i])
			glTexImage2D(GL_TEXTURE_2D, 0, iformats[i], self.width, self.height,\
				0, formats[i], types[i], None)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0+i,\
				GL_TEXTURE_2D, self.textures[i], 0)

		draw_buffers = [GL_COLOR_ATTACHMENT0 + i for i in range(4)]
		glDrawBuffers(4, draw_buffers)
		status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
		if status != GL_FRAMEBUFFER_COMPLETE:
			print("GBuffer FBO incomplete!")

	def add_objects(self, objects, camera):
		for object in objects:
			for mesh in object.meshes:
				for material in mesh.materials:
					if material not in self.mat_cache:
						shader = material.getShader()
						shader.setSource(*self.gbuffer_src)
						shader.setSampler("albedo_map", 0)
						self.mat_cache[material] = True

	def pre_draw(self):
		glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
		glDisable(GL_SCISSOR_TEST)

		width = bge.render.getWindowWidth()
		height = bge.render.getWindowHeight()

		if width != self.width or height != self.height:
			self.width = width
			self.height = height
			self._resize_fbo()

		glViewport(0, 0, width, height)
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	def _draw_lights(self, lights, camera):
		if self.shadow_texture == 0:
			for i in range(self.textures[0]):
				try:
					glBindTexture(GL_TEXTURE_2D, i)
				except OpenGL.error.GLError:
					continue
				format = glGetTexLevelParameteriv(GL_TEXTURE_2D, \
					0, GL_TEXTURE_INTERNAL_FORMAT)
				size = glGetTexLevelParameteriv(GL_TEXTURE_2D, \
					0, GL_TEXTURE_WIDTH)
				if format == GL_RG32F and size == 1024:
					self.shadow_texture = i
					break
			else:
				self.shadow_texture = -1
		proj_mat = camera.projection_matrix
		inv_proj_mat = proj_mat.inverted()
		proj_mat = [i for col in proj_mat.col for i in col]
		inv_proj_mat = [i for col in inv_proj_mat.col for i in col]
		view_mat = camera.modelview_matrix
		glUseProgram(self.light_prog.program)
		for i in range(4):
			glActiveTexture(GL_TEXTURE0+i)
			glBindTexture(GL_TEXTURE_2D, self.textures[i])

		loc = self.light_prog.get_location("inv_proj_mat")
		glUniformMatrix4fv(loc, 1, GL_FALSE, inv_proj_mat)

		loc = self.light_prog.get_location("proj_mat")
		glUniformMatrix4fv(loc, 1, GL_FALSE, proj_mat)

		glEnable(GL_BLEND)
		glEnable(GL_CULL_FACE)
		glDepthMask(GL_FALSE)
		glBlendEquation(GL_FUNC_ADD)
		glBlendFunc(GL_ONE, GL_ONE)
		glDisable(GL_DEPTH_TEST)

		for light in lights:
			if light.type == light.SUN:
				loc = self.light_prog.get_location("light_isdir")
				glUniform1i(loc, 1)
				glActiveTexture(GL_TEXTURE4)
				if self.shadow_texture > 0:
					lproj = mathutils.Matrix.Identity(4)
					lproj[0][0] = lproj[1][1] = 1.0 / CLIP_SIZE
					lproj[2][2] = -2.0 / (CLIP_END - CLIP_START)
					lproj[2][3] = -(CLIP_END + CLIP_START)/(CLIP_END-CLIP_START)
					spersmat = lproj
					spersmat = spersmat * light.worldTransform.inverted()
					spersmat = spersmat * view_mat.inverted()
					spersmat = [i for col in spersmat.col for i in col]
					loc = self.light_prog.get_location("light_spersmat")
					glUniformMatrix4fv(loc, 1, GL_FALSE, spersmat)
					glBindTexture(GL_TEXTURE_2D, self.shadow_texture)
					loc = self.light_prog.get_location("light_shadowmap")
					glUniform1i(loc, 4);
				else:
					glBindTexture(GL_TEXTURE_2D, 0)
				lori = view_mat.to_3x3() * light.worldOrientation
				lpos = lori * mathutils.Vector((0, 0, -1))
			else:
				loc = self.light_prog.get_location("light_isdir")
				glUniform1i(loc, 0)
				lpos = light.worldPosition
				lpos = view_mat * lpos
			loc = self.light_prog.get_location("light_position")
			glUniform3f(loc, *lpos)

			lcolor = mathutils.Vector(light.color)
			lcolor *= light.energy
			loc = self.light_prog.get_location("light_color")
			glUniform3f(loc, *lcolor)

			loc = self.light_prog.get_location("light_dist")
			glUniform1f(loc, light.distance)

			if light.type == light.SUN:
				# glDisable(GL_DEPTH_TEST)
				glBegin(GL_TRIANGLE_FAN)
				glVertexAttrib2f(1, 1, 1)
				glVertexAttrib3f(0, 1, 1, -1);
				glVertexAttrib2f(1, 0, 1)
				glVertexAttrib3f(0, -1, 1, -1)
				glVertexAttrib2f(1, 0, 0)
				glVertexAttrib3f(0, -1, -1, -1)
				glVertexAttrib2f(1, 1, 0)
				glVertexAttrib3f(0, 1, -1, -1)
				glEnd()
			else:
				# glEnable(GL_DEPTH_TEST)
				glCullFace(GL_FRONT)
				scale_mat = mathutils.Matrix.Scale(light.distance, 4)
				trans_mat = mathutils.Matrix.Translation(light.worldPosition)
				model_mat = trans_mat * scale_mat
				modelview_mat = view_mat * model_mat
				modelview_mat = [i for col in modelview_mat.col for i in col]
				loc = self.light_prog.get_location("modelview_mat")
				glUniformMatrix4fv(loc, 1, GL_FALSE, modelview_mat)
				draw_sphere()
				glCullFace(GL_BACK)

		glDisable(GL_BLEND)

	def post_draw(self, lights, camera):
		# glClearColor(0.0, 0.025, 0.05, 0.0)
		glClearColor(*AMBIENT_LIGHT)
		glClear(GL_COLOR_BUFFER_BIT)
		glDepthMask(GL_FALSE)
		self._draw_lights(lights, camera)