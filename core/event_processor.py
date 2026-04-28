from core.state_engine import StateEngine
from core.decision_engine import DecisionEngine
from core.alert_engine import AlertEngine  
from persistance.mongo_repository import MongoRepository
import json
from datetime import datetime
import re

class EventProcessor:

    def __init__(self, state_engine: StateEngine, mongo_repo: MongoRepository, 
                 decision_engine: DecisionEngine, alert_engine: AlertEngine):
        self.state_engine = state_engine
        self.mongo_repo = mongo_repo
        self.decision_engine = decision_engine
        self.alert_engine = alert_engine # Nova dependência centralizada

    def process(self, topic, payload):
        try:
            data = json.loads(payload)
        except Exception:
            print("[ERROR] Invalid JSON. Ignored.")
            return

        data = self._normalize_keys(data)
        player = self._extract_player(topic)

        if topic.startswith("pisid_mazemov"):
            self._handle_movement(data, player)

        elif topic.startswith("pisid_mazetemp"):
            self._handle_temperature(data, player)

        elif topic.startswith("pisid_mazesound"):
            self._handle_sound(data, player)

        else:
            print("[WARNING] Unknown topic:", topic)

    def _normalize_keys(self, data):
        normalized = {}
        for key, value in data.items():
            clean_key = key.lower()
            clean_key = re.sub(r'[^a-z]', '', clean_key)
            normalized[clean_key] = value
        return normalized

    def _extract_player(self, topic):
        try:
            return int(topic.split("_")[-1])
        except:
            return None

    def _handle_movement(self, data, player):
        required_fields = ["marsami", "roomorigin", "roomdestiny", "status"]
        if not all(field in data for field in required_fields):
            return

        marsami = data["marsami"]
        origin = data["roomorigin"]
        destiny = data["roomdestiny"]
        status = data["status"]

        if not isinstance(marsami, int) or status not in [0, 1, 2]:
            return

        event, changed_rooms = self.state_engine.process_movement(
            marsami_id=marsami,
            origin=origin,
            destiny=destiny,
            status=status
        )

        if event:
            event["player"] = player
            if "timestamp" not in event or event["timestamp"] is None:
                event["timestamp"] = datetime.now()

            self.mongo_repo.save_movement(event)

            if event.get("is_valid") and changed_rooms:
                self.mongo_repo.save_room_occupancy(
                    changed_rooms,
                    self.state_engine.rooms,
                    event["timestamp"]
                )

            # Avalia lógica de pontuação/equilíbrio (Jogo)
            if self.state_engine.game_started:
                self.decision_engine.evaluate()

    def _handle_temperature(self, data, player):
        if "temperature" not in data:
            return

        value = data["temperature"]
        timestamp = data.get("hour")

        if not isinstance(value, (int, float)):
            return

        parsed_time = self._parse_timestamp(timestamp)
        event = self.state_engine.update_temperature(timestamp=parsed_time, temp=value)
        
        event["player"] = player
        self.mongo_repo.save_temperature(event)

        # Se a leitura for válida, passa para o motor de alertas processar níveis e AC
        if event.get("is_valid"):
            self.alert_engine.process_temperature(value)
            
            if self.state_engine.game_started:
                self.decision_engine.evaluate()

    def _handle_sound(self, data, player):
        if "sound" not in data:
            return

        value = data["sound"]
        timestamp = data.get("hour")

        if not isinstance(value, (int, float)):
            return

        parsed_time = self._parse_timestamp(timestamp)
        event = self.state_engine.update_sound(timestamp=parsed_time, sound=value)

        event["player"] = player
        self.mongo_repo.save_sound(event)

        # Se a leitura for válida, passa para o motor de alertas processar níveis e Portas
        if event.get("is_valid"):
            self.alert_engine.process_noise(value)

            if self.state_engine.game_started:
                self.decision_engine.evaluate()

    def _parse_timestamp(self, timestamp):
        if not timestamp:
            return None
        try:
            return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
        except Exception:
            return None