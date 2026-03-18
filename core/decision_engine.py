from core.state_engine import StateEngine
import json
import threading
import time
import paho.mqtt.client as mqtt


class DecisionEngine:

    MAX_TRIGGERS_PER_ROOM = 3

    DECISION_INTERVAL = 1.0

    def __init__(self, player_id, state_engine: StateEngine, broker, port,
                 temp_config, noise_config):

        self.player_id = player_id
        self.state_engine = state_engine

        self.normal_temp = temp_config["normal"]
        self.temp_high_tol = temp_config["high_tol"]
        self.temp_low_tol = temp_config["low_tol"]

        self.normal_noise = noise_config["normal"]
        self.noise_tol = noise_config["tolerance"]

        self._trigger_state = {}
        self._ac_on = False

        self.last_decision_time = 0

        self._lock = threading.Lock()

        self._mqtt = mqtt.Client(client_id=f"decision_engine_{player_id}")
        self._mqtt.connect(broker, port)
        self._mqtt.loop_start()


    def _publish(self, payload):

        message = json.dumps(payload)

        self._mqtt.publish("pisid_mazeact", message)

        # print("[ACT]", message)


    def evaluate(self):

        with self._lock:

            now = time.time()

            if now - self.last_decision_time < self.DECISION_INTERVAL:
                return

            self.last_decision_time = now

            self._check_triggers()
            self._check_temperature()
            self._check_noise()
            self._balance_rooms()


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


    def _check_temperature(self):

        temp = self.state_engine.last_temp_value

        if temp is None:
            return

        upper = self.normal_temp + self.temp_high_tol
        lower = self.normal_temp - self.temp_low_tol

        if temp > upper and not self._ac_on:

            print("[TEMP] Too hot → turning AC ON")

            self.set_ac(True)

        elif temp < lower and self._ac_on:

            print("[TEMP] Temperature safe → turning AC OFF")

            self.set_ac(False)

    def set_ac(self, on: bool):

        self._ac_on = on

        self._publish({
        "Type": "AcOn" if on else "AcOff",
        "Player": self.player_id
    })


    def _check_noise(self):

        sound = self.state_engine.last_sound_value

        if sound is None:
            return

        limit = self.normal_noise + self.noise_tol

        if sound <= limit:
            return

        print("[NOISE] High noise detected")

        graph = self.state_engine.room_graph

        closed = 0

        for origin in graph:
            for destiny in graph[origin]:

                if closed >= 2:
                    return

                self.close_corridor(origin, destiny)

                closed += 1


    def _balance_rooms(self):

        rooms = self.state_engine.rooms
        graph = self.state_engine.room_graph

        for room_id, occ in rooms.items():

            odd = occ["odd"]
            even = occ["even"]

            if odd == even:
                continue

            diff = odd - even

            # if diff > 0:
            #     print(f"[BALANCE] Room {room_id} has too many ODD")

            # else:
            #     print(f"[BALANCE] Room {room_id} has too many EVEN")

            if room_id in graph:

                for destiny in graph[room_id]:

                    self.open_corridor(room_id, destiny)


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


    def stop(self):

        self._mqtt.loop_stop()

        self._mqtt.disconnect()

        print("[DecisionEngine] stopped")