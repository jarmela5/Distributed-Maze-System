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

    broker = "broker.emqx.io"
    port = 1883

    state_engine = StateEngine(maze_graph)

    mongo_repo = MongoRepository()

    event_processor = EventProcessor(state_engine, mongo_repo, decision_engine)

    mqtt_listener = MQTTListener(
        broker,
        port,
        player_id=6,
        event_processor=event_processor
    )

    decision_engine = DecisionEngine(
    player_id=6,
    state_engine=state_engine,
    mongo_repo=mongo_repo,
    broker=broker,
    port=port
    )

    mqtt_listener.start()


if __name__ == "__main__":
    main()