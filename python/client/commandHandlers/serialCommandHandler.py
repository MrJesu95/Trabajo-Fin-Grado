# serial_commands.py
import time

class SerialCommandHandler:
    """Manejador de comandos seriales para procesar y ejecutar operaciones con JSON y Socket.IO."""
    
    def __init__(self, handleJSON, handleSocketIO, listener):
        """
        Inicializa el manejador de comandos seriales con sus dependencias.
        
        Args:
            handleJSON (HandleJSON): Instancia para operaciones con archivos JSON
            handleSocketIO (SocketIOCommandHandler): Instancia para comunicaciones Socket.IO
            listener (SerialEvent): Instancia de listener serial para enviar respuestas
        """
        self.handleJSON = handleJSON
        self.listener = listener  # Listener como dependencia para enviar respuestas
        self.handleSocketIO = handleSocketIO
        
    def serial_handle(self, command):
        """
        Método principal para procesar comandos seriales entrantes y dirigirlos a los manejadores adecuados.
        
        Args:
            command (str): Comando en texto plano recibido por conexion serial
        """
        parts = command.split()
        if not parts or len(parts) <= 1:
            print("Error: Comando vacio")
            return

        # Caso especial para el comando "Get SerialNumber"
        if str(command).lower() == "get serialnumber":
            return self._get_serial_number()

        # Validacion básica de estructura del comando
        if len(parts) < 3:
            print("Error: Formato de comando incorrecto")
            return

        cmd_type, cmd, *values = parts  # Descompone los valores restantes

        cmd_type = str(cmd_type).lower()
        cmd = str(cmd).lower()

        values = [str(valor).replace('_', ' ') for valor in values]

        handlers = {
            'set': {
                'serialnumber': lambda v: self._set_serial_number(v[0]),
                'numbersession': lambda v: self._set_number_session(v[0]),
                'countdown': lambda v: self._set_countdown(v[0]),
                'param': lambda v: self._set_param(*v),
            }
        }

        # Ejecucion del comando
        try:
            if cmd_type in handlers and cmd in handlers[cmd_type]:
                handlers[cmd_type][cmd](values)
            else:
                print(f"Comando no reconocido: {command}")
        except Exception as e:
            print(f"Error al ejecutar '{command}': {str(e)}")

    def _get_serial_number(self):
        """
        Maneja el comando 'Get SerialNumber' - obtiene y envia el numero de serie actual.
        
        Returns:
            str: Numero de serie actual del JSON
        """
        serial_number = self.handleJSON.getJsonValue('serialNumber')
        self.listener.send(f"{serial_number}")  # Usa el listener para enviar respuesta
        print(f"Dato enviado por serial: {serial_number}")
        return serial_number

    def _set_serial_number(self, value):
        """
        Maneja el comando 'Set SerialNumber' - actualiza el numero de serie en el sistema.
        
        Args:
            value (str): Nuevo valor para el numero de serie
        """
        try:
            self.handleSocketIO.order_SerialNumber(value)
            self.handleJSON.editJson('serialNumber', value)
            print(f"Numero de serie actualizado a: {value}")
        except Exception as e:
            print(f"Error al actualizar serial number: {e}")

    def _set_number_session(self, value):
        """
        Maneja el comando 'Set NumberSession' - actualiza el contador de sesiones.
        
        Args:
            value (str): Nuevo valor para el contador (debe ser convertible a int)
        """
        try:
            n_sesion = int(value)
            self.handleSocketIO.order_sessionState()
            self.handleJSON.editJson('nSesiones', n_sesion)
            time.sleep(2)
            self.handleSocketIO.order_reset_with_error(n_sesion)
            print(f"Numero de sesion actualizado a: {n_sesion}")
        except ValueError:
            print("Error: El valor debe ser un numero entero")

    def _set_countdown(self, value):
        """
        Maneja el comando 'Set Countdown' - actualiza la duracion de sesion.
        
        Args:
            value (str): Nueva duracion (debe ser convertible a float)
        """
        try:
            time_val = float(value)
            self.handleSocketIO.order_CountDown(value)
            self.handleJSON.editJson('timeSesion', time_val)
            print(f"Tiempo de sesion actualizado a: {value}")
        except ValueError:
            print("Error: El valor debe ser un numero")

    def _set_param(self, typeSignal, amplitude, frequency, offset):
        """
        Maneja el comando 'Set Param' - actualiza multiples parámetros de señal.
        
        Args:
            typeSignal (str): Tipo de señal
            amplitude (str): Amplitud de señal
            frequency (str): Frecuencia de señal
            offset (str): Offset de señal
        """
        try:
            typeSignal = str(typeSignal)
            amplitude = str(amplitude)
            frequency = str(frequency)
            offset = str(offset)
            value={
                "typeSignal": typeSignal,
                "amplitude": amplitude,
                "frequency": frequency,
                "offset": offset
            }
            self.handleSocketIO.order_param(value)
            self.handleJSON.editJson('typeSignal', typeSignal)
            self.handleJSON.editJson('amplitude', amplitude)
            self.handleJSON.editJson('frequency', frequency)
            self.handleJSON.editJson('offset', offset)
            print(f"Parámetros cambiados: Tipo Señal: {typeSignal}, Amplitud: {amplitude}, Frecuencia: {frequency}, Offset: {offset}")
        except ValueError:
            print("Error: Los valores deben ser texto")