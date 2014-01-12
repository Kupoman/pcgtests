import json


class EffectData:
	def __init__(self, name="", value=0, stat="", apply_func="apply_stat", remove_func="remove_stat", tick_func="tick_stat"):
		self.value = value
		self.type = name
		self._stat = stat

		self.apply = getattr(self, apply_func)
		self.remove = getattr(self, remove_func)
		self.tick = getattr(self, tick_func)

	def apply_stat(self, character, points):
		val = getattr(character, self._stat) + self.value * points
		setattr(character, self._stat, val)

	def remove_stat(self, character, points):
		val = getattr(character, self._stat) - self.value * points
		setattr(character, self._stat, val)

	def tick_stat(self, character, points):
		pass

	def tick_dot(self, character, points):
		self.apply_stat(character, points)


class Effect:
	def __init__(self, data, points, duration):
		self._data = data
		self._points = points
		self.duration = duration

	@property
	def type(self):
		return self._data.type

	@property
	def value(self):
		return self._points * self._data.value

	def apply(self, character):
		self._data.apply(character, self._points)

	def remove(self, character):
		self._data.remove(character, self._points)

	def tick(self, character):
		self._data.tick(character, self._points)


class EffectFactory:
	def __init__(self):
		elist = []
		with open("effects.json", "r") as fin:
			elist = json.load(fin)

		self._effects = {}
		for effect in elist:
			self._effects[effect['name']] = EffectData(**effect)

	def create_effect(self, name="HP-", points=1, duration=0):
		data = self._effects[name]
		return Effect(data, points, duration)