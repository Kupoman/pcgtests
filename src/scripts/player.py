import bge
import time
import mathutils

ENCOUNTER_DISTANCE = 1.25

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
		
		
def init(cont):
	main = bge.logic.getCurrentScene().objects["Main"]
	main["player"] = Player(cont.owner)
	main["player"].tile_position = mathutils.Vector(main["player_start_loc"])
	main["encounter_scene"] = False


def update(cont):
	main = bge.logic.getCurrentScene().objects["Main"]

	if main["encounter_scene"]:
		return

	dmap = main["dmap"]
	player = main["player"]
	cam = bge.logic.getCurrentScene().active_camera

	if player.cam_target:
		cam.worldPosition.xy = cam.worldPosition.xy.lerp(player.cam_target, 0.1)

	if player.move_factor < player.MOVE_TIME:
		#print("Move to", player.tile_target, "from", player.tile_position)
		player.move_factor += time.time() - player.last_move
		player.last_move = time.time()
		if player.move_factor > player.MOVE_TIME or player.move_factor / player.MOVE_TIME > 0.95:
			player.move_factor = player.MOVE_TIME
		
		kworld = mathutils.Vector(dmap.tile_to_world(player.tile_position))
		vworld = mathutils.Vector(dmap.tile_to_world(player.tile_target))

		cont.owner.worldPosition.xy = kworld.lerp(vworld, player.move_factor/player.MOVE_TIME)

		player.cam_target = player.orig_cam.xy + player._obj.worldPosition.xy

		if player.move_factor == player.MOVE_TIME:
			player.tile_position = player.tile_target

			if not player.is_teleporting and dmap.is_teleporter(player.tile_target):
				player.tile_target = mathutils.Vector(dmap.get_teleporter_loc(player.tile_target))
				player.move_factor = 0
				player.is_teleporting = True
			else:
				player.is_teleporting = False

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

	# Check encounters
	for i in main["encounters"][:]:
		d2 = (player._obj.worldPosition - i.worldPosition).length_squared

		if d2 < ENCOUNTER_DISTANCE**2:
			print("Encounter!")
			main["encounters"].remove(i)
			i.endObject()
			bge.logic.addScene("Combat")
			main["encounter_scene"] = True