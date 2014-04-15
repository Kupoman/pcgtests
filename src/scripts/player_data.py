from scripts import spells


class PlayerData:
	def __init__(self, name, spell_list):
		self.name = name
		self.spell_list = spell_list

	@classmethod
	def new(cls, name):
		# Create player data with four all damage spells
		spell_list = []
		sdna = spells.SpellDna()
		sdna.effects[0] = 1
		for i in range(4):
			spell_list.append(spells.Spell.from_dna(sdna))

		return PlayerData(name, spell_list)

