import pymongo
import os
from datetime import datetime


class MongoRepository:
    def __init__(self, uri=None, db_name="distributed_maze"):
        uri = uri or os.environ.get("MONGO_URI", "mongodb://root:root@localhost:27017/")
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]

        self.temperature_events = self.db["temperature_events"]
        self.sound_events       = self.db["sound_events"]
        self.movement_events    = self.db["movement_events"]

        self._create_indexes()
        print("[MongoDB] MongoRepository connected to", db_name)

    def _create_indexes(self):
        self.temperature_events.create_index("timestamp")
        self.temperature_events.create_index("player")
        self.sound_events.create_index("timestamp")
        self.sound_events.create_index("player")
        self.movement_events.create_index("timestamp")
        self.movement_events.create_index("player")
        self.movement_events.create_index("marsami_id")

    def save_temperature(self, event: dict):
        doc = {
            "player":     event.get("player"),
            "timestamp":  event.get("timestamp", datetime.now()),
            "value":      event.get("value"),
            "is_outlier": event.get("is_invalid", False),
            "reason":     event.get("reason", None),
        }
        self.temperature_events.insert_one(doc)

    def save_sound(self, event: dict):
        doc = {
            "player":     event.get("player"),
            "timestamp":  event.get("timestamp", datetime.now()),
            "value":      event.get("value"),
            "is_outlier": event.get("is_invalid", False),
            "reason":     event.get("reason", None),
        }
        self.sound_events.insert_one(doc)

    def save_movement(self, event: dict):
        doc = {
            "player":     event.get("player"),
            "marsami_id": event.get("marsami_id"),
            "origin":     event.get("origin"),
            "destiny":    event.get("destiny"),
            "status":     event.get("status"),
            "is_invalid": event.get("is_invalid", False),
            "reason":     event.get("reason", None),
            "timestamp":  event.get("timestamp", datetime.now()),
        }
        self.movement_events.insert_one(doc)