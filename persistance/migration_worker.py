import time
import json
import threading
import paho.mqtt.client as mqtt
from persistance.mongo_repository import MongoRepository


class MigrationWorker:
    """
    Lê documentos não migrados do MongoDB e publica num único tópico MQTT
    com campo 'type' para distinguir o tipo de evento.
    A ordem de publicação segue o campo 'seq' garantindo ordem de chegada.
    Só marca migrated: True após confirmação do MySQLWriter via pisid_migrate_confirm.
    """

    COLLECTIONS = ["movement_events", "temperature_events", "sound_events", "room_occupancy", "alert_events"]

    TYPE_MAP = {
        "movement_events":    "movement",
        "temperature_events": "temperature",
        "sound_events":       "sound",
        "room_occupancy":     "occupancy",
            "alert_events": "alert",

    }

    TOPIC         = "pisid_migrate_all"
    TOPIC_CONFIRM = "pisid_migrate_confirm"

    def __init__(self, mongo_repo: MongoRepository, broker, port, polling_interval=2):
        self.mongo_repo = mongo_repo
        self.polling_interval = polling_interval
        self._running = True

        # pending: seq → (collection_name, doc_id)
        self._pending = {}
        self._pending_lock = threading.Lock()

        self._mqtt = mqtt.Client(client_id="migration_worker")
        self._mqtt.on_connect = self._on_connect
        self._mqtt.on_message = self._on_confirm
        self._mqtt.connect(broker, port)
        self._mqtt.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(self.TOPIC_CONFIRM, qos=1)
            print(f"[MigrationWorker] Subscribed to {self.TOPIC_CONFIRM}")

    def _on_confirm(self, client, userdata, msg):
        """Recebe confirmação do MySQLWriter e marca o documento como migrado."""
        try:
            data = json.loads(msg.payload.decode())
            seq = data.get("seq")
            success = data.get("success", False)

            if not success:
                print(f"[MigrationWorker] Insert falhou para seq={seq} — será reenviado")
                with self._pending_lock:
                    self._pending.pop(seq, None)
                return

            with self._pending_lock:
                if seq in self._pending:
                    collection_name, doc_id = self._pending.pop(seq)
                    self.mongo_repo.mark_as_migrated(collection_name, doc_id)
                    print(f"[MigrationWorker] Confirmado e marcado migrated: seq={seq}")

        except Exception as e:
            print(f"[MigrationWorker] Erro ao processar confirmação: {e}")

    def _get_all_unmigrated(self):
        """Vai buscar docs não migrados de todas as coleções, ordenados por seq."""
        all_docs = []
        for collection_name in self.COLLECTIONS:
            docs = self.mongo_repo.get_unmigrated(collection_name)
            for doc in docs:
                all_docs.append((collection_name, doc))
        all_docs.sort(key=lambda x: x[1].get("seq", 0))
        return all_docs

    def _publicar(self, collection_name, doc):
        """Publica documento no tópico único com campo type e aguarda confirmação MQTT."""
        payload = {
            "type": self.TYPE_MAP[collection_name],
            "seq":  doc.get("seq"),
        }

        if collection_name == "movement_events":
            payload.update({
                "timestamp":  str(doc.get("timestamp")),
                "origin":     doc.get("origin"),
                "destiny":    doc.get("destiny"),
                "marsami_id": doc.get("marsami_id"),
                "status":     doc.get("status"),
                "is_valid":   doc.get("is_valid", True),
                "msg":       doc.get("msg"),

            })
        elif collection_name == "room_occupancy":
            payload.update({
                "timestamp": str(doc.get("timestamp")),
                "room_id":   doc.get("room_id"),
                "odd":       doc.get("odd"),
                "even":      doc.get("even"),
                "total":     doc.get("total"),
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
            seq = doc.get("seq")

            with self._pending_lock:
                if seq in self._pending:
                    continue

            try:
                self._publicar(collection_name, doc)

                with self._pending_lock:
                    self._pending[seq] = (collection_name, doc["_id"])

                publicados += 1

            except Exception as e:
                print(f"[ERROR] Falha ao publicar doc {doc['_id']} de {collection_name}: {e}")

        return publicados

    def stop(self):
        self._running = False
        self._mqtt.loop_stop()
        self._mqtt.disconnect()

    def run(self):
        print("[MigrationWorker] A iniciar MongoDB → MQTT (com confirmação MySQL)")

        while self._running:
            total = self._migrar()

            if total > 0:
                print(f"[MigrationWorker] {total} documento(s) publicado(s) — aguardando confirmação")
            else:
                print("[MigrationWorker] Nenhum documento novo")

            time.sleep(self.polling_interval)