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
NOTION_TOKEN=dein_notion_integration_token
NOTION_DB_ID=deine_notion_datenbank_id
```

> ℹ️ Hol dir dein `access_token` von Strava über OAuth:  
> [Strava OAuth Anleitung ↗](https://developers.strava.com/docs/getting-started/#oauth)

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
  ```

---

## 🙌 Inspiration

Dieses Projekt ist ideal für alle, die:
- ihre Bike-Aktivitäten gerne tracken & auswerten 📊
- Notion als zentrales Dashboard nutzen
- einen schönen Überblick über ihre Touren wünschen 🌄

---

## 🛠 ToDo

- [ ] Token automatisch per `refresh_token` verlängern
- [ ] Discord Push wenn erfolgreich
