# usage:
#   Linux: python chkmodule.py "{modulename}"
#   Windows: py -3 chkmodule.py "{modulename}"

import sys
import importlib
try:
	module = importlib.import_module(sys.argv[1], package=None)
except ImportError as err:
	print(err)
	sys.exit(1)
print("YES, there is a module named \'{}\'".format(sys.argv[1]))
sys.exit(0)
