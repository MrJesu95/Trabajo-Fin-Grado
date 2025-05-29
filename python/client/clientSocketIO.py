# clientSocketIO.py

import time
import socketio


class ClientSocketIO:
    def __init__(self, sio=socketio.Client(), token=None):
        """
        Inicializa el cliente Socket.IO con configuración básica.
        
        Args:
            sio (socketio.Client): Instancia del cliente Socket.IO (por defecto nueva instancia)
            token (str): Token de autenticación para conexión (opcional)
        """
        self.sio = sio
        self.token = token

    def conectar(self):
        """
        Establece conexión con el servidor Socket.IO con reintentos automáticos.
        Intenta conectarse indefinidamente hasta lograr conexión exitosa.
        """
        intentos = 0
        while True:
            try:
                print(f"Intentando conectar al servidor... (Intento {intentos + 1})")
                self.sio.connect('http://localhost:5000', headers={
                    'Authorization': f'Bearer {self.token}'
                })
                print("Conexion exitosa: SocketIO")
                break
            except Exception as e:
                print(f"Error al conectar: {e}")
                intentos += 1
                time.sleep(1)

    def receive_data(self, evento, func=None, *args, **kwargs):
        """
        Configura un manejador para eventos recibidos del servidor.
        
        Args:
            evento (str): Nombre del evento a escuchar
            func (callable): Función callback para procesar los datos (opcional)
            *args: Argumentos posicionales adicionales para el callback
            **kwargs: Argumentos clave adicionales para el callback
        """
        @self.sio.on(evento)
        def on_message(data):
            print(f'\nI received a message! Datos: {data}')
            if func is not None:
                func(data, *args, **kwargs)
    
    def send_data(self, fun, event, data):
        """
        Envía datos al servidor empaquetados en un diccionario.
        
        Args:
            fun (str): Nombre del evento a emitir
            event (str): Clave para los datos en el payload
            data: Valor a enviar (será convertido a string)
        """
        self.sio.emit(fun, {event: f'{data}'})
    
    def send_data_full(self, fun, data):
        """
        Envía datos completos al servidor sin formato específico.
        
        Args:
            fun (str): Nombre del evento a emitir
            data: Datos a enviar (cualquier formato serializable)
        """
        self.sio.emit(fun, data)
    
    def desconectar(self):
        """Cierra la conexión con el servidor Socket.IO."""
        self.sio.disconnect()