import threading
from core.config_manager import ConfigManager
from core.state_engine import StateEngine
from core.event_processor import EventProcessor
from core.decision_engine import DecisionEngine
from mqtt.mqtt_listener import MQTTListener
from persistance.mongo_repository import MongoRepository
from persistance.migration_worker import MigrationWorker
from persistance.mysql_writer import MySQLWriter


def main():

    print("Starting Distributed Maze Pipeline")

    config_manager = ConfigManager()

    maze_graph = config_manager.get_maze_graph()
    temp_var   = config_manager.get_temperature_config()
    noise_var  = config_manager.get_noise_config()

    broker = "broker.emqx.io"
    port   = 1883

    state_engine = StateEngine(maze_graph)

    mongo_repo = MongoRepository()

    decision_engine = DecisionEngine(
        player_id=6,
        state_engine=state_engine,
        broker=broker,
        port=port,
        temp_config=temp_var,
        noise_config=noise_var
    )

    event_processor = EventProcessor(state_engine, mongo_repo, decision_engine)

    #  MigrationWorker: MongoDB → MQTT 
    migration_worker = MigrationWorker(mongo_repo, broker=broker, port=port, polling_interval=2)
    migration_thread = threading.Thread(target=migration_worker.run, daemon=True)
    migration_thread.start()
    print("[Main] MigrationWorker iniciado em thread separada")

    # MySQLWriter: MQTT → MySQL 
    mysql_writer = MySQLWriter(broker=broker, port=port)
    mysql_thread = threading.Thread(target=mysql_writer.start, daemon=True)
    mysql_thread.start()
    print("[Main] MySQLWriter iniciado em thread separada")
    

    mqtt_listener = MQTTListener(
        broker,
        port,
        player_id=6,
        event_processor=event_processor
    )

    try:
        mqtt_listener.start()

    except KeyboardInterrupt:
        print("\nShutting down system...")

    finally:
        try:
            migration_worker.stop()
        except:
            pass
        try:
            mysql_writer.stop()
        except:
            pass
        try:
            mqtt_listener.stop()
        except:
            pass
        try:
            decision_engine.stop()
        except:
            pass
        try:
            mongo_repo.client.close()
        except:
            pass
        try:
            config_manager.close()
        except:
            pass

        print("System stopped cleanly.")


if __name__ == "__main__":
    main()