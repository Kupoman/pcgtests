import bge
import bgl
import random
from mathutils import Vector

from . import bsp
from . import engine


class DungeonMap:
	def __init__(self, sw, sh, min_roomx, min_roomy):
		bsp_data = bsp.gen(sw, sh, min_roomx, min_roomy)
		self._bsp_data = bsp_data
		self._img_data = []
		self._img_height = len(bsp_data)
		self._img_width = len(bsp_data[0])

		self.telemap = {}
		self.telepos = {}
		self.encounters = []
		self.player_start_loc = (0, 0)

		for y in range(len(bsp_data)):
			for x in range(len(bsp_data[y])):
				tile = bsp_data[y][x]

				color = (0, 0, 0)
				if tile in ('#', '*', '$') or tile.isdigit():
					color = (255, 255, 255)
					tpos = Vector((x - sw / 2, y - sh / 2, -random.random() * 0.1))
					engine.add_object("DungeonTile", tpos)

					if tile == '$':
						color = (128, 128, 128)
						enc = engine.add_object("MonsterSpawn", tpos + Vector((0, 0, 1.75)))
						self.encounters.append(enc)
					elif tile == '*':
						self.player_start_loc = (x, y)
						engine.add_object("ClayGolemArm", (tpos.x, tpos.y, 0.75))
					elif tile.isdigit():
						tele = engine.add_object("Teleporter", (tpos.x, tpos.y, 0.75))
						if tile not in self.telemap:
							self.telemap[tile] = [(x, y)]
							self.telepos[tile] = Vector((tpos.x, tpos.y, 1.25))
						else:
							self.telemap[tile].append((x, y))
							tele_link = engine.add_object("TeleLink", (tpos.x, tpos.y, 1.25))

							target_pos = self.telepos[tile]
							cur_pos = Vector((tpos.x, tpos.y, 1.25))
							
							target_vec = target_pos - cur_pos
							link_scale = target_vec.length
							tele_link.localScale = (1, link_scale, 1)
							tele_link.alignAxisToVect(-target_vec, 1)

				self._img_data.append(color)

	def tile_to_world(self, tile_pos):
		return (tile_pos[0] - self._img_height / 2, tile_pos[1] - self._img_width / 2)

	def world_to_tile(self, world_pos):
		return (world_pos[0] + self._img_width / 2, world_pos[1] + self._img_height / 2)

	def is_teleporter(self, tile_pos):
		return self._bsp_data[int(tile_pos[1])][int(tile_pos[0])].isdigit()

	def get_teleporter_loc(self, tile_pos):
		tile = self._bsp_data[int(tile_pos[1])][int(tile_pos[0])]
		teleloc = tile_pos
		if tile in self.telemap:
			for i in self.telemap[tile]:
				if tile_pos[0] != i[0] or tile_pos[1] != i[1]:
					teleloc = i
					break

		return teleloc

	def valid_tile(self, tile_pos):
		tile = self._bsp_data[int(tile_pos[1])][int(tile_pos[0])]
		#print(tile)
		return tile != '.'


def init(cont):
	# Todo: Remove this method next time main.blend is open for modifications.
	pass
