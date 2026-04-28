import time
from core.config_manager import ConfigManager
from core.state_engine import StateEngine
from core.event_processor import EventProcessor
from core.decision_engine import DecisionEngine
from mqtt.mqtt_listener import MQTTListener
from persistance.mongo_repository import MongoRepository
from persistance.migration_worker import MigrationWorker
from persistance.mysql_writer import MySQLWriter

def main():
    TEMP_TRESHOLD = 15
    SOUND_TRESHOLD = 15

    print("Starting Distributed Maze Pipeline")

    config_manager = ConfigManager()
    maze_graph = config_manager.get_maze_graph()
    temp_var   = config_manager.get_temperature_config()
    noise_var  = config_manager.get_noise_config()
    thresholds = config_manager.get_thresholds()
    

    broker = "broker.emqx.io"
    port   = 1883

    state_engine    = StateEngine(maze_graph, thresholds)
    mongo_repo      = MongoRepository()
    decision_engine = DecisionEngine(
        player_id=6,
        state_engine=state_engine,
        broker=broker,
        port=port,
        temp_config=temp_var,
        noise_config=noise_var
    )

    event_processor  = EventProcessor(state_engine, mongo_repo, decision_engine, temp_var, noise_var)
    migration_worker = MigrationWorker(mongo_repo, broker=broker, port=port, polling_interval=2)
    mysql_writer     = MySQLWriter(broker=broker, port=port)
    mqtt_listener    = MQTTListener(broker, port, player_id=6, event_processor=event_processor)

    # Todos os componentes MQTT correm em background (loop_start internamente)
    mqtt_listener.start()
    print("[Main] MQTTListener iniciado")

    last_migration = 0
    last_mysql_flush = 0

    try:
        while True:
            now = time.time()

            # MigrationWorker: polling a cada 2 segundos
            if now - last_migration >= migration_worker.polling_interval:
                migration_worker._migrar()
                #total = migration_worker._migrar()
                ##print(f"[MIGRATION] publicados={total} pending={len(migration_worker._pending)}")
                last_migration = now

            # MySQLWriter: processar buffer continuamente
            mysql_writer._process_buffer()
            ##print(f"[BUFFER] tamanho={len(mysql_writer._buffer)}")

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nShutting down system...")

    finally:
        mqtt_listener.stop()
        migration_worker.stop()
        mysql_writer.stop()
        decision_engine.stop()
        mongo_repo.client.close()
        config_manager.close()
        print("System stopped cleanly.")


if __name__ == "__main__":
    main()