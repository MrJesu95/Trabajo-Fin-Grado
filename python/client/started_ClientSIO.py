import time
import socketio
import os
import platform
from clientSocketIO import ClientSocketIO
from commandHandlers.jsonCommandHandler import HandleJSON
from commandHandlers.socketIOCommandHandler import SocketIOCommandHandler
from commandHandlers.serialCommandHandler import SerialCommandHandler
from serialEvent import SerialEvent
from GPIO_Event import GPIO_Event
import sys

class Started:
    """
    Clase principal que inicia y coordina todos los componentes del sistema.
    Gestiona la comunicación entre Socket.IO, serial y GPIO.
    """
    
    # Configuración inicial de Socket.IO
    sio = socketio.Client()
    token = "Tvhc]+@Ud*cvNsQwB|.2}I14%£|k3o)+nqz1l1~Tl-tox45?pZ"
    
    # Configuración del puerto serial según el sistema operativo
    if platform.system() == 'Windows':
        puerto = "COM3"  # Puerto común en Windows
    elif platform.system() == 'Linux':
        puerto = "/dev/serial0"  # Puerto común en Raspberry Pi
    else:
        raise OSError("Sistema operativo no soportado")
    baudrate = 9600
    evento = "serial_event"

    @staticmethod
    def get_base_path():
        """
        Determina la ruta base correcta tanto para ejecutables como para scripts.
        
        Returns:
            str: Ruta base del proyecto
        """
        if getattr(sys, 'frozen', False):
            # Si es un .exe, la ruta base es donde está el ejecutable
            return os.path.dirname(sys.executable)
        else:
            # Si es un script, usa la ruta del script (__file__)
            return os.path.dirname(__file__)

    dir_actual = get_base_path() # Directorio del script actual
    ruta_json = os.path.join(dir_actual, '../..', 'resources/data.json')
    handleJSON = HandleJSON(ruta_json)

    def start(self):
        """
        Método principal que inicia todos los componentes del sistema.
        Configura y conecta Socket.IO, serial y GPIO con sus respectivos handlers.
        """
        try:
            # Redirigir stdout a stderr temporalmente para capturar logs
            stdOut = sys.stdout
            sys.stdout = sys.stderr

            # Inicialización de componentes principales
            clientSocketIO = ClientSocketIO(token=self.token)
            listener = SerialEvent(self.puerto, self.baudrate, self.evento)
            gpio = GPIO_Event(TIME_WINDOW=0.5, ACTIVE=True)

            # Configuración de handlers
            handleJSON = HandleJSON(self.ruta_json)
            handleSocketIO = SocketIOCommandHandler(handleJSON, gpio, clientSocketIO)
            handleSerial = SerialCommandHandler(handleJSON, handleSocketIO, listener)

            # Establecimiento de conexiones
            clientSocketIO.conectar()
            
            # Configuración de manejadores de eventos
            clientSocketIO.receive_data('buttonClick', handleSocketIO.click_handle)
            clientSocketIO.receive_data('getStatusBeforeError', handleSocketIO.error_handle)
            clientSocketIO.receive_data('countdownFinished', handleSocketIO.final_pulse)
            listener.start(handleSerial.serial_handle)

            # Configuración de GPIO
            gpio.monitor_pulse_timeout(
                timeout=0.7, 
                timeout_callback=handleSocketIO.order_error, 
                pulse_after_timeout_callback=handleSocketIO.after_error_handle
            )
            
            # Mantener el programa en ejecución
            listener.thread.join()

        except Exception as e:
            print(f"Error en la ejecución principal: {e}")
        finally:
            # Restaurar stdout original
            sys.stdout = stdOut

if __name__ == "__main__":
    """
    Punto de entrada principal del programa.
    Crea una instancia de Started y ejecuta el sistema.
    """
    started = Started()
    started.start()