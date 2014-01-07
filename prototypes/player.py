STAMINA_RATE = 0.25
DODGE_COST = 0.3
FIRE_COST = 0.4

class Player:
	def __init__(self, kxobj):
		self.kxobj = kxobj
		self._inbound = []
		self.stamina = 0.0
		self.hp = 3

		self.dodging = False

	def update(self, dt):
		self.stamina += STAMINA_RATE * dt
		self.stamina = min(max(self.stamina, 0.0), 1.0)
	
		for proj in self._inbound:
			if proj.invalid:
				self._inbound.remove(proj)
				continue

			distance = (proj.worldPosition - self.kxobj.worldPosition).length_squared
			if distance < 1:
				self.hp -= 1
				proj.endObject()
				continue

			if self.dodging and distance < 9:
				proj.endObject()
				continue

		self.dodging = False

	def dodge(self):
		if self.stamina > DODGE_COST:
			self.dodging = True
			self.stamina -= DODGE_COST

			import random

	def fire(self, scene, target, origin):
		if self.stamina > FIRE_COST:
			self.stamina -= FIRE_COST

			proj = scene.addObject("Projectile", origin, 0)

			if type(target) == str:
				proj["target"] = target
				target = scene.objects.get(target, None)
			else:
				proj["target"] = target.name

			if target and not target.invalid:
				if "class" in target.attrDict:
					target["class"]._inbound.append(proj)
