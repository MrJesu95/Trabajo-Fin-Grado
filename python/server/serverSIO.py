# ServerSIO.py
from threading import Lock
from flask import Flask, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
from engineio.async_drivers import gevent

class ServerSIO:
    """Servidor principal para manejar conexiones Socket.IO con autenticación y eventos en tiempo real."""

    # Configuración del modo asíncrono (puede ser 'threading', 'eventlet' o 'gevent')
    async_mode = 'gevent'
    
    # Aplicación Flask básica
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "Tvhc]+@Ud*cvNsQwB|.2}I14%£|k3o)+nqz1l1~Tl-tox45?pZ"
    
    # Configuración del servidor Socket.IO
    socketio = SocketIO(app, 
                       async_mode=async_mode, 
                       cors_allowed_origins='*',  # Permite CORS para todos los orígenes (# file://)
                       logger=False,              # Desactiva logging estándar
                       engineio_logger=True)      # Activa logging de Engine.IO
    
    thread = None        # Hilo para operaciones en segundo plano
    thread_lock = Lock() # Lock para sincronización de hilos
    n_conex = 0          # Contador de conexiones activas

    def background_thread():
        """Ejemplo de hilo en segundo plano para enviar eventos periódicos a los clientes."""
        count = 0
        while True:
            ServerSIO.socketio.sleep(10)
            count += 1
            ServerSIO.socketio.emit('respuesta',
                        {'data': 'Server generated event', 'count': count})

    # ==============================================
    # Manejadores de eventos principales
    # ==============================================

    @socketio.event
    def setStatus(message):
        """Actualiza y difunde el estado del sistema a todos los clientes excepto al emisor."""
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('setStatus', message, broadcast=True, include_self=False)
    
    @socketio.event
    def setNumSesion(message):
        """Actualiza y difunde el número de sesiones disponibles."""
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('setNumSesion', message, broadcast=True, include_self=False)
    
    @socketio.event
    def setNumSerie(message):
        """Actualiza y difunde el número de serie del dispositivo."""
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('setNumSerie', message, broadcast=True, include_self=False)
    
    @socketio.event
    def setParam(message):
        """Actualiza y difunde los parámetros de configuración."""
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('setParam', message, broadcast=True, include_self=False)
        
    @socketio.event
    def setCountDown(message):
        """Actualiza y difunde el estado del contador regresivo."""
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('setCountDown', message, broadcast=True, include_self=False)
        
    @socketio.event
    def buttonClick(message):
        """Procesa y difunde eventos de clic de botón desde los clientes."""
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('buttonClick', message, broadcast=True, include_self=False)

    @socketio.event
    def getStatusBeforeError(message):
        """Maneja solicitudes para obtener el estado previo a un error."""
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('getStatusBeforeError', message, broadcast=True, include_self=False)

    @socketio.event
    def countdownFinished(message):
        """Notifica cuando el contador regresivo ha finalizado."""
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('countdownFinished', message, broadcast=True, include_self=False)

    # @socketio.on('*')
    # def catch_all(event, data):
    #     session['receive_count'] = session.get('receive_count', 0) + 1
    #     emit('my_response',
    #          {'data': [event, data], 'count': session['receive_count']})

    # ==============================================
    # Manejadores de conexión/desconexión
    # ==============================================

    @socketio.event
    def disconnect_request():
        """Maneja solicitudes de desconexión segura con confirmación."""
        @copy_current_request_context
        def can_disconnect():
            """Función de callback para confirmar desconexión segura."""
            disconnect()

        session['receive_count'] = session.get('receive_count', 0) + 1
        ServerSIO.n_conex -= 1
        emit('my_response',
            {'data': 'Disconnected!', 
             'count': session['receive_count'], 
             'n_conex': ServerSIO.n_conex},
            callback=can_disconnect)

    @socketio.event
    def my_ping():
        """Responde a mensajes ping para mantener la conexión activa."""
        emit('my_pong')

    @socketio.event
    def connect():
        """Maneja nuevas conexiones con autenticación por token Bearer."""
        token = request.headers.get('Authorization')

        # Validación del token de autorización
        if not token or not token.startswith("Bearer ") or token.split(" ")[1] != ServerSIO.app.config['SECRET_KEY']:
            print("Conexión rechazada: token inválido o ausente")
            return False  # Rechaza la conexión
        # global thread
        # with ServerSIO.thread_lock:
        #     if thread is None:
        #         thread = ServerSIO.socketio.start_background_task(ServerSIO.queue_sender)
        ServerSIO.n_conex += 1
        emit('my_response', {'data': 'Connected', 'n_conex': ServerSIO.n_conex}, broadcast=True)
        # origin = request.headers.get('Origin')
        # print (f'///////////////////////////////////////////////////////////////////  {origin}')

    @socketio.on('disconnect')
    def test_disconnect(reason):
        """Maneja eventos de desconexión de clientes."""
        ServerSIO.n_conex -= 1
        emit('my_response', {'data': 'Connected', 'n_conex': ServerSIO.n_conex}, broadcast=True)
        print('Client disconnected', request.sid, reason)

if __name__ == '__main__':
    """Punto de entrada principal para ejecutar el servidor en localhost:5000."""
    ServerSIO.socketio.run(ServerSIO.app, host='127.0.0.1', port=5000)