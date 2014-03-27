from bge import logic


def add_object(ob, position):
	scene = logic.getCurrentScene()
	adder = scene.objects["Main"]

	added = scene.addObject(ob, adder)
	added.worldPosition = position
	return added