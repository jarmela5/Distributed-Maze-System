from datetime import datetime


class StateEngine:

    def __init__(self, maze_graph):

        self.room_graph = maze_graph

        self.rooms = {}

        self.marsami_positions = {}

        self.marsami_types = {}

        self.last_temp_value = None
        self.last_sound_value = None

        self.MAX_TEMP_DELTA = 5
        self.MAX_SOUND_DELTA = 10

        self.game_started = False


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
            "is_invalid": False,
            "reason": None
        }

        if origin == 0 and destiny != 0:

            self._ensure_room_exists(destiny)

            self.rooms[destiny]["total"] += 1
            self.rooms[destiny][marsami_type] += 1

            self.marsami_positions[marsami_id] = destiny
            event["current_room"] = destiny

            return event

        if origin != 0 and destiny != 0:
            
            self.game_started = True

            if marsami_id not in self.marsami_positions:
                event["is_invalid"] = True
                event["reason"] = "Unknown current position"
                return event

            current_room = self.marsami_positions[marsami_id]

            if current_room != origin:
                event["is_invalid"] = True
                event["reason"] = "Origin mismatch"
                return event

            if origin not in self.room_graph:
                event["is_invalid"] = True
                event["reason"] = "Origin not in graph"
                return event

            if destiny not in self.room_graph[origin]:
                event["is_invalid"] = True
                event["reason"] = "Invalid corridor"
                return event

            self._ensure_room_exists(origin)
            self._ensure_room_exists(destiny)

            self.rooms[origin]["total"] -= 1
            self.rooms[origin][marsami_type] -= 1

            self.rooms[destiny]["total"] += 1
            self.rooms[destiny][marsami_type] += 1

            self.marsami_positions[marsami_id] = destiny
            event["current_room"] = destiny

            return event

        if origin == 0 and destiny == 0 and status == 2:
            
            self.game_started = False

            event["current_room"] = self.marsami_positions.get(marsami_id)

            return event


    def update_temperature(self, timestamp, temp):

        event = {
            "timestamp": timestamp,
            "value": temp,
            "is_invalid": False,
            "reason": None
        }

        if self.last_temp_value is None:
            self.last_temp_value = temp
            return event

        delta = abs(temp - self.last_temp_value)

        if delta > self.MAX_TEMP_DELTA:
            event["is_invalid"] = True
            event["reason"] = "Temperature spike"
            return event

        self.last_temp_value = temp
        return event


    def update_sound(self, timestamp, sound):

        event = {
            "timestamp": timestamp,
            "value": sound,
            "is_invalid": False,
            "reason": None
        }

        if self.last_sound_value is None:
            self.last_sound_value = sound
            return event

        delta = abs(sound - self.last_sound_value)

        if delta > self.MAX_SOUND_DELTA:
            event["is_invalid"] = True
            event["reason"] = "Sound spike"
            return event

        self.last_sound_value = sound
        return event