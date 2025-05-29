from gpiozero import DigitalInputDevice, DigitalOutputDevice
from gpiozero import Device
from gpiozero.pins.rpigpio import RPiGPIOFactory
import time

class GPIO_Event():
    def __init__(self, INPUT_PIN=17, OUTPUT_PIN=27, SAMPLE_RATE=0.01, ACTIVATION_THRESHOLD=2, TIME_WINDOW=0.5, ACTIVE=True):
        """
        Inicializa el controlador de eventos GPIO con parámetros configurables.
        
        Args:
            INPUT_PIN (int): Pin GPIO para entrada (por defecto 17)
            OUTPUT_PIN (int): Pin GPIO para salida (por defecto 27)
            SAMPLE_RATE (float): Intervalo de muestreo en segundos (por defecto 0.01)
            ACTIVATION_THRESHOLD (int): Umbral de pulsos para activación (por defecto 2)
            TIME_WINDOW (float): Ventana temporal para contar pulsos en segundos (por defecto 0.5)
            ACTIVE (bool): Habilitar/deshabilitar funcionalidad (por defecto True)
        """
        self.INPUT_PIN = INPUT_PIN
        self.OUTPUT_PIN = OUTPUT_PIN
        self.SAMPLE_RATE = SAMPLE_RATE  # Muestreo (10 ms)
        self.ACTIVATION_THRESHOLD = ACTIVATION_THRESHOLD  # Número de pulsos requeridos
        self.TIME_WINDOW = TIME_WINDOW  # Ventana de tiempo en segundos
        self.ACTIVE = ACTIVE
        

    def send_pulse(self, duration=0.3, pulses=1, interval=0.3):
        """
        Envía uno o varios pulsos por el pin de salida configurado.
        
        Args:
            duration (float): Duración de cada pulso en segundos (por defecto 0.3)
            pulses (int): Número de pulsos a enviar (por defecto 1)
            interval (float): Tiempo entre pulsos en segundos (por defecto 0.3)
        """
        if self.ACTIVE == False:
            return
        if self.OUTPUT_PIN is not None:
            try:
                output_device = DigitalOutputDevice(self.OUTPUT_PIN)
                for i in range(pulses):
                    output_device.on()
                    time.sleep(duration)
                    output_device.off()
                    print(f"Pulso {i+1}/{pulses} enviado por el pin {self.OUTPUT_PIN} durante {duration} segundos")
                    
                    # No esperar después del último pulso
                    if i < pulses - 1:
                        time.sleep(interval)
            finally:
                output_device.close()
        else:
            print("Error: No se ha configurado un pin de salida (OUTPUT_PIN)")

    def start_INPUT_GPIO(self, callback=None, *args, **kwargs):
        """
        Monitorea pulsos de entrada y ejecuta callback al alcanzar umbral.
        
        Args:
            callback (function): Función a ejecutar al activarse
            *args: Argumentos posicionales para el callback
            **kwargs: Argumentos clave para el callback
        """
        if self.ACTIVE == False:
            return

        sensor = DigitalInputDevice(self.INPUT_PIN, pull_up=True)
        last_state = sensor.value
        pulse_times = []  # Almacenará tiempos en segundos
        
        try:
            while True:
                current_state = sensor.value
                
                # Detectar flanco de subida (LOW → HIGH)
                if current_state and not last_state:
                    current_time = time.time()
                    print(f"¡Pulso detectado! (Tiempo: {current_time} s)")
                    pulse_times.append(current_time)
                    
                    # Filtrar pulsos fuera de la ventana
                    pulse_times = [t for t in pulse_times if (current_time - t) <= self.TIME_WINDOW]
                    
                    # Verificar si hay suficientes pulsos
                    if len(pulse_times) >= self.ACTIVATION_THRESHOLD:
                        print(f"¡Orden activada! ({len(pulse_times)} pulsos en {self.TIME_WINDOW} s)") 
                        
                        if callback:
                            callback(*args, **kwargs)

                        pulse_times = []  # Reiniciar contador
                
                last_state = current_state
                time.sleep(self.SAMPLE_RATE)
                
        except KeyboardInterrupt:
            print("\nPrograma terminado")
        finally:
            sensor.close()

    def monitor_pulse_timeout(
        self,
        timeout=5.0,                   # Tiempo máximo permitido en estado LOW
        timeout_callback=None,         # Se ejecuta si LOW dura más del timeout
        pulse_after_timeout_callback=None  # Se ejecuta cuando vuelve a HIGH después del timeout
    ):
        """
        Monitoriza la entrada GPIO y ejecuta callbacks según:
        - Si el estado LOW dura más de 'timeout' segundos
        - Cuando vuelve a HIGH después de un timeout
        
        Args:
            timeout (float): Máxima duración permitida en estado LOW (segundos)
            timeout_callback (callable): Ejecutar cuando LOW supera el timeout
            pulse_after_timeout_callback (callable): Ejecutar al volver a HIGH después de timeout
        """
        if self.ACTIVE == False:
            print("Desactivado GPIO")
            return

        if self.INPUT_PIN is None:
            print("Error: No se ha configurado INPUT_PIN")
            return

        sensor = DigitalInputDevice(self.INPUT_PIN, pull_up=True)
        low_state_start = None
        timeout_triggered = False
        last_state = 1  # Asumimos estado inicial HIGH (pull-up)

        try:
            while True:
                current_state = sensor.value
                current_time = time.time()
                
                # Detección de flanco de bajada (HIGH -> LOW)
                if current_state == 0 and last_state == 1:
                    low_state_start = current_time
                    timeout_triggered = False
                    print(f"Estado LOW detectado (Tiempo: {current_time})")
                
                # Detección de flanco de subida (LOW -> HIGH)
                elif current_state == 1 and last_state == 0:
                    low_duration = current_time - low_state_start if low_state_start else 0
                    print(f"Estado HIGH recuperado. LOW duró: {low_duration:.3f}s")
                    
                    # Si habíamos tenido timeout y ahora recuperamos HIGH
                    if timeout_triggered and pulse_after_timeout_callback:
                        pulse_after_timeout_callback()
                        timeout_triggered = False
                
                # Verificar timeout en estado LOW
                if current_state == 0 and low_state_start and not timeout_triggered:
                    low_duration = current_time - low_state_start
                    if low_duration >= timeout:
                        print(f"Timeout LOW: Estado bajo por {low_duration:.3f}s")
                        if timeout_callback:
                            timeout_callback()
                        timeout_triggered = True
                
                last_state = current_state
                time.sleep(self.SAMPLE_RATE)

        except KeyboardInterrupt:
            print("\nMonitorización terminada")
        finally:
            sensor.close()
    
    def visual_state():
        """
        Muestra cambios de estado en tiempo real para diagnóstico.
        Monitorea el pin GPIO 17 y muestra transiciones HIGH/LOW con duraciones.
        """
        sensor = DigitalInputDevice(17, pull_up=True)
        last_state = sensor.value
        last_change_time = time.monotonic()  # Más preciso para mediciones de tiempo
        
        print(f"Estado inicial: {'HIGH' if last_state else 'LOW'}")
        
        while True:
            current_state = sensor.value
            if current_state != last_state:
                current_time = time.monotonic()
                duration = current_time - last_change_time
                
                print(f"[{time.strftime('%H:%M:%S')}] Cambio: {'HIGH' if last_state else 'LOW'}→"
                    f"{'HIGH' if current_state else 'LOW'} | "
                    f"Duración: {duration:.3f}s")
                
                last_state = current_state
                last_change_time = current_time
            
            time.sleep(0.01)
#GPIO_Event.visual_state()