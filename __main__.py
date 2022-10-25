# -*- coding: utf-8 -*-

from GuiSM import *
import sys

##############################

if __name__ == "__main__":
    
	App = Application()
	
	if len(sys.argv) > 1:
		with open(mode='r', file=sys.argv[1])  as entryFile:
			App.fileName.configure(text=f'File : {entryFile.name}')
			App.file = entryFile.read()

	App.mainloop()
