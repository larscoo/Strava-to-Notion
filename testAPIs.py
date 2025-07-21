import os
import requests
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

STRAVA_TOKEN = os.getenv("STRAVA_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

notion = Client(auth=NOTION_TOKEN)

def test_strava_connection():
    url = "https://www.strava.com/api/v3/athlete"
    headers = {"Authorization": f"Bearer {STRAVA_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("✅ Strava-Verbindung erfolgreich!")
        print("👤 Athlete:", response.json().get("username", "Unbekannt"))
    else:
        print("❌ Fehler bei Strava-Verbindung:", response.status_code)
        print(response.text)


def test_notion_connection():
    try:
        db_info = notion.databases.retrieve(database_id=NOTION_DB_ID)
        print("✅ Notion-Verbindung erfolgreich!")
        print("📊 Datenbank-Name:", db_info['title'][0]['text']['content'])
    except Exception as e:
        print("❌ Fehler bei Notion-Verbindung:", e)


def inspect_notion_database():
    try:
        db_info = notion.databases.retrieve(database_id=NOTION_DB_ID)
        print("📋 Spalten in deiner Notion-Datenbank:")
        for key, prop in db_info["properties"].items():
            name = prop["name"]
            typ = prop["type"]
            print(f"🔸 {name} (Typ: {typ})")
    except Exception as e:
        print("❌ Fehler beim Abrufen der Datenbankstruktur:", e)


def test_discord_webhook():
    if not DISCORD_WEBHOOK_URL:
        print("❌ Kein Webhook-URL gefunden. Bitte in der .env-Datei setzen.")
        return

    message = {"content": "✅ Discord-Webhook-Test erfolgreich!"}

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=message)
        if response.status_code == 204:
            print("✅ Nachricht erfolgreich an Discord gesendet!")
        else:
            print(f"❌ Fehler beim Senden: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print("❌ Ausnahme beim Senden:", e)

if __name__ == "__main__":
    print("🔌 API Verbindungstest:")
    print("Strava:")
    test_strava_connection()
    print("Discord:")
    test_discord_webhook()
    print("Notion:")
    test_notion_connection()
    print("-" * 60)
    inspect_notion_database()
