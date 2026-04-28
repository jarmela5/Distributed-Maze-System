import mysql.connector


class ConfigManager:

    def __init__(self):
        self.conn_cloud = mysql.connector.connect(
            user="aluno",
            host="194.210.86.10",
            database="maze",
            passwd="aluno"
        )

        self.conn_local = mysql.connector.connect(
            user='software',
            host='localhost',
            database='maze_local',
            passwd='software'
        )

    def get_thresholds(self):
        cursor = self.conn_local.cursor()

        # tentar ir buscar da simulação ativa
        cursor.execute("""
            SELECT OutlierTempThreshold, OutlierNoiseThreshold
            FROM Simulacao
            WHERE Estado = 'Ativo'
            LIMIT 1
        """)

        result = cursor.fetchone()

        if not result or result[0] is None or result[1] is None:
            cursor.execute("""
                SELECT DefaultTempThreshold, DefaultNoiseThreshold
                FROM ConfiguracaoSistema
                WHERE is_active = 1
                LIMIT 1
            """)
            result = cursor.fetchone()

        cursor.close()

        if not result:
            raise Exception("Configuração não encontrada")

        return {
            "temp": result[0],
            "noise": result[1]
        }

    def close(self):
        self.conn_cloud.close()
        self.conn_local.close()