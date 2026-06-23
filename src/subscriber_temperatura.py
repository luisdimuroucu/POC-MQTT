import paho.mqtt.client as mqtt
from datetime import datetime

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "sensores/+/temperatura"
ALERTA_ALTA = 28.0  # °C


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe(TOPIC)
        print(f"Conectado. Escuchando: {TOPIC}\n")
    else:
        print(f"Error: {reason_code}")


def on_message(client, userdata, msg):
    hora  = datetime.now().strftime("%H:%M:%S")
    valor = float(msg.payload.decode())
    aula  = msg.topic.split("/")[1]

    alerta = "[ALERTA: temperatura alta]" if valor >= ALERTA_ALTA else ""
    print(f"[{hora}]  {aula:<10}  {valor:.1f} °C{alerta}")


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