from datetime import datetime
import json
import time
import mysql.connector
import paho.mqtt.client as mqtt


class MySQLWriter:

    TOPIC         = "pisid_migrate_all"
    TOPIC_CONFIRM = "pisid_migrate_confirm"

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
        # se já existe um jogo ativo, reutiliza-o
        cursor = self.mysql_conn.cursor()
        cursor.execute("SELECT IDSimulacao FROM Simulacao WHERE Estado='Ativo' LIMIT 1")
        result = cursor.fetchone()
        cursor.close()

        if result:
            simulation_id = result[0]
            print(f"[MySQLWriter] Jogo ativo encontrado ID={simulation_id}")
            return simulation_id

        # caso contrário cria um novo
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

        print(f"[MySQLWriter] Simulação criada e iniciada ID={simulation_id}")
        return simulation_id

    def _get_active_jogo_id(self):
        return self.simulation_id

    def _publicar_confirmacao(self, seq, success):
        """Publica confirmação de insert para o MigrationWorker."""
        payload = json.dumps({"seq": seq, "success": success})
        self._mqtt.publish(self.TOPIC_CONFIRM, payload, qos=1)

    # MQTT handlers

    def _on_connect(self, client, userdata, flags, rc):

        if rc == 0:
            client.subscribe(self.TOPIC, qos=1)
            print(f"[MySQLWriter] Subscribed to {self.TOPIC}")
        else:
            print(f"[MySQLWriter] Connection failed: {rc}")

    def _on_message(self, client, userdata, msg):

        cursor = None
        seq = None

        try:
            doc = json.loads(msg.payload.decode())
            seq = doc.get("seq")
            event_type = doc.get("type")

            id_jogo = self._get_active_jogo_id()

            if id_jogo is None:
                print("[MySQLWriter] Nenhuma simulação encontrada — mensagem ignorada")
                self._publicar_confirmacao(seq, False)
                return

            cursor = self.mysql_conn.cursor()

            if event_type == "movement":
                self._insert_movement(cursor, doc, id_jogo)
            elif event_type == "temperature":
                self._insert_temperature(cursor, doc, id_jogo)
            elif event_type == "sound":
                self._insert_sound(cursor, doc, id_jogo)
            elif event_type == "occupancy":
                print(f"[DEBUG] occupancy doc: {doc}")
                self._insert_occupancy(cursor, doc, id_jogo)
            elif event_type == "alert":
                self._insert_alert(cursor, doc, id_jogo)    
            else:
                print(f"[MySQLWriter] Tipo desconhecido: {event_type}")
                self._publicar_confirmacao(seq, False)
                return

            self.mysql_conn.commit()

            # confirma sucesso ao MigrationWorker
            self._publicar_confirmacao(seq, True)
            print(f"[MySQLWriter] Inserido e confirmado (type={event_type}, seq={seq})")

        except mysql.connector.Error as e:

            print("[MySQLWriter] MySQL error:", e)

            try:
                self.mysql_conn.rollback()
            except:
                pass

            # confirma falha — MigrationWorker vai reenviar
            if seq is not None:
                self._publicar_confirmacao(seq, False)

            self._reconnect_mysql()

        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass

    # Inserts MySQL

    def _insert_movement(self, cursor, doc, id_jogo):

        cursor.execute("""
            INSERT INTO MedicoesPassagens
            (seq, Hora, SalaOrigem, SalaDestino, Marsami, Status, is_valid, IDJogo)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE seq = seq
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

    def _insert_temperature(self, cursor, doc, id_jogo):

        cursor.execute("""
            INSERT INTO Temperatura
            (seq, Hora, Temperatura, is_valid, IDJogo)
            VALUES (%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE seq = seq
        """, (
            doc.get("seq"),
            doc.get("timestamp"),
            round(float(doc.get("value", 0)), 2),
            doc.get("is_valid", True),
            id_jogo
        ))

    def _insert_sound(self, cursor, doc, id_jogo):

        cursor.execute("""
            INSERT INTO Som
            (seq, Hora, Som, is_valid, IDJogo)
            VALUES (%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE seq = seq
        """, (
            doc.get("seq"),
            doc.get("timestamp"),
            round(float(doc.get("value", 0)), 2),
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

    # ifecycle 

    def start(self):
        print("[MySQLWriter] A iniciar MQTT → MySQL (com confirmação)")
        self._mqtt.loop_forever()

    def stop(self):
        self._running = False
        self._mqtt.loop_stop()
        self._mqtt.disconnect()
        self.mysql_conn.close()
        print("[MySQLWriter] stopped")

    def _reconnect_mysql(self):

        while True:
            try:
                print("[MySQLWriter] Reconnecting to MySQL...")
                self.mysql_conn = self._conectar_mysql()
                self.mysql_conn.autocommit = False
                print("[MySQLWriter] MySQL reconnected")
                return
            except Exception:
                time.sleep(3)