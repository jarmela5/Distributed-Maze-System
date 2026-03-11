import time
import mysql.connector
from persistance.mongo_repository import MongoRepository


class MigrationWorker:
    """
    Lê documentos não migrados do MongoDB e insere no MySQL local.
    Só marca como migrado APÓS confirmar o insert no MySQL.
    """

    COLLECTIONS = ["movement_events", "temperature_events", "sound_events"]

    def __init__(self, mongo_repo: MongoRepository, polling_interval=2):
        self.mongo_repo = mongo_repo
        self.polling_interval = polling_interval
        self.mysql_conn = self._conectar_mysql()

    def _conectar_mysql(self):
        conn = mysql.connector.connect(
            user='root',
            host='localhost',
            database='maze_local',
            passwd='root'
        )
        conn.autocommit = False
        return conn

    # ─── Insert no MySQL por tipo de evento ─────────────────────

    def _insert_movement(self, cursor, doc):
        # MongoDB: marsami_id, origin, destiny, status, is_invalid
        # MySQL:   Marsami,    SalaOrigem, SalaDestino, Status, is_valid
        cursor.execute("""
            INSERT INTO MedicoesPassagens (Hora, SalaOrigem, SalaDestino, Marsami, Status, is_valid)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            doc.get("timestamp"),
            doc.get("origin"),
            doc.get("destiny"),
            doc.get("marsami_id"),
            doc.get("status"),
            not doc.get("is_invalid", False),  # is_invalid → is_valid (invertido)
        ))

    def _insert_temperature(self, cursor, doc):
        # MongoDB: value, is_outlier
        # MySQL:   Temperatura, is_valid (varchar 12 — arredonda para 2 casas decimais)
        cursor.execute("""
            INSERT INTO Temperatura (Hora, Temperatura, is_valid)
            VALUES (%s, %s, %s)
        """, (
            doc.get("timestamp"),
            str(round(doc.get("value"), 2)),
            not doc.get("is_outlier", False),  # is_outlier → is_valid (invertido)
        ))

    def _insert_sound(self, cursor, doc):
        # MongoDB: value, is_outlier
        # MySQL:   Som, is_valid (varchar 12 — arredonda para 2 casas decimais)
        cursor.execute("""
            INSERT INTO Som (Hora, Som, is_valid)
            VALUES (%s, %s, %s)
        """, (
            doc.get("timestamp"),
            str(round(doc.get("value"), 2)),
            not doc.get("is_outlier", False),  # is_outlier → is_valid (invertido)
        ))

    #Ciclo de migração 

    def _migrar_colecao(self, collection_name):
        insert_fn = {
            "movement_events":    self._insert_movement,
            "temperature_events": self._insert_temperature,
            "sound_events":       self._insert_sound,
        }[collection_name]

        docs = self.mongo_repo.get_unmigrated(collection_name)
        if not docs:
            return 0

        cursor = self.mysql_conn.cursor()
        migrados = 0

        for doc in docs:
            try:
                insert_fn(cursor, doc)
                self.mysql_conn.commit()

                # só marca como migrado APÓS confirmar o insert
                self.mongo_repo.mark_as_migrated(collection_name, doc["_id"])
                migrados += 1

            except Exception as e:
                self.mysql_conn.rollback()
                print(f"[ERROR] Falha ao migrar doc {doc['_id']} de {collection_name}: {e}")

        cursor.close()
        return migrados

    def run(self):
        print("[MigrationWorker] A iniciar migração incremental MongoDB → MySQL local")

        while True:
            total = 0
            for collection in self.COLLECTIONS:
                total += self._migrar_colecao(collection)

            if total > 0:
                print(f"[MigrationWorker] {total} documento(s) migrado(s) para o MySQL")
            else:
                print("[MigrationWorker] Nenhum documento novo")

            time.sleep(self.polling_interval)