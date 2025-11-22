import pytest
import sys
import os

# Add the group01 directory (parent of flask_app) to the path so we can import flask_app package
group01_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if group01_dir not in sys.path:
    sys.path.insert(0, group01_dir)

from flask_app.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()
