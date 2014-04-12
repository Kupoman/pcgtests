from spell import SpellFactory

class Character:
	def __init__(self, name):
		self.name = name
		self.hp = 20
		self.mana = 30
		self.magic = 5
		self.defense = 5
		self.speed = 1

		self.effects = {}
		self.spells = []

	def __repr__(self):
		return self.name

	def apply_effect(self, effect):
		if effect.type in self.effects and self.effect[effect.type].value > effect.value:
			print("Stronger effect for %s already exists on %s" % (effect.type, self.name))

		self.effects[effect.type] = effect
		effect.apply(self)

class Encounter:
	def __init__(self, participants):
		self.participants = participants
		for i in self.participants:
			i.atb = 0

	def tick(self):
		for i in self.participants:
			i.atb += i.speed

			if i.atb >= 10:
				self.do_turn(i)
				i.atb -= 10

	def validate_participant(self, part):
		if part.hp <=0:
			self.participants.remove(part)

	def do_turn(self, ch):
		print("%s's turn!" % (ch,))

		# Tick any active effects
		for fxtype, fx in ch.effects.items():
			fx.tick(ch)
			fx.duration -= 1
		self.validate_participant(ch)

		# Remove any completed effects
		for fx in [i for i in ch.effects.values() if i.duration <= 0]:
			del ch.effects[fx.type]

		# Display options
		option = -1
		while option < 0:
			print("HP: ", ch.hp)
			print("Spells:")
			for i, spell in enumerate(ch.spells):
				print("\t%d. %s" %(i+1, spell.name.title()))
 
			inp = input("Enter option: ")
			try:
				option = int(inp) -1
			except ValueError:
				option = -1
			if option > len(ch.spells)-1 or option < 0:
				option = -1
				print("Invalid option")
   
		# if option == 1:
		spell = ch.spells[option]

		# Choose Target
		targets = self.participants[:]
		targets.remove(ch)

		target = None
		while target is None:
			print("Attacking, pick a target:")
			for idx, i in enumerate(targets):
				print("\t%d. %s" % (idx+1, i))
			
			tidx = input("Target: ")
			try:
				tidx = int(tidx)-1
			except ValueError:
				tidx = -1
			if 0 < tidx < len(targets) - 1:
				print("Invalid target")
			else:
				target = targets[tidx]

		# Cast Spell
		for effect in spell.effects:
			target.apply_effect(effect)
			effect.tick(target)
		self.validate_participant(target)
		for cost in spell.costs:
			ch.apply_effect(cost)
			cost.tick(ch)
		self.validate_participant(ch)

		print()

if __name__ == '__main__':
	sfactory = SpellFactory()
	participants = [
			Character("Foo"),
			Character("Bar"),
		]

	for p in participants:
		p.spells.append(sfactory.get_predefined("attack"))

	e = Encounter(participants)
	while len(e.participants) > 1:
		e.tick()

	print("Encounter done!")
