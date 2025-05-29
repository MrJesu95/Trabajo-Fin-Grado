import { io } from "./socket.io.esm.min.js"
import { 
    setRunning, 
    setPaused, 
    setError, 
    setSessionState, 
    setNumberSession, 
    setNumberSerie, 
    setParam, 
    setLoading, 
    setCountDown, 
    setReady, 
    setReset, 
    getStatus, 
    setZeroSession 
} from '../../renderer/renderer.js'

// Configuración del cliente Socket.IO con autenticación
export const socket = io("http://localhost:5000", {
    extraHeaders: {
        Authorization: "Bearer Tvhc]+@Ud*cvNsQwB|.2}I14%£|k3o)+nqz1l1~Tl-tox45?pZ"
    }
})

// ==============================================
// Manejadores de eventos del socket
// ==============================================

// Conexión establecida
socket.on('connect', () => {
    console.log('Conectado al servidor WebSocket')
})

// Respuesta genérica del servidor
socket.on('my_response', (data) => {
    console.log('Mensaje recibido del backend:', data)
    // Mostrar estado de carga o listo según conexiones
    data.n_conex < 2 ? setLoading() : setReady()
})

// Manejo de estados principales
socket.on('setStatus', (data) => {
    console.log('Mensaje recibido del backend:', data)
    switch (data.status) {
        case 'reset':
            setReset()
            break
        case 'error':
            // Obtener estado actual antes del error
            socket.emit('getStatusBeforeError', { "getStatusBeforeError": getStatus()})
            setError()
            break
        case 'paused':
            setPaused()
            break
        case 'running':
            setRunning()
            break
        case 'sessionState':
            setSessionState()
            break
        default:
            console.warn('Estado no reconocido:', data.status)
    }
})

// Recepción de número de serie
socket.on('setNumSerie', (data) => {
    console.log('Mensaje recibido del backend:', data)
    setNumberSerie(data.numSerie)
})

// Recepción de parámetros
socket.on('setParam', (data) => {
    console.log('Mensaje recibido del backend:', data)
    setParam(data.typeSignal, data.amplitude, data.frequency, data.offset)
})

// Recepción de número de sesiones
socket.on('setNumSesion', (data) => {
    console.log('Mensaje recibido del backend:', data)
    setNumberSession(data.numSesion)
})

// Recepción de contador regresivo
socket.on('setCountDown', (data) => {
    console.log('Mensaje recibido del backend:', data)
    setCountDown(data.countDown)
})

// Manejo de desconexión
socket.on('disconnect', () => {
    console.log('Desconectado del servidor WebSocket')
})

// ==============================================
// Eventos de UI
// ==============================================

// Manejador de clic para el botón de acción
document.getElementById("actionButton").addEventListener("click", () => {
    // Enviar estado actual al hacer clic
    socket.emit('buttonClick', { "buttonClick": getStatus()})
})