'''
Functionality to switch spacing styles in Plover without having to open your config.
'''

BEFORE='Before Output'
AFTER='After Output'

from plover.engine import StenoEngine

def space_placement_toggle(engine: StenoEngine, _) -> None:
	'''
	Toggle the spacing type.
	'''

	if engine.config['space_placement'] == BEFORE:
		engine.config = { 'space_placement' : AFTER }
	else:
		engine.config = { 'space_placement' : BEFORE }

def space_placement_before(engine: StenoEngine, _) -> None:
	'''
	Set spacing to before.
	'''

	engine.config = { 'space_placement' : BEFORE }

def space_placement_after(engine: StenoEngine, _) -> None:
	'''
	Set spacing to after.
	'''

	engine.config = { 'space_placement' : AFTER }