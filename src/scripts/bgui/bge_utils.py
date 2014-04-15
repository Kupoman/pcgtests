from .system import System as BguiSystem
from .widget import Widget, BGUI_MOUSE_NONE, BGUI_MOUSE_CLICK, BGUI_MOUSE_RELEASE, BGUI_MOUSE_ACTIVE
from .text.blf import BlfTextLibrary
from . import key_defs
from bge import logic, events, render
import collections


class Layout(Widget):
	"""A base layout class to be used with the BGESystem"""

	def __init__(self, sys, data):
		"""
		:param sys: The BGUI system
		:param data: User data
		"""

		super().__init__(sys, size=[1,1])
		self.data = data

	def update(self):
		"""A function that is called by the system to update the widget (subclasses should override this)"""
		pass


class System(BguiSystem):
	"""A system that is intended to be used with BGE games"""

	def __init__(self, theme=None):
		"""
		:param theme: the path to a theme directory

		"""
		super().__init__(BlfTextLibrary(), theme)

		self.mouse = logic.mouse

		# All layouts will be a widget subclass, so we can just keep track of one widget
		self.layout = None

		# We can also add 'overlay' layouts
		self.overlays = collections.OrderedDict()

		# Now we generate a dict to map BGE keys to bgui keys
		self.keymap = {getattr(events, val): getattr(key_defs, val) for val in dir(events) if val.endswith('KEY') or val.startswith('PAD')}

		# Now setup the scene callback so we can draw
		logic.getCurrentScene().post_draw.append(self._render)

	def load_layout(self, layout, data=None):
		"""Load a layout and replace any previously loaded layout

		:param layout: The layout to load (None to have no layouts loaded)
		:param data: User data to send to the layout's constructor
		"""

		if self.layout:
			self._remove_widget(self.layout)

		if layout:
				self.layout = layout(self, data)
		else:
			self.layout = None

	def add_overlay(self, layout, data=None):
		"""Add an overlay layout, which sits on top of the currently loaded layout

		:param layout: The layout to add as an overlay
		:param data: User data to send to the layout's constructor"""

		if layout in self.overlays:
			print("Overlay: %s, is already added" % layout)
			return

		self.overlays[layout.__class__.__name__] = layout(self, data)

	def remove_overlay(self, overlay):
		"""Remove an overlay layout by name

		:param overlay: the class name of the overlay to remove (this is the same name as the layout used to add the overlay)
		"""

		if overlay in self.overlays:
			self._remove_widget(self.overlays[overlay])
			del self.overlays[overlay]
		else:
			print("WARNING: Overlay: %s was not found, nothing was removed" % overlay)

	def toggle_overlay(self, overlay):
		"""Toggle an overlay (if the overlay is active, remove it, otherwise add it)

		:param overlay: The class name of the layout to toggle
		"""

		if overlay in self.overlays:
			self.remove_overlay(overlay)
		else:
			self.add_overlay(overlay)

	def _render(self):
		try:
			super().render()
		except:
			# If there was a problem with rendering, stop so we don't spam the console
			import traceback
			traceback.print_exc()
			logic.getCurrentScene().post_draw.remove(self._render)

	def run(self):
		"""A high-level method to be run every frame"""

		if not self.layout:
			return

		# Update the layout and overlays
		self.layout.update()

		for key, value in self.overlays.items():
			value.update()

		# Handle the mouse
		mouse = self.mouse
		mouse_events = mouse.events

		pos = list(mouse.position[:])
		pos[0] *= render.getWindowWidth()
		pos[1] = render.getWindowHeight() - (render.getWindowHeight() * pos[1])

		if mouse_events[events.LEFTMOUSE] == logic.KX_INPUT_JUST_ACTIVATED:
			mouse_state = BGUI_MOUSE_CLICK
		elif mouse_events[events.LEFTMOUSE] == logic.KX_INPUT_JUST_RELEASED:
			mouse_state = BGUI_MOUSE_RELEASE
		elif mouse_events[events.LEFTMOUSE] == logic.KX_INPUT_ACTIVE:
			mouse_state = BGUI_MOUSE_ACTIVE
		else:
			mouse_state = BGUI_MOUSE_NONE

		self.update_mouse(pos, mouse_state)

		# Handle the keyboard
		keyboard = logic.keyboard

		key_events = keyboard.events
		is_shifted = key_events[events.LEFTSHIFTKEY] == logic.KX_INPUT_ACTIVE or \
					key_events[events.RIGHTSHIFTKEY] == logic.KX_INPUT_ACTIVE

		for key, state in keyboard.events.items():
			if state == logic.KX_INPUT_JUST_ACTIVATED:
				self.update_keyboard(self.keymap[key], is_shifted)