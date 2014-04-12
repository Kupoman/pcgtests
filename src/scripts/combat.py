from bge import logic, events
from bgl import *
from scripts import engine
import time


class Combatant:
	STAMINA_RATE = 0.25
	DODGE_COST = 0.3

	def __init__(self, kxobj):
		self.object = kxobj
		self.stamina = 0
		self.hp = 3

	def update(self, dt):
		self.stamina += self.STAMINA_RATE * dt
		self.stamina = max(self.stamina, 1.0)


class Combat:
	def __init__(self):
		self.main = logic.getSceneList()[0].objects["Main"]
		self.player = Combatant(engine.add_object("Player", (8, 2, 0)))
		self.pring = engine.add_object("DodgeRing", (8, 2, 1))
		self.enemies = [
			Combatant(engine.add_object("Player", (-8, 7, 0))),
			Combatant(engine.add_object("Player", (-8, 2, 0))),
			Combatant(engine.add_object("Player", (-8, -3, 0))),
		]

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

		for i in self.enemies + [self.player]:
			i.update(dt)

		if evts[events.SPACEKEY] == logic.KX_INPUT_ACTIVE:
			logic.getSceneList()[0].resume()
			self.main["encounter_scene"] = False
			logic.getCurrentScene().end()


g_combat = None


def init(cont):
	global g_combat

	print("Combat init")
	g_combat = Combat()


def update(cont):
	global g_combat
	if g_combat is not None:
		g_combat.update()