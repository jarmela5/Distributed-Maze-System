from core.config_manager import ConfigManager
from core.state_engine import StateEngine
from core.event_processor import EventProcessor
from mqtt.mqtt_listener import MQTTListener
from persistance.mongo_repository import MongoRepository
from core.decision_engine import DecisionEngine


def main():

    print("Starting Distributed Maze Pipeline")

    config_manager = ConfigManager()

    maze_graph = config_manager.get_maze_graph()
    temp_var = config_manager.get_temperature_config()
    noise_var = config_manager.get_noise_config()

    broker = "broker.emqx.io"
    port = 1883

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