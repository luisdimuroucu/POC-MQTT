import random
import time

import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
INTERVALO = 2  # segundos entre lecturas

SENSORES = {
    "sensores/aula1/temperatura": (20.0, 30.0),
    "sensores/aula1/humedad":     (50.0, 80.0),
    "sensores/aula2/temperatura": (18.0, 28.0),
    "sensores/aula2/humedad":     (45.0, 75.0),
}


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"Conectado a {BROKER_HOST}:{BROKER_PORT}\n")
    else:
        print(f"Error: {reason_code}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(BROKER_HOST, BROKER_PORT)
    client.loop_start()

    try:
        while True:
            for topico, (minimo, maximo) in SENSORES.items():
                valor = round(random.uniform(minimo, maximo), 1)
                client.publish(topico, str(valor))
                print(f"[PUB] {topico} -> {valor}")
            print()
            time.sleep(INTERVALO)

    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()