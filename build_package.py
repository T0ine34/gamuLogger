"""
This script builds a Python package using the `build` module.
It allows for passing additional arguments to the build command and
supports specifying a version number via command line arguments.
It also sets the `PACKAGE_VERSION` environment variable if a version is provided.
"""

import os
import subprocess
import sys

if "--version" in sys.argv:
    idx = sys.argv.index("--version")
    version = sys.argv[idx + 1]
    os.environ["PACKAGE_VERSION"] = version
    sys.argv.pop(idx)  # remove --version
    sys.argv.pop(idx)  # remove version value

print(f"{sys.executable} -m build {' '.join(sys.argv[1:])}")
subprocess.run([sys.executable, "-m", "build"] + sys.argv[1:],
               check=True, stderr=sys.stderr, stdout=sys.stdout)
