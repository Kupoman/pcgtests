from OpenGL.GL import *

import bge

from .shaders import Shader

class PostProcessor:
	def __init__(self, depth_target=0):
		self.fbos = glGenFramebuffers(3)
		self.textures = glGenTextures(3)

		self.width = bge.render.getWindowWidth()
		self.height = bge.render.getWindowHeight()
		self.depth_target = depth_target
		self._resize_fbo()

		self.prog_post = Shader("post.vs", "post.fs")

		self._delete_framebuffers = glDeleteFramebuffers
		self._delete_textures = glDeleteTextures

	def __del__(self):
		self._delete_framebuffers(3, self.fbos)
		self._delete_textures(self.textures)

	def _resize_fbo(self):
		for i in range(3):
			glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[i])
			glBindTexture(GL_TEXTURE_2D, self.textures[i])
			filter = GL_LINEAR_MIPMAP_LINEAR if i ==2 else GL_NEAREST
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32F, self.width, self.height,\
				0, GL_RGB, GL_FLOAT, None)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)
			glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
			glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,\
				GL_TEXTURE_2D, self.textures[i], 0)
			glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, \
				GL_RENDERBUFFER, self.depth_target)
			status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
			if status != GL_FRAMEBUFFER_COMPLETE:
				print("Render FBO %d incomplete!" % i)

	def post_draw_capture(self):
		glBindFramebuffer(GL_FRAMEBUFFER, self.fbos[0])

		width = bge.render.getWindowWidth()
		height = bge.render.getWindowHeight()

		if width != self.width or height != self.height:
			self.width = width
			self.height = height
			self._resize_fbo()

		glPushAttrib(GL_VIEWPORT_BIT)
		glViewport(0, 0, width, height)

		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	def post_draw_process(self):
		glPopAttrib()
		glBindFramebuffer(GL_FRAMEBUFFER, 0)
		glEnable(GL_SCISSOR_TEST)
		glEnable(GL_DEPTH_TEST)

		glUseProgram(self.prog_post.program)
		glActiveTexture(GL_TEXTURE0)
		glBindTexture(GL_TEXTURE_2D, self.textures[0])
		glBegin(GL_QUADS)
		glTexCoord2i(1, 1)
		glVertex3i(1, 1, 1)
		glTexCoord2i(0, 1)
		glVertex3i(-1, 1, 1)
		glTexCoord2i(0, 0)
		glVertex3i(-1, -1, 1)
		glTexCoord2i(1, 0)
		glVertex3i(1, -1, 1)
		glEnd()

		glDepthMask(GL_TRUE)
		glUseProgram(0)