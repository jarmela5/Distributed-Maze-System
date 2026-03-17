import time
import json
import paho.mqtt.client as mqtt
from persistance.mongo_repository import MongoRepository


class MigrationWorker:
    """
    Lê documentos não migrados do MongoDB e publica num único tópico MQTT
    com campo 'type' para distinguir o tipo de evento.
    A ordem de publicação segue o campo 'seq' garantindo ordem de chegada.
    """

    COLLECTIONS = ["movement_events", "temperature_events", "sound_events", "room_occupancy"]

    TYPE_MAP = {
        "movement_events":    "movement",
        "temperature_events": "temperature",
        "sound_events":       "sound",
        "room_occupancy":     "occupancy"
    }

    TOPIC = "pisid_migrate_all"

    def __init__(self, mongo_repo: MongoRepository, broker, port, polling_interval=2):
        self.mongo_repo = mongo_repo
        self.polling_interval = polling_interval
        self._running = True

        self._mqtt = mqtt.Client(client_id="migration_worker")
        self._mqtt.connect(broker, port)
        self._mqtt.loop_start()

    def _get_all_unmigrated(self):
        """
        Vai buscar documentos não migrados de todas as coleções
        e ordena globalmente por seq — garante ordem real de chegada.
        """
        all_docs = []
        for collection_name in self.COLLECTIONS:
            docs = self.mongo_repo.get_unmigrated(collection_name)
            for doc in docs:
                all_docs.append((collection_name, doc))

        # ordena por seq global
        all_docs.sort(key=lambda x: x[1].get("seq", 0))
        return all_docs

    def _publicar(self, collection_name, doc):
        """Publica documento no tópico único com campo type e aguarda confirmação."""
        payload = {
            "type": self.TYPE_MAP[collection_name],
            "seq":  doc.get("seq"),
        }

        # copia os campos relevantes conforme o tipo
        if collection_name == "movement_events":
            payload.update({
                "timestamp":  str(doc.get("timestamp")),
                "origin":     doc.get("origin"),
                "destiny":    doc.get("destiny"),
                "marsami_id": doc.get("marsami_id"),
                "status":     doc.get("status"),
                "is_valid":   doc.get("is_valid", True),
            })
        elif collection_name == "room_occupancy":
            payload.update({
                "timestamp": str(doc.get("timestamp")),
                "room_id": doc.get("room_id"),
                "odd": doc.get("odd"),
                "even": doc.get("even"),
                "total": doc.get("total")
            })
        else:
            payload.update({
                "timestamp": str(doc.get("timestamp")),
                "value":     doc.get("value"),
                "is_valid":  doc.get("is_valid", True),
            })

        result = self._mqtt.publish(self.TOPIC, json.dumps(payload), qos=1)
        result.wait_for_publish()

    def _migrar(self):
        all_docs = self._get_all_unmigrated()
        if not all_docs:
            return 0

        publicados = 0
        for collection_name, doc in all_docs:
            try:
                self._publicar(collection_name, doc)
                self.mongo_repo.mark_as_migrated(collection_name, doc["_id"])
                publicados += 1
            except Exception as e:
                print(f"[ERROR] Falha ao publicar doc {doc['_id']} de {collection_name}: {e}")

        return publicados

    def stop(self):
        self._running = False
        self._mqtt.loop_stop()
        self._mqtt.disconnect()

    def run(self):
        print("[MigrationWorker] A iniciar MongoDB → MQTT (tópico único)")

        while self._running:
            total = self._migrar()

            if total > 0:
                print(f"[MigrationWorker] {total} documento(s) publicado(s) em '{self.TOPIC}'")
            else:
                print(f"[MigrationWorker] Nenhum documento novo")

            time.sleep(self.polling_interval)