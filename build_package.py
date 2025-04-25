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
subprocess.run([sys.executable, "-m", "build"] + sys.argv[1:], check=True, stderr=sys.stderr, stdout=sys.stdout)
