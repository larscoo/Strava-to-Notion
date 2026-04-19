import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

SYNC_TARGETS = {
    "bike": {
        "label": "Bike",
        "database_id": os.getenv("NOTION_DB_ID_BIKE"),
        "sport_types": ["Ride", "GravelRide", "MountainBikeRide", "EBikeRide"],
        "excluded_titles": ["B2W", "B2H"],
        "summary_property": "Art of Bike",
        "summary_default": "Unbekannt",
    },
    "run": {
        "label": "Run",
        "database_id": os.getenv("NOTION_DB_ID_RUN"),
        "sport_types": ["Run", "TrailRun", "VirtualRun"],
        "excluded_titles": [],
        "summary_property": "Sportart",
        "summary_default": "Run",
    },
}
