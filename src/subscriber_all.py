import paho.mqtt.client as mqtt
from datetime import datetime

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "sensores/#"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe(TOPIC)
        print(f"Conectado. Escuchando: {TOPIC}\n")
    else:
        print(f"Error: {reason_code}")


def on_message(client, userdata, msg):
    hora  = datetime.now().strftime("%H:%M:%S")
    valor = msg.payload.decode()
    print(f"[{hora}]  {msg.topic:<40} {valor}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()