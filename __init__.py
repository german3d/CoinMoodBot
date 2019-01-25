import os
import sys


parent_path = os.path.abspath(os.curdir)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)
