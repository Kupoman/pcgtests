from bge import events, logic
import enum
import os
import sys


STATUS = enum.Enum('status', 'ACTIVE PRESS RELEASE INACTIVE')


_BGE_STATUS_MAP = {
	logic.KX_INPUT_ACTIVE: STATUS.ACTIVE,
	logic.KX_INPUT_JUST_ACTIVATED: STATUS.PRESS,
	logic.KX_INPUT_JUST_RELEASED: STATUS.RELEASE,
	logic.KX_INPUT_NONE: STATUS.INACTIVE,
}

_JOYEVENTS = [
	"DPAD_UP",
	"DPAD_DOWN",
	"DPAD_LEFT",
	"DPAD_RIGHT",

	"X_BUTTON",
	"Y_BUTTON",
	"A_BUTTON",
	"B_BUTTON",

	"LEFT_BUMPER",
	"LEFT_TRIGGER",
	"RIGHT_BUMPER",
	"RIGHT_TRIGGER",
]


def _conf_to_dict(conf, convert_input):
	retval = {}

	for line in conf:
		line = line.strip()

		# Use semi-colons as comments
		if not line or line.startswith(';'):
			continue

		try:
			event, inputs = line.split('=')
		except ValueError:
			print("Invalid line: {0}".format(line))
			continue

		event = event.strip()

		for inp in inputs.split(','):
			inp = inp.strip()

			if convert_input:
				cinp = getattr(events, inp, None)

				if cinp is None:
					# The input wasn't in bge.events, check for joystick events
					if inp in _JOYEVENTS:
						cinp = inp
					else:
						print("Warning, unsupported input: {0}".format(inp))
						continue

				inp = cinp

			if inp in retval:
				retval[inp].append(event)
			else:
				retval[inp] = [event]

	return retval


class InputSystem:
	def __init__(self, conf_file, joy_conf_dir='', print_joy=False):
		self.inputs = _conf_to_dict(conf_file, True)

		# Configure joystick if it's available
		if logic.joysticks[0]:
			joy_conf_dir = os.path.join(joy_conf_dir, sys.platform)
			if print_joy:
				print("Found joystick:", logic.joysticks[0].name)
			confname = logic.joysticks[0].name + '.conf'
			confpath = os.path.join(joy_conf_dir, confname)
			if confname in os.listdir(joy_conf_dir):
				with open(confpath) as f:
					self._joyconf = _conf_to_dict(f, False)
			else:
				if print_joy:
					print('Warning, no joystick config found at "{0}"'.format(confpath))
				self._joyconf = None
		else:
			self._joyconf = None

		self._last_joy_events = {}

	def run(self):
		evts = {}

		def check_events(event_dict, convert_status):
			for inp, status in event_dict.items():
				if inp in self.inputs:
					if convert_status:
						status = _BGE_STATUS_MAP[status]
					for evt in self.inputs[inp]:
						if evt in evts:
							print("Warning duplicate event {0} from {1}".format(evt, events.EventToString(inp)))
							continue
						evts[evt] = status

		# Keyboard
		check_events(logic.keyboard.active_events, True)

		# Joystick
		if self._joyconf is not None:
			# Translate raw events to our generic events
			gevts = {}
			def add_gevt(name, evttype):
				gevtlist = self._joyconf.get(name)

				if gevtlist is not None:
					for gevt in gevtlist:
						gevts[gevt] = STATUS.ACTIVE if gevt in self._last_joy_events else STATUS.PRESS
				else:
					print("Warning, unmapped {0}: {1}".format(name, evttype))

			for btn in logic.joysticks[0].activeButtons:
				add_gevt('BUTTON.' + str(btn), 'button')

			for idx, hat in enumerate(logic.joysticks[0].hatValues):
				add_gevt('HAT.' + str(idx) + "." + str(hat), 'hat')

			for axis, value in enumerate(logic.joysticks[0].axisValues):
				if value > 0.1:
					print(value)
					add_gevt('AXIS.' + str(axis) + '.POS', 'axis')
				elif value < -0.1:
					print(value)
					add_gevt('AXIS.' + str(axis) + '.NEG', 'axis')

			# Handle RELEASE events
			for evt in self._last_joy_events:
				if evt not in gevts and self._last_joy_events[evt] == STATUS.ACTIVE:
					gevts[evt] = STATUS.RELEASE

			self._last_joy_events = gevts

			# Now process the generic events
			check_events(gevts, False)

		# Inactive events
		for evtlist in self.inputs.values():
			for evt in evtlist:
				if evt not in evts:
					evts[evt] = STATUS.INACTIVE

		return evts
