# 🚴‍♂️ Strava ➜ Notion Sync

Automatisiere den Import deiner Strava-Mountainbike-Fahrten direkt in deine Notion-Datenbank – inklusive Distanz, Dauer, Höhenmeter, Ø-Geschwindigkeit und mehr. Ideal für dein persönliches Bike-Logbuch 🗂️

![Notion Beispiel](./data/notion-bike-db.png)

---

## ✨ Features

- 🚀 Lädt automatisch die letzten Fahrten aus Strava
- 🧠 Konvertiert Werte wie Distanz, Geschwindigkeit und Zeitformate
- 🗂️ Schreibt strukturierte Einträge in deine Notion-Tabelle
- 🔁 Unterstützt Gravel, MTB & E-MTB
- 🔒 Sichere Authentifizierung über `.env`
- 📅 Optional als Cronjob ausführbar

---

## 🧱 Anforderungen

- Python 3.8+
- Strava Developer Account & API-Zugang
- Notion Developer Token & geteilte Datenbank

---

## 🔧 Installation

```bash
git clone https://github.com/deinname/strava-to-notion.git
cd strava-to-notion
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📁 `.env` Beispiel

Erstelle im Projektverzeichnis eine Datei `.env`:

```env
STRAVA_TOKEN=dein_strava_access_token
STRAVA_CLIENT_ID=deine_strava_client_id
STRAVA_CLIENT_SECRET=dein_strava_client_secret
NOTION_TOKEN=dein_notion_integration_token
NOTION_DB_ID=deine_notion_datenbank_id
DISCORD_WEBHOOK=https://discord.com/api/webhooks/xyz

```

> ℹ️ Hol dir dein `access_token` von Strava über OAuth:  
> [Strava OAuth Anleitung ↗](https://developers.strava.com/docs/getting-started/#oauth)


**Automatisches aktualisieren des Access Token's (manuell)**

Im Terminal folgenden Befehl absetzen:
```bash
curl -X POST https://www.strava.com/oauth/token \
  -F client_id=strava_client_id \
  -F client_secret=strava_client_secret \
  -F code=strava_access_code \
  -F grant_type=authorization_code
```

Die Antwort sieht dann folgendermassen aus:
```bash
{"token_type":"Bearer","expires_at":1753228041,"expires_in":21600,"refresh_token":"token","access_token":"token","athlete":{"id":90841942,"username":"larscools","resource_state":2,"firstname":"Lars","lastname":"Cools","bio":null,"city":"Glarus","state":"","country":"Switzerland","sex":"M","premium":false,"summit":false,"created_at":"2021-08-19T12:26:50Z","updated_at":"2025-07-17T13:58:32Z","badge_type_id":0,"weight":0.0,"profile_medium":"https://dgalywyr863hv.cloudfront.net/pictures/athletes/90841942/25554900/2/medium.jpg","profile":"https://dgalywyr863hv.cloudfront.net/pictures/athletes/90841942/25554900/2/large.jpg","friend":null,"follower":null}}
```

→ beinhaltet refresh_token und access_token<br>
→ mit refresh_token kann ein neuer Token generiert werden, wenn dieser abgelaufen ist

---

## ▶️ Ausführen

```bash
python uploadToNotion.py
```

Die letzten 10 Fahrten werden (falls `type == "Ride"`) in Notion übernommen.

---

## 🧪 Notion Datenbankstruktur

- Name
- Datum
- Länge (km)
- Höhenmeter (m)
- Ø - Geschwindigkeit
- Maximale Geschwindigkeit
- Fahrzeit
- Dauer
- Bemerkung
- Strava URL
- Strava ID

> ✅ Stelle sicher, dass deine Spaltennamen und Typen in Notion exakt zur Struktur im Skript passen.

---

## 🔄 Automatisieren (optional)

Füge dem Crontab folgenden Eintrag hinzu, um das Skript täglich auszuführen:

```bash
crontab -e
```

```cron
0 8 * * * /pfad/zum/.venv/bin/python /pfad/zum/strava-to-notion/uploadToNotion.py
```

---

## 🛡 Sicherheit

- Dein `.env`-File sollte **nicht** ins Repository! Füge dies zur `.gitignore` hinzu:
  ```
  .env
  .venv/
  .idea/
  ```

---

## 🙌 Inspiration

Dieses Projekt ist ideal für alle, die:
- ihre Bike-Aktivitäten gerne tracken & auswerten 📊
- Notion als zentrales Dashboard nutzen
- einen schönen Überblick über ihre Touren wünschen 🌄
