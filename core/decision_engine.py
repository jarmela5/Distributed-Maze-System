import json
import threading
import paho.mqtt.client as mqtt
from datetime import datetime


class DecisionEngine:
    """
    Responsible for:
    - Detecting odd == even equilibrium per room and firing triggers (max 3 per room)
    - Scoring: +1 if trigger fires while equilibrium holds, -0.5 if it breaks before confirmed
    - Sending actuator commands via MQTT (open/close corridors, AC)
    - AC control based on temperature threshold
    """
    #hardcoded
    TEMP_DANGER_THRESHOLD = 80   # below this we turn AC off; above, turn AC on
    TEMP_SAFE_THRESHOLD   = 60   # once AC brings temp below this, turn it off

    MAX_TRIGGERS_PER_ROOM = 3

    def __init__(self, player_id: int, state_engine, mongo_repo, broker: str, port: int):
        self.player_id   = player_id
        self.state_engine = state_engine
        self.mongo_repo   = mongo_repo

        # --- MQTT publisher client (separate from the subscriber) ---
        self._mqtt = mqtt.Client(client_id=f"decision_engine_{player_id}")
        self._mqtt.on_connect    = self._on_connect
        self._mqtt.on_disconnect = self._on_disconnect
        self._mqtt.connect(broker, port, keepalive=60)
        self._mqtt.loop_start()   # background thread

        # --- Trigger state ---
        # {room_id: {"count": int, "pending": bool, "pending_since": datetime}}
        self._trigger_state: dict[int, dict] = {}

        # --- Score ---
        self.score: float = 0.0

        # --- AC state ---
        self._ac_on: bool = False

        # --- Lock for thread safety (MQTT callbacks + main loop) ---
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # MQTT helpers
    # ------------------------------------------------------------------

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[DecisionEngine] MQTT publisher connected")
        else:
            print(f"[DecisionEngine] MQTT publisher connection failed: rc={rc}")

    def _on_disconnect(self, client, userdata, rc):
        print(f"[DecisionEngine] MQTT publisher disconnected (rc={rc})")

    def _publish(self, payload: dict):
        message = json.dumps(payload)
        self._mqtt.publish("pisid_mazeact", message)
        print(f"[ACT] {message}")

    # ------------------------------------------------------------------
    # Public entry point — call this after every movement event
    # ------------------------------------------------------------------

    def evaluate(self):
        """
        Main decision loop. Call this whenever StateEngine state changes
        (after every processed movement, temperature or sound event).
        """
        with self._lock:
            self._check_triggers()
            self._check_temperature()

    # ------------------------------------------------------------------
    # Trigger logic
    # ------------------------------------------------------------------

    def _check_triggers(self):
        rooms = self.state_engine.rooms  # {room_id: {"total", "odd", "even"}}

        for room_id, occupancy in rooms.items():
            odd  = occupancy.get("odd",  0)
            even = occupancy.get("even", 0)

            if room_id not in self._trigger_state:
                self._trigger_state[room_id] = {
                    "count":         0,
                    "pending":       False,
                    "pending_since": None
                }

            state = self._trigger_state[room_id]

            # Exhausted triggers for this room — skip
            if state["count"] >= self.MAX_TRIGGERS_PER_ROOM:
                continue

            equilibrium = (odd == even) and (odd > 0)  # at least 1 of each

            if equilibrium and not state["pending"]:
                # New equilibrium detected — fire trigger immediately
                self._fire_trigger(room_id, state, odd, even)

            elif not equilibrium and state["pending"]:
                # Equilibrium broke before we could confirm it — penalise
                self._resolve_pending_trigger(room_id, state, success=False)

    def _fire_trigger(self, room_id: int, state: dict, odd: int, even: int):
        """Send Score actuator command and mark trigger as pending confirmation."""
        payload = {
            "Type":   "Score",
            "Player": self.player_id,
            "Room":   room_id
        }
        self._publish(payload)

        state["pending"]       = True
        state["pending_since"] = datetime.now()

        # Optimistically award the point; we reverse it if equilibrium breaks
        # (see PPT slide 5: +1 if trigger fires WHILE equilibrium holds)
        # In practice the server validates, but we track locally for monitoring.
        print(f"[TRIGGER] Room {room_id}: odd={odd} even={even} — trigger fired "
              f"({state['count'] + 1}/{self.MAX_TRIGGERS_PER_ROOM})")

    def _resolve_pending_trigger(self, room_id: int, state: dict, success: bool):
        """Resolve a pending trigger with success or failure."""
        state["count"]   += 1
        state["pending"]  = False

        #nao sei se estas pontuacoes sao para dar aqui?????? acho qye n
        if success:
            self.score += 1.0
            result = "+1 point"
        else:
            self.score -= 0.5
            result = "-0.5 points"

        print(f"[TRIGGER] Room {room_id} resolved: {result} | Total score: {self.score}")

        self.mongo_repo.db["trigger_events"].insert_one({
            "player":    self.player_id,
            "room_id":   room_id,
            "success":   success,
            "score_delta": 1.0 if success else -0.5,
            "timestamp": datetime.now()
        })

    def confirm_trigger_if_pending(self, room_id: int):
        """
        Call this when you receive external confirmation that the equilibrium
        still holds (e.g. from a server ack). If you don't have server acks,
        you can call this from evaluate() after N stable ticks.
        """
        with self._lock:
            state = self._trigger_state.get(room_id)
            if state and state["pending"]:
                self._resolve_pending_trigger(room_id, state, success=True)


    def _check_temperature(self):
        temp = self.state_engine.last_temp_value

        if temp is None:
            return

        if temp >= self.TEMP_DANGER_THRESHOLD and not self._ac_on:
            self._set_ac(on=True)

        elif temp <= self.TEMP_SAFE_THRESHOLD and self._ac_on:
            self._set_ac(on=False)

    def _set_ac(self, on: bool):
        """
        The PPT mentions AC as an actuator that incrementally lowers temperature.
        There is no explicit MQTT command for it in the spec, so we use a
        CloseAllDoor / OpenAllDoor strategy combined with a dedicated AC flag.

        If your mazerun.exe supports a dedicated AC command, replace the body
        of this method with the correct payload.
        """
        self._ac_on = on
        action = "ON" if on else "OFF"
        print(f"[AC] Air conditioning turned {action} (temp={self.state_engine.last_temp_value})")

        # Placeholder: emit a custom event that your server/pipeline can handle.
        # Replace with the correct actuator type when the server spec is clarified.
        self.mongo_repo.db["ac_events"].insert_one({
            "player":    self.player_id,
            "ac_on":     on,
            "temp":      self.state_engine.last_temp_value,
            "timestamp": datetime.now()
        })

    # ------------------------------------------------------------------
    # Corridor control — call these from your game strategy
    # ------------------------------------------------------------------

    def open_corridor(self, room_origin: int, room_destiny: int):
        """Open a single corridor."""
        self._publish({
            "Type":        "OpenDoor",
            "Player":      self.player_id,
            "RoomOrigin":  room_origin,
            "RoomDestiny": room_destiny
        })

    def close_corridor(self, room_origin: int, room_destiny: int):
        """Close a single corridor."""
        self._publish({
            "Type":        "CloseDoor",
            "Player":      self.player_id,
            "RoomOrigin":  room_origin,
            "RoomDestiny": room_destiny
        })

    def close_all_corridors(self):
        """Close every corridor at once (marsamis stop moving)."""
        self._publish({
            "Type":   "CloseAllDoor",
            "Player": self.player_id
        })

    def open_all_corridors(self):
        """Open every corridor at once."""
        self._publish({
            "Type":   "OpenAllDoor",
            "Player": self.player_id
        })

    # ------------------------------------------------------------------
    # Graceful shutdown
    # ------------------------------------------------------------------

    def stop(self):
        self._mqtt.loop_stop()
        self._mqtt.disconnect()
        print("[DecisionEngine] Stopped")