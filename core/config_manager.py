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

        cursor.execute("""
            SELECT OutlierTempThreshold, OutlierNoiseThreshold
            FROM Simulacao
            WHERE Estado = 'Ativo'
            LIMIT 1
        """)

        result = cursor.fetchone()

        if (not result or result[0] is None or result[1] is None or
            float(result[0]) == 0 or float(result[1]) == 0):
            
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
            "temp": float(result[0]),
            "noise": float(result[1])
        }

    def get_maze_graph(self):

        cursor = self.conn_cloud.cursor()

        cursor.execute("""
            SELECT RoomA, RoomB
            FROM Corridor
            WHERE active = 1
        """)

        rows = cursor.fetchall()
        cursor.close()

        graph = {}

        for a, b in rows:
            graph.setdefault(a, []).append(b)
            graph.setdefault(b, []).append(a)

        return graph


    def get_temperature_config(self):

        cursor = self.conn_cloud.cursor()

        cursor.execute("""
            SELECT normaltemperature,
                   temperaturevarhightoleration,
                   temperaturevarlowtoleration
            FROM SetupMaze
            LIMIT 1
        """)

        result = cursor.fetchone()
        cursor.close()

        if not result:
            raise Exception("Configuração de temperatura não encontrada")

        normal, high_tol, low_tol = result

        return {
            "normal": normal,
            "high_tol": high_tol,
            "low_tol": low_tol
        }


    def get_noise_config(self):

        cursor = self.conn_cloud.cursor()

        cursor.execute("""
            SELECT normalnoise,
                   noisevartoleration
            FROM SetupMaze
            LIMIT 1
        """)

        result = cursor.fetchone()
        cursor.close()

        if not result:
            raise Exception("Configuração de ruído não encontrada")

        normal, tol = result

        return {
            "normal": result[0],
            "tolerance": result[1]
        }

    def close(self):
        if self.conn_cloud.is_connected():
            self.conn_cloud.close()

        if self.conn_local.is_connected():
            self.conn_local.close()
