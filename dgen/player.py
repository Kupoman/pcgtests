import bge
import time
import mathutils

class Player:
	MOVE_TIME = 0.3

	def __init__(self, kxobj):
		self.tile_target = None
		self.tile_position = None
		self.move_factor = 1
		self.last_move = None
		self._obj = kxobj
		
		
def init(cont):
	main = bge.logic.getCurrentScene().objects["Main"]
	main["player"] = Player(cont.owner)
	main["player"].tile_position = mathutils.Vector(main["player_start_loc"])


def update(cont):
	main = bge.logic.getCurrentScene().objects["Main"]
	dmap = main["dmap"]
	player = main["player"]

	if player.move_factor < player.MOVE_TIME:
		#print("Move to", player.tile_target, "from", player.tile_position)
		player.move_factor += time.time() - player.last_move
		if player.move_factor > player.MOVE_TIME:
			player.move_factor = player.MOVE_TIME
		
		kworld = mathutils.Vector(dmap.tile_to_world(player.tile_position))
		vworld = mathutils.Vector(dmap.tile_to_world(player.tile_target))

		cont.owner.worldPosition.xy = kworld.lerp(vworld, player.move_factor/player.MOVE_TIME)

		if player.move_factor == player.MOVE_TIME:
			player.tile_position = player.tile_target
	if player.move_factor >= player.MOVE_TIME:	
		events = bge.logic.keyboard.events
		target_tile = player.tile_position.copy()
		
		if events[bge.events.WKEY] == bge.logic.KX_INPUT_ACTIVE:
			target_tile += mathutils.Vector((0, 1))
		elif events[bge.events.AKEY] == bge.logic.KX_INPUT_ACTIVE:
			target_tile += mathutils.Vector((-1, 0))
		elif events[bge.events.SKEY] == bge.logic.KX_INPUT_ACTIVE:
			target_tile += mathutils.Vector((0, -1))
		elif events[bge.events.DKEY] == bge.logic.KX_INPUT_ACTIVE:
			target_tile += mathutils.Vector((1, 0))

		#print(target_tile, player.tile_position)
		if target_tile != player.tile_position and dmap.valid_tile(target_tile):
			#print("found new tile")
			player.tile_target = target_tile
			player.move_factor = 0
			player.last_move = time.time()

