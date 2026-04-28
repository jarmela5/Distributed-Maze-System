import time
import paho.mqtt.client as mqtt
from core.config_manager import ConfigManager
from core.state_engine import StateEngine
from core.event_processor import EventProcessor
from core.decision_engine import DecisionEngine
from core.alert_engine import AlertEngine  # Importante!
from mqtt.mqtt_listener import MQTTListener
from persistance.mongo_repository import MongoRepository
from persistance.migration_worker import MigrationWorker
from persistance.mysql_writer import MySQLWriter

def main():

    PLAYER_ID = 6
    BROKER = "broker.emqx.io"
    PORT = 1883

    print(f"--- Starting Distributed Maze Pipeline (Player {PLAYER_ID}) ---")

    config_manager = ConfigManager()
    maze_graph = config_manager.get_maze_graph()
    temp_var   = config_manager.get_temperature_config()
    noise_var  = config_manager.get_noise_config()
    threshold_var = config_manager.get_thresholds()

    mongo_repo   = MongoRepository()
    state_engine = StateEngine(maze_graph, threshold_var)

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
        broker=BROKER, 
        port=PORT
    )

    event_processor = EventProcessor(
        state_engine=state_engine, 
        mongo_repo=mongo_repo, 
        decision_engine=decision_engine, 
        alert_engine=alert_engine
    )

    migration_worker = MigrationWorker(mongo_repo, broker=BROKER, port=PORT, polling_interval=2)
    mysql_writer     = MySQLWriter(broker=BROKER, port=PORT)
    mqtt_listener    = MQTTListener(BROKER, PORT, player_id=PLAYER_ID, event_processor=event_processor)

    mqtt_listener.start()
    print("[System] All components initialized and running.")

    last_migration = 0

    try:
        while True:
            now = time.time()

            if now - last_migration >= migration_worker.polling_interval:
                migration_worker._migrar()
                last_migration = now
            mysql_writer._process_buffer()

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n[System] Shutting down...")

    finally:
        mqtt_listener.stop()
        migration_worker.stop()
        mysql_writer.stop()
        decision_engine.stop()
        common_mqtt.loop_stop()
        common_mqtt.disconnect()
        mongo_repo.client.close()
        config_manager.close()
        print("[System] Stopped cleanly.")

if __name__ == "__main__":
    main()