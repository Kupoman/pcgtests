from scripts import spells

MAJORS = ("WATER", "EARTH", "WIND")

def get_starting_spells(major):
	slist = []
	dna = spells.SpellDna()
	dna.effects = [1, 0, 0, 0]
	slist.append(spells.Spell.from_dna(dna))

	if major == "WATER":
		dna.effects = [0, 1, 0, 0]
		slist.append(spells.Spell.from_dna(dna))
	elif major == "EARTH":
		dna.effects = [0, 0, 1, 0]
		slist.append(spells.Spell.from_dna(dna))
	elif major == "WIND":
		dna.effects = [0, 0, 0, 1]
		slist.append(spells.Spell.from_dna(dna))
	else:
		print("Invalid major:", major)

	return slist