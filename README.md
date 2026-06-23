# Sensores IoT MQTT — Prueba de Concepto con Mosquitto

POC académica para la materia **Análisis y Diseño de Aplicaciones**  
Módulo: *Implementando soluciones de arquitectura* — Tema: **Mensajería asíncrona (MQTT)**

---

## Objetivo académico

Demostrar en vivo los siguientes conceptos de arquitectura de software mediante un caso de sensores IoT distribuidos:

- Comunicación **asíncrona** entre dispositivos
- **Desacoplamiento total** entre publishers y subscribers
- **Broker de mensajería** como intermediario central
- Patrón **Publish / Subscribe** puro
- **Tópicos jerárquicos** para organización de datos
- Uso de **wildcards (`+` y `#`)** para suscripciones flexibles
- **Escalabilidad** de subscribers sin modificar publishers
- Distribución de eventos en **tiempo real**

---

## El caso: Sistema de sensores IoT en aulas

Un conjunto de sensores distribuidos en aulas envían datos de telemetría en tiempo real.  
Cada sensor publica su información **sin conocer quién la consume**.  
Los consumidores se suscriben únicamente a los tópicos que les interesan.

Cuando un sensor registra una lectura, publica el dato en Mosquitto.  
Dos clientes independientes consumen esos eventos simultáneamente:

| Subscriber              | Responsabilidad                                                 |
|-------------------------|-----------------------------------------------------------------|
| subscriber_all.py       | Recibe lecturas en tiempo real de todas las aulas              |
| subscriber_temperatura.py | Filtra solo los datos de temperatura para alertas            |

---

## Arquitectura

```
        ┌──────────────────────────┐    ┌──────────────────────────┐
        │  Sensor Aula 1           │    │  Sensor Aula 2           │
        │  (Publisher)             │    │  (Publisher)             │
        │                          │    │                          │
        │  sensores/aula1/temp     │    │  sensores/aula2/temp     │
        │  sensores/aula1/humedad  │    │  sensores/aula2/humedad  │
        └────────────┬─────────────┘    └────────────┬─────────────┘
                     │                               │
                     └───────────────┬───────────────┘
                                     │ publica dato de telemetría
                                     │ (MQTT · texto plano · tópico jerárquico)
                                     ▼
                    ┌────────────────────────────────┐
                    │        Mosquitto Broker        │
                    │           (Docker)             │
                    │                                │
                    │  Enruta mensajes por tópico    │
                    └───────────┬────────────────────┘
                                │
               ┌────────────────┼────────────────┐
               ▼                ▼                ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │  sub_all     │ │  sub_temp    │ │   Otros      │
      │  sensores/#  │ │ sensores/+/  │ │  clientes    │
      │              │ │ temperatura  │ │              │
      └──────────────┘ └──────────────┘ └──────────────┘
        (subscriber)     (subscriber)     (subscriber)
```

> **Nota:** Mosquitto corre **dentro de Docker**. Los clientes (`mosquitto_sub` /
> `mosquitto_pub`) corren **dentro del mismo contenedor** o desde tu máquina
> local conectándose a `localhost:1883` vía MQTT.

---

## Diferencia clave con AMQP

| Característica       | MQTT (esta POC)                         | AMQP (RabbitMQ)                          |
|----------------------|------------------------------------------|------------------------------------------|
| Modelo               | Publish / Subscribe puro                | Exchange → Queue → Consumer              |
| Colas                | No existen (el broker enruta por tópico)| Colas durables por consumer              |
| Persistencia         | Opcional (retained messages, QoS 1/2)   | Garantizada (mensajes persistentes)      |
| Consumer caído       | Pierde mensajes (QoS 0 por defecto)     | Acumula mensajes en la cola              |
| Routing              | Jerárquico por tópico + wildcards        | Exchange types (direct, fanout, topic)   |
| Protocolo            | Liviano, binario, ideal para IoT        | Más robusto, orientado a enterprise      |
| UI de administración | No incluida                             | UI web en puerto 15672                   |

---

## Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo
- Python 3.8 o superior instalado
- Terminal (PowerShell, bash, zsh, etc.)

---

## Estructura del proyecto

```
mqtt-mosquitto-poc/
├── docker-compose.yml              <- Levanta Mosquitto
├── requirements.txt                <- Dependencia: paho-mqtt
├── README.md                       <- Este archivo
├── mosquitto/
│   └── config/
│       └── mosquitto.conf          <- Configuración del broker
└── src/
    ├── publisher.py                <- Simula sensores publicando telemetría
    ├── subscriber_all.py           <- Subscriber: recibe todos los tópicos
    └── subscriber_temperatura.py   <- Subscriber: solo temperatura, con alertas
```

---

## Configuración del broker

```conf
listener 1883
allow_anonymous true
```

> Configuración simplificada para entorno académico. En producción se
> configuraría autenticación con usuario/contraseña o certificados TLS.

---

## Instalación y puesta en marcha

### 1. Levantar Mosquitto con Docker

```bash
docker compose up -d
```

Verificar que el contenedor está corriendo:

```bash
docker ps
```

Verificar los logs del broker:

```bash
docker compose logs mosquitto
```

---

### 2. Crear el entorno virtual e instalar dependencias

```bash
python -m venv venv
```

Activar el entorno:

- **Windows:** `.\venv\Scripts\activate`
- **macOS / Linux:** `source venv/bin/activate`

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## Ejecutar la demo

Abre **3 terminales** desde la raíz del proyecto.

### Terminal 1 — Subscriber general (recibe todo)

```bash
python src/subscriber_all.py
```

Se suscribe a `sensores/#` y muestra todas las lecturas en tiempo real con marca de hora.

También se puede ejecutar directamente desde el contenedor:

```bash
docker exec -it mosquitto sh
mosquitto_sub -v -t sensores/#
```

---

### Terminal 2 — Subscriber de temperatura (solo temperatura)

```bash
python src/subscriber_temperatura.py
```

Se suscribe a `sensores/+/temperatura` y filtra solo temperatura. Muestra una alerta cuando la lectura supera los 28 °C.

También se puede ejecutar directamente desde el contenedor:

```bash
docker exec -it mosquitto sh
mosquitto_sub -v -t sensores/+/temperatura
```

---

### Terminal 3 — Publisher (sensores simulados)

```bash
python src/publisher.py
```

Simula dos sensores (Aula 1 y Aula 2) publicando temperatura y humedad cada 2 segundos con valores aleatorios.

También se puede publicar manualmente desde el contenedor:

```bash
docker exec -it mosquitto sh
mosquitto_pub -t sensores/aula1/temperatura -m "24.7"
mosquitto_pub -t sensores/aula1/humedad -m "65"
```

---

## Escenarios de demostración

### Escenario 1 — Flujo normal

1. Inicia `subscriber_all.py` (Terminal 1) y `subscriber_temperatura.py` (Terminal 2).
2. Ejecuta el publisher (Terminal 3).
3. Observa que el subscriber general recibe temperatura y humedad de ambas aulas, mientras el subscriber de temperatura solo recibe temperatura.
4. Ambos reciben los datos simultáneamente sin que el publisher sepa quién está escuchando.

---

### Escenario 2 — Wildcards en acción

1. Con los subscribers activos, publicá manualmente desde el contenedor:

   ```bash
   docker exec -it mosquitto sh
   mosquitto_pub -t sensores/aula1/temperatura -m "24.7"
   mosquitto_pub -t sensores/aula2/temperatura -m "22.3"
   mosquitto_pub -t sensores/aula3/temperatura -m "26.1"
   ```

2. Observa que `subscriber_temperatura.py` (`sensores/+/temperatura`) recibe las tres lecturas, incluyendo el Aula 3 que no existía antes.
3. Publicá humedad:

   ```bash
   mosquitto_pub -t sensores/aula1/humedad -m "65"
   ```

4. `subscriber_temperatura.py` **no recibe este mensaje**. `subscriber_all.py` sí.

> Esto demuestra el **filtrado flexible** por tópico sin necesidad de lógica en el broker.

---

### Escenario 3 — Subscriber caído (diferencia con AMQP)

1. Detén `subscriber_all.py` con `Ctrl+C` en la Terminal 1.
2. Dejá el publisher corriendo — sigue publicando mensajes.
3. Volvé a iniciar el subscriber:

   ```bash
   python src/subscriber_all.py
   ```

4. Observa que **no recibe los mensajes publicados mientras estuvo caído**.

> Esto ilustra la diferencia fundamental con AMQP: **MQTT por defecto (QoS 0)
> no garantiza entrega** si el subscriber no está conectado. En AMQP, los
> mensajes se acumulan en la cola y se entregan cuando el consumer se recupera.

---

### Escenario 4 — Escalabilidad: nuevos subscribers sin cambiar nada

1. Abrí una cuarta terminal y ejecutá `subscriber_temperatura.py` nuevamente:

   ```bash
   python src/subscriber_temperatura.py
   ```

2. Observa que ahora hay **dos instancias** recibiendo los mismos mensajes en paralelo.
3. El publisher no requirió ningún cambio — no sabe cuántos subscribers hay.

> Esto demuestra **escalabilidad y desacoplamiento**: cualquier nuevo cliente
> puede suscribirse en cualquier momento sin coordinación con los publishers.

---

## Wildcards — Referencia rápida

### `#` — Multinivel

```bash
mosquitto_sub -v -t sensores/#
```

Recibe: `sensores/aula1/temperatura`, `sensores/aula2/humedad`, `sensores/aula1/co2/ppm`, etc.  
Captura todo lo que esté bajo `sensores/` sin importar profundidad.

---

### `+` — Un nivel

```bash
mosquitto_sub -v -t sensores/+/temperatura
```

Recibe: `sensores/aula1/temperatura`, `sensores/aula2/temperatura`  
**No recibe:** `sensores/aula1/humedad`, `sensores/edificioA/aula1/temperatura`

---

### Combinación

```bash
mosquitto_sub -v -t sensores/aula1/+
```

Recibe todos los tipos de sensor del Aula 1 (temperatura, humedad, co2, etc.)  
pero no de otras aulas.

---

## Conceptos demostrados

| Concepto            | Dónde se ve en la POC                                                                        |
|---------------------|----------------------------------------------------------------------------------------------|
| **Broker**          | Mosquitto actúa como intermediario entre publishers y subscribers                            |
| **Publisher**       | `publisher.py` publica sin saber quién está suscripto; o `mosquitto_pub` manualmente         |
| **Subscriber**      | `subscriber_all.py` y `subscriber_temperatura.py` reciben mensajes de forma independiente    |
| **Tópicos**         | `sensores/aula1/temperatura` — jerarquía con `/` como separador                              |
| **Wildcard `#`**    | Suscripción a múltiples niveles — usado en `subscriber_all.py`                               |
| **Wildcard `+`**    | Suscripción a un nivel específico — usado en `subscriber_temperatura.py`                     |
| **Desacoplamiento** | Los publishers no conocen ni dependen de los subscribers                                     |
| **Escalabilidad**   | Se pueden agregar subscribers en cualquier momento sin cambiar nada                          |
| **QoS 0**           | Fire-and-forget: el broker no garantiza entrega si el subscriber está desconectado           |

---

## Preguntas posibles en la presentación

**¿Qué pasa si Mosquitto se reinicia?**  
Con la configuración de esta POC (QoS 0, sin persistencia), los mensajes publicados durante el downtime se pierden. Para mayor durabilidad se pueden usar mensajes retained o QoS 1/2.

**¿Qué es un mensaje retained?**  
Un mensaje marcado como retained es almacenado por el broker y enviado inmediatamente a cualquier nuevo subscriber que se conecte a ese tópico. Útil para que un sensor "anuncie" su último valor conocido.

**¿Qué es QoS en MQTT?**  
Quality of Service define la garantía de entrega:
- QoS 0: Fire-and-forget, sin confirmación (esta POC).
- QoS 1: Al menos una entrega (puede haber duplicados).
- QoS 2: Exactamente una entrega.

**¿Cuál es la diferencia entre MQTT y REST/HTTP?**  
HTTP es síncrono: el emisor espera la respuesta del receptor. MQTT es asíncrono: el publisher publica en el broker y continúa sin esperar. El broker se encarga de distribuir el mensaje a todos los subscribers conectados.

**¿Cuándo usaría MQTT en vez de AMQP?**  
MQTT es ideal para dispositivos con recursos limitados (sensores, microcontroladores) y redes inestables, donde la ligereza del protocolo es crítica. AMQP es preferible cuando se necesitan garantías fuertes de entrega, persistencia de mensajes y routing complejo en sistemas enterprise.

---

## Detener el entorno

```bash
docker compose down
```

---

## Conclusión

MQTT es un protocolo de mensajería asíncrona basado en broker que permite desacoplar completamente publishers y subscribers mediante un sistema de tópicos jerárquicos. Su diseño liviano lo hace ideal para sistemas IoT y telemetría en tiempo real, donde la simplicidad y la eficiencia de red son prioritarias sobre las garantías de entrega de protocolos más robustos como AMQP.