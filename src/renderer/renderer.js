// Importación del socket desde el archivo clientSocketIO
import { socket } from '../main/utils/clientSocketIO.js'

// Obtención de elementos del DOM
const countdownElement = document.getElementById("countdown")
const sesionElement = document.getElementById("nSession")
const nserieElement = document.getElementById("nserie")
const paramElement = document.getElementById("param")
const statusElement = document.getElementById("status")
const actionButton = document.getElementById('actionButton')
const shutdownButton = document.getElementById('shutdown-btn')
let dJSON
let countdownValueMax
let countdownValue
let countdownInterval

// Evento que se ejecuta cuando el DOM está completamente cargado
document.addEventListener("DOMContentLoaded", async () => {
    dJSON = await window.electronAPI.loadJSON('data.json')
    init()
})

// Configuración del modal de apagado
document.getElementById("shutdown-btn").addEventListener("click", () => {
    document.getElementById("shutdown-modal").classList.remove("hidden")
})

document.getElementById("shutdown-confirm").addEventListener("click", () => {
    document.getElementById("shutdown-modal").classList.add("hidden")
    window.electronAPI.shutdownComputer()
})

document.getElementById("shutdown-cancel").addEventListener("click", () => {
    document.getElementById("shutdown-modal").classList.add("hidden")
})

// Función de inicialización
function init() {
    countdownValueMax = dJSON.timeSesion * 60
    countdownValue = countdownValueMax
    setNumberSession(dJSON.nSesiones)
    setNumberSerie(dJSON.serialNumber)
    setParam(dJSON.typeSignal, dJSON.amplitude, dJSON.frequency, dJSON.offset)
    if (dJSON.nSesiones > 0) {
        setReset()
    } else {
        setZeroSession()
    }
}

// Función para obtener el estado actual
export function getStatus() {
    return statusElement.className
}

// Función para establecer estado "listo" (oculta pantalla de carga)
export function setReady() {
    const loadingScreen = document.getElementById("loading-screen")

    // Ocultar la pantalla de carga
    loadingScreen.classList.add("hidden")
    loadingScreen.classList.remove("visible")
}

// Función para establecer estado "cargando" (muestra pantalla de carga)
export function setLoading() {
    const loadingScreen = document.getElementById("loading-screen")

    // Mostrar la pantalla de carga
    loadingScreen.classList.add("visible")
    loadingScreen.classList.remove("hidden")
}

// Función para establecer estado "en ejecución"
export function setRunning() {
    if (sesionElement.textContent > 0 || countdownValue > 0){
        updateCountdownDisplay(countdownValue)
        startCountdownDisplay()
        statusElement.className = 'container running'
        swapButton()
    }
    else{
        setZeroSession()
    }
}

// Función para establecer estado "pausado"
export function setPaused() {
    if (sesionElement.textContent > 0 || countdownValue > 0){
        updateCountdownDisplay(countdownValue)
        clearInterval(countdownInterval)
        countdownInterval = null
        statusElement.className = 'container paused'
        swapButton()
    }
    else{
        setZeroSession()
    }
}

// Función para establecer estado "error"
export function setError() {
    if (sesionElement.textContent > 0 || countdownValue > 0){
        updateCountdownDisplay(countdownValue)
        clearInterval(countdownInterval)
        countdownInterval = null
        statusElement.className = 'container error'
        swapButton()
        countdownElement.textContent = `Error de conexión`
        // countdownElement.innerHTML = `${countdownElement.innerHTML}<br>Error de conexión`
    }
    else{
        setZeroSession()
    }
}

// Función para establecer estado "reset"
export function setReset() {
    if (sesionElement.textContent > 0){
        countdownValue = countdownValueMax
        updateCountdownDisplay(countdownValue)
        clearInterval(countdownInterval)
        countdownInterval = null
        statusElement.className = 'container init'
        swapButton()
    }
    else{
        setZeroSession()
    }
}

// Función para establecer estado "cargando sesiones"
export function setSessionState() {
    clearInterval(countdownInterval)
    countdownInterval = null
    statusElement.className = 'container sessionState'
    countdownElement.textContent = 'CARGANDO SESIONES'
    swapButton()
}

// Función para establecer estado "sin sesiones"
export function setZeroSession() {
    updateCountdownDisplay(countdownValue)
    clearInterval(countdownInterval)
    countdownInterval = null
    statusElement.className = 'container error'
    countdownElement.textContent = 'SIN SESIONES'
    swapButton()
    setNumberSession(0)
}

// Función para actualizar el número de sesiones mostrado
export function setNumberSession(data) {
    sesionElement.textContent = data
}

// Función para actualizar el número de serie mostrado
export function setNumberSerie(data) {
    nserieElement.textContent = data
}

// Función para actualizar los parámetros mostrados
export function setParam(typeSignal, amplitude, frequency, offset) {
    paramElement.innerHTML = `Señal: ${typeSignal}<br>Amplitud: ${amplitude}<br>Frecuencia: ${frequency}<br>Offset: ${offset}`
}

// Función para establecer el valor del contador
export function setCountDown(data) {
    countdownValueMax = data * 60
    countdownValue = countdownValueMax
    updateCountdownDisplay(countdownValue)
}

// document.getElementById("actionButton").addEventListener("click", () => {
//     setRunning()
// })

// Función para iniciar y controlar la cuenta regresiva visual
function startCountdownDisplay() {
    // Si no hay un intervalo activo, iniciamos uno
    if (!countdownInterval) {
        countdownInterval = setInterval(() => {
            if (countdownValue > 0) {
                countdownValue--
                updateCountdownDisplay(countdownValue)
            } else {
                clearInterval(countdownInterval)
                countdownInterval = null
                if (sesionElement.textContent == 0) { setZeroSession() }
                else {
                    setReset()
                    socket.emit('countdownFinished', { "countdownFinished": 0})
                    countdownValue = countdownValueMax
                    updateCountdownDisplay(countdownValue)
                }
            }
        }, 1000)
    }
}

// Función para actualizar la visualización del contador
function updateCountdownDisplay(countdownValue) {
    const minutes = Math.floor(countdownValue / 60)
    const seconds = countdownValue % 60

    countdownElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds
        .toString()
        .padStart(2, '0')}`
}


// document.getElementById("stop").addEventListener("click", () => {
//     clearInterval(countdownInterval)
//     countdownInterval = null
//     setPaused()
// })

// Función para cambiar el botón de acción según el estado
function swapButton() {
    // Reset de clases
    actionButton.classList.remove('init', 'continue', 'pause', 'hidden')
    shutdownButton.classList.remove('shutdown-btn', 'hidden')

    if (statusElement.classList.contains('init')) {
        actionButton.textContent = "Empezar"
        actionButton.classList.add('init')
        shutdownButton.classList.add('shutdown-btn')
    }
    else if (statusElement.classList.contains('paused')) {
        actionButton.textContent = "Continuar"
        actionButton.classList.add('continue')
        shutdownButton.classList.add('shutdown-btn')
    }
    else if (statusElement.classList.contains('running')) {
        actionButton.textContent = "Pausar"
        actionButton.classList.add('pause')
        shutdownButton.classList.add('shutdown-btn')
    }
    else if (statusElement.classList.contains('sessionState')) {
        actionButton.textContent = "Ocultar"
        actionButton.classList.add('hidden')
        shutdownButton.classList.add('hidden')
    }
    else if (statusElement.classList.contains('error')){
        actionButton.textContent = "Ocultar"
        actionButton.classList.add('hidden')
        shutdownButton.classList.add('shutdown-btn')
    }
}

// Asignar evento
//actionButton.addEventListener('click', swapButton)