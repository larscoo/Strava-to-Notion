import os
import requests
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

STRAVA_TOKEN = os.getenv("STRAVA_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")

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

if __name__ == "__main__":
    print("🔌 API Verbindungstest:")
    test_strava_connection()
    test_notion_connection()

    print("-" * 60)

    inspect_notion_database()
