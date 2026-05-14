# 🤖 SmartAlarm – Firmware ESP32

Questo repository contiene il firmware per **ESP32-WROOM**, progettato per integrarsi con l'app mobile [SmartAlarm](https://github.com/mijji89/SmartAlarmApp).  
Il microcontrollore gestisce l’automazione domestica e la logica delle sveglie comunicando tramite **MQTT over WebSocket**.

---

## ⚙️ Tecnologie e caratteristiche principali

- **MicroPython** – linguaggio di programmazione leggero ed efficiente per ESP32
- **MQTT (su WebSocket)** – comunicazione bidirezionale con l’app
- **Programmazione asincrona** – miglior gestione delle operazioni simultanee
- **Multithreading** – suddivisione delle attività in thread separati per una risposta più rapida e fluida

---

## 🔧 Funzionalità implementate

### ⏰ Gestione sveglie
- Ricezione di orari dalla app
- Riproduzione di allarmi sonori con buzzer
- Salvataggio delle sveglie in memoria volatile

### 💡 Controllo utenze
- Accensione e spegnimento **luci** tramite relè
- Apertura e chiusura **serranda** (motorizzata)

### 🌡️ Monitoraggio ambientale
- Rilevamento di **temperatura** e **umidità** con sensore ( DHT22)
- Rilevamento di **luminosità** con apposito sensore (TSL2561)
- Invio periodico dei dati ambientali alla app

### 🔁 Comunicazione MQTT
- Connessione a broker MQTT (locale o remoto)
- Ricezione comandi da app (es. `light_on`, `set_alarm`, `open_window`)
- Pubblicazione di dati (temperatura, stato utenze) su topic dedicati
