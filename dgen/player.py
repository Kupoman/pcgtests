import bge
import mathutils

class Player:
	def __init__(self, kxobj):
		self._obj = kxobj
		
		
def init(cont):
	main = bge.logic.getCurrentScene().objects["Main"]
	main["player"] = Player(cont.owner)
	
def update(cont):
	main = bge.logic.getCurrentScene().objects["Main"]
	dmap = main["dmap"]
	
	movement = mathutils.Vector((0, 0, 0))
	
	events = bge.logic.keyboard.events
	
	if events[bge.events.WKEY] == bge.logic.KX_INPUT_ACTIVE:
		movement += mathutils.Vector((0, 1, 0))
	if events[bge.events.AKEY] == bge.logic.KX_INPUT_ACTIVE:
		movement += mathutils.Vector((-1, 0, 0))
	if events[bge.events.SKEY] == bge.logic.KX_INPUT_ACTIVE:
		movement += mathutils.Vector((0, -1, 0))
	if events[bge.events.DKEY] == bge.logic.KX_INPUT_ACTIVE:
		movement += mathutils.Vector((1, 0, 0))

	movement.normalize()
	# movement *= 0.25
	
	obj = cont.owner
	movement = movement * obj.worldOrientation
	new_pos = obj.worldPosition + movement * (0.25 + 0.6)
	# new_pos[0] = round(new_pos[0])
	# new_pos[1] = round(new_pos[1])
	
	if dmap.valid_tile(new_pos[0], new_pos[1]):
		cont.owner.applyMovement(movement * 0.25, False)
		# obj.worldPosition = new_pos
		