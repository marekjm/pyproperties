#!/usr/bin/env python3

import sys, shutil, os

install_location = ""

for path in sys.path:
    path = path.split("/")
    if path[-1] == "site-packages" and path[1] != "home": 
        install_location = "/".join(path)
        break

print("./modules/pyproperties.py -> {0}\t".format(os.path.join(install_location, "pyproperties.py")), end="")
try:
    shutil.copy("./modules/pyproperties.py", install_location)
    print("[ OK ]")
except PermissionError as e:
    print("[FAIL]")
    raise
finally:
    pass
