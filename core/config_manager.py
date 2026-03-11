import mysql.connector


class ConfigManager:

    def __init__(self):
        self.conn = mysql.connector.connect(
            user='aluno',
            host='194.210.86.10',
            database='maze',
            passwd='aluno'
        )

    def get_maze_graph(self):

        cursor = self.conn.cursor()

        query = """
        SELECT Rooma,
               Roomb,
               distance
        FROM corridor
        WHERE active = 1
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()

        room_graph = {}

        for room_a, room_b, distance in rows:

            if room_a not in room_graph:
                room_graph[room_a] = []

            room_graph[room_a].append(room_b)

        return room_graph

    def close(self):
        self.conn.close()


# if __name__ == "__main__":

#     manager = ConfigManager()

#     graph = manager.get_maze_graph()

#     print("Maze graph:", graph)

#     manager.close()