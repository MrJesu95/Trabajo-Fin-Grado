import time

class SocketIOCommandHandler():
    """Manejador de comandos para comunicaciones Socket.IO con el frontend."""
    
    control_repeat = False  # Control para evitar repetición de comandos
    getStatusBeforeError = 'container init'  # Almacena el estado previo a un error
    inError = False  # Indica si el sistema está en estado de error
    
    def __init__(self, handleJSON, gpio, clientSocketIO):
        """
        Inicializa el manejador de comandos.
        
        Args:
            handleJSON (HandleJSON): Instancia para manejar el archivo JSON de configuración
            gpio (GPIO_Event): Instancia para controlar los pines GPIO
            clientSocketIO (ClientSocketIO): Cliente para comunicación Socket.IO
        """
        self.handleJSON = handleJSON
        self.gpio = gpio
        self.clientSocketIO = clientSocketIO

    def order_start(self):   
        """Envía comando para iniciar sesión y actualiza el contador."""
        self.handleJSON.editJsonDec('nSesiones')
        nSesiones = self.handleJSON.getJsonValue('nSesiones')
        self.clientSocketIO.send_data('setStatus', 'status', "running")
        self.clientSocketIO.send_data('setNumSesion', 'numSesion', nSesiones)
        print("Se manda: running")

    def order_pause(self):
        """Envía comando para pausar la sesión."""
        self.clientSocketIO.send_data('setStatus', 'status', "paused")
        print("Se manda: paused")

    def order_play(self):
        """Envía comando para reanudar sesión pausada."""
        self.clientSocketIO.send_data('setStatus', 'status', "running")
        print("Se manda: running")

    def order_error(self):
        """Envía comando para indicar estado de error."""
        self.clientSocketIO.send_data('setStatus', 'status', "error")
        print("Se manda: error")
    
    def order_sessionState(self):
        """Envía comando para estado de carga de sesiones."""
        self.clientSocketIO.send_data('setStatus', 'status', "sessionState")
        print("Se manda: sessionState")

    def order_SerialNumber(self, nSerie):
        """Envía comando para actualizar número de serie.
        
        Args:
            nSerie (str): Nuevo número de serie
        """
        self.clientSocketIO.send_data('setNumSerie', 'numSerie', nSerie)
        print("Se manda: setNumSerie")
    
    def order_CountDown(self, timeSesion):
        """Envía comando para actualizar tiempo de sesión.
        
        Args:
            timeSesion (str): Nuevo tiempo de sesión
        """
        self.clientSocketIO.send_data('setCountDown', 'countDown', timeSesion)
        print("Se manda: setCountDown")

    def order_reset(self, nSesiones=None):
        """Envía comando para resetear el sistema.
        
        Args:
            nSesiones (int, optional): Número de sesiones a enviar
        """
        if nSesiones != None:
            self.clientSocketIO.send_data('setNumSesion', 'numSesion', nSesiones)
        self.clientSocketIO.send_data('setStatus', 'status', "reset")
        self.control_repeat = False

    def order_reset_with_error(self, nSesiones=None):
        """Envía comando reset, considerando estado de error.
        
        Args:
            nSesiones (int, optional): Número de sesiones a enviar
        """
        if self.inError == True:
            self.order_error()
        else:
            if nSesiones != None:
                self.clientSocketIO.send_data('setNumSesion', 'numSesion', nSesiones)
            self.clientSocketIO.send_data('setStatus', 'status', "reset")
            self.control_repeat = False
    
    def order_param(self, param):
        """Envía comando para actualizar parámetros de sesión.
        
        Args:
            param (dict): Diccionario con parámetros a actualizar
        """
        self.clientSocketIO.send_data_full('setParam', param)
        print("Se manda: setParam")

    def click_handle(self, last_data):
        """Maneja eventos de clic desde el frontend.
        
        Args:
            last_data (dict): Datos recibidos del frontend
        """
        try:
            if self.control_repeat == False:
                self.control_repeat = True
                self.gpio.send_pulse(pulses=1)
                if last_data['buttonClick'] == 'container init':
                    self.order_start()
                elif last_data['buttonClick'] == 'container running':
                    self.order_pause()
                elif last_data['buttonClick'] == 'container paused':
                    self.order_play()
                time.sleep(0.2)
                self.control_repeat = False
        except Exception as e:
            print(f"Fallo en click_handle: {e}") 
    
    def error_handle(self, last_data):
        """Maneja eventos de error desde el frontend.
        
        Args:
            last_data (dict): Datos recibidos del frontend
        """
        if self.control_repeat == False:
            self.control_repeat = True

            self.inError = True
            if last_data['getStatusBeforeError'] != 'container error':
                self.getStatusBeforeError = last_data['getStatusBeforeError']

            time.sleep(0.2)
            self.control_repeat = False
    
    def after_error_handle(self):
        """Maneja recuperación después de un error."""
        nSesiones = self.handleJSON.getJsonValue('nSesiones')
        try:
            if self.control_repeat == False:
                self.control_repeat = True
                self.inError = False
                if self.getStatusBeforeError == 'container init' or self.getStatusBeforeError == 'container sessionState':
                    self.order_reset(nSesiones)
                elif self.getStatusBeforeError == 'container running':
                    self.order_play()
                    self.gpio.send_pulse(pulses=1)
                elif self.getStatusBeforeError == 'container paused':
                    self.order_pause()
                    self.gpio.send_pulse(pulses=1)
                time.sleep(0.2)
                self.control_repeat = False
        except Exception as e:
            print(f"Fallo en click_handle: {e}")

    def final_pulse(self, _):
        """Maneja el pulso final de sesion"""
        self.gpio.send_pulse(pulses=1)