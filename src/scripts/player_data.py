import json
import os

import bge

from scripts import spells
from scripts import majors

SAVE_DIR = bge.logic.expandPath("//saves")


class PlayerData:
	def __init__(self, name, major):
		self.name = name
		self.spell_list = majors.get_starting_spells(major)
		self.major = major

	@classmethod
	def new(cls, name, major="WATER"):
		return PlayerData(name, major)

	def save(self):
		serial = {}

		serial["name"]  = self.name
		serial["major"] = self.major

		serial["spell_list"] = []
		for spell in self.spell_list:
			serial_spell = {}
			for field in spell.dna.save_fields:
				serial_spell[field] = getattr(spell.dna, field)
			serial["spell_list"].append(serial_spell)

		if not os.access(SAVE_DIR, os.F_OK):
			os.mkdir(SAVE_DIR)

		with open(SAVE_DIR+"/"+self.name+".save", "w") as fout:
			json.dump(serial, fout)

