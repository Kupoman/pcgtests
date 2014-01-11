import bge
import bgl
import random

class DungeonMap:
	def __init__(self, bsp_data):
		self._bsp_data = bsp_data
		self._img_data = []
		self._img_height = len(bsp_data)
		self._img_width = len(bsp_data[0])

		self.telemap = {}
		self.telecolors = {}

		for y in range(len(bsp_data)):
			for x in range(len(bsp_data[y])):
				tile = bsp_data[y][x]
				if tile == '#':
					color = (255, 255, 255)
				elif tile == '*':
					color = (255, 0, 0)
				elif tile.isdigit():
					if tile not in self.telecolors:
						self.telecolors[tile] = (random.random(), random.random(), random.random(), 1.0)
					if tile not in self.telemap:
						self.telemap[tile] = [(x, y)]
					else:
						self.telemap[tile].append((x, y))

					color = [int(i*255) for i in self.telecolors[tile][:3]]
				else:
					color = (0, 0, 0)

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

	def add_teleporter(self, tile_pos):
		telenum = self._bsp_data[int(tile_pos[1])][int(tile_pos[0])]
		return self.telecolors[telenum]
                    
_map = None

def init(bsp_data):
	_map = DungeonMap(bsp_data)
	return _map

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
