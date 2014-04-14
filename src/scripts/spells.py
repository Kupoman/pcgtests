import math

EFFECTS = ('damage', 'heal', 'slow', 'haste')
COSTS = ('stamina', 'cast_time', 'cool_down', 'health')

_NAME_GEN_EFFECTS = {
	'damage': 'nox',
	'heal': 'anim',
	'slow': 'grav',
	'haste': 'celer',
}

_NAME_GEN_REP = {
	1: '',
	2: 'bi',
	3: 'tern',
	4: 'quadra',
}


class SpellDna:
	def __init__(self):
		self.effects = [0, 0, 0, 0]
		self.costs = [0, 0, 0, 0]
		self.cost = 0

	def normalize(self):
		sum = 0
		for i in range(len(self.effects)):
			sum += self.effects[i]
		for i in range(len(self.effects)):
			self.effects[i] /= sum

		sum = 0
		for i in range(len(self.costs)):
			sum += self.costs[i]
		for i in range(len(self.costs)):
			self.costs[i] /= sum


class Spell:
	def __init__(self):
		self.dna = None
		self.effects = []
		self.costs = []
		self.rank = 1
		self.cost = 0
		self.points = self.rank
		self.name = ""

	@classmethod
	def from_dna(cls, dna):
		spell = Spell()
		spell.dna = dna
		spell._recalc()
		return spell

	def _recalc(self):
		self.cost = math.floor(self.dna.cost * (self.rank + 1))
		self.points = self.rank + self.cost

		temp = self.dna.effects.copy()
		for i in range(self.points):
			max_index, max_val = max(enumerate(temp), key=lambda x: x[1])
			if max_val == 0.0:
				return
			temp[max_index] -= 1 / self.points
			self.effects.append(EFFECTS[max_index])

		temp = self.dna.costs.copy()
		for i in range(self.cost):
			max_index, max_val = max(enumerate(temp), key=lambda x: x[1])
			temp[max_index] -= 1 / self.cost
			self.costs.append(COSTS[max_index])

		self.name = ""
		for i in EFFECTS:
			count = self.effects.count(i)
			if count > 0:
				self.name += _NAME_GEN_REP[count] + _NAME_GEN_EFFECTS[i]

		self.name = self.name.title()

	def __repr__(self):
		return self.name