from scripts import spells
from scripts import majors


class PlayerData:
	def __init__(self, name, spell_list):
		self.name = name
		self.spell_list = spell_list

	@classmethod
	def new(cls, name, major="WATER"):
		return PlayerData(name, majors.get_starting_spells(major))

