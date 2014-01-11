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
				else:
					color = (0, 0, 0)

				self._img_data.append(color)

	def tile_to_world(self, tile_pos):
		return (tile_pos[0] - self._img_height / 2, tile_pos[1] - self._img_width / 2)

	def world_to_tile(self, world_pos):
		return (world_pos[0] + self._img_width / 2, world_pos[1] + self._img_height / 2)

	def valid_tile(self, tile_pos):
		tile = self._bsp_data[int(tile_pos[1])][int(tile_pos[0])]
		#print(tile)
		return tile != '.'

	def add_teleporter(self, tile_pos):
			telenum = self._bsp_data[int(tile_pos[1])][int(tile_pos[0])]
			if telenum not in self.telecolors:
				self.telecolors[telenum] = (random.random(), random.random(), random.random(), 1.0)

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
