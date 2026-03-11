import threading
from core.config_manager import ConfigManager
from core.state_engine import StateEngine
from core.event_processor import EventProcessor
from mqtt.mqtt_listener import MQTTListener
from persistance.mongo_repository import MongoRepository
from persistance.migration_worker import MigrationWorker


def main():

    print("Starting Distributed Maze Pipeline")

    config_manager = ConfigManager()

    broker_config  = config_manager.get_broker_config()
    outlier_config = config_manager.get_outlier_config()
    maze_graph     = config_manager.get_maze_graph()

    broker = broker_config["broker"]
    port   = broker_config["port"]

    state_engine = StateEngine(
        maze_graph,
        outlier_config["temp_outlier"],
        outlier_config["sound_outlier"]
    )

    mongo_repo = MongoRepository()

    event_processor = EventProcessor(state_engine, mongo_repo)

    # Migração corre em thread separada para não bloquear o MQTTListener
    migration_worker = MigrationWorker(mongo_repo, polling_interval=2)
    migration_thread = threading.Thread(target=migration_worker.run, daemon=True)
    migration_thread.start()
    print("[Main] MigrationWorker iniciado em thread separada")
    

    mqtt_listener = MQTTListener(
        broker,
        port,
        player_id=6,
        event_processor=event_processor
    )

    mqtt_listener.start()  # bloqueia aqui (loop_forever)


if __name__ == "__main__":
    main()