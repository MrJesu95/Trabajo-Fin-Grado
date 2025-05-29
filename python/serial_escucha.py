from client.serialEvent import SerialEvent
import time
import os
import platform

def clear_screen():
    """Limpia la terminal después de 2 segundos"""
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    # Detectar el sistema operativo y asignar el puerto serial
    if platform.system() == 'Windows':
        puerto = "COM3"  # Puerto común en Windows
    elif platform.system() == 'Linux':
        puerto = "/dev/serial0"  # Puerto común en Raspberry Pi
    else:
        raise OSError("Sistema operativo no soportado")
    baudrate = 9600
    evento = "serial_event"

    listener = SerialEvent(puerto, baudrate, evento)

    try:
        listener.start(SerialEvent.handle_event)
        print("Conexión serial establecida. Escribe tus mensajes (o 'exit' para salir):")
        
        while True:
            mensaje = input("> ")  # Prompt para entrada de usuario
            
            if mensaje.lower() == 'exit':
                break
                
            listener.send(mensaje)
            clear_screen()
            print("Conexión serial activa. Escribe otro mensaje (o 'exit' para salir):")

    except KeyboardInterrupt:
        print("\nInterrupción por teclado detectada.")
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        listener.stop()