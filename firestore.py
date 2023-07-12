import json
from google.cloud import firestore
from google.oauth2 import service_account

import streamlit as st


def get_secret(key):
    """Get secret from Streamlit secrets"""
    return st.secrets[key]


def get_firebase_client():
    """Get Firebase client"""
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(get_secret("textkey"))
    )
    client = firestore.Client(credentials=credentials, project=credentials.project_id)
    return client


fb_client = get_firebase_client()
