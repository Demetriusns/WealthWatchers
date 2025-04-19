import sys
import os

# Add the virtual environment to the path
sys.path.insert(0, "C:/Program Files/Ampps/www/WealthWatcher")
sys.path.insert(1, "C:/Program Files/Ampps/WealthWatcher_venv/Lib/site-packages")

from app import app as application