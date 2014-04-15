from bge import logic, render, events

import scripts.bgui as bgui
import scripts.bgui.bge_utils as bgui_bge_utils

from scripts.player_data import PlayerData

from collections import OrderedDict


class Menu(bgui.ListBox):
	class MenuItemRenderer(bgui.ListBoxRenderer):
		def __init__(self, lb):
			super().__init__(lb)
			self.lb = lb

		def render_item(self, item):
			text = "> " if self.lb.selected == item else "   "
			self.label.text = text + str(item)
			return self.label

	def __init__(self, parent, menu_options, size=[1,1], pos=[0,0], options=0):
		super().__init__(parent, items=menu_options, size=size, pos=pos, options=options)
		self.renderer = self.MenuItemRenderer(self)
		self.selected = self.items[0]

	def _handle_mouse(self, pos, event):
		bgui.Widget._handle_mouse(self, pos, event)


class Title(bgui_bge_utils.Layout):
	def __init__(self, sys, data):
		super().__init__(sys, data)

		self.menu_options = OrderedDict([
			("New Character", self.new_char),
			("Load Character", self.new_char),
			("Exit", self.exit),
		])

		self.title = bgui.Label(self, text="pcgtest", pt_size=72, pos=[0.1, 0.7])
		self.menu = Menu(self, list(self.menu_options.keys()), size=[0.8, 0.3], pos=[0.15, 0.3])

	def update(self):
		evts = logic.keyboard.events

		if evts[events.ENTERKEY] == logic.KX_INPUT_JUST_ACTIVATED or \
			evts[events.SPACEKEY] == logic.KX_INPUT_JUST_ACTIVATED:
			self.menu_select()
		if evts[events.DOWNARROWKEY] == logic.KX_INPUT_JUST_ACTIVATED:
			self.menu_down()
		if evts[events.UPARROWKEY] == logic.KX_INPUT_JUST_ACTIVATED:
			self.menu_up()

	def menu_select(self):
		self.menu_options[self.menu.selected]()

	def menu_down(self):
		sidx = self.menu.items.index(self.menu.selected)
		sidx = (sidx + 1) % len(self.menu_options)
		self.menu.selected = self.menu.items[sidx]

	def menu_up(self):
		sidx = self.menu.items.index(self.menu.selected)
		sidx -= 1
		self.menu.selected = self.menu.items[sidx]

	def new_char(self):
		self.data.ui.load_layout(NewCharacter, self.data)

	def exit(self):
		logic.endGame()


class NewCharacter(bgui_bge_utils.Layout):
	def __init__(self, sys, data):
		super().__init__(sys, data)


		bgui.Label(self, text="New Student Registration", pt_size=48, pos=[0, 0.8], options=bgui.BGUI_CENTERX)
		self.student_name = bgui.TextInput(self, prefix="Name: ", text="Enter a name", size=[0.8, 0.05], pos=[0, 0.6], options=bgui.BGUI_CENTERX | bgui.BGUI_INPUT_SELECT_ALL)
		self.done_btn = bgui.Label(self, text="Done", pos=[0, 0.4], options=bgui.BGUI_CENTERX)

		self.menu_options = OrderedDict([
			(0, (self.student_name, self.name_enter, self.name_exit)),
			(1, (self.done_btn, self.done_enter, None)),
		])

		self.selected = 0
		self.entered = False

		# Setup highlight
		self.highlight = bgui.Frame(self, options=bgui.BGUI_NO_NORMALIZE)
		self.highlight.colors = [[0.8, 0.8, 0.8, 0.8]] * 4

	def update(self):
		evts = logic.keyboard.events

		if self.entered:
			if evts[events.ENTERKEY] == logic.KX_INPUT_JUST_ACTIVATED:
				self.entered = False
				self.menu_options[self.selected][2]()
		else:
			if evts[events.ENTERKEY] == logic.KX_INPUT_JUST_ACTIVATED:
				self.entered = True
				self.menu_options[self.selected][1]()
			if evts[events.DOWNARROWKEY] == logic.KX_INPUT_JUST_ACTIVATED:
				self.selected = (self.selected + 1) % len(self.menu_options)
			if evts[events.UPARROWKEY] == logic.KX_INPUT_JUST_ACTIVATED:
				self.selected -= 1
				if self.selected < 0:
					self.selected = 0

			highlight_widget = self.menu_options[self.selected][0]
			self.highlight.size = highlight_widget.size
			self.highlight.position = highlight_widget.position

	def name_enter(self):
		self.highlight.visible = False
		self.student_name.activate()

	def name_exit(self):
		self.highlight.visible = True
		self.student_name.deactivate()

	def done_enter(self):
		logic.globalDict['player_data'] = PlayerData.new(self.student_name.text)
		act = self.data.controller.actuators['StartGame']
		self.data.controller.activate(act)


class PreGame:
	def __init__(self, cont):
		self.ui = bgui_bge_utils.System()
		self.ui.load_layout(Title, self)
		self.controller = cont

	def update(self):
		self.ui.run()


def update(cont):
	main = cont.owner
	if 'PreGame' not in main:
		main['PreGame'] = PreGame(cont)

	main['PreGame'].update()