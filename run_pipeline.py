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
    # Configurações de validação de ruído/temp (filtros da StateEngine)
    TEMP_TRESHOLD = 15
    SOUND_TRESHOLD = 15
    PLAYER_ID = 6
    BROKER = "broker.emqx.io"
    PORT = 1883

    print(f"--- Starting Distributed Maze Pipeline (Player {PLAYER_ID}) ---")

    # 1. Carregar configurações do MySQL via ConfigManager
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
        player_id=PLAYER_ID,
        state_engine=state_engine,
        broker=BROKER, # A DecisionEngine internamente cria o seu próprio cliente se o teu código original assim o dita
        port=PORT
    )

    # 6. Inicializar Processador de Eventos (O Orquestrador)
    event_processor = EventProcessor(
        state_engine=state_engine, 
        mongo_repo=mongo_repo, 
        decision_engine=decision_engine, 
        alert_engine=alert_engine
    )

    # 7. Inicializar Componentes de Persistência e Escuta
    migration_worker = MigrationWorker(mongo_repo, broker=BROKER, port=PORT, polling_interval=2)
    mysql_writer     = MySQLWriter(broker=BROKER, port=PORT)
    mqtt_listener    = MQTTListener(BROKER, PORT, player_id=PLAYER_ID, event_processor=event_processor)

    mqtt_listener.start()
    print("[System] All components initialized and running.")

    last_migration = 0

    try:
        while True:
            now = time.time()

            # Executa a migração de dados do Mongo para o Tópico de Migração
            if now - last_migration >= migration_worker.polling_interval:
                migration_worker._migrar()
                last_migration = now

            # Processa o buffer do MySQL (recebe do tópico de migração e grava no SQL)
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