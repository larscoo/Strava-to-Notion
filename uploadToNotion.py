import os
import requests
from notion_client import Client
from dotenv import load_dotenv
from datetime import timedelta

# .env laden
load_dotenv()

# ENV Variablen
STRAVA_TOKEN = os.getenv("STRAVA_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

# Notion Client initialisieren
notion = Client(auth=NOTION_TOKEN)

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

def format_duration(seconds):
    t = timedelta(seconds=seconds)
    hours, remainder = divmod(t.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}min" if hours else f"{minutes}min"

def get_strava_activities():
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {STRAVA_TOKEN}"}
    params = {"per_page": 10}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

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
    if "Gravel" or "Ride" in bike_type:
        bike_category = "Gravel"
    elif "E-Bike" in bike_type:
        bike_category = "E-MTB"
    else:
        bike_category = "MTB"

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

    # Seite in Notion erstellen
    notion.pages.create(parent={"database_id": NOTION_DB_ID}, properties=props)

# Hauptfunktion
def main():
    activities = get_strava_activities()
    valid_bike_sports = ["Ride", "GravelRide", "MountainBikeRide", "EBikeRide"]

    for act in activities:
        sport = act.get("sport_type", "")
        if sport not in valid_bike_sports:
            print(f"⏭ Überspringe {act.get('name')} ({sport}) – nicht relevant.")
            continue
        if is_already_logged(act["id"]):
            print(f"⏭ {act['name']} – bereits eingetragen.")
            continue
        save_to_notion(act)
        print(f"✅ Gespeichert: {act['name']}")

if __name__ == "__main__":
    print("🔌 Skript start:")
    main()
