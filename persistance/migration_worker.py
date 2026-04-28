import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime

class MigrationWorker:

    COLLECTIONS = [
        "movement_events",
        "temperature_events",
        "sound_events",
        "room_occupancy",
        "system_events"
    ]

    TYPE_MAP = {
        "movement_events": "movement",
        "temperature_events": "temperature",
        "sound_events": "sound",
        "room_occupancy": "occupancy",
        "system_events": "alert"
    }

    TOPIC = "pisid_migrate_all"
    TOPIC_CONFIRM = "pisid_migrate_confirm"

    def __init__(self, mongo_repo, broker, port, polling_interval=2):
        self.mongo_repo = mongo_repo
        self.polling_interval = polling_interval
        self._running = True

        self._pending = {}
        self._retries = {}

        self._mqtt = mqtt.Client(
            client_id="migration_worker",
            clean_session=False
        )

        self._mqtt.on_connect = self._on_connect
        self._mqtt.on_message = self._on_confirm
        self._mqtt.on_disconnect = self._on_disconnect

        self._mqtt.connect(broker, port)
        self._mqtt.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(self.TOPIC_CONFIRM, qos=1)

    def _on_disconnect(self, client, userdata, rc):
        print("[MigrationWorker] reconectando...")
        while True:
            try:
                client.reconnect()
                break
            except:
                time.sleep(3)

    def _on_confirm(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())

            seq = data.get("seq")
            success = data.get("success", False)

            if not success:
                count = self._retries.get(seq, 0) + 1
                self._retries[seq] = count

                if count > 5:
                    print(f"[DROP] seq={seq}")
                    self._pending.pop(seq, None)
                    return

                self._pending.pop(seq, None)
                return

            if seq in self._pending:
                collection_name, doc_id = self._pending.pop(seq)

                self.mongo_repo.mark_as_migrated(
                    collection_name,
                    doc_id
                )

                self._retries.pop(seq, None)

        except Exception as e:
            print(f"[ERROR confirm] {e}")

    def _get_all_unmigrated(self):
        all_docs = []

        for collection_name in self.COLLECTIONS:
            docs = self.mongo_repo.get_unmigrated(collection_name)

            for doc in docs:
                all_docs.append((collection_name, doc))

        all_docs.sort(key=lambda x: x[1].get("seq", 0))
        return all_docs
    
    def _sanitize(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, dict):
            return {k: self._sanitize(v) for k, v in obj.items()}

        if isinstance(obj, list):
            return [self._sanitize(v) for v in obj]

        return obj

    def _publicar(self, collection_name, doc):

        clean_doc = self._sanitize(doc)

        payload = {
            "type": self.TYPE_MAP[collection_name],
            "seq": clean_doc.get("seq")
        }

        if collection_name == "movement_events":
            payload.update({
                "timestamp": clean_doc.get("timestamp"),
                "origin": clean_doc.get("origin"),
                "destiny": clean_doc.get("destiny"),
                "marsami_id": clean_doc.get("marsami_id"),
                "status": clean_doc.get("status"),
                "is_valid": clean_doc.get("is_valid", True)
            })

        elif collection_name == "room_occupancy":
            payload.update({
                "timestamp": clean_doc.get("timestamp"),
                "room_id": clean_doc.get("room_id"),
                "odd": clean_doc.get("odd"),
                "even": clean_doc.get("even"),
                "total": clean_doc.get("total")
            })

        elif collection_name == "system_events":
            payload.update({
                "timestamp": clean_doc.get("timestamp"),
                "sala": clean_doc.get("sala"),
                "sensor": clean_doc.get("sensor"),
                "leitura": clean_doc.get("leitura"),
                "tipo": clean_doc.get("tipo"),
                "msg": clean_doc.get("msg")
            })

        else:
            payload.update({
                "timestamp": clean_doc.get("timestamp"),
                "value": clean_doc.get("value"),
                "is_valid": clean_doc.get("is_valid", True)
            })

        self._mqtt.publish(
            self.TOPIC,
            json.dumps(payload),
            qos=1
        )

    def _migrar(self):
        all_docs = self._get_all_unmigrated()

        publicados = 0

        for collection_name, doc in all_docs:
            seq = doc.get("seq")

            if seq in self._pending:
                continue

            try:
                self._publicar(collection_name, doc)

                self._pending[seq] = (
                    collection_name,
                    doc["_id"]
                )

                publicados += 1

            except Exception as e:
                print(f"[ERROR publish] {e}")

        return publicados

    def run(self):
        print("[MigrationWorker] iniciado")

        while self._running:

            total = self._migrar()

            print(f"[STATE] pending={len(self._pending)} retries={len(self._retries)}")

            sleep_time = self.polling_interval

            if len(self._pending) > 50:
                sleep_time = 5

            time.sleep(sleep_time)

    def stop(self):
        self._running = False
        self._mqtt.loop_stop()
        self._mqtt.disconnect()