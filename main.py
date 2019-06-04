import sys

def add_paths():
	sys.path.insert(0, './gui')
	sys.path.insert(0, './helpers')
	sys.path.insert(0, './computation')

add_paths()	

import gui_manager as gui

if (__name__ == "__main__"):
	sys.setrecursionlimit(100000)

	gui.run_application()
