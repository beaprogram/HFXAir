import firebase_admin
from firebase_admin import credentials
import os
from pathlib import Path

# Get Firebase credentials path from environment variable or use default
firebase_creds_path = os.getenv(
    'FIREBASE_CREDENTIALS_PATH',
    'config/testing-hfxair-firebase-adminsdk-fbsvc-c584fb82ef.json'
)

# Convert to absolute path if relative
if not os.path.isabs(firebase_creds_path):
    firebase_creds_path = Path(__file__).parent / firebase_creds_path

cred = credentials.Certificate(str(firebase_creds_path))
firebase_admin.initialize_app(cred)
