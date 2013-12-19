import bge
import bgl

class DungeonMap:
	def __init__(self, bsp_data):
		self._bsp_data = bsp_data
		self._img_data = []
		self._img_height = len(bsp_data)
		self._img_width = len(bsp_data[0])

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
				
	def valid_tile(self, x, y):
		x = int(x-2.0) + self._img_width/2
		y = int(y+2.0) + self._img_height/2
		return self._bsp_data[int(y)][int(x)] != '.'

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