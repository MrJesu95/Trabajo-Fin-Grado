import time
import socketio
import os
import platform
from client.clientSocketIO import ClientSocketIO

# Configuración inicial
token = "Tvhc]+@Ud*cvNsQwB|.2}I14%£|k3o)+nqz1l1~Tl-tox45?pZ"
client = ClientSocketIO(token=token)  # Crear instancia del cliente

def limpiar_pantalla():
    if platform.system() == "Windows":
        os.system("cls")  # Comando para Windows
    else:
        os.system("clear")  # Comando para Linux y macOS

def send_status(opcion, status):
    print(f"Has seleccionado la opción {opcion}.")
    print(f"Enviando estado: {status}...\n")
    client.send_data('setStatus', 'status', status)
    time.sleep(1)

def send_contador(opcion, contador):
    print(f"Has seleccionado la opción {opcion}.")
    print(f"Enviando contador: {contador}...\n")
    client.send_data('setNumSesion', 'numSesion', contador)
    time.sleep(1)

def mostrar_menu():
    print("==== MENÚ PRINCIPAL ====")
    print("1. Send Running")
    print("2. Send Pause")
    print("3. Send Error")
    print("4. Send Reset")
    print("5. Send Cargar Sesiones")
    print("6. Send Contador")
    print("x. Exit")
    print("=========================")

def handle_incoming_data(data):
    """Manejador para datos entrantes"""
    print(f"\nDato recibido del servidor: {data}")
    # Aquí puedes añadir más lógica para procesar los datos recibidos

def main():
    # Conectar al servidor
    client.conectar()
    
    # Configurar el manejador de datos entrantes
    client.receive_data('buttonClick', handle_incoming_data)
    
    try:
        while True:
            limpiar_pantalla()
            mostrar_menu()
            
            opcion = input("Selecciona una opción: ")
            print()  # Línea vacía para separar visualmente las acciones
            
            if opcion == '1':
                send_status(opcion, "running")
            elif opcion == '2':
                send_status(opcion, "paused")
            elif opcion == '3':
                send_status(opcion, "error")
            elif opcion == '4':
                send_status(opcion, "reset")
            elif opcion == '5':
                send_status(opcion, "sessionState")
            elif opcion == '6':
                contador = input("Numero del contador: ")
                send_contador(opcion, contador)
            elif opcion.lower() == 'x':
                print("Saliendo del simulador...")
                break
            else:
                print("Opción inválida. Por favor, selecciona una opción correcta.\n")
                time.sleep(3)
    except KeyboardInterrupt:
        print("\nInterrupción recibida, saliendo...")
    finally:
        client.desconectar()
        print("Conexión cerrada correctamente")

if __name__ == "__main__":
    main()