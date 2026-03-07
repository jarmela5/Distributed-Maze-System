import mysql.connector


class ConfigManager:

  def __init__(self):
    self.conn = mysql.connector.connect(
        user='aluno',
        host='194.210.86.10',
        database='maze',
        passwd='aluno'
    )


  def get_broker_config(self):

    cursor = self.conn.cursor()

    query = """
    SELECT broker,
            portbroker
    FROM setup
    WHERE active = 1
    """

    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()

    if result is None:
        raise Exception("No active broker configuration found")

    broker, port = result

    return {
        "broker": broker,
        "port": port
    }


  def get_outlier_config(self):

    cursor = self.conn.cursor()

    query = """
    SELECT error_outlier_sound,
            error_outlier_temp,
            error_origin_move_abnormal,
            error_destiny_move_abnormal
    FROM setup
    WHERE active = 1
    """

    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()

    if result is None:
        raise Exception("No active outlier configuration found")

    sound_outlier, temp_outlier, origin_error, destiny_error = result

    return {
        "sound_outlier": sound_outlier,
        "temp_outlier": temp_outlier,
        "origin_error": origin_error,
        "destiny_error": destiny_error
    }


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


if __name__ == "__main__":

    manager = ConfigManager()

    broker = manager.get_broker_config()
    outliers = manager.get_outlier_config()
    graph = manager.get_maze_graph()

    print("Broker config:", broker)
    print("Outlier config:", outliers)
    print("Maze graph:", graph)

    manager.close()