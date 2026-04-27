from datetime import datetime


class StateEngine:

    def __init__(self, maze_graph, temp_threshold, sound_threshold):

        self.room_graph = maze_graph

        self.rooms = {}
        self.marsami_positions = {}
        self.marsami_types = {}

        # Para média acumulada
        self.temp_sum = 0
        self.temp_count = 0

        self.sound_sum = 0
        self.sound_count = 0

        self.temp_threshold = temp_threshold
        self.sound_threshold = sound_threshold

        self.game_started = False

        self.last_temp_value = None
        self.last_temp_timestamp = None

        self.last_sound_value = None
        self.last_sound_timestamp = None


    def _ensure_room_exists(self, room_id):
        if room_id not in self.rooms:
            self.rooms[room_id] = {"total": 0, "odd": 0, "even": 0}


    def _get_type(self, marsami_id):
        if marsami_id not in self.marsami_types:
            self.marsami_types[marsami_id] = "even" if marsami_id % 2 == 0 else "odd"
        return self.marsami_types[marsami_id]


    def process_movement(self, marsami_id, origin, destiny, status):

        marsami_type = self._get_type(marsami_id)

        event = {
            "marsami_id": marsami_id,
            "origin": origin,
            "destiny": destiny,
            "status": status,
            "timestamp": datetime.now(),
            "current_room": None,
            "is_valid": True,
            "reason": None
        }

        # Entrada inicial
        if origin == 0 and destiny != 0:

            self._ensure_room_exists(destiny)

            self.rooms[destiny]["total"] += 1
            self.rooms[destiny][marsami_type] += 1

            self.marsami_positions[marsami_id] = destiny
            event["current_room"] = destiny

            return event, [destiny]

        # Movimento entre salas
        if origin != 0 and destiny != 0:

            self.game_started = True

            if marsami_id not in self.marsami_positions:
                event["is_valid"] = False
                event["reason"] = "Unknown current position"
                return event, []

            current_room = self.marsami_positions[marsami_id]

            if current_room != origin:
                event["is_valid"] = False
                event["reason"] = "Origin mismatch"
                return event, []

            if origin not in self.room_graph:
                event["is_valid"] = False
                event["reason"] = "Origin not in graph"
                return event, []

            if destiny not in self.room_graph[origin]:
                event["is_valid"] = False
                event["reason"] = "Invalid corridor"
                return event, []

            self._ensure_room_exists(origin)
            self._ensure_room_exists(destiny)

            self.rooms[origin]["total"] -= 1
            self.rooms[origin][marsami_type] -= 1

            self.rooms[destiny]["total"] += 1
            self.rooms[destiny][marsami_type] += 1

            self.marsami_positions[marsami_id] = destiny
            event["current_room"] = destiny

            return event, [origin, destiny]

        # Fim da simulação
        if origin == 0 and destiny == 0 and status == 2:

            self.game_started = False
            event["current_room"] = self.marsami_positions.get(marsami_id)

            return event, []

        # Caso inválido
        event["is_valid"] = False
        event["reason"] = "Invalid movement pattern"
        return event, []


    def update_temperature(self, timestamp, temp):

        event = {
            "timestamp": timestamp,
            "value": temp,
            "is_valid": True,
            "reason": None
        }

        if timestamp is None:
            event["is_valid"] = False
            event["reason"] = "Invalid timestamp"
            return event

        if self.temp_count == 0:
            self.temp_sum += temp
            self.temp_count += 1
            self.last_temp_value = temp
            self.last_temp_timestamp = timestamp
            return event

        media = self.temp_sum / self.temp_count
        delta = abs(temp - media)

        if delta > self.temp_threshold:
            event["is_valid"] = False
            event["reason"] = "Temperature outlier"
            return event

        self.temp_sum += temp
        self.temp_count += 1

        self.last_temp_value = temp
        self.last_temp_timestamp = timestamp

        return event


    def update_sound(self, timestamp, sound):

        event = {
            "timestamp": timestamp,
            "value": sound,
            "is_valid": True,
            "reason": None
        }

        # Timestamp inválido
        if timestamp is None:
            event["is_valid"] = False
            event["reason"] = "Invalid timestamp"
            return event

        # Primeira leitura válida
        if self.sound_count == 0:
            self.sound_sum += sound
            self.sound_count += 1
            return event

        media = self.sound_sum / self.sound_count
        delta = abs(sound - media)

        # Outlier
        if delta > self.sound_threshold:
            event["is_valid"] = False
            event["reason"] = "Sound outlier"
            return event

        # Atualiza média só com valores válidos
        self.sound_sum += sound
        self.sound_count += 1

        self.last_sound_value = sound
        self.last_sound_timestamp = timestamp

        return event