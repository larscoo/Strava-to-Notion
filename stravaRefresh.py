import requests
import time

# Deine Daten von Strava
client_id = "130434"
client_secret = "5b88dd94fadaeadcedfd0aa556b14421da20b4b1"
refresh_token = "49bedbf0cb4c6f753838f61c9f69039aa443fdd1"

def get_access_token():
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )
    response_data = response.json()

    # Neue Tokens
    access_token = response_data["access_token"]
    expires_at = response_data["expires_at"]
    new_refresh_token = response_data["refresh_token"]  # den solltest du speichern

    return access_token, expires_at, new_refresh_token

# Beispielaufruf
access_token, expires_at, refresh_token = get_access_token()
print("Access Token:", access_token)
print("Gültig bis:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires_at)))
