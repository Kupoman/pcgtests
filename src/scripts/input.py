from bge import events, logic
import enum


STATUS = enum.Enum('status', 'ACTIVE PRESS RELEASE INACTIVE')


_BGE_STATUS_MAP = {
	logic.KX_INPUT_ACTIVE: STATUS.ACTIVE,
	logic.KX_INPUT_JUST_ACTIVATED: STATUS.PRESS,
	logic.KX_INPUT_JUST_RELEASED: STATUS.RELEASE,
	logic.KX_INPUT_NONE: STATUS.INACTIVE,
}


def _conf_to_dict(conf):
	retval = {}

	for line in conf:
		line = line.strip()

		# Use semi-colons as comments
		if not line or line.startswith(';'):
			continue

		event, inputs = line.split('=')
		event = event.strip()

		for inp in inputs.split(','):
			inp = getattr(events, inp.strip())

			if inp in retval:
				retval[inp].append(event)
			else:
				retval[inp] = [event]

	return retval


class InputSystem:
	def __init__(self, conf_file):
		self.inputs = _conf_to_dict(conf_file)

	def run(self):
		evts = {}

		for inp, status in logic.keyboard.active_events.items():
			if inp in self.inputs:
				status = _BGE_STATUS_MAP[status]
				for evt in self.inputs[inp]:
					if evt in evts:
						print("Warning duplicate event {0} from {1}".format(evt, events.EventToString(inp)))
						continue
					evts[evt] = status

		for evtlist in self.inputs.values():
			for evt in evtlist:
				if evt not in evts:
					evts[evt] = STATUS.INACTIVE

		return evts
