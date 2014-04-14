import json

from effect import EffectFactory


class Spell:
	def __init__(self, name, effects=[], costs=[]):
		self.name = name
		self.effects = effects
		self.costs = costs


class SpellFactory:
	def __init__(self):
		self._efactory = EffectFactory()
		self._predefined = {}

		with open("spells.json", "r") as fin:
			_json = json.load(fin)
			for item in _json:
				name = item["name"]
				effects = []
				for effect in item["effects"]:
					effects.append(self._efactory.create_effect(**effect))
				costs = []
				for cost in item["costs"]:
					costs.append(self._efactory.create_effect(**effect))
				self._predefined[name] = Spell(name, effects, costs)

	def get_predefined(self, name):
		return self._predefined[name]

	def generate(self):
		return self.get_predefined("attack")