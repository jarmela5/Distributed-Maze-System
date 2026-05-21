from persistance.mongo_repository import MongoRepository
from persistance.migration_worker import MigrationWorker


def main():

    BROKER = "broker.emqx.io"
    PORT = 1883

    print("--- PC1: Mongo -> MQTT Migration ---")

    mongo_repo = MongoRepository()

    migration_worker = MigrationWorker(
        mongo_repo=mongo_repo,
        broker=BROKER,
        port=PORT,
        polling_interval=2
    )

    try:

        migration_worker.run()

    except KeyboardInterrupt:

        print("\n[MigrationWorker] Shutting down...")

    finally:

        migration_worker.stop()

        mongo_repo.client.close()

        print("[MigrationWorker] Stopped cleanly.")


if __name__ == "__main__":
    main()