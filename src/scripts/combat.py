from bge import logic, events
from bgl import *
from scripts import engine, spells
import scripts.bgui as bgui
import scripts.bgui.bge_utils as bgui_bge_utils
import time
import random


class Projectile:
	def __init__(self, target, effect, rank, obname, origin):
		self.object = engine.add_object(obname, origin)
		self.origin = self.object.worldPosition.copy()
		self.effect = effect
		self.rank = rank
		target._inbound.append(self)
		self.target = target.object.worldPosition.copy()
		self.target[2] += 1

	def move(self, dt):
		vec = self.target - self.origin
		vec.normalized()

		self.object.worldPosition += vec * dt * 0.5

	@property
	def distance(self):
		return (self.target - self.object.worldPosition).length_squared

	def end(self):
		self.object.endObject()


class Combatant:
	STAMINA_RATE = 0.25
	DODGE_COST = 0.3

	def __init__(self, kxobj):
		self.object = kxobj
		self.stamina = 0
		self.hp =  self.maxhp = 3
		self.dodging = False

		sdna = spells.SpellDna()
		sdna.effects[0] = 1
		self.spells = [spells.Spell.from_dna(sdna)] * 4

		self.enemy_target = None
		self.ally_target = self

		self._inbound = []

	def update(self, dt):
		self.stamina += self.STAMINA_RATE * dt
		self.stamina = min(self.stamina, 1.0)

		for proj in self._inbound[:]:
			d = proj.distance
			if d < 0.5:
				if proj.effect == 'damage':
					self.hp -= 1
				else:
					raise NotImplementedError(proj.effect)

				proj.end()
				self._inbound.remove(proj)
			elif self.dodging and d < 8:
				proj.end()
				self._inbound.remove(proj)
			else:
				proj.move(dt)

		self.dodging = False

	def use_spell(self, idx):
		spell = self.spells[idx]

		if spell.stamina_cost > self.stamina:
			print("Not enough stamina")
			return False

		self.stamina -= spell.stamina_cost

		projloc = self.object.worldPosition.copy()
		projloc[2] += 1

		for i in spell.effects:
			if i == 'damage':
				Projectile(self.enemy_target, i, 1, "DamageProjectile", projloc)
			else:
				raise NotImplementedError(i)

		return True

	def dodge(self):
		if self.stamina > self.DODGE_COST:
			self.dodging = True
			self.stamina -= self.DODGE_COST
			return True
		return False

	def end(self):
		self.object.endObject()
		for i in self._inbound:
			i.end()


class Hero(Combatant):
	def __init__(self, location):
		super().__init__(engine.add_object("ClayGolemArm", location))

		self.object.alignAxisToVect((-1, 0, 0), 1)
		self.object.alignAxisToVect((0, 0, 1))
		self.object.playAction("cg.Idle", 0, 32, play_mode=logic.KX_ACTION_MODE_LOOP)

		ringloc = location[:]
		ringloc[2] += 1
		self.ring = engine.add_object("DodgeRing",ringloc)

		self.spells = logic.globalDict['player_data'].spell_list

	def update(self, dt):
		super().update(dt)

		self.object.playAction("cg.Idle", 0, 32, priority=1, play_mode=logic.KX_ACTION_MODE_LOOP)

	def use_spell(self, idx):
		if super().use_spell(idx):
			self.object.playAction("cg.Attack", 0, 24, speed=2.0)

	def dodge(self):
		if super().dodge():
			self.object.playAction("cg.Death", 0, 32, speed=5.0)

	def end(self):
		super().end()
		self.ring.endObject()


class Enemy(Combatant):
	FIRE_CHANCE = 0.0035

	def __init__(self, location):
		super().__init__(engine.add_object("Monster", location))

	def update(self, dt):
		super().update(dt)

		if random.random() < self.FIRE_CHANCE:
			self.use_spell(0)


class SpellRenderer(bgui.ListBoxRenderer):
	def __init__(self, lb):
		super().__init__(lb)
		self.lb = lb
		self.idx_to_key = {
			0: "Q",
			1: "W",
			2: "E",
			3: "R",
		}

	def render_item(self, item):
		idx = self.lb.items.index(item)
		self.label.text = "[" + self.idx_to_key[idx] + "]\t" + str(item)
		return self.label

class CombatLayout(bgui_bge_utils.Layout):
	def __init__(self, sys, data):
		super().__init__(sys, data)

		self.stamina = bgui.ProgressBar(self, size=[0.8, 0.03], pos=[0, 0.05], options=bgui.BGUI_CENTERX)
		self.stamina.fill_colors = [[1, 1, 1, 1]] * 4
		self.stamina.border = 3

		self.health = bgui.ProgressBar(self, size=[0.8, 0.03], pos=[0, 0.09], options=bgui.BGUI_CENTERX)
		self.health.fill_colors = [[0.6, 0, 0, 1]] * 4
		self.health.border = 3

		lbframe = bgui.Frame(self, size=[0.2, 0.25], pos=[0.7, 0.2])
		lbframe.colors = [[0.8, 0.8, 0.8, 0.8]] * 4
		lbframe.border = 2
		self.spells = bgui.ListBox(lbframe, items=data.player.spells, padding=0.1, size=[0.95, 0.95], options=bgui.BGUI_CENTERED)
		self.spells.renderer = SpellRenderer(self.spells)

	def update(self):
		player = self.data.player

		self.stamina.percent = player.stamina
		self.health.percent = player.hp / player.maxhp


class Combat:
	def __init__(self):
		self.main = logic.getSceneList()[0].objects["Main"]

		# Setup player
		self.player = Hero([8, 2, 0])

		# Setup enemies
		locs = ((-8, 7, 0), (-8, 2, 0), (-8, -3, 0))
		self.enemies = []
		for i in locs:
			enemy = Enemy(i)
			enemy.enemy_target = self.player
			self.enemies.append(enemy)

		# Give the player something to shoot at
		self.player.enemy_target = self.enemies[0]

		# UI
		self.ui = bgui_bge_utils.System()
		self.ui.load_layout(CombatLayout, self)

		self.prev_time = time.time()

	def update(self):
		self.ui.run()

		evts = logic.keyboard.events

		dt = time.time() - self.prev_time
		self.prev_time = time.time()

		# Player
		self.player.update(dt)

		for i in self.enemies[:]:
			if i.hp > 0:
				i.update(dt)
			else:
				self.enemies.remove(i)
				if self.player.enemy_target == i:
					self.player.enemy_target = None
				i.end()

		if not self.enemies or self.player.hp <= 0:
			logic.getSceneList()[0].resume()
			self.main["encounter_scene"] = False
			logic.getCurrentScene().end()
		elif self.player.enemy_target is None:
			self.player.enemy_target = self.enemies[0]

		if evts[events.QKEY] == logic.KX_INPUT_JUST_ACTIVATED:
			self.player.use_spell(0)
		if evts[events.WKEY] == logic.KX_INPUT_JUST_ACTIVATED:
			self.player.use_spell(1)
		if evts[events.EKEY] == logic.KX_INPUT_JUST_ACTIVATED:
			self.player.use_spell(2)
		if evts[events.RKEY] == logic.KX_INPUT_JUST_ACTIVATED:
			self.player.use_spell(3)
		if evts[events.SPACEKEY] == logic.KX_INPUT_JUST_ACTIVATED:
			self.player.dodge()


def init(cont):
	cont.owner['combat'] = Combat()


def update(cont):
	combat = cont.owner.get('combat')
	if combat is not None:
		combat.update()