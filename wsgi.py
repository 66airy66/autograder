import os, sys

# Put the parent folder (NOT autograder) on the path
parent = "/home/kanhampujar/tcx2003project"
if parent not in sys.path:
    sys.path.insert(0, parent)

# Env vars (use your real values)
os.environ["DB_HOST"] = "kanhampujar.mysql.pythonanywhere-services.com"
os.environ["DB_USER"] = "kanhampujar"
os.environ["DB_PASSWORD"] = "<sumit321>"
os.environ["DB_NAME"] = "kanhampujar$tcx2003"
os.environ["SECRET_KEY"] = "chingchong"
os.environ["FLASK_DEBUG"] = "0"

# DEBUG: prove we’re editing the right file
import sys as _sys
_sys.stderr.write("WSGI LOADED: using autograder\n")

# Import the Flask app **from the package**
from autograder.flask_app import app as application