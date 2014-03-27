import bge
import bgl
import random
from mathutils import Vector

from . import bsp
from . import engine


class DungeonMap:
	def __init__(self, sw, sh):
		bsp_data = bsp.gen(sw, sh)
		self._bsp_data = bsp_data
		self._img_data = []
		self._img_height = len(bsp_data)
		self._img_width = len(bsp_data[0])

		self.telemap = {}
		self.telecolors = {}
		self.encounters = []
		self.player_start_loc = (0, 0)

		for y in range(len(bsp_data)):
			for x in range(len(bsp_data[y])):
				tile = bsp_data[y][x]

				color = (0, 0, 0)
				if tile in ('#', '*', '$') or tile.isdigit():
					tpos = Vector((x - sw / 2, y - sh / 2, -random.random() * 0.1))
					engine.add_object("DungeonTile", tpos)

					if tile == '#':
						color = (255, 255, 255)
					elif tile == '$':
						color = (128, 128, 128)
						enc = engine.add_object("MonsterSpawn", tpos + Vector((0, 0, 1.75)))
						self.encounters.append(enc)
					elif tile == '*':
						color = (255, 0, 0)
						self.player_start_loc = (x, y)
						engine.add_object("PlayerStart", (tpos.x, tpos.y, 0.75))
						engine.add_object("Player", (tpos.x, tpos.y, 0.75))
					elif tile.isdigit():
						if tile not in self.telecolors:
							self.telecolors[tile] = (random.random(), random.random(), random.random(), 1.0)
						if tile not in self.telemap:
							self.telemap[tile] = [(x, y)]
						else:
							self.telemap[tile].append((x, y))

						color = [int(i*255) for i in self.telecolors[tile][:3]]

						tele = engine.add_object("Teleporter", (tpos.x, tpos.y, 0.75))
						tele.color = self.telecolors[tile]

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
				if tile_pos[0] != i[0] and tile_pos[1] != i[1]:
					teleloc = i
					break

		return teleloc

	def valid_tile(self, tile_pos):
		tile = self._bsp_data[int(tile_pos[1])][int(tile_pos[0])]
		#print(tile)
		return tile != '.'


_map = None


def init(cont):
	global _map
	main = cont.owner
	_map = DungeonMap(50, 50)

	main["dmap"] = _map



def minimap_add(cont):
	global _map
	if _map == None:
		_map = bge.logic.getSceneList()[0].objects["Main"]["dmap"]
		
	obj = cont.owner
	id = bge.texture.materialID(obj, "IMUntitled")
	object_texture = bge.texture.Texture(obj, id)
	
	new_source = bge.texture.ImageBuff()
	buffer = bgl.Buffer(bgl.GL_BYTE, (_map._img_width* _map._img_height, 3), _map._img_data)
	new_source.load(buffer, _map._img_width, _map._img_height)
	
	obj["map_img"] = object_texture
	
	obj["map_img"].source = new_source
	obj["map_img"].refresh(False)
