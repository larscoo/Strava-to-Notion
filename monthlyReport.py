import logging
import os
import sys
from datetime import datetime, timedelta

import requests
from notion_client import Client

from config import NOTION_TOKEN, SYNC_TARGETS

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/monthly_report.log"),
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
        logging.warning("Kein Discord Webhook gefunden.")
        return

    try:
        response = requests.post(webhook_url, json={"content": content})
        if response.status_code == 204:
            logging.info("✅ Monatsbericht an Discord gesendet.")
        else:
            logging.warning("⚠️ Discord Fehler: %s – %s", response.status_code, response.text)
    except Exception as exc:
        logging.error("❌ Fehler beim Senden an Discord: %s", exc)


def get_previous_month_date_range():
    today = datetime.today()
    first_day = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day = today.replace(day=1) - timedelta(days=1)
    return first_day, last_day


def query_monthly_pages(database_id, start_date, end_date):
    return notion.databases.query(
        database_id=database_id,
        filter={
            "and": [
                {"property": "Datum", "date": {"on_or_after": start_date}},
                {"property": "Datum", "date": {"on_or_before": end_date}},
            ]
        },
    )["results"]


def get_summary_value(page, target):
    summary_property = target["summary_property"]
    summary_prop = page["properties"].get(summary_property, {})

    if "select" in summary_prop:
        return summary_prop.get("select", {}).get("name") or target["summary_default"]

    return target["summary_default"]


def build_target_stats(target, pages):
    stats = {}

    for page in pages:
        props = page["properties"]
        category = get_summary_value(page, target)
        distance_prop = props.get("Länge") or props.get("Distanz") or {}
        distance = distance_prop.get("number", 0) or 0
        elevation = props.get("Höhenm.", {}).get("number", 0) or 0

        if category not in stats:
            stats[category] = {"count": 0, "distance": 0.0, "elevation": 0}

        stats[category]["count"] += 1
        stats[category]["distance"] += distance
        stats[category]["elevation"] += elevation

    return stats


def format_target_report(target_key, target, pages):
    if not pages:
        return None

    label_emoji = {"bike": "🚴", "run": "🏃"}.get(target_key, "📌")
    stats = build_target_stats(target, pages)
    lines = [f"{label_emoji} **{target['label']}**"]

    for category, values in stats.items():
        lines.append(
            f"- {category}: {values['count']} Aktivitäten | {round(values['distance'])} km | {values['elevation']} hm"
        )

    return "\n".join(lines)


def generate_monthly_report():
    first_day, last_day = get_previous_month_date_range()
    month_str = first_day.strftime("%B %Y")
    logging.info("📆 Bericht für %s wird erstellt...", month_str)

    sections = [f"**📆 Monatsbericht – {month_str}**"]

    for target_key, target in SYNC_TARGETS.items():
        database_id = target["database_id"]
        if not database_id:
            logging.warning("⏭ Überspringe Monatsbericht für %s – keine DB konfiguriert.", target["label"])
            continue

        pages = query_monthly_pages(
            database_id,
            first_day.strftime("%Y-%m-%d"),
            last_day.strftime("%Y-%m-%d"),
        )

        section = format_target_report(target_key, target, pages)
        if section:
            sections.append(section)

    if len(sections) == 1:
        logging.info("ℹ️ Keine Aktivitäten im letzten Monat gefunden.")
        return

    send_discord_message("\n".join(sections))


if __name__ == "__main__":
    logging.info("🔁 Starte Monatsbericht...")
    generate_monthly_report()
