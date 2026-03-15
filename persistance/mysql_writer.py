from datetime import datetime
import json
import mysql.connector
import paho.mqtt.client as mqtt


class MySQLWriter:
    """
    Subscreve o tópico único de migração no MQTT e insere no MySQL local.
    Usa o campo 'type' para distinguir movimento, temperatura e som.
    A ordem de inserção é garantida pela ordem de chegada das mensagens no tópico.
    """

    TOPIC = "pisid_migrate_all"

    def __init__(self, broker, port):
        self.mysql_conn = self._conectar_mysql()
        self._running = True
        self.simulation_id = self._create_simulation()

        self._mqtt = mqtt.Client(client_id="mysql_writer")
        self._mqtt.on_connect = self._on_connect
        self._mqtt.on_message = self._on_message
        self._mqtt.connect(broker, port)

    def _conectar_mysql(self):
        conn = mysql.connector.connect(
            user='root',
            host='localhost',
            database='maze_local',
            passwd='root'
        )
        conn.autocommit = False
        return conn
    
    def _create_simulation(self):

        cursor = self.mysql_conn.cursor()

        dados = json.dumps({
            "Email": "system",
            "StartTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Descricao": "Simulação iniciada automaticamente"
        })

        args = [dados, 0]

        result = cursor.callproc("CriarJogo", args)

        simulation_id = result[1]

        self.mysql_conn.commit()
        cursor.close()

        print(f"[MySQLWriter] Simulação criada ID={simulation_id}")

        return simulation_id
    

    def _get_active_jogo_id(self):
        return self.simulation_id

    # Handlers MQTT 

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(self.TOPIC, qos=1)
            print(f"[MySQLWriter] Subscribed to {self.TOPIC}")
        else:
            print(f"[MySQLWriter] Connection failed: {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            doc = json.loads(msg.payload.decode())
            event_type = doc.get("type")

            id_jogo = self._get_active_jogo_id()
            if id_jogo is None:
                print("[MySQLWriter] Nenhuma simulação encontrada — mensagem ignorada")
                return

            cursor = self.mysql_conn.cursor()

            if event_type == "movement":
                self._insert_movement(cursor, doc, id_jogo)

            elif event_type == "temperature":
                self._insert_temperature(cursor, doc, id_jogo)

            elif event_type == "sound":
                self._insert_sound(cursor, doc, id_jogo)

            elif event_type == "occupancy":
                self._insert_occupancy(cursor, doc, id_jogo)
            else:
                print(f"[MySQLWriter] Tipo desconhecido: {event_type}")
                return

            self.mysql_conn.commit()
            cursor.close()
            print(f"[MySQLWriter] Inserido no MySQL (type={event_type}, seq={doc.get('seq')})")

        except Exception as e:
            self.mysql_conn.rollback()
            print("[MySQLWriter] ERRO SQL:")
            print(e)
            print("DOC:", doc)

    #Inserts MySQL

    def _insert_movement(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO MedicoesPassagens (Hora, SalaOrigem, SalaDestino, Marsami, Status, is_valid, IDJogo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            doc.get("timestamp"),
            doc.get("origin"),
            doc.get("destiny"),
            doc.get("marsami_id"),
            doc.get("status"),
            doc.get("is_valid", True),
            id_jogo,
        ))

    def _insert_temperature(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO Temperatura (Hora, Temperatura, is_valid, IDJogo)
            VALUES (%s, %s, %s, %s)
        """, (
            doc.get("timestamp"),
            str(round(float(doc.get("value", 0)), 2)),
            doc.get("is_valid", True),
            id_jogo,
        ))

    def _insert_sound(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO Som (Hora, Som, is_valid, IDJogo)
            VALUES (%s, %s, %s, %s)
        """, (
            doc.get("timestamp"),
            str(round(float(doc.get("value", 0)), 2)),
            doc.get("is_valid", True),
            id_jogo,
        ))

    def _insert_occupancy(self, cursor, doc, id_jogo):

        cursor.execute("""
            INSERT INTO OcupacaoLabirinto (IDJogo, Sala, NumeroMarsamisOdd, NumeroMarsamisEven)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                NumeroMarsamisOdd = VALUES(NumeroMarsamisOdd),
                NumeroMarsamisEven = VALUES(NumeroMarsamisEven)
        """, (
            id_jogo,
            doc.get("room_id"),
            doc.get("odd"),
            doc.get("even")
        ))

    # Start/Stop

    def start(self):
        print("[MySQLWriter] A iniciar MQTT → MySQL")
        self._mqtt.loop_forever()

    def stop(self):
        self._running = False
        self._mqtt.loop_stop()
        self._mqtt.disconnect()
        self.mysql_conn.close()
        print("[MySQLWriter] stopped")