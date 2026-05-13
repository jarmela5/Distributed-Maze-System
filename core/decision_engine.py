from core.state_engine import StateEngine
import time
import paho.mqtt.client as mqtt


class DecisionEngine:

    MAX_TRIGGERS_PER_ROOM = 3
    DECISION_INTERVAL = 0.2

    def __init__(self, player_id, state_engine: StateEngine, mongo_repo, broker, port):

        self.player_id = player_id
        self.state_engine = state_engine
        self.mongo_repo = mongo_repo

        self._trigger_state = {}

        self.last_decision_time = 0

        self._mqtt = mqtt.Client(client_id=f"decision_engine_{player_id}")
        self._mqtt.connect(broker, port)
        self._mqtt.loop_start()


    def _publish(self, payload):
        parts = []

        for key, value in payload.items():
            parts.append(f"{key}: {value}")

        message = "{" + ", ".join(parts) + "}"

        result = self._mqtt.publish(
            "pisid_mazeact",
            message,
            qos=1
        )

        result.wait_for_publish()


    def evaluate(self, movement_event=None):

        now = time.time()

        if now - self.last_decision_time < self.DECISION_INTERVAL:
            return

        self.last_decision_time = now

        self._check_triggers(movement_event)


    def _check_triggers(self, movement):

        rooms = self.state_engine.rooms

        for room_id, occ in rooms.items():

            odd = occ["odd"]
            even = occ["even"]

            state = self._trigger_state.setdefault(room_id, {
                "count": 0,
                "in_equilibrium": False
            })

            if state["count"] >= self.MAX_TRIGGERS_PER_ROOM:
                continue

            is_equilibrium = (odd == even and odd > 0)

            predicted = False
            if movement and movement.get("is_valid"):
                predicted = self._predict_equilibrium(room_id, movement)

            should_trigger = False

            if (is_equilibrium or predicted) and not state["in_equilibrium"]:
                should_trigger = True
                state["in_equilibrium"] = True

            elif not is_equilibrium:
                state["in_equilibrium"] = False

            if should_trigger:
                self._fire_trigger(room_id)
                state["count"] += 1


    def _predict_equilibrium(self, room_id, movement):

        destiny = movement.get("destiny")
        origin = movement.get("origin")
        marsami_id = movement.get("marsami_id")

        if marsami_id is None:
            return False

        occ = self.state_engine.rooms.get(room_id)
        if not occ:
            return False

        odd = occ["odd"]
        even = occ["even"]

        is_even = (marsami_id % 2 == 0)

        if origin == room_id:
            if is_even:
                even -= 1
            else:
                odd -= 1

        if destiny == room_id:
            if is_even:
                even += 1
            else:
                odd += 1

        return odd == even and odd > 0


    def _fire_trigger(self, room_id):

        self._publish({
            "Type": "Score",
            "Player": self.player_id,
            "Room": room_id
        })
        
        self._save_trigger_event(room_id)

    def _save_trigger_event(self, room_id):

        self.mongo_repo.save_event({
            "player": self.player_id,
            "timestamp": None,  # vai usar datetime.now() no repo
            "sala": room_id,
            "sensor": "game",
            "leitura": None,
            "tipo": "EquilibrioMarsamis",
            "msg": f"Equilíbrio de marsamis na sala {room_id}"
        })


    def stop(self):
        self._mqtt.loop_stop()
        self._mqtt.disconnect()
        print("[DecisionEngine] stopped")
