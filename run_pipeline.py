from core.config_manager import ConfigManager
from core.state_engine import StateEngine
from core.event_processor import EventProcessor
from mqtt.mqtt_listener import MQTTListener
from persistance.mongo_repository import MongoRepository


def main():

    print("Starting Distributed Maze Pipeline")

    config_manager = ConfigManager()

    maze_graph = config_manager.get_maze_graph()

    broker = "broker.emqx.io"
    port = 1883

    state_engine = StateEngine(maze_graph)

    mongo_repo = MongoRepository()

    event_processor = EventProcessor(state_engine, mongo_repo)

    mqtt_listener = MQTTListener(
        broker,
        port,
        player_id=6,
        event_processor=event_processor
    )

    mqtt_listener.start()


if __name__ == "__main__":
    main()