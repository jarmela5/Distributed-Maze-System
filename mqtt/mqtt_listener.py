import paho.mqtt.client as mqtt
import time
import sys

# =============================
# CONFIGURAÇÃO
# =============================

BROKER = "broker.emqx.io"
PORT = 1883
PLAYER_ID = 6

TOPICS = [
    f"pisid_mazemov_{PLAYER_ID}",
    f"pisid_mazetemp_{PLAYER_ID}",
    f"pisid_mazesound_{PLAYER_ID}"
]

# =============================
# CALLBACKS
# =============================

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[CONNECTED] Successfully connected to broker.")
        for topic in TOPICS:
            client.subscribe(topic)
            print(f"[SUBSCRIBED] {topic}")
    else:
        print(f"[ERROR] Connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"\n[RECEIVED]")
    print(f"Topic: {msg.topic}")
    print(f"Payload: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    print("[DISCONNECTED] Attempting to reconnect...")
    while True:
        try:
            client.reconnect()
            print("[RECONNECTED]")
            break
        except:
            print("Reconnect failed. Retrying in 5 seconds...")
            time.sleep(5)

# =============================
# MAIN
# =============================

def main():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    try:
        print("Connecting to broker...")
        client.connect(BROKER, PORT, 60)
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

    client.loop_forever()

if __name__ == "__main__":
    main()