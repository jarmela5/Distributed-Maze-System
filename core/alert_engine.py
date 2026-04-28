import json
import time
from datetime import datetime

class AlertEngine:
    def __init__(self, player_id, mqtt_client, mongo_repo, temp_config, noise_config, maze_graph):
        self.player_id = player_id
        self.mqtt = mqtt_client
        self.mongo = mongo_repo
        self.graph = maze_graph

        # Conversão para float das configurações
        self.t_normal = float(temp_config["normal"])
        self.t_tol    = float(temp_config["high_tol"])
        
        self.n_normal = float(noise_config["normal"])
        self.n_tol    = float(noise_config["tolerance"])

        # Estado Interno
        self.last_temp_level = 0
        self.last_noise_level = 0
        self.last_temp_alert_time = 0
        self.last_noise_alert_time = 0
        self.last_noise_value = 0
        
        self.ac_on = False
        self.closed_doors = [] # Lista de tuplos (origem, destino)
        self.intervals = {1: 10, 2: 7, 3: 5}

    def _get_level(self, value, normal, tolerance):
        if value <= normal: return 0
        diff = value - normal
        if diff >= 0.75 * tolerance: return 3
        if diff >= 0.50 * tolerance: return 2
        if diff >= 0.25 * tolerance: return 1
        return 0

    def _publish_act(self, payload):
        """Método central de publicação para os atuadores"""
        self.mqtt.publish("pisid_mazeact", json.dumps(payload))

    # --- FUNÇÕES DE ATUAÇÃO (Baseadas no teu código antigo) ---

    def set_ac(self, on: bool):
        self.ac_on = on
        payload = {
            "Type": "AcOn" if on else "AcOff",
            "Player": self.player_id
        }
        self._publish_act(payload)
        print(f"[ACTUATOR] AC {'ON' if on else 'OFF'} enviado.")

    def close_corridor(self, origin, destiny):
        payload = {
            "Type": "CloseDoor",
            "Player": self.player_id,
            "RoomOrigin": int(origin),
            "RoomDestiny": int(destiny)
        }
        self._publish_act(payload)
        print(f"[ACTUATOR] CloseDoor: {origin} -> {destiny}")

    def open_all_corridors(self):
        payload = {
            "Type": "OpenAllDoor",
            "Player": self.player_id
        }
        self._publish_act(payload)
        self.closed_doors = []
        print("[ACTUATOR] OpenAllDoor enviado.")

    # --- PROCESSAMENTO ---

    def process_temperature(self, value):
        current_level = self._get_level(value, self.t_normal, self.t_tol)
        now = time.time()
        
        # 1. Lógica de Alerta
        should_alert = False
        if current_level > self.last_temp_level:
            should_alert = True
        elif current_level > 0 and current_level == self.last_temp_level:
            if now - self.last_temp_alert_time >= self.intervals.get(current_level, 10):
                should_alert = True

        if should_alert:
            self._generate_alert("Temperatura", value, f"Nível {current_level}: Temperatura Alta", "TemperaturaAlta")
            self.last_temp_alert_time = now

        # 2. Lógica de Controlo do AC (Usando set_ac)
        if current_level >= 1 and not self.ac_on:
            self.set_ac(True)
        elif value <= self.t_normal and self.ac_on:
            self.set_ac(False)

        self.last_temp_level = current_level

    def process_noise(self, value):
        current_level = self._get_level(value, self.n_normal, self.n_tol)
        now = time.time()
        
        # 1. Lógica de Alerta
        should_alert = False
        if current_level > self.last_noise_level:
            should_alert = True
        elif current_level > 0 and current_level == self.last_noise_level:
            if now - self.last_noise_alert_time >= self.intervals.get(current_level, 10):
                should_alert = True

        if should_alert:
            self._generate_alert("Som", value, f"Nível {current_level}: Ruído Excessivo", "RuidoAlto")
            self.last_noise_alert_time = now
            
            # Se o ruído não estiver a descer, fecha a próxima porta
            if value >= self.last_noise_value:
                self._find_and_close_next()

        # 2. Reabertura total quando volta ao normal
        if value <= self.n_normal and len(self.closed_doors) > 0:
            self.open_all_corridors()

        self.last_noise_level = current_level
        self.last_noise_value = value

    def _find_and_close_next(self):
        """Procura no grafo uma porta que ainda não fechámos"""
        for origin, neighbors in self.graph.items():
            for dest in neighbors:
                # Criar um identificador único para a porta (ordenado para evitar duplicados 1-2 e 2-1)
                door = tuple(sorted((int(origin), int(dest))))
                if door not in self.closed_doors:
                    self.closed_doors.append(door)
                    self.close_corridor(origin, dest)
                    return # Fecha apenas uma porta por alerta emitido

    def _generate_alert(self, sensor, value, msg, tipo_alerta):
        seq_id = int(time.time() * 1000)
        alert_data = {
            "seq": seq_id,
            "player": self.player_id,
            "sala": 0, 
            "sensor": sensor,
            "leitura": value,
            "tipo": tipo_alerta,
            "timestamp": datetime.now(),
            "msg": msg,
            "migrated": False
        }
        self.mongo.db["alert_events"].insert_one(alert_data)
        print(f"[ALERT] {tipo_alerta} (Seq: {seq_id})")