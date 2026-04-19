import logging
import os
import sys
from datetime import timedelta

import requests
from notion_client import Client

from config import NOTION_TOKEN, SYNC_TARGETS
from stravaTokenHandler import get_valid_access_token

STRAVA_TOKEN = None

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/strava.log"),
        logging.StreamHandler(sys.stdout),
    ],
    force=True,
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("notion_client").setLevel(logging.WARNING)

notion = Client(auth=NOTION_TOKEN)


def send_discord_message(content):
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    if not webhook_url:
        logging.warning("📭 Kein Webhook gesetzt – Discord Nachricht wird übersprungen.")
        return

    try:
        response = requests.post(webhook_url, json={"content": content})
        if response.status_code == 204:
            logging.info("✅ Discord Nachricht gesendet.")
        else:
            logging.warning("⚠️ Discord Fehler: %s – %s", response.status_code, response.text)
    except Exception as exc:
        logging.error("❌ Fehler beim Senden an Discord: %s", exc)


def format_duration(seconds):
    tdelta = timedelta(seconds=seconds)
    total_seconds = int(tdelta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}min" if hours else f"{minutes}min"


def format_pace(distance_meters, moving_time_seconds):
    if not distance_meters or not moving_time_seconds:
        return None

    seconds_per_km = moving_time_seconds / (distance_meters / 1000)
    minutes = int(seconds_per_km // 60)
    seconds = int(round(seconds_per_km % 60))

    if seconds == 60:
        minutes += 1
        seconds = 0

    return f"{minutes}:{seconds:02d} /km"


def pace_to_minutes(distance_meters, moving_time_seconds):
    if not distance_meters or not moving_time_seconds:
        return None
    return round((moving_time_seconds / 60) / (distance_meters / 1000), 2)


def seconds_to_minutes(seconds):
    if seconds is None:
        return None
    return round(seconds / 60, 2)


def get_strava_activities():
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {STRAVA_TOKEN}"}
    params = {"per_page": 25}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_target_for_activity(activity):
    sport_type = activity.get("sport_type", "")

    for key, target in SYNC_TARGETS.items():
        if sport_type in target["sport_types"]:
            return key, target

    return None, None


def is_already_logged(database_id, strava_id):
    query = {
        "database_id": database_id,
        "filter": {
            "property": "Strava ID",
            "rich_text": {"equals": str(strava_id)},
        },
    }
    results = notion.databases.query(**query)
    return len(results["results"]) > 0


def build_common_properties(activity, distance_label):
    title = activity.get("name") or "Strava Aktivität"
    date = activity.get("start_date_local", "").split("T")[0]
    description = activity.get("description", "")
    distance_km = round(activity.get("distance", 0) / 1000, 1)
    moving_time = activity.get("moving_time", 0)
    elapsed_time = activity.get("elapsed_time", 0)
    elevation_gain = round(activity.get("total_elevation_gain", 0))
    strava_id = activity.get("id")
    strava_url = f"https://www.strava.com/activities/{strava_id}"

    props = {
        "Name": {"title": [{"text": {"content": title}}]},
        "Datum": {"date": {"start": date}},
        distance_label: {"number": distance_km},
        "Höhenm.": {"number": elevation_gain},
        "Dauer": {"rich_text": [{"text": {"content": format_duration(elapsed_time)}}]},
        "Strava URL": {"url": strava_url},
        "Strava ID": {"rich_text": [{"text": {"content": str(strava_id)}}]},
    }

    if description:
        props["Bemerkung"] = {"rich_text": [{"text": {"content": description}}]}

    return props


def build_bike_properties(activity):
    props = build_common_properties(activity, "Länge")
    moving_time = activity.get("moving_time", 0)
    average_speed = round(activity.get("average_speed", 0) * 3.6, 1)
    max_speed = round(activity.get("max_speed", 0) * 3.6, 1)
    elevation_high = activity.get("elev_high")
    sport_type = activity.get("sport_type", "")

    bike_type_map = {
        "GravelRide": "Gravel",
        "Ride": "Gravel",
        "EBikeRide": "E-MTB",
        "MountainBikeRide": "MTB",
    }
    bike_category = bike_type_map.get(sport_type, "Unbekannt")

    props.update(
        {
            "Fahrzeit": {"rich_text": [{"text": {"content": format_duration(moving_time)}}]},
            "Ø - Geschw.": {"number": average_speed},
            "Max. Geschw.": {"number": max_speed},
            "Art of Bike": {"select": {"name": bike_category}},
        }
    )

    if elevation_high is not None:
        props["Max. Höhe"] = {"number": round(elevation_high)}

    return props, {"type": "emoji", "emoji": {"MTB": "🚵", "Gravel": "🚴", "E-MTB": "🚵"}.get(bike_category, "🚴")}


def build_run_properties(activity):
    props = build_common_properties(activity, "Distanz")
    moving_time = activity.get("moving_time", 0)
    pace_minutes = pace_to_minutes(activity.get("distance", 0), moving_time)
    sport_type = activity.get("sport_type", "Run")
    average_hr = activity.get("average_heartrate")
    max_hr = activity.get("max_heartrate")
    elapsed_minutes = seconds_to_minutes(activity.get("elapsed_time", 0))
    moving_minutes = seconds_to_minutes(moving_time)

    props.update(
        {
            "Laufzeit": {"number": moving_minutes},
            "Dauer": {"number": elapsed_minutes},
            "Sportart": {"select": {"name": sport_type}},
        }
    )

    if pace_minutes is not None:
        props["Ø Pace"] = {"number": pace_minutes}
    if average_hr is not None:
        props["Avg HR"] = {"number": round(average_hr)}
    if max_hr is not None:
        props["Max HR"] = {"number": round(max_hr)}

    return props, {"type": "emoji", "emoji": "🏃"}


def build_notion_payload(target_key, activity):
    if target_key == "bike":
        return build_bike_properties(activity)
    if target_key == "run":
        return build_run_properties(activity)

    raise ValueError(f"Unbekanntes Sync-Target: {target_key}")


def save_to_notion(database_id, target_key, activity):
    properties, icon = build_notion_payload(target_key, activity)
    notion.pages.create(parent={"database_id": database_id}, properties=properties, icon=icon)


def validate_targets():
    missing_targets = [target["label"] for target in SYNC_TARGETS.values() if not target["database_id"]]
    if missing_targets:
        raise ValueError(
            "Fehlende Notion-DB Konfiguration für: " + ", ".join(missing_targets)
        )


def main():
    validate_targets()
    activities = get_strava_activities()
    saved_counts = {key: 0 for key in SYNC_TARGETS}

    for activity in activities:
        target_key, target = get_target_for_activity(activity)
        if not target:
            logging.info(
                "⏭ Überspringe %s (%s) – kein konfiguriertes Ziel.",
                activity.get("name"),
                activity.get("sport_type", ""),
            )
            continue

        title = (activity.get("name") or "").strip().upper()
        if title in target["excluded_titles"]:
            logging.info("⏭ Überspringe %s – ausgeschlossene Aktivität.", activity.get("name"))
            continue

        if is_already_logged(target["database_id"], activity["id"]):
            logging.info("⏭ %s – bereits in %s eingetragen.", activity["name"], target["label"])
            continue

        save_to_notion(target["database_id"], target_key, activity)
        logging.info("✅ Gespeichert: %s -> %s", activity["name"], target["label"])
        saved_counts[target_key] += 1

    messages = []
    if saved_counts["bike"]:
        count = saved_counts["bike"]
        text = "eine neue Strava-Fahrt" if count == 1 else f"{count} neue Strava-Fahrten"
        messages.append(f"🚴 {text} in Notion gespeichert.")
    if saved_counts["run"]:
        count = saved_counts["run"]
        text = "ein neuer Lauf" if count == 1 else f"{count} neue Läufe"
        messages.append(f"🏃 {text} in Notion gespeichert.")

    if messages:
        send_discord_message("\n".join(messages))


if __name__ == "__main__":
    logging.info("🔌 Skriptstart")
    STRAVA_TOKEN = get_valid_access_token()
    main()
