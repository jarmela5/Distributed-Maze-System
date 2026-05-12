"""
PC1 — MQTT listener, event processing, MongoDB persistence, migration to MQTT.
Requires: MongoDB running locally (or via MONGO_URI env var).
"""

import time
import paho.mqtt.client as mqtt
from core.config_manager import ConfigManager
from core.state_engine import StateEngine
from core.event_processor import EventProcessor
from core.decision_engine import DecisionEngine
from core.alert_engine import AlertEngine
from mqtt.mqtt_listener import MQTTListener
from persistance.mongo_repository import MongoRepository
from persistance.migration_worker import MigrationWorker


def main():

    PLAYER_ID = 6
    BROKER = "broker.emqx.io"
    PORT = 1883

    print(f"--- PC1: Listener + Processing + Migration (Player {PLAYER_ID}) ---")

    config_manager = ConfigManager()
    maze_graph    = config_manager.get_maze_graph()
    temp_var      = config_manager.get_temperature_config()
    noise_var     = config_manager.get_noise_config()
    threshold_var = config_manager.get_thresholds()
    normal_values = config_manager.get_normal_values()

    mongo_repo   = MongoRepository()
    state_engine  = StateEngine(maze_graph, threshold_var, normal_values["normal_temp"], normal_values["normal_noise"])

    # Shared MQTT client for actuator commands (AlertEngine + DecisionEngine)
    common_mqtt = mqtt.Client(client_id=f"maze_engines_{PLAYER_ID}")
    common_mqtt.connect(BROKER, PORT)
    common_mqtt.loop_start()

    alert_engine = AlertEngine(
        player_id=PLAYER_ID,
        mqtt_client=common_mqtt,
        mongo_repo=mongo_repo,
        temp_config=temp_var,
        noise_config=noise_var,
        maze_graph=maze_graph
    )

    decision_engine = DecisionEngine(
        player_id=PLAYER_ID,
        state_engine=state_engine,
        mongo_repo=mongo_repo,
        broker=BROKER,
        port=PORT
    )

    event_processor = EventProcessor(
        state_engine=state_engine,
        mongo_repo=mongo_repo,
        decision_engine=decision_engine,
        alert_engine=alert_engine
    )

    migration_worker = MigrationWorker(
        mongo_repo,
        broker=BROKER,
        port=PORT,
        polling_interval=2
    )

    mqtt_listener = MQTTListener(
        BROKER, PORT,
        player_id=PLAYER_ID,
        event_processor=event_processor
    )

    mqtt_listener.start()
    print("[PC1] All components running. Ctrl+C to stop.")

    last_migration = 0

    try:
        while True:
            now = time.time()

            if now - last_migration >= migration_worker.polling_interval:
                migration_worker._migrar()
                last_migration = now

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n[PC1] Shutting down...")

    finally:
        mqtt_listener.stop()
        migration_worker.stop()
        decision_engine.stop()
        common_mqtt.loop_stop()
        common_mqtt.disconnect()
        mongo_repo.client.close()
        config_manager.close()
        print("[PC1] Stopped cleanly.")


if __name__ == "__main__":
    main()