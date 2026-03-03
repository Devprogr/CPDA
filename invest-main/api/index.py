# api/index.py
import sys
import os

# Make sure the project root is in Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app  # this imports your app.py "app = Flask(...)"

# Vercel needs a variable named "app"