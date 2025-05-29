import serial
import time
import threading

class SerialEvent:
    def __init__(self, port, baudrate, evento, timeout=1):
        """
        Inicializa el manejador de eventos seriales con configuración básica.
        
        Args:
            port (str): Puerto serial (ej: 'COM3' o '/dev/ttyUSB0')
            baudrate (int): Velocidad en baudios (ej: 9600)
            evento (str): Identificador del evento serial
            timeout (float): Tiempo de espera para operaciones seriales (segundos)
        """
        self.port = port
        self.baudrate = baudrate
        self.evento = evento
        self.timeout = timeout
        
        self.lock = threading.Lock()
        self.running = False
        self.connected = False
        self.ser = None
        self.thread = None

    def getConnected(self):
        """
        Obtiene el estado actual de conexión de forma thread-safe.
        
        Returns:
            bool: True si está conectado, False en caso contrario
        """
        with self.lock:
            return self.connected

    def conect(self):
        """
        Intenta establecer conexión serial de forma thread-safe.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        with self.lock:
            if self.connected:
                return True
            try:
                self.ser = serial.Serial(
                    self.port, 
                    self.baudrate, 
                    timeout=self.timeout
                )
                self.connected = True
                print(f"Conexion establecida en {self.port} a {self.baudrate} bps.")
                return True
            except serial.SerialException:
                print(f"Intento conectar en {self.port}.")
                return False

    def listen(self, func=None, *args, **kwargs):
        """
        Escucha continuamente datos del puerto serial y ejecuta callback.
        
        Args:
            func (callable): Función callback para procesar datos recibidos
            *args: Argumentos posicionales adicionales para el callback
            **kwargs: Argumentos clave adicionales para el callback
        """
        print(f"Escuchando evento: {self.evento}")
        while True:
            with self.lock:
                if not self.connected or not self.ser or not self.ser.is_open:
                    break
                ser = self.ser
            
            try:
                if ser.in_waiting > 0:
                    data = ser.readline().decode('utf-8').strip()
                    func(data, *args, **kwargs)
            except serial.SerialException:
                print("Conexion perdida.")
                break
            except UnicodeDecodeError:
                print("Error decodificando datos.")
            except Exception as e:
                print(f"Error inesperado: {str(e)}")
                break
        
        with self.lock:
            if self.connected:
                self.ser.close()
                self.connected = False

    def send(self, message):
        """
        Envía un mensaje por el puerto serial de forma thread-safe.
        
        Args:
            message (str): Mensaje a enviar (será codificado a UTF-8)
        """
        with self.lock:
            if not self.connected or not self.ser or not self.ser.is_open:
                print("No se puede enviar: desconectado.")
                return
            
            try:
                self.ser.write(message.encode('utf-8'))
                print(f"Mensaje enviado: {message}")
            except serial.SerialException as e:
                print(f"Error enviando datos: {str(e)}")
                self.connected = False
                self.ser.close()

    def start(self, *args, **kwargs):
        """
        Inicia el hilo principal que gestiona la conexión serial.
        """
        with self.lock:
            if self.running:
                return
            self.running = True
        
        self.thread = threading.Thread(
            target=self._manage_connection,
            args=args,
            kwargs=kwargs,
            daemon=True
        )
        self.thread.start()

    def _manage_connection(self, *args, **kwargs):
        """
        Gestiona el ciclo de conexión/reconexión del puerto serial.
        Método interno ejecutado en un hilo separado.
        """
        while self.running:
            if self.conect():
                listen_thread = threading.Thread(
                    target=self.listen,
                    args=args,
                    kwargs=kwargs,
                    daemon=True
                )
                listen_thread.start()
                listen_thread.join()
            
            with self.lock:
                if self.ser and self.ser.is_open:
                    self.ser.close()
                self.connected = False
            
            time.sleep(1)

    def stop(self):
        """
        Detiene todos los hilos y cierra la conexión serial de forma segura.
        """
        with self.lock:
            self.running = False
            if self.ser and self.ser.is_open:
                self.ser.close()
            self.connected = False
            self.ser = None
        print("Conexion serial cerrada.")

    @staticmethod
    def handle_event(data):
        """
        Manejador por defecto para eventos seriales (puede ser sobreescrito).
        
        Args:
            data (str): Datos recibidos del puerto serial
        """
        print(f"Mensaje recibido: {data}")

# if __name__ == "__main__":
#     puerto = "COM3"
#     baudrate = 9600
#     evento = "serial_event"

#     listener = SerialEvent(puerto, baudrate, evento, SerialEvent.handle_event)

#     try:
#         listener.start()
#         while True:
#             listener.send("Hola desde la PC")
#             time.sleep(5)
#     except KeyboardInterrupt:
#         print("\nDeteniendo...")
#     finally:
#         listener.stop()