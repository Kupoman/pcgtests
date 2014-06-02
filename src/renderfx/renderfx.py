import os
import sys

import bge

os.chdir(bge.logic.expandPath('//'))
sys.path.append("./renderfx")
from OpenGL.GL import *

from .deferred_shading import DeferredShader
from .post_processing import PostProcessor

class RenderFX:
	def __init__(self):
		self.deferred_shader = DeferredShader()
		self.post_processor = PostProcessor(depth_target=self.deferred_shader.depth_buffer)

_global_rfx = None
def init(cont):
	global _global_rfx

	_global_rfx = RenderFX()

	scene = bge.logic.getCurrentScene()
	_global_rfx.deferred_shader.add_objects(scene.objects+scene.objectsInactive,
		scene.active_camera)

	scene.pre_draw.insert(0, pre_draw)
	scene.post_draw.insert(0, post_draw)

def pre_draw():
	scene = bge.logic.getCurrentScene()
	# _global_rfx.post_processor.post_draw_capture()
	_global_rfx.deferred_shader.pre_draw()

def post_draw():
	scene = bge.logic.getCurrentScene()
	lights = scene.lights
	camera = scene.active_camera

	_global_rfx.post_processor.post_draw_capture()
	_global_rfx.deferred_shader.post_draw(lights, camera)
	_global_rfx.post_processor.post_draw_process()
