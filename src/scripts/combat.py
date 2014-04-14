from bge import logic, events
from bgl import *
from scripts import engine, spells
import time


class Combatant:
	STAMINA_RATE = 0.25
	DODGE_COST = 0.3

	def __init__(self, kxobj):
		self.object = kxobj
		self.stamina = 0
		self.hp = 3

		sdna = spells.SpellDna()
		sdna.effects[0] = 1
		self.spells = [spells.Spell.from_dna(sdna)] * 4

		self.enemy_target = None
		self.ally_target = self

	def update(self, dt):
		self.stamina += self.STAMINA_RATE * dt
		self.stamina = max(self.stamina, 1.0)

	def use_spell(self, idx):
		spell = self.spells[idx]

		for i in spell.effects:
			if i == 'damage':
				self.enemy_target.hp -= 1
			else:
				raise NotImplementedError(i)

	def end(self):
		self.object.endObject()


class Hero(Combatant):
	def __init__(self, location):
		super().__init__(engine.add_object("Player", location))

		ringloc = location[:]
		ringloc[2] += 1
		self.ring = engine.add_object("DodgeRing",ringloc)

	def end(self):
		super().end()
		self.ring.endObject()


class Enemy(Combatant):
	def __init__(self, location):
		super().__init__(engine.add_object("Player", location))


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

		logic.getCurrentScene().post_draw.append(self._render_bg)

		self.prev_time = time.time()

	def _render_bg(self):
		glMatrixMode(GL_TEXTURE)
		glPushMatrix()
		glLoadIdentity()
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		glLoadIdentity()
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()

		glColor3f(0.5, 1.0, 0.0)

		positions = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
		glBegin(GL_QUADS)
		for i in range(4):
			glVertex3f(positions[i][0], positions[i][1], 1)
		glEnd()

		glPopMatrix()
		glMatrixMode(GL_TEXTURE)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		glPopMatrix()

	def update(self):
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
				i.object.endObject()

		if not self.enemies:
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


g_combat = None


def init(cont):
	global g_combat

	g_combat = Combat()


def update(cont):
	global g_combat
	if g_combat is not None:
		g_combat.update()