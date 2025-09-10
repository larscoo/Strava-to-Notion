import os
import requests
from notion_client import Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging

# .env laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/monthly_report.log"),
        logging.StreamHandler()
    ]
)

# Notion Setup
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
notion = Client(auth=NOTION_TOKEN)

# Discord
def send_discord_message(content):
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    if not webhook_url:
        logging.warning("Kein Discord Webhook gefunden.")
        return
    payload = {"content": content}
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            logging.info("✅ Monatsbericht an Discord gesendet.")
        else:
            logging.warning(f"⚠️ Discord Fehler: {response.status_code} – {response.text}")
    except Exception as e:
        logging.error(f"❌ Fehler beim Senden an Discord: {e}")

# Bericht generieren
def generate_monthly_report():
    today = datetime.today()
    first_day = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day = today.replace(day=1) - timedelta(days=1)

    logging.info(f"📆 Bericht für {first_day.strftime('%B %Y')} wird erstellt...")

    filter_query = {
        "database_id": NOTION_DB_ID,
        "filter": {
            "and": [
                {
                    "property": "Datum",
                    "date": {
                        "on_or_after": first_day.strftime("%Y-%m-%d")
                    }
                },
                {
                    "property": "Datum",
                    "date": {
                        "on_or_before": last_day.strftime("%Y-%m-%d")
                    }
                }
            ]
        }
    }

    results = notion.databases.query(**filter_query)
    if not results["results"]:
        logging.info("ℹ️ Keine Aktivitäten im letzten Monat gefunden.")
        return

    stats = {}
    for page in results["results"]:
        props = page["properties"]
        bike = props["Art of Bike"].get("select", {}).get("name", "Unbekannt")
        dist = props["Länge"].get("number", 0)
        elev = props["Höhenm."].get("number", 0)

        if bike not in stats:
            stats[bike] = {"fahrten": 0, "km": 0.0, "hm": 0}
        stats[bike]["fahrten"] += 1
        stats[bike]["km"] += dist or 0
        stats[bike]["hm"] += elev or 0

    month_str = first_day.strftime("%B %Y")
    msg_lines = [f"**📆 Monatsbericht – {month_str}**"]

    emoji_map = {"MTB": "🚵", "Gravel": "🚴", "E-MTB": "⚡🚵"}

    for bike, data in stats.items():
        emoji = emoji_map.get(bike, "🚴")
        msg_lines.append(
            f"{emoji} **{bike}:** {data['fahrten']} Fahrten | {round(data['km'])}km | {data['hm']}höm"
        )

    discord_msg = "\n".join(msg_lines)
    send_discord_message(discord_msg)

# Start
if __name__ == "__main__":
    logging.info("🔁 Starte Monatsbericht...")
    generate_monthly_report()
