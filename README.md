# Interfaz Gráfica para Control de Sesiones de Dispositivo Médico con Raspberry Pi

![Estado del Proyecto](https://img.shields.io/badge/Estado-Terminado-success)

## Descripción del Proyecto

Sistema de control para el dispositivo médico MINESTIM APCM-01 (estimulación magnética transcraneal para fibromialgia) que reemplaza la interfaz basada en LEDs por:

- Interfaz gráfica intuitiva desarrollada con Electron.js
- Comunicación en tiempo real mediante WebSockets (Socket.IO)
- Backend en Python para control de hardware (GPIO y comunicación serial)
- Integración con Raspberry Pi para despliegue en entornos clínicos

## Características Principales

✔️ Gestión visual de sesiones terapéuticas  
✔️ Temporizador con cuenta regresiva (20 minutos por sesión)  
✔️ Visualización de parámetros y sesiones restantes  
✔️ Sistema de estados con feedback visual claro (inicial, ejecución, pausa, error)  
✔️ Comunicación serial para configuración del dispositivo  
✔️ Control de pines GPIO para interacción con hardware médico  
✔️ Ejecución automática al iniciar el sistema  

## Tecnologías Utilizadas

**Frontend:**
- Electron.js (HTML/CSS/JavaScript)
- Socket.IO Client

**Backend:**
- Python 3
- RPi.GPIO
- PySerial
- Socket.IO Server

**Hardware:**
- Raspberry Pi 5
- Pantalla táctil oficial de 7"
- Microcontrolador personalizado (compatible con ESP8266 para desarrollo)

## Instalación y Uso

Aplicación compilada descarga en: https://drive.google.com/file/d/1SrXqiT6Du4YDvl7AicSFSUnsmups-fk6/view?usp=drive_link

### Requisitos Previos
- Raspberry Pi OS (última versión estable)
- Node.js v16+
- Python 3.8+

### Pasos de Instalación
Copiar el archivo TFG.zip, descomprimir y ejecutar el archivo tfg. Para la ejecucion automatica copiar y pegar archivo autostart.desktop en el siguiente directorio:
/home/[nombre_usuario]/.config/autostart

Para mas información consultar la memoria en PDF.