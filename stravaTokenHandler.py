import os
import json
import time
import logging
import requests
from dotenv import load_dotenv

# .env laden
load_dotenv()

# Konstante Datei mit gespeicherten Tokens
TOKEN_FILE = "stravaToken.json"

# CLIENT Daten aus .env
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")


def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError("❌ Token-Datei nicht gefunden. Bitte manuell initialisieren.")
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

def save_tokens(token_data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)

def is_token_expired(token_data):
    return int(token_data.get("expires_at", 0)) <= int(time.time())

def refresh_token(token_data):
    logging.info("🔁 Access Token abgelaufen – Aktualisierung wird durchgeführt...")
    url = "https://www.strava.com/oauth/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": token_data["refresh_token"]
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    new_tokens = response.json()

    updated_token_data = {
        "access_token": new_tokens["access_token"],
        "refresh_token": new_tokens["refresh_token"],
        "expires_at": new_tokens["expires_at"]
    }
    save_tokens(updated_token_data)
    logging.info("✅ Access Token aktualisiert und gespeichert.")
    return updated_token_data

def get_valid_access_token():
    token_data = load_tokens()
    if is_token_expired(token_data):
        token_data = refresh_token(token_data)
    return token_data["access_token"]


# Beispiel-Aufruf
if __name__ == "__main__":
    access_token = get_valid_access_token()
    logging.info("🔐 Aktueller Access Token:", access_token)
