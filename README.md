# MQTT — Prueba de Concepto con Mosquitto

POC académica para la materia **Análisis y Diseño de Aplicaciones**  
Módulo: *Implementando soluciones de arquitectura* — Tema: **Mensajería asíncrona (MQTT)**

---

## Objetivo académico

Demostrar los siguientes conceptos de arquitectura de software mediante un sistema de sensores IoT:

- Comunicación **asíncrona** entre dispositivos
- Patrón **Publish / Subscribe**
- **Broker de mensajería** como intermediario central
- **Desacoplamiento total** entre productores y consumidores
- **Tópicos jerárquicos** para organización de datos
- Uso de **wildcards (`+` y `#`)**
- Escalabilidad de consumidores sin modificar productores
- Distribución de eventos en tiempo real

---

## El caso: Sistema de sensores IoT

Un sistema simula sensores distribuidos en aulas que envían datos de telemetría.

Cada sensor publica información sin conocer quién la consume.

Los consumidores se suscriben a los tópicos que les interesan.

```
Sensor (Publisher)
        │
        ▼
┌──────────────────┐
│ Mosquitto Broker │
│   (Docker)       │
└─────────┬────────┘
          │
  ┌───────┴────────┐
  ▼                ▼
Dashboard      Monitor técnico
(Subscriber)   (Subscriber)
```

---

## Arquitectura

```
        Publisher (sensores simulados)
                      │
                      ▼
             ┌───────────────────┐
             │  Mosquitto Broker │
             │   (Docker)        │
             └─────────┬─────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 Dashboard        Monitor        Otros clientes
 (subscriber)     (subscriber)   (subscriber)
```

---

## Requisitos previos

- Docker Desktop
- Docker Compose

---

## Estructura del proyecto

```
mqtt-mosquitto-poc/
├── docker-compose.yml
├── mosquitto/
│   └── config/
│       └── mosquitto.conf
└── README.md
```

---

## Configuración del broker

```conf
listener 1883
allow_anonymous true
```

> Configuración simplificada para entorno académico.

---

## Instalación y puesta en marcha

### Levantar el broker

```bash
docker compose up -d
```

Verificar:

```bash
docker ps
```

---

## Ejecución

### Suscriptores

```bash
docker exec -it mosquitto sh
mosquitto_sub -v -t sensores/#
```

### Publicador

```bash
docker exec -it mosquitto sh
mosquitto_pub -t sensores/aula1/temperatura -m "24.7"
```

---

## Ejemplo

Suscriptores:

```bash
mosquitto_sub -v -t sensores/#
```

Publicación:

```bash
mosquitto_pub -t sensores/aula1/temperatura -m "24.7"
```

Resultado:

```
sensores/aula1/temperatura 24.7
```

---

## Uso de múltiples sensores

```bash
mosquitto_pub -t sensores/aula1/temperatura -m "24"
mosquitto_pub -t sensores/aula1/humedad -m "65%"
```

---

## Wildcards

### #

```bash
mosquitto_sub -v -t sensores/#
```

### +

```bash
mosquitto_sub -v -t sensores/+/temperatura
```

---

## Conceptos

| Concepto | Descripción |
|----------|------------|
| Broker | Intermediario de mensajes |
| Publish / Subscribe | Comunicación desacoplada |
| Tópicos | Organización jerárquica |
| Wildcards | Filtrado flexible |
| Escalabilidad | Múltiples consumidores |
| Desacoplamiento | Independencia entre servicios |

---

## Escenarios

### Flujo normal

1. Iniciar suscriptores
2. Publicar mensajes
3. Recibir datos en tiempo real

### Múltiples consumidores

Todos reciben el mismo mensaje simultáneamente.

### Nuevos consumidores

Se incorporan sin modificar el sistema.

---

## Detener entorno

```bash
docker compose down
```

---

## Conclusión

MQTT es un protocolo de mensajería asíncrona basado en broker que permite desacoplar completamente productores y consumidores, ideal para sistemas IoT y telemetría en tiempo real.