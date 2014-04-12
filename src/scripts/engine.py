from bge import logic


def add_object(ob, position):
	scene = logic.getCurrentScene()
	adder = scene.objects.get("Main", None)

	if adder is None:
		adder = scene.objects["CombatMain"]

	added = scene.addObject(ob, adder)
	added.worldPosition = position
	return added