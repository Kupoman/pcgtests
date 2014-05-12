from builtins import property
import math
import copy
import random
import itertools
import bisect
import sys

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
		self.save_fields = ["effects", "costs", "cost"]
		self.effects = [0, 0, 0, 0]
		self.costs = [0, 0, 0, 0]
		self.cost = 0
		self.fitness = 0

	@classmethod
	def generate(cls):
		sdna = SpellDna()
		sdna.cost = random.random()

		for i in range(len(sdna.effects)):
			sdna.effects[i] = random.random()
		for i in range(len(sdna.costs)):
			sdna.costs[i] = random.random()
		sdna.normalize()

		return sdna

	@classmethod
	def crossover(cls, parents):
		new_dna = SpellDna()
		for i in range(len(new_dna.effects)):
			new_dna.effects[i] = random.choice(parents).effects[i]
		for i in range(len(new_dna.costs)):
			new_dna.costs[i] = random.choice(parents).costs[i]
		new_dna.cost = random.choice(parents).cost
		new_dna.normalize()

		return new_dna

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

	def mutate(self, rate):
		for i in range(len(self.effects)):
			if random.random() < rate:
				self.effects[i] = random.uniform(0, 2*self.effects[i])
		for i in range(len(self.costs)):
			if random.random() < rate:
				self.costs[i] = random.uniform(0, 2*self.costs[i])
		if random.random() < rate:
			self.cost = random.uniform(0, 2*self.cost)
			cmax = 1.0 - sys.float_info.epsilon
			if self.cost > cmax:
				self.cost = cmax

		self.normalize()

	def update_fitness(self, pool):
		self.fitness = 0
		for samp in pool:
			efit = 0
			for i in range(len(self.effects)):
				efit += self.effects[i] * samp.effects[i]
			cfit = 0
			for i in range(len(self.costs)):
				cfit += self.costs[i] * samp.costs[i]
			self.fitness += efit + cfit


class Spell:
	BASE_STAMINA = 0.4

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
		spell.dna = copy.copy(dna)
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

	@property
	def stamina_cost(self):
		# ToDo add extra stamina from cost vector
		return self.BASE_STAMINA

	def __repr__(self):
		return self.name


def weighted_choice(choices, weights):
	cumdist = list(itertools.accumulate(weights))
	x = random.random() * cumdist[-1]
	return choices[bisect.bisect(cumdist, x)]


def weighted_sample(choices, weights, n):
	sample = set()
	while (len(sample) < n):
		c = weighted_choice(choices, weights)
		sample.add(c)
	return list(sample)


def generate_set(pool, n):
		pop = [SpellDna.generate() for i in range(n)]
		player_dna = [s.dna for s in pool]
		for dna in pop:
			dna.update_fitness(player_dna)
		for i in range(3):
			new_pop = [SpellDna.crossover(weighted_sample(pop, [d.fitness for d in pop], 3)) for i in range(n)]
			for dna in new_pop:
				dna.mutate(0.5)
			pop = new_pop
			for dna in pop:
				dna.update_fitness(player_dna)

		return [Spell.from_dna(dna) for dna in pop]