import mysql.connector


class ConfigManager:

    def __init__(self):
        self.conn = mysql.connector.connect(
            user="aluno",
            host="194.210.86.10",
            database="maze",
            passwd="aluno"
        )

    def get_maze_graph(self):

        cursor = self.conn.cursor()

        query = """
        SELECT RoomA, RoomB
        FROM Corridor
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()

        graph = {}

        for a, b in rows:

            if a not in graph:
                graph[a] = []

            if b not in graph:
                graph[b] = []

            graph[a].append(b)
            graph[b].append(a)

        return graph


    def get_temperature_config(self):

        cursor = self.conn.cursor()

        query = """
        SELECT normaltemperature,
               temperaturevarhightoleration,
               temperaturevarlowtoleration
        FROM SetupMaze
        """

        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()

        normal, high_tol, low_tol = result

        return {
            "normal": normal,
            "high_tol": high_tol,
            "low_tol": low_tol
        }


    def get_noise_config(self):

        cursor = self.conn.cursor()

        query = """
        SELECT normalnoise,
               noisevartoleration
        FROM SetupMaze
        """

        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()

        normal, tol = result

        return {
            "normal": normal,
            "tolerance": tol
        }


    def close(self):
        self.conn.close()