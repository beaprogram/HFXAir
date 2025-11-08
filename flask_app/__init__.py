import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("config/testing-hfxair-firebase-adminsdk-fbsvc-c584fb82ef.json")
firebase_admin.initialize_app(cred)
