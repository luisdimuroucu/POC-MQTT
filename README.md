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

| Subscriber          | Responsabilidad                                                 |
|---------------------|-----------------------------------------------------------------|
| dashboard           | Muestra lecturas en tiempo real de todas las aulas             |
| monitor técnico     | Filtra solo los datos de temperatura para alertas              |

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
      │  Dashboard   │ │   Monitor    │ │   Otros      │
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
- Terminal (PowerShell, bash, zsh, etc.)

---

## Estructura del proyecto

```
mqtt-mosquitto-poc/
├── docker-compose.yml          ← Levanta Mosquitto
├── mosquitto/
│   └── config/
│       └── mosquitto.conf      ← Configuración del broker
└── README.md                   ← Este archivo
```

---

## Configuración del broker

```conf
listener 1883
allow_anonymous true
```

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

### 2. Abrir una sesión en el contenedor

Todos los comandos de la demo se ejecutan dentro del contenedor de Mosquitto:

```bash
docker exec -it mosquitto sh
```

---

## Ejecutar la demo

Abre **3 terminales** y en cada una ingresa al contenedor:

```bash
docker exec -it mosquitto sh
```

### Terminal 1 — Dashboard (recibe todo)

```bash
mosquitto_sub -v -t sensores/#
```

> El wildcard `#` captura **cualquier tópico** que empiece con `sensores/`.  
> Este subscriber simula un dashboard que muestra todas las lecturas.

---

### Terminal 2 — Monitor técnico (solo temperatura)

```bash
mosquitto_sub -v -t sensores/+/temperatura
```

> El wildcard `+` reemplaza **exactamente un nivel** del tópico.  
> Este subscriber recibe temperatura de cualquier aula, pero ignora humedad.

---

### Terminal 3 — Publicar lecturas de sensores

```bash
mosquitto_pub -t sensores/aula1/temperatura -m "24.7"
mosquitto_pub -t sensores/aula1/humedad -m "65"
mosquitto_pub -t sensores/aula2/temperatura -m "22.3"
mosquitto_pub -t sensores/aula2/humedad -m "70"
```

Ejecuta cada línea por separado y observa en las otras terminales qué recibe cada subscriber.

---

## Escenarios de demostración

### Escenario 1 — Flujo normal

1. Inicia los 2 subscribers (Terminales 1 y 2).
2. Publica mensajes desde la Terminal 3.
3. Observa que el **dashboard** recibe todos los mensajes y el **monitor técnico** solo los de temperatura.
4. Ambos subscribers reciben los datos en tiempo real y de forma simultánea.

---

### Escenario 2 — Wildcards en acción

1. Con los subscribers activos, publica desde distintas aulas:

   ```bash
   mosquitto_pub -t sensores/aula1/temperatura -m "24.7"
   mosquitto_pub -t sensores/aula2/temperatura -m "22.3"
   mosquitto_pub -t sensores/aula3/temperatura -m "26.1"
   ```

2. Observa que el monitor técnico (`sensores/+/temperatura`) recibe las tres lecturas.
3. Ahora publica humedad:

   ```bash
   mosquitto_pub -t sensores/aula1/humedad -m "65"
   ```

4. El monitor técnico **no recibe este mensaje**. El dashboard sí.

> Esto demuestra el **filtrado flexible** por tópico sin necesidad de lógica en el broker.

---

### Escenario 3 — Subscriber caído (diferencia con AMQP)

1. Detén el dashboard con `Ctrl+C` en la Terminal 1.
2. Publica varios mensajes:

   ```bash
   mosquitto_pub -t sensores/aula1/temperatura -m "25.0"
   mosquitto_pub -t sensores/aula1/temperatura -m "25.5"
   mosquitto_pub -t sensores/aula1/temperatura -m "26.0"
   ```

3. Vuelve a iniciar el dashboard:

   ```bash
   mosquitto_sub -v -t sensores/#
   ```

4. Observa que el dashboard **no recibe los mensajes publicados mientras estuvo caído**.

> Esto ilustra la diferencia fundamental con AMQP: **MQTT por defecto (QoS 0)
> no garantiza entrega** si el subscriber no está conectado. En AMQP, los
> mensajes se acumulan en la cola y se entregan cuando el consumer se recupera.

---

### Escenario 4 — Escalabilidad: nuevos subscribers sin cambiar nada

1. Abre una cuarta terminal e ingresa al contenedor.
2. Suscríbete a un nuevo tópico específico:

   ```bash
   mosquitto_sub -v -t sensores/aula1/#
   ```

3. Publica mensajes de distintas aulas:

   ```bash
   mosquitto_pub -t sensores/aula1/temperatura -m "24.7"
   mosquitto_pub -t sensores/aula2/temperatura -m "22.3"
   ```

4. El nuevo subscriber recibe solo los mensajes del Aula 1, sin haber modificado nada en los publishers.

> Esto demuestra **escalabilidad y desacoplamiento**: cualquier nuevo cliente
> puede suscribirse a cualquier tópico sin coordinación con los publishers.

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

| Concepto            | Dónde se ve en la POC                                                              |
|---------------------|------------------------------------------------------------------------------------|
| **Broker**          | Mosquitto actúa como intermediario entre publishers y subscribers                  |
| **Publisher**       | Los comandos `mosquitto_pub` publican sin saber quién está suscripto               |
| **Subscriber**      | Los comandos `mosquitto_sub` reciben mensajes de forma independiente               |
| **Tópicos**         | `sensores/aula1/temperatura` — jerarquía con `/` como separador                    |
| **Wildcard `#`**    | Suscripción a múltiples niveles — útil para el dashboard general                   |
| **Wildcard `+`**    | Suscripción a un nivel específico — útil para filtrar por tipo de dato             |
| **Desacoplamiento** | Los publishers no conocen ni dependen de los subscribers                           |
| **Escalabilidad**   | Se pueden agregar subscribers en cualquier momento sin cambiar nada                |
| **QoS 0**           | Fire-and-forget: el broker no garantiza entrega si el subscriber está desconectado |

---

## Preguntas posibles en la presentación

**¿Qué pasa si Mosquitto se reinicia?**  
Con la configuración de esta POC (QoS 0, sin persistencia), los mensajes publicados durante el downtime se pierden. Para mayor durabilidad se pueden usar mensajes retained o QoS 1/2.

**¿Qué es un mensaje retained?**  
Un mensaje marcado como retained es almacenado por el broker y enviado inmediatamente a cualquier nuevo subscriber que se conecte a ese tópico. Útil para que un sensor "anuncie" su último valor conocido.

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