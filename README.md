# Strava -> Notion Sync

Synchronisiert Strava-Aktivitäten nach Notion. Aktuell unterstützt das Projekt:

- Bike-Aktivitäten in eine Bike-DB
- Running-Aktivitäten in eine separate Run-DB
- monatliche Zusammenfassungen per Discord

![Notion Beispiel](./data/notion-bike-db.png)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## `.env`

```env
STRAVA_CLIENT_ID=deine_strava_client_id
STRAVA_CLIENT_SECRET=dein_strava_client_secret
NOTION_TOKEN=dein_notion_integration_token
NOTION_DB_ID_BIKE=deine_bike_datenbank_id
NOTION_DB_ID_RUN=deine_run_datenbank_id
DISCORD_WEBHOOK=https://discord.com/api/webhooks/xyz
```

Die Strava-Tokens liegen weiterhin in `stravaToken.json` und werden über `stravaTokenHandler.py` aktualisiert.

## Ausführen

```bash
python uploadToNotion.py
```

Das Skript lädt die letzten 25 Strava-Aktivitäten und routet sie anhand von `sport_type` automatisch in die passende Notion-Datenbank:

- Bike: `Ride`, `GravelRide`, `MountainBikeRide`, `EBikeRide`
- Run: `Run`, `TrailRun`, `VirtualRun`

## Empfohlene Notion-Struktur

### Bike-DB

- `Name` (Title)
- `Datum` (Date)
- `Länge` (Number)
- `Höhenm.` (Number)
- `Fahrzeit` (Text)
- `Dauer` (Text)
- `Ø - Geschw.` (Number)
- `Max. Geschw.` (Number)
- `Art of Bike` (Select)
- `Max. Höhe` (Number, optional)
- `Bemerkung` (Text, optional)
- `Strava URL` (URL)
- `Strava ID` (Text)

### Run-DB

- `Name` (Title)
- `Datum` (Date)
- `Distanz` (Number)
- `Höhenm.` (Number)
- `Laufzeit` (Text)
- `Dauer` (Text)
- `Ø Pace` (Text)
- `Sportart` (Select)
- `Avg HR` (Number, optional)
- `Max HR` (Number, optional)
- `Bemerkung` (Text, optional)
- `Strava URL` (URL)
- `Strava ID` (Text)

## Monatsbericht

```bash
python monthlyReport.py
```

Der Report aggregiert Bike und Run getrennt über ihre jeweiligen Notion-Datenbanken und sendet eine gemeinsame Discord-Nachricht.

## Server-Setup

Empfohlener Ablauf:

1. Repo einmal auf den Server klonen, z. B. nach `/opt/strava-to-notion`
2. `.venv`, `.env` und `stravaToken.json` dort einmalig einrichten
3. Änderungen nur noch per `git pull` ausrollen

Deploy auf dem Server:

```bash
cd /opt/strava-to-notion
bash deploy.sh
```

`deploy.sh` macht:

- `git pull --ff-only`
- `pip install -r requirements.txt`
- Syntax-Check der Python-Dateien

Die produktiven Secrets bleiben auf dem Server in:

- `.env`
- `stravaToken.json`

## Cronjob

Für Cron liegen zwei Wrapper-Skripte im Repo:

- `run_sync.sh`
- `run_monthly_report.sh`

Beispiel:

```cron
*/30 * * * * cd /opt/strava-to-notion && bash run_sync.sh >> logs/cron.log 2>&1
0 8 1 * * cd /opt/strava-to-notion && bash run_monthly_report.sh >> logs/cron.log 2>&1
```

Damit zeigt dein Cronjob immer auf stabile Wrapper-Skripte und nicht direkt auf einzelne Python-Dateien.

## Optionaler schneller Deploy von lokal

Wenn du per SSH auf den Server kommst, reicht künftig:

```bash
ssh dein-server 'cd /opt/strava-to-notion && bash deploy.sh'
```

## Privates Repo auf Ubuntu Server

Für ein privates Repo ist SSH mit einem Deploy Key die einfachste Variante.

Auf dem Server:

```bash
ssh-keygen -t ed25519 -C "strava-server"
cat ~/.ssh/id_ed25519.pub
```

Den ausgegebenen Public Key dann im privaten GitHub- oder GitLab-Repo als Deploy Key hinterlegen.

Test:

```bash
ssh -T git@github.com
```

Danach kannst du das Repo direkt klonen:

```bash
git clone git@github.com:USER/REPO.git
```

Wenn du mehrere SSH-Keys auf dem Server verwendest, hilft zusätzlich eine `~/.ssh/config`.

## Struktur

- [uploadToNotion.py](/Volumes/fhgr/Code-Projekte/Strava-to-Notion/uploadToNotion.py)
- [monthlyReport.py](/Volumes/fhgr/Code-Projekte/Strava-to-Notion/monthlyReport.py)
- [config.py](/Volumes/fhgr/Code-Projekte/Strava-to-Notion/config.py)
- [stravaTokenHandler.py](/Volumes/fhgr/Code-Projekte/Strava-to-Notion/stravaTokenHandler.py)
- [deploy.sh](/Volumes/fhgr/Code-Projekte/Strava-to-Notion/deploy.sh)
- [run_sync.sh](/Volumes/fhgr/Code-Projekte/Strava-to-Notion/run_sync.sh)
- [run_monthly_report.sh](/Volumes/fhgr/Code-Projekte/Strava-to-Notion/run_monthly_report.sh)
