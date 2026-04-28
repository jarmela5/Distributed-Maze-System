from core.state_engine import StateEngine
import json
import threading
import time
import paho.mqtt.client as mqtt


class DecisionEngine:

    MAX_TRIGGERS_PER_ROOM = 3

    DECISION_INTERVAL = 1.0

    def __init__(self, player_id, state_engine: StateEngine, broker, port ):

        self.player_id = player_id
        self.state_engine = state_engine

        self._trigger_state = {}

        self.last_decision_time = 0

        self._lock = threading.Lock()

        self._mqtt = mqtt.Client(client_id=f"decision_engine_{player_id}")
        self._mqtt.connect(broker, port)
        self._mqtt.loop_start()


    def _publish(self, payload):

        message = json.dumps(payload)

        self._mqtt.publish("pisid_mazeact", message)

    def evaluate(self):

        with self._lock:

            now = time.time()

            if now - self.last_decision_time < self.DECISION_INTERVAL:
                return

            self.last_decision_time = now

            self._check_triggers()


    def _check_triggers(self):

        rooms = self.state_engine.rooms

        for room_id, occ in rooms.items():

            odd = occ["odd"]
            even = occ["even"]

            if room_id not in self._trigger_state:
                self._trigger_state[room_id] = 0

            if self._trigger_state[room_id] >= self.MAX_TRIGGERS_PER_ROOM:
                continue

            if odd == even and odd > 0:

                self._publish({
                    "Type": "Score",
                    "Player": self.player_id,
                    "Room": room_id
                })

                self._trigger_state[room_id] += 1

                print(f"[TRIGGER] Room {room_id} equilibrium")

    def stop(self):

        self._mqtt.loop_stop()

        self._mqtt.disconnect()

        print("[DecisionEngine] stopped")

    def close_all_corridors(self):

        self._publish({
            "Type": "CloseAllDoor",
            "Player": self.player_id
        })

    def open_all_corridors(self):

        self._publish({
            "Type": "OpenAllDoor",
            "Player": self.player_id
        })

    def open_corridor(self, origin, destiny):

        self._publish({
            "Type": "OpenDoor",
            "Player": self.player_id,
            "RoomOrigin": origin,
            "RoomDestiny": destiny
        })

    def close_corridor(self, origin, destiny):

        self._publish({
            "Type": "CloseDoor",
            "Player": self.player_id,
            "RoomOrigin": origin,
            "RoomDestiny": destiny
        })