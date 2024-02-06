# dropbox_auth.py
import requests
import streamlit as st

def refresh_access_token(refresh_token):
    url = "https://api.dropboxapi.com/oauth2/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": st.secrets["APP_KEY"],
        "client_secret": st.secrets["APP_SECRET"]
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code ==  200:
        return response.json()
    else:
        raise Exception(f"Failed to refresh access token: {response.content}")


import requests

def exchange_auth_code_for_tokens(auth_code, app_key, app_secret):
    url = "https://api.dropboxapi.com/oauth2/token"
    payload = {
        "code": auth_code,
        "grant_type": "authorization_code",
        "client_id": app_key,
        "client_secret": app_secret
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code ==  200:
        return response.json()
    else:
        raise Exception(f"Failed to exchange authorization code: {response.content}")

# Example usage:
# Replace with your actual authorization code, app key, and app secret
auth_code = "lykG7GlvE0AAAAAAAAACh-jtezEKqzBBrdJnCEGGDVg"
app_key = "3m7zqkve4kxol9o"
app_secret = "5h7a836siq1whsq"

try:
    tokens = exchange_auth_code_for_tokens(auth_code, app_key, app_secret)
    print("Access Token:", tokens['access_token'])
    print("Refresh Token:", tokens['refresh_token'])
except Exception as e:
    print(e)