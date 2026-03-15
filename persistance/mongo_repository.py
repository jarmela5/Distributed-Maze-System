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
        self.room_occupancy     = self.db["room_occupancy"]

        self._create_indexes()
        print("[MongoDB] MongoRepository connected to", db_name)

    def _create_indexes(self):
        self.temperature_events.create_index("seq")
        self.temperature_events.create_index("player")
        self.temperature_events.create_index("migrated")
        self.sound_events.create_index("seq")
        self.sound_events.create_index("player")
        self.sound_events.create_index("migrated")
        self.movement_events.create_index("seq")
        self.movement_events.create_index("player")
        self.movement_events.create_index("marsami_id")
        self.movement_events.create_index("migrated")
        self.room_occupancy.create_index("seq")
        self.room_occupancy.create_index("migrated")
        self.room_occupancy.create_index("room_id")

    def _next_seq(self):
        """Contador atómico global — garante ordem real de chegada das mensagens."""
        result = self.db["counters"].find_one_and_update(
            {"_id": "seq"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER
        )
        return result["seq"]

    def save_temperature(self, event: dict):
        doc = {
            "seq":        self._next_seq(),
            "player":     event.get("player"),
            "timestamp":  event.get("timestamp", datetime.now()),
            "value":      event.get("value"),
            "is_valid":   not event.get("is_invalid", False),
            "reason":     event.get("reason"),
            "migrated":   False,
        }
        self.temperature_events.insert_one(doc)

    def save_sound(self, event: dict):
        doc = {
            "seq":        self._next_seq(),
            "player":     event.get("player"),
            "timestamp":  event.get("timestamp", datetime.now()),
            "value":      event.get("value"),
            "is_valid":   not event.get("is_invalid", False),
            "reason":     event.get("reason"),
            "migrated":   False,
        }
        self.sound_events.insert_one(doc)

    def save_movement(self, event: dict):
        doc = {
            "seq":        self._next_seq(),
            "player":     event.get("player"),
            "marsami_id": event.get("marsami_id"),
            "origin":     event.get("origin"),
            "destiny":    event.get("destiny"),
            "status":     event.get("status"),
            "is_valid":   not event.get("is_invalid", False),
            "reason":     event.get("reason"),
            "timestamp":  event.get("timestamp", datetime.now()),
            "migrated":   False,
        }
        self.movement_events.insert_one(doc)

    def save_room_occupancy(self, changed_rooms, rooms):

        for room_id in changed_rooms:

            data = rooms[room_id]

            doc = {
                "seq": self._next_seq(),
                "room_id": room_id,
                "odd": data["odd"],
                "even": data["even"],
                "total": data["total"],
                "timestamp": datetime.now(),
                "migrated": False
            }

            self.room_occupancy.insert_one(doc)

    # Métodos de suporte à migração

    def get_unmigrated(self, collection_name: str, batch_size=100):
        """Devolve documentos ainda não migrados, ordenados por ordem de chegada."""
        collection = self.db[collection_name]
        return list(
            collection.find({"migrated": False})
            .sort("seq", pymongo.ASCENDING)
            .limit(batch_size)
        )

    def mark_as_migrated(self, collection_name: str, doc_id):
        """Marca um documento como migrado APÓS confirmação do insert no MySQL."""
        collection = self.db[collection_name]
        collection.update_one({"_id": doc_id}, {"$set": {"migrated": True}})

    def reset_migration(self, collection_name: str = None):
        """
        Reinicializa o processo de migração (chamado pelo administrador).
        Se collection_name for None, repõe todas as coleções.
        """
        collections = (
            [self.db[collection_name]]
            if collection_name
            else [self.temperature_events, self.sound_events, self.movement_events]
        )
        for col in collections:
            result = col.update_many({}, {"$set": {"migrated": False}})
            print(f"[RESET] {col.name}: {result.modified_count} documentos repostos")