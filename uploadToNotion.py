import os
import requests
import logging
from notion_client import Client
from dotenv import load_dotenv
from datetime import timedelta
from stravaTokenHandler import get_valid_access_token

# .env laden
load_dotenv()

# ENV Variablen
STRAVA_TOKEN = None
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

# Logging konfigurieren
logging.basicConfig(
    filename="strava.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Notion Client initialisieren
notion = Client(auth=NOTION_TOKEN)

# Prüfen, auf Duplikate
def is_already_logged(strava_id):
    query = {
        "database_id": NOTION_DB_ID,
        "filter": {
            "property": "Strava ID",
            "rich_text": {
                "equals": str(strava_id)
            }
        }
    }
    results = notion.databases.query(**query)
    return len(results["results"]) > 0

# Strava Token aktualisieren
def refresh_strava_token():
    logging.info("🔁 Aktualisiere Strava Access Token...")
    url = "https://www.strava.com/oauth/token"
    data = {
        "client_id": os.getenv("STRAVA_CLIENT_ID"),
        "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("STRAVA_REFRESH_TOKEN")
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    tokens = response.json()

    new_access_token = tokens["access_token"]
    new_refresh_token = tokens["refresh_token"]

    # Optional: neue Tokens in .env zurückschreiben oder speichern
    logging.info("✅ Neuer Access Token erhalten.")
    return new_access_token

# Zeit formatieren
def format_duration(seconds):
    t = timedelta(seconds=seconds)
    hours, remainder = divmod(t.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}min" if hours else f"{minutes}min"

# Aktivitäten laden
def get_strava_activities():
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {STRAVA_TOKEN}"}
    params = {"per_page": 10}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Aktivitäten speichern
def save_to_notion(activity):
    title = activity.get("name")
    date = activity.get("start_date_local")
    distance_km = round(activity.get("distance", 0) / 1000, 1)
    moving_time = activity.get("moving_time", 0)
    elapsed_time = activity.get("elapsed_time", 0)
    average_speed = round(activity.get("average_speed", 0) * 3.6, 1)
    max_speed = round(activity.get("max_speed", 0) * 3.6, 1)
    elevation_gain = round(activity.get("total_elevation_gain", 0))
    elevation_high = activity.get("elev_high")
    elevation_high = round(elevation_high) if elevation_high else None
    description = activity.get("description", "")
    strava_url = f"https://www.strava.com/activities/{activity.get('id')}"

    # Art of Bike zuweisen
    bike_type = activity.get("sport_type", "")

    if bike_type == "GravelRide":
        bike_category = "Gravel"
    elif bike_type == "Ride":
        bike_category = "Gravel"
    elif bike_type == "EBikeRide":
        bike_category = "E-MTB"
    elif bike_type in ["MountainBikeRide"]:
        bike_category = "MTB"
    else:
        bike_category = "Unbekannt"

    # Properties aufbauen
    props = {
        "Name": {"title": [{"text": {"content": title}}]},
        "Datum": {"date": {"start": date}},
        "Länge": {"number": distance_km},
        "Fahrzeit": {"rich_text": [{"text": {"content": format_duration(elapsed_time)}}]},
        "Dauer": {"rich_text": [{"text": {"content": format_duration(moving_time)}}]},
        "Ø - Geschw.": {"number": average_speed},
        "Max. Geschw.": {"number": max_speed},
        "Höhenm.": {"number": elevation_gain},
        "Strava URL": {"url": strava_url},
        "Art of Bike": {"select": {"name": bike_category}},
        "Strava ID": {"rich_text": [{"text": {"content": str(activity.get("id"))}}]},
    }

    if elevation_high is not None:
        props["Max. Höhe"] = {"number": elevation_high}
    if description:
        props["Bemerkung"] = {"rich_text": [{"text": {"content": description}}]}

    # Match Emoji
    emoji_map = {
        "MTB": "🚵",
        "Gravel": "🚴",
        "E-MTB": "🚵"
    }
    bike_emoji = emoji_map.get(bike_category, "🚴")

    # Seite in Notion erstellen
    notion.pages.create(parent={"database_id": NOTION_DB_ID}, properties=props, icon={"type":"emoji", "emoji":bike_emoji})

# Hauptfunktion
def main():
    activities = get_strava_activities()
    valid_bike_sports = ["Ride", "GravelRide", "MountainBikeRide", "EBikeRide"]

    for act in activities:
        sport = act.get("sport_type", "")
        if sport not in valid_bike_sports:
            logging.info(f"⏭ Überspringe {act.get('name')} ({sport}) – nicht relevant.")
            continue
        if is_already_logged(act["id"]):
            logging.info(f"⏭ {act['name']} – bereits eingetragen.")
            continue
        save_to_notion(act)
        logging.info(f"✅ Gespeichert: {act['name']}")

if __name__ == "__main__":
    logging.info("🔌 Skript start:")
    STRAVA_TOKEN = get_valid_access_token()
    main()
