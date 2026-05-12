import pymongo
import os
import time
from datetime import datetime


class MongoRepository:
    def __init__(self, uri=None, db_name="distributed_maze"):
        self.db_name = db_name
        self.ports = [27017, 27018, 27019]
        self.client = None
        self.db = None
        self._connect()

        self.temperature_events = self.db["temperature_events"]
        self.sound_events       = self.db["sound_events"]
        self.movement_events    = self.db["movement_events"]
        self.room_occupancy     = self.db["room_occupancy"]
        self.system_events      = self.db["system_events"]

        self._create_indexes()
        print("[MongoDB] MongoRepository connected to", db_name)

    def _connect(self):
        """Encontra o PRIMARY entre os 3 nós e liga-se a ele."""
        for port in self.ports:
            try:
                client = pymongo.MongoClient(
                    f"mongodb://localhost:{port}/?directConnection=true",
                    serverSelectionTimeoutMS=2000
                )
                info = client.admin.command("isMaster")
                if info.get("ismaster"):
                    self.client = client
                    self.db = client[self.db_name]
                    print(f"[MongoDB] PRIMARY encontrado na porta {port}")
                    return
                client.close()
            except Exception:
                continue
        raise Exception("[MongoDB] Não foi possível encontrar nenhum PRIMARY")

    def _reconnect(self):
        """Tenta reconectar ao PRIMARY quando a ligação falha."""
        print("[MongoDB] A tentar reconectar ao PRIMARY...")
        for attempt in range(5):
            try:
                self._connect()
                # Atualiza as referências às coleções
                self.temperature_events = self.db["temperature_events"]
                self.sound_events       = self.db["sound_events"]
                self.movement_events    = self.db["movement_events"]
                self.room_occupancy     = self.db["room_occupancy"]
                self.system_events      = self.db["system_events"]
                print("[MongoDB] Reconectado com sucesso!")
                return
            except Exception as e:
                print(f"[MongoDB] Reconexão falhou (tentativa {attempt+1}/5): {e}")
                time.sleep(3)
        raise Exception("[MongoDB] Não foi possível reconectar após 5 tentativas")

    def _retry(self, func, label="operação"):
        for attempt in range(5):
            try:
                return func()
            except pymongo.errors.PyMongoError as e:
                print(f"[MongoDB] Erro {label} (tentativa {attempt+1}/5): {e}")
                try:
                    self._reconnect()
                except Exception:
                    pass
                time.sleep(3)
        raise Exception(f"[MongoDB] Falha após 5 tentativas: {label}")

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
        self.system_events.create_index("seq")
        self.system_events.create_index("migrated")

    def _next_seq(self):
        def op():
            result = self.db["counters"].find_one_and_update(
                {"_id": "seq"},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=pymongo.ReturnDocument.AFTER
            )
            return result["seq"]
        return self._retry(op, "next_seq")

    def save_temperature(self, event: dict):
        doc = {
            "seq":      self._next_seq(),
            "player":   event.get("player"),
            "timestamp":event.get("timestamp"),
            "value":    event.get("value"),
            "is_valid": event.get("is_valid", True),
            "reason":   event.get("reason"),
            "migrated": False,
        }
        self._retry(lambda: self.temperature_events.insert_one(doc), "save_temperature")

    def save_sound(self, event: dict):
        doc = {
            "seq":      self._next_seq(),
            "player":   event.get("player"),
            "timestamp":event.get("timestamp"),
            "value":    event.get("value"),
            "is_valid": event.get("is_valid", True),
            "reason":   event.get("reason"),
            "migrated": False,
        }
        self._retry(lambda: self.sound_events.insert_one(doc), "save_sound")

    def save_movement(self, event: dict):
        doc = {
            "seq":        self._next_seq(),
            "player":     event.get("player"),
            "marsami_id": event.get("marsami_id"),
            "origin":     event.get("origin"),
            "destiny":    event.get("destiny"),
            "status":     event.get("status"),
            "is_valid":   event.get("is_valid", True),
            "reason":     event.get("reason"),
            "timestamp":  event.get("timestamp"),
            "migrated":   False,
        }
        self._retry(lambda: self.movement_events.insert_one(doc), "save_movement")

    def save_room_occupancy(self, changed_rooms, rooms, timestamp):
        for room_id in changed_rooms:
            data = rooms[room_id]
            doc = {
                "seq":      self._next_seq(),
                "room_id":  room_id,
                "odd":      data["odd"],
                "even":     data["even"],
                "total":    data["total"],
                "timestamp":timestamp,
                "migrated": False
            }
            self._retry(lambda: self.room_occupancy.insert_one(doc), "save_room_occupancy")

    def save_event(self, event: dict):
        doc = {
            "seq":       self._next_seq(),
            "player":    event.get("player") or datetime.now().isoformat(),
            "timestamp": event.get("timestamp"),
            "sala":      event.get("sala"),
            "sensor":    event.get("sensor"),
            "leitura":   event.get("leitura"),
            "tipo":      event.get("tipo"),
            "msg":       event.get("msg"),
            "migrated":  False,
        }
        self._retry(lambda: self.system_events.insert_one(doc), "save_event")

    def get_unmigrated(self, collection_name: str, batch_size=100):
        def op():
            collection = self.db[collection_name]  # busca sempre do db atual
            return list(collection.find({"migrated": False}).sort("seq", pymongo.ASCENDING).limit(batch_size))
        return self._retry(op, "get_unmigrated")

    def mark_as_migrated(self, collection_name: str, doc_id):
        def op():
            collection = self.db[collection_name]  # busca sempre do db atual
            collection.update_one({"_id": doc_id}, {"$set": {"migrated": True}})
        return self._retry(op, "mark_as_migrated")

    def reset_migration(self, collection_name: str = None):
        collections = (
            [self.db[collection_name]]
            if collection_name
            else [
                self.temperature_events,
                self.sound_events,
                self.movement_events,
                self.room_occupancy,
                self.system_events
            ]
        )
        for col in collections:
            result = col.update_many({}, {"$set": {"migrated": False}})
            print(f"[RESET] {col.name}: {result.modified_count} documentos repostos")