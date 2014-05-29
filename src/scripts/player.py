import bge
import time
import mathutils
import math
import random

import scripts.bgui as bgui
import scripts.bgui.bge_utils as bgui_bge_utils

from scripts.bgui.gl_utils import *

from scripts.player_data import PlayerData
from scripts import input
import scripts.spells as Spells

ENCOUNTER_DISTANCE = 1.25

class HUDLayout(bgui_bge_utils.Layout):
	def __init__(self, sys, data):
		super().__init__(sys, data)

		self.dmap = data["dmap"]
		self.player = data["player"]
		self.map_texture = MapTexture(data["dmap"])
		self.map = bgui.Image(self, None, size=[0, 0.355], aspect=1,
			pos=[.7815, .61])
		self.map._texture = self.map_texture
		dot = bgui.Frame(self.map, size=[0.015, 0.015], pos=[0.5, 0.5])
		dot.colors = [[0.6, 0.0, 0.0, 0.85]] * 4

	def update(self):
		player_uv = self.player.tile_position.copy()
		player_uv[0] /= self.dmap._img_width
		player_uv[1] /= self.dmap._img_height

		view_width = 0.75

		uvs = [[0,0], [0,0], [0,0], [0,0]]
		uvs[0][0] = player_uv[0] - view_width
		uvs[0][1] = player_uv[1] - view_width
		uvs[1][0] = player_uv[0] + view_width
		uvs[1][1] = player_uv[1] - view_width
		uvs[2][0] = player_uv[0] + view_width
		uvs[2][1] = player_uv[1] + view_width
		uvs[3][0] = player_uv[0] - view_width
		uvs[3][1] = player_uv[1] + view_width

		self.map.texco = uvs


class MapTexture:
	def __init__(self, dmap):
		# Needed for compatibility with the bgui image module
		self.interp_mode = 0

		def _add_alpha(color):
			alpha = 255
			if color[0] == 0 and color[1] == 0 and color[2] == 0:
				alpha = 64
			return (color[0], color[1], color[2], alpha)

		img_data = [_add_alpha(i) for i in dmap._img_data]
		buffer = Buffer(GL_BYTE, (dmap._img_width*dmap._img_height, 4), img_data)
		self._id = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self._id)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, dmap._img_width, dmap._img_height,
			0, GL_RGBA, GL_UNSIGNED_BYTE, buffer)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

	def __del__(self):
		glDeleteTextures((self._id,))

	def bind(self):
		glBindTexture(GL_TEXTURE_2D, self._id)


class SpellLayout(bgui_bge_utils.Layout):
	def __init__(self, sys, data):
		super().__init__(sys, data)

		frame = bgui.Frame(self)
		frame.colors = [[0.0, 0.0, 0.0, 0.66]] * 4

		spell_list = bge.logic.globalDict['player_data'].spell_list.copy()

		for i in range(4 - len(spell_list)):
			spell = Spells.Spell.from_dna(Spells.SpellDna())
			spell.name = "Unused"
			spell_list.append(spell)

		# Player Spells
		self.spell_frame = bgui.Frame(self, size=[1.0, 0.3], pos=[0, 0.1],
			options=bgui.BGUI_CENTERX)
		dummy = SpellWidget(self.spell_frame, spell_list[0], -1)
		width = dummy._base_size[0] / self.spell_frame._base_size[0]
		pad = 0.01 / self.spell_frame._base_size[0]
		width += pad
		self.spell_frame.size = [width * len(spell_list), 0.3]
		self.spell_frame._remove_widget(dummy)

		for i, spell in enumerate(spell_list):
			card = SpellWidget(self.spell_frame, spell, i)
			card.position = [i*1/len(spell_list)+pad/2, 0.0]

		# Generated Spells
		new_list = Spells.generate_set(spell_list, 8)
		self.new_frame = bgui.Frame(self, size=[width*len(new_list), 0.3],
			pos=[0, 0.6], options=bgui.BGUI_CENTERX)
		for i, spell in enumerate(new_list):
			card = SpellWidget(self.new_frame, spell, i)
			card.position = [i*1/len(new_list)+pad/2, 0.0]

		# Effects key
		texture_dir = bge.logic.expandPath("//assets/textures/ui/")
		img = bgui.Image(self, texture_dir+"spell_key_effects.png", aspect=2/3,
			size=[0, 0.3], pos=[0.07, 0.1])
		bgui.Label(img, text="Effects", color=[0.9,0.9,0.9,1], pos=[0,.9],
			pt_size=22, options=bgui.BGUI_CENTERX)

		# Costs Key
		img = bgui.Image(self, texture_dir+"spell_key_costs.png", aspect=2/3,
			size=[0, 0.3], pos=[0.07, 0.1])
		width = img._base_size[0] / self._base_size[0]
		img.position = [0.93 - width, 0.1]
		bgui.Label(img, text="Costs", color=[0.9,0.9,0.9,1], pos=[0,.9],
			pt_size=22, options=bgui.BGUI_CENTERX)

		# Selector
		self.idx = 0
		selected = self.new_frame.children[0]
		self.selector = bgui.Image(selected, texture_dir+"spell_selector.png",
			name="selector")
		self.curframe = self.new_frame
		self.genidx = 0

	def update(self):
		events = self.data["input_system"].run()

		size = len(self.curframe.children)

		if events["LEFT"] == input.STATUS.PRESS:
			self.idx = (size + self.idx - 1) % size
		if events["RIGHT"] == input.STATUS.PRESS:
			self.idx = (self.idx + 1) % size
		if events["ACCEPT"] == input.STATUS.PRESS:
			if self.curframe == self.new_frame:
				self.curframe = self.spell_frame
				self.genidx = self.idx
			else:
				spell_list = bge.logic.globalDict['player_data'].spell_list
				scard = self.spell_frame.children[self.idx]
				gcard = self.new_frame.children[self.genidx]
				if self.idx == len(spell_list):
					spell_list.append(gcard.spell)
				elif self.idx > len(spell_list):
					offset = self.idx - len(spell_list)
					spell_list.append(gcard.spell)
					print("Gap detected!, offset ==", offset)
					scard = self.spell_frame.children[self.idx-offset]
				else:
					spell_list[self.idx] = gcard.spell
				scard.spell, gcard.spell = gcard.spell, scard.spell
				self.curframe = self.new_frame
			self.idx = 0

		self.selector.parent = self.curframe.children[self.idx]


class SpellWidget(bgui.Image):
	def __init__(self, parent, spell, index):
		image_path = bge.logic.expandPath("//assets/textures/ui/spell_card.png")
		super().__init__(parent, image_path, name=index, aspect=2/3)

		self.spell = spell

		self.name_lbl = bgui.Label(self, text=spell.name, color=[0.9,0.9,0.9,1],
			pos=[0,.9], pt_size=22, options=bgui.BGUI_CENTERX)

	def _draw(self):
		super()._draw()

		self.name_lbl.text = self.spell.name

		center = [0,0]
		center[0] = (self.gl_position[0][0] + self.gl_position[1][0]) / 2.0
		center[1] = (self.gl_position[1][1] + self.gl_position[2][1]) / 2.0
		width = abs(self.gl_position[1][0] - self.gl_position[0][0])

		scale = 0.65 * width * 0.5

		angles = [math.radians(a + 22.5) for a in range(0, 361, 45)]
		values = self.spell.dna.effects+self.spell.dna.costs
		magnitudes = [scale * max(v, 0.05) for v in values]

		glLineWidth(2.0)
		glBegin(GL_LINE_STRIP)
		for i in range(len(angles)):
			if 3 < i < 8:
				glColor4f(0.0, 0.0, 0.6, 1.0)
			else:
				glColor4f(0.6, 0.0, 0.0, 1.0)
			x = magnitudes[i%8] * math.cos(angles[i])
			y = magnitudes[i%8] * math.sin(angles[i])
			glVertex2f(center[0]+x, center[1]+y)
		glEnd()
		glLineWidth(1.0)


class Player:
	MOVE_TIME = 0.1

	def __init__(self, kxobj):
		self.tile_target = None
		self.tile_position = None
		self.move_factor = 1
		self.last_move = None
		self._obj = kxobj
		self.is_teleporting = False

		cam = bge.logic.getCurrentScene().active_camera
		self.orig_cam = cam.worldPosition.copy()
		cam.worldPosition.xy = self.orig_cam.xy + self._obj.worldPosition.xy
		self.cam_target = None

		self.animate("idle")

	def face(self, dir):
		v = dir[0], dir[1], 0
		self._obj.alignAxisToVect(v, 1)
		self._obj.alignAxisToVect((0, 0, 1))

	def animate(self, anim):
		if anim == "moving":
			self._obj.playAction("cg.Run", 0, 22, play_mode=bge.logic.KX_ACTION_MODE_LOOP, speed=2.0)
		elif anim == "idle":
			self._obj.playAction("cg.Idle", 0, 32, play_mode=bge.logic.KX_ACTION_MODE_LOOP)
		else:
			raise NotImplementedError("Action: " + anim)



def init(cont):
	scene = bge.logic.getCurrentScene()
	main = scene.objects["Main"]
	main["player"] = Player(scene.objects["ClayGolemArm"])
	main["player"].tile_position = mathutils.Vector(main["dmap"].player_start_loc)
	main["encounter_scene"] = False
	with open(bge.logic.expandPath('//input.conf')) as f:
		main["input_system"] = input.InputSystem(f, bge.logic.expandPath('//joyconfs'))

	# Make sure we always have a PlayerData
	if "player_data" not in bge.logic.globalDict:
		print("Using debug player.")
		bge.logic.globalDict['player_data'] = PlayerData.new("__DEBUG__")

	# UI
	main["ui"] = bgui_bge_utils.System()
	main["ui"].load_layout(HUDLayout, main)
	main["in_menu"] = False


def update(cont):
	main = bge.logic.getCurrentScene().objects["Main"]
	main["ui"].run()

	# Just in case init hasn't been called yet
	if "player" not in main:
		return

	if main["encounter_scene"]:
		return

	dmap = main["dmap"]
	player = main["player"]
	cam = bge.logic.getCurrentScene().active_camera

	if player.cam_target:
		cam.worldPosition.xy = cam.worldPosition.xy.lerp(player.cam_target, 0.1)

	if player.move_factor < player.MOVE_TIME:
		#print("Move to", player.tile_target, "from", player.tile_position)
		player.animate("moving")
		player.move_factor += time.time() - player.last_move
		player.last_move = time.time()
		if player.move_factor > player.MOVE_TIME or player.move_factor / player.MOVE_TIME > 0.95:
			player.move_factor = player.MOVE_TIME

		kworld = mathutils.Vector(dmap.tile_to_world(player.tile_position))
		vworld = mathutils.Vector(dmap.tile_to_world(player.tile_target))

		player._obj.worldPosition.xy = kworld.lerp(vworld, player.move_factor/player.MOVE_TIME)

		player.cam_target = player.orig_cam.xy + player._obj.worldPosition.xy

		if player.move_factor == player.MOVE_TIME:
			player.tile_position = player.tile_target

			if not player.is_teleporting and dmap.is_teleporter(player.tile_target):
				player.tile_target = mathutils.Vector(dmap.get_teleporter_loc(player.tile_target))
				player.move_factor = 0
				player.is_teleporting = True
			else:
				player.is_teleporting = False

	events = main['input_system'].run()
	if player.move_factor >= player.MOVE_TIME:
		target_tile = player.tile_position.copy()

		if not main["in_menu"]:
			if events["MOVE_UP"] == input.STATUS.ACTIVE:
				target_tile += mathutils.Vector((0, 1))
				player.face((0, 1))
			elif events["MOVE_LEFT"] == input.STATUS.ACTIVE:
				target_tile += mathutils.Vector((-1, 0))
				player.face((-1, 0))
			elif events["MOVE_DOWN"] == input.STATUS.ACTIVE:
				target_tile += mathutils.Vector((0, -1))
				player.face((0, -1))
			elif events["MOVE_RIGHT"] == input.STATUS.ACTIVE:
				target_tile += mathutils.Vector((1, 0))
				player.face((1, 0))

		if target_tile != player.tile_position and dmap.valid_tile(target_tile):
			player.tile_target = target_tile
			player.move_factor = 0
			player.last_move = time.time()
		else:
			player.animate("idle")

	if events["OPEN_MENU"] == input.STATUS.PRESS:
		main["ui"].toggle_overlay(SpellLayout, main)
		main["in_menu"] = not main["in_menu"]

	if events["SAVE_PLAYER"] == input.STATUS.PRESS:
		bge.logic.globalDict["player_data"].save()

	# Check encounters
	for i in dmap.encounters[:]:
		d2 = (player._obj.worldPosition - i.worldPosition).length_squared

		if d2 < ENCOUNTER_DISTANCE**2:
			print("Encounter!")
			dmap.encounters.remove(i)
			i.endObject()
			bge.logic.addScene("Combat")
			bge.logic.getCurrentScene().suspend()
			main["encounter_scene"] = True

	if not main['encounter_scene'] and not dmap.encounters:
		bge.logic.getCurrentScene().restart()
