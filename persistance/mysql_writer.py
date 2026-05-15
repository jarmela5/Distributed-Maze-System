from datetime import datetime
import heapq
import json
import time
import mysql.connector
import paho.mqtt.client as mqtt


class MySQLWriter:
    TOPIC = "pisid_migrate_all"
    TOPIC_CONFIRM = "pisid_migrate_confirm"

    # 1. CORREÇÃO: Adicionado php_mode=False como argumento padrão
    def __init__(self, broker, port, php_mode=False):
        self.mysql_conn = self._conectar_mysql()
        self._running = True
        
        # 2. CORREÇÃO: Guardar a variável na instância para poder ser lida noutros métodos
        self.php_mode = php_mode
        self.simulation_id = None if self.php_mode else self._create_simulation()

        # Buffer ordenado + controlo de duplicados
        self._buffer = []
        self._seen = set()

        self._mqtt = mqtt.Client(
            client_id="mysql_writer",
            clean_session=True
        )

        self._mqtt.on_connect = self._on_connect
        self._mqtt.on_message = self._on_message
        self._mqtt.on_disconnect = self._on_disconnect

        print(f"[MySQLWriter] CONNECTING TO BROKER (PHP Mode: {self.php_mode})...")
        self._mqtt.connect(broker, port)
        self._mqtt.loop_start()

    def _conectar_mysql(self):
        conn = mysql.connector.connect(
            user='software',
            host='127.0.0.1',
            database='maze_local',
            passwd='software'
        )
        conn.autocommit = False
        return conn

    def _create_simulation(self):
        cursor = self.mysql_conn.cursor()
        cursor.execute("SELECT IDSimulacao FROM Simulacao WHERE Estado='Ativo' LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            print(f"[MySQLWriter] Simulação ativa encontrada: {result[0]}")
            cursor.close()
            return result[0]

        args = [6, "Simulação automática", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Ativo", 0]
        result = cursor.callproc("CriarJogo", args)
        simulation_id = result[4]

        self.mysql_conn.commit()
        cursor.close()
        print(f"[MySQLWriter] Nova simulação criada com ID: {simulation_id}")
        return simulation_id

    def _get_active_simulation_php(self):
        """Procura na BD o ID da simulação ativa aberta pelo PHP."""
        cursor = self.mysql_conn.cursor()
        cursor.execute("SELECT IDSimulacao FROM Simulacao WHERE Estado='Ativo' ORDER BY IDSimulacao DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    # --- MQTT CALLBACKS ---

    def _on_connect(self, client, userdata, flags, rc):
        print(f"[MySQLWriter] CONNECT rc={rc}")
        if rc == 0:
            client.subscribe(self.TOPIC, qos=1)

    def _on_disconnect(self, client, userdata, rc):
        print("[MySQLWriter] Desconectado — a reconectar...")
        while True:
            try:
                client.reconnect()
                break
            except:
                time.sleep(3)

    def _on_message(self, client, userdata, msg):
        try:
            doc = json.loads(msg.payload.decode())
            seq = doc.get("seq")
            event_type = doc.get("type")

            if event_type == "simulation_end":
                cursor = self.conn_local.cursor()
                query = """
                    UPDATE Simulacao 
                    SET Estado = 'Inativa' 
                    WHERE Estado = 'Ativo'
                """
                cursor.execute(query)
                self.conn_local.commit()
                cursor.close()
                print(f"[PC2] Simulação do Player {doc.get('player')} também foi marcada como Inativa localmente.")

            if seq is None:
                return

            if seq not in self._seen:
                if self.php_mode:
                    current_id = self._get_active_simulation_php()
                    if not current_id:
                        print(f"[MySQLWriter] Msg seq={seq} descartada. PHP não tem simulações ativas.")
                        self._publicar_confirmacao(seq, False)
                        return
                    doc["_resolved_id"] = current_id  
                
                # 3. CORREÇÃO: Removida a duplicação do push que tinhas aqui
                heapq.heappush(self._buffer, (seq, doc))
                self._seen.add(seq)

        except Exception as e:
            print(f"[MySQLWriter] MQTT error: {e}")

    def _publicar_confirmacao(self, seq, success):
        self._mqtt.publish(
            self.TOPIC_CONFIRM,
            json.dumps({"seq": seq, "success": success}),
            qos=1
        )

    def _process_buffer(self):
        while self._buffer:
            seq, doc = heapq.heappop(self._buffer)
            self._inserir(seq, doc)

    def _inserir(self, seq, doc):
        cursor = None
        try:
            cursor = self.mysql_conn.cursor()
            event_type = doc.get("type")
            
            # 4. CORREÇÃO: Escolhe dinamicamente entre o ID injetado (PHP) ou o fixo (Python)
            id_jogo = doc.get("_resolved_id") if self.php_mode else self.simulation_id

            if id_jogo is None and event_type != "simulation_end":
                print(f"[MySQLWriter WARNING] Mensagem seq={seq} ignorada. Sem ID de simulação válido.")
                self._publicar_confirmacao(seq, False)
                return

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
            elif event_type == "simulation_end" and not self.php_mode:
                self._finish_simulation(cursor)
            else:
                self._publicar_confirmacao(seq, False)
                return

            self.mysql_conn.commit()
            self._publicar_confirmacao(seq, True)

        except mysql.connector.Error as e:
            if e.errno == 1062:  
                print(f"[DUPLICATE] seq={seq}")
                self._publicar_confirmacao(seq, True)
                return

            print(f"[MySQLWriter ERROR] seq={seq}: {e}")
            try:
                self.mysql_conn.rollback()
            except:
                pass
            self._publicar_confirmacao(seq, False)
        finally:
            if cursor:
                cursor.close()

    # --- INSERTS ---

    def _insert_movement(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO MedicoesPassagens (seq, Hora, SalaOrigem, SalaDestino, Marsami, Status, is_valid, IDJogo)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (doc.get("seq"), doc.get("timestamp"), doc.get("origin"), doc.get("destiny"), 
              doc.get("marsami_id"), doc.get("status"), doc.get("is_valid", True), id_jogo))

    def _insert_temperature(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO Temperatura (seq, Hora, Temperatura, is_valid, IDJogo)
            VALUES (%s,%s,%s,%s,%s)
        """, (doc.get("seq"), doc.get("timestamp"), float(doc.get("value", 0)), doc.get("is_valid", True), id_jogo))

    def _insert_sound(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO Som (seq, Hora, Som, is_valid, IDJogo)
            VALUES (%s,%s,%s,%s,%s)
        """, (doc.get("seq"), doc.get("timestamp"), float(doc.get("value", 0)), doc.get("is_valid", True), id_jogo))

    def _insert_occupancy(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO OcupacaoLabirinto (IDJogo, Sala, NumeroMarsamisOdd, NumeroMarsamisEven)
            VALUES (%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                NumeroMarsamisOdd = VALUES(NumeroMarsamisOdd),
                NumeroMarsamisEven = VALUES(NumeroMarsamisEven)
        """, (id_jogo, doc.get("room_id"), doc.get("odd"), doc.get("even")))

    def _insert_alert(self, cursor, doc, id_jogo):
        cursor.execute("""
            INSERT INTO Mensagens (seq, Hora, Sala, Sensor, Leitura, TipoAlerta, Msg, HoraEscrita, IDJogo)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (doc.get("seq"), doc.get("timestamp"), doc.get("sala"), doc.get("sensor"), 
              doc.get("leitura"), doc.get("tipo"), doc.get("msg"), datetime.now(), id_jogo))

    # --- CONTROL ---

    def start(self):
        while self._running:
            self._process_buffer()
            time.sleep(0.05)

    def stop(self):
        self._running = False
        self._mqtt.loop_stop()
        self._mqtt.disconnect()
        self.mysql_conn.close()

    def _finish_simulation(self, cursor):
        cursor.execute("UPDATE Simulacao SET Estado = 'Inativo' WHERE Estado = 'Ativo'")
        self.mysql_conn.commit()
        self.simulation_id = None
        print("[MySQLWriter] Simulação marcada como Inativa via Cursor")

    def _finish_simulation_direct(self):
        cursor = self.mysql_conn.cursor()
        try:
            cursor.execute("UPDATE Simulacao SET Estado = 'Inativo' WHERE Estado = 'Ativo'")
            self.mysql_conn.commit()
            self.simulation_id = None
            print("[MySQLWriter] Simulação marcada como Inativa de forma Direta")
        except Exception as e:
            print(f"[MySQLWriter] Erro ao finalizar simulação: {e}")
        finally:
            cursor.close()
