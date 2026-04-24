from datetime import datetime
import heapq
import json
import time
import mysql.connector
import paho.mqtt.client as mqtt


class MySQLWriter:

    TOPIC = "pisid_migrate_all"
    TOPIC_CONFIRM = "pisid_migrate_confirm"

    def __init__(self, broker, port):

        self.mysql_conn = self._conectar_mysql()
        self._running = True
        self.simulation_id = self._create_simulation()

        # buffer ordenado por seq
        self._buffer = []

        # MQTT
        self._mqtt = mqtt.Client(
            client_id="mysql_writer",
            clean_session=False
        )

        self._mqtt.on_connect = self._on_connect
        self._mqtt.on_message = self._on_message
        self._mqtt.on_disconnect = self._on_disconnect

        print("[MySQLWriter] CONNECTING TO BROKER...")
        self._mqtt.connect(broker, port)

    #  MYSQL 

    def _conectar_mysql(self):
        conn = mysql.connector.connect(
            user='root',
            host='localhost',
            database='maze_local',
            passwd='root'
        )
        conn.autocommit = False
        return conn

    #  SIMULAÇÃO 

    def _create_simulation(self):
        cursor = self.mysql_conn.cursor()
        cursor.execute("SELECT IDSimulacao FROM Simulacao WHERE Estado='Ativo' LIMIT 1")
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]

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

        cursor = self.mysql_conn.cursor()
        cursor.callproc("IniciarJogo", [simulation_id])
        self.mysql_conn.commit()
        cursor.close()

        return simulation_id

    #  MQTT 

    def _on_connect(self, client, userdata, flags, rc):
        print(f"[MySQLWriter] CONNECT rc={rc}")

        if rc == 0:
            client.subscribe(self.TOPIC, qos=1)
            print(f"[MySQLWriter] Subscribed to {self.TOPIC}")

    def _on_disconnect(self, client, userdata, rc):
        print("[MySQLWriter] Desconectado — a reconectar...")

        while True:
            try:
                client.reconnect()
                print("[MySQLWriter] Reconectado")
                break
            except:
                time.sleep(3)

    def _on_message(self, client, userdata, msg):
        try:
            raw = msg.payload.decode()
            print("[MySQLWriter] MQTT RECEIVED:", raw)

            doc = json.loads(raw)
            seq = doc.get("seq")

            if seq is None:
                print("[MySQLWriter] MSG sem seq ignorada")
                return

            if not any(s == seq for s, _ in self._buffer):
                heapq.heappush(self._buffer, (seq, doc))
                print(f"[MySQLWriter] buffered seq={seq}")

        except Exception as e:
            print(f"[MySQLWriter] MQTT error: {e}")

    #  CONFIRMAÇÃO 

    def _publicar_confirmacao(self, seq, success):
        self._mqtt.publish(
            self.TOPIC_CONFIRM,
            json.dumps({"seq": seq, "success": success}),
            qos=1
        )

    #  PROCESSAMENTO 

    def _process_buffer(self):
        """
        Processa por ordem crescente de seq,
        mas sem exigir sequência perfeita.
        """

        while self._buffer:
            seq, doc = heapq.heappop(self._buffer)
            self._inserir(seq, doc)

    #  INSERT PRINCIPAL 

    def _inserir(self, seq, doc):

        print(f"[MySQLWriter] INSERT START seq={seq}, type={doc.get('type')}")

        cursor = None

        try:
            event_type = doc.get("type")
            id_jogo = self.simulation_id

            cursor = self.mysql_conn.cursor()

            if event_type == "movement":
                self._insert_movement(cursor, doc, id_jogo)

            elif event_type == "temperature":
                self._insert_temperature(cursor, doc, id_jogo)

            elif event_type == "sound":
                self._insert_sound(cursor, doc, id_jogo)

            elif event_type == "occupancy":
                self._insert_occupancy(cursor, doc, id_jogo)

            elif event_type == "alert":
                self._insert_alert(cursor, doc, id_jogo)

            else:
                print(f"[MySQLWriter] TIPO DESCONHECIDO: {event_type}")
                self._publicar_confirmacao(seq, False)
                return

            self.mysql_conn.commit()
            self._publicar_confirmacao(seq, True)

            print(f"[MySQLWriter] OK type={event_type} seq={seq}")

        except mysql.connector.Error as e:
            print(f"[MySQLWriter ERROR] seq={seq}: {e}")

            try:
                self.mysql_conn.rollback()
            except:
                pass

            self._publicar_confirmacao(seq, False)

        finally:
            if cursor:
                cursor.close()

    #  INSERTS MYSQL 

    def _insert_movement(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO MedicoesPassagens
            (seq, Hora, SalaOrigem, SalaDestino, Marsami, Status, is_valid, IDJogo)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE IDJogo = VALUES(IDJogo)
        """, (
            doc.get("seq"),
            doc.get("timestamp"),
            doc.get("origin"),
            doc.get("destiny"),
            doc.get("marsami_id"),
            doc.get("status"),
            doc.get("is_valid", True),
            id_jogo
        ))

    def _insert_temperature(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO Temperatura
            (seq, Hora, Temperatura, is_valid, IDJogo)
            VALUES (%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE Temperatura = VALUES(Temperatura)
        """, (
            doc.get("seq"),
            doc.get("timestamp"),
            float(doc.get("value", 0)),
            doc.get("is_valid", True),
            id_jogo
        ))

    def _insert_sound(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO Som
            (seq, Hora, Som, is_valid, IDJogo)
            VALUES (%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE Som = VALUES(Som)
        """, (
            doc.get("seq"),
            doc.get("timestamp"),
            float(doc.get("value", 0)),
            doc.get("is_valid", True),
            id_jogo
        ))

    def _insert_occupancy(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO OcupacaoLabirinto
            (IDJogo, Sala, NumeroMarsamisOdd, NumeroMarsamisEven)
            VALUES (%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                NumeroMarsamisOdd = VALUES(NumeroMarsamisOdd),
                NumeroMarsamisEven = VALUES(NumeroMarsamisEven)
        """, (
            id_jogo,
            doc.get("room_id"),
            doc.get("odd"),
            doc.get("even")
        ))

    def _insert_alert(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO Mensagens
            (Hora, Sala, Sensor, Leitura, TipoAlerta, Msg, HoraEscrita, IDJogo)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            doc.get("timestamp"),
            doc.get("sala"),
            doc.get("sensor"),
            doc.get("leitura"),
            doc.get("tipo"),
            doc.get("msg"),
            datetime.now(),
            id_jogo
        ))

    #  MAIN LOOP 

    def start(self):
        print("[MySQLWriter] iniciado")

        self._mqtt.loop_start()

        while self._running:
            self._process_buffer()
            time.sleep(0.05)

    def stop(self):
        self._running = False
        self._mqtt.loop_stop()
        self._mqtt.disconnect()
        self.mysql_conn.close()
        print("[MySQLWriter] stopped")