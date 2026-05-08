"""
PC2 — MySQL writer.
Subscribes to pisid_migrate_all (published by PC1's MigrationWorker),
inserts rows into MySQL, and publishes confirmations to pisid_migrate_confirm.
Requires: MySQL running locally.
No MongoDB dependency.
"""

from persistance.mysql_writer import MySQLWriter


def main():

    BROKER = "broker.emqx.io"
    PORT = 1883

    print("--- PC2: MySQL Writer ---")

    mysql_writer = MySQLWriter(broker=BROKER, port=PORT)

    print("[PC2] Listening for migration messages. Ctrl+C to stop.")

    try:
        mysql_writer.start()          # blocking loop

    except KeyboardInterrupt:
        print("\n[PC2] Shutting down...")

    finally:
        mysql_writer.stop()
        print("[PC2] Stopped cleanly.")


if __name__ == "__main__":
    main()