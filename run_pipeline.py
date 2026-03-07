from core.config_manager import ConfigManager
from core.state_engine import StateEngine
from core.event_processor import EventProcessor
from mqtt.mqtt_listener import MQTTListener


def main():

    print("Starting Distributed Maze Pipeline")

    config_manager = ConfigManager()

    broker_config = config_manager.get_broker_config()
    outlier_config = config_manager.get_outlier_config()
    maze_graph = config_manager.get_maze_graph()

    broker = broker_config["broker"]
    port = broker_config["port"]

    state_engine = StateEngine(
        maze_graph,
        outlier_config["temp_outlier"],
        outlier_config["sound_outlier"]
    )

    event_processor = EventProcessor(state_engine)

    mqtt_listener = MQTTListener(
        broker,
        port,
        player_id=6,
        event_processor=event_processor
    )

    mqtt_listener.start()


if __name__ == "__main__":
    main()