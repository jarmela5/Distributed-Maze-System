import time
from datetime import datetime


class AlertEngine:

    def __init__(self, player_id, mqtt_client, mongo_repo,
                 temp_config, noise_config, maze_graph):

        self.player_id = player_id
        self.mqtt = mqtt_client
        self.mongo = mongo_repo
        self.graph = maze_graph

        self.t_normal = float(temp_config["normal"])
        self.t_tol = float(temp_config["high_tol"])

        self.n_normal = float(noise_config["normal"])
        self.n_tol = float(noise_config["tolerance"])

        self.last_temp_level = 0
        self.last_noise_level = 0

        self.last_temp_alert_time = 0
        self.last_noise_alert_time = 0

        self.last_noise_value = 0

        self.ac_on = False

        self.closed_doors = set()

        self.intervals = {
            1: 10,
            2: 7,
            3: 5
        }

    def _get_level(self, value, normal, tolerance):

        if value <= normal:
            return 0

        diff = value - normal

        if diff >= 0.75 * tolerance:
            return 3

        if diff >= 0.50 * tolerance:
            return 2

        if diff >= 0.25 * tolerance:
            return 1

        return 0

    def _publish_act(self, payload):

        parts = []

        for key, value in payload.items():
            parts.append(f"{key}: {value}")

        message = "{" + ", ".join(parts) + "}"

        result = self.mqtt.publish(
            "pisid_mazeact",
            message,
            qos=1
        )

        result.wait_for_publish()

    def set_ac(self, on: bool):

        if self.ac_on == on:
            return

        self.ac_on = on

        payload = {
            "Type": "AcOn" if on else "AcOff",
            "Player": self.player_id
        }

        self._publish_act(payload)

        print(f"[ACTUATOR] AC {'ON' if on else 'OFF'} enviado.")

    def process_temperature(self, value):

        current_level = self._get_level(
            value,
            self.t_normal,
            self.t_tol
        )

        now = time.time()

        should_alert = False

        if current_level > self.last_temp_level:
            should_alert = True

        elif (
            current_level > 0 and
            current_level == self.last_temp_level
        ):

            interval = self.intervals.get(current_level, 10)

            if now - self.last_temp_alert_time >= interval:
                should_alert = True

        if should_alert:

            self._generate_alert(
                sensor="Temperatura",
                value=value,
                msg=f"Nível {current_level}: Temperatura Alta",
                tipo_alerta="TemperaturaAlta"
            )

            self.last_temp_alert_time = now

        if current_level >= 1 and not self.ac_on:
            self.set_ac(True)

        elif value <= self.t_normal and self.ac_on:
            self.set_ac(False)

        self.last_temp_level = current_level

    def process_noise(self, value):

        current_level = self._get_level(
            value,
            self.n_normal,
            self.n_tol
        )

        now = time.time()

        should_alert = False

        if current_level > self.last_noise_level:
            should_alert = True

        elif (
            current_level > 0 and
            current_level == self.last_noise_level
        ):

            interval = self.intervals.get(current_level, 10)

            if now - self.last_noise_alert_time >= interval:
                should_alert = True

        if should_alert:

            self._generate_alert(
                sensor="Som",
                value=value,
                msg=f"Nível {current_level}: Ruído Excessivo",
                tipo_alerta="RuidoAlto"
            )

            self.last_noise_alert_time = now

            if value >= self.last_noise_value:
                self._find_and_close_next()

        if value <= self.n_normal and len(self.closed_doors) > 0:
            self.open_all_corridors()

        self.last_noise_level = current_level
        self.last_noise_value = value

    def close_corridor(self, origin, destiny):

        payload = {
            "Type": "CloseDoor",
            "Player": self.player_id,
            "RoomOrigin": int(origin),
            "RoomDestiny": int(destiny)
        }

        self._publish_act(payload)

        print(f"[ACTUATOR] CloseDoor: {origin} -> {destiny}")

    def open_corridor(self, origin, destiny):

        payload = {
            "Type": "OpenDoor",
            "Player": self.player_id,
            "RoomOrigin": int(origin),
            "RoomDestiny": int(destiny)
        }

        self._publish_act(payload)

        print(f"[ACTUATOR] OpenDoor: {origin} -> {destiny}")

    def close_all_corridors(self):

        payload = {
            "Type": "CloseAllDoor",
            "Player": self.player_id
        }

        self._publish_act(payload)

        print("[ACTUATOR] CloseAllDoor enviado.")

    def open_all_corridors(self):

        payload = {
            "Type": "OpenAllDoor",
            "Player": self.player_id
        }

        self._publish_act(payload)

        self.closed_doors.clear()

        print("[ACTUATOR] OpenAllDoor enviado.")

    def _find_and_close_next(self):

        for origin, neighbors in self.graph.items():

            for dest in neighbors:

                door = tuple(sorted((int(origin), int(dest))))

                if door not in self.closed_doors:

                    self.closed_doors.add(door)

                    self.close_corridor(origin, dest)

                    return

    def _generate_alert(self, sensor, value, msg, tipo_alerta):

        alert_data = {
            "player": self.player_id,
            "sala": None,
            "sensor": sensor,
            "leitura": value,
            "tipo": tipo_alerta,
            "timestamp": datetime.now().isoformat(),
            "msg": msg
        }

        self.mongo.save_event(alert_data)

        print(f"[ALERT] {tipo_alerta}")