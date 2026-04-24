import paho.mqtt.client as mqtt
import time


class MQTTListener:

    def __init__(self, broker, port, player_id, event_processor):

        self.broker = broker
        self.port = port
        self.player_id = player_id
        self.event_processor = event_processor

        self.topics = [
            f"pisid_mazemov_{player_id}",
            f"pisid_mazetemp_{player_id}",
            f"pisid_mazesound_{player_id}"
        ]

        self.client = mqtt.Client()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect


    def on_connect(self, client, userdata, flags, rc):

        if rc == 0:

            print("[CONNECTED] MQTT")

            for topic in self.topics:
                client.subscribe(topic)
                print("[SUBSCRIBED]", topic)

        else:
            print("[ERROR] MQTT connection failed", rc)


    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()

        print("\n[DEBUG MQTT]")
        print("TOPIC:", msg.topic)
        print("PAYLOAD:", payload)

        self.event_processor.process(msg.topic, payload)


    def on_disconnect(self, client, userdata, rc):

        print("[DISCONNECTED] Reconnecting...")

        while True:
            try:
                client.reconnect()
                print("[RECONNECTED]")
                break

            except:
                print("Retry in 5 seconds")
                time.sleep(5)


    def start(self):

        print("Connecting to broker:", self.broker)

        self.client.connect(self.broker, self.port, 60)

        self.client.loop_forever()