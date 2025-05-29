const { app, BrowserWindow, ipcMain, ipcRenderer, globalShortcut } = require('electron')
const { spawn, exec } = require('child_process')
const path = require('path')
const fs = require('fs')
//const isDev = true;
const isDev = process.argv.includes('--dev') // Verificar si estamos en modo desarrollo

// Función para crear la ventana principal de la aplicación
const createWindow = () => {
    const options = {
        width: 1280,
        height: 720,
        icon: path.join(__dirname, '../assets/icon.png'), // Ruta del icono de la aplicación
        frame: false, // Ventana sin marco
        resizable: false, // No permitir redimensionamiento
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'), // Archivo de precarga
            devTools: isDev // Mostrar herramientas de desarrollo solo en modo dev
        }
    }

    // Configuración adicional para producción
    if (!isDev) {
        Object.assign(options, { 
            frame: false, 
            movable: false, 
            fullscreen: true 
        }) // Pantalla completa en producción
    }

    const win = new BrowserWindow(options)
    win.loadFile(path.join(__dirname, '../renderer/index.html')) // Cargar archivo HTML principal
}

// Deshabilitar atajos de teclado en producción
if (!isDev) {
    app.on('browser-window-focus', () => {
        globalShortcut.register("CommandOrControl+R", () => {
            console.log("Ctrl + R está deshabilitado")
        })
    })

    app.on('browser-window-blur', () => {
        globalShortcut.unregister("CommandOrControl+R")
    })
}

// Array para almacenar los procesos en ejecución
const pythonProcesses = []

// Scripts que se ejecutarán
const scriptNames = [
    '/server/serverSIO.py', 
    '/client/started_ClientSIO.py'
]

// Función para iniciar procesos ejecutables
const launchExecutableProcesses = (executables) => {
    if (!Array.isArray(executables) || executables.length === 0) {
        console.error("Debes proporcionar un array con nombres de ejecutables")
        return
    }

    executables.forEach((execName, index) => {
        // Determinar la ruta según si está empaquetado o no
        const execDir = app.isPackaged 
            ? path.join(process.resourcesPath, 'bin')
            : path.join(__dirname, '../../bin')
        
        const execPath = path.join(execDir, execName)
        
        // Establecer permisos de ejecución en sistemas Unix
        if (process.platform !== 'win32') {
            fs.chmodSync(execPath, 0o755)
        }

        // Iniciar el proceso
        const childProcess = spawn(execPath, [], {
            stdio: 'pipe',
            shell: false
        })

        // Registrar el proceso
        pythonProcesses.push({ name: execName, process: childProcess })

        // Manejar salida estándar
        childProcess.stdout.on('data', (data) => {
            console.log(`Proceso ${index + 1} (${execName}): ${data}`)
        })

        // Manejar errores
        childProcess.stderr.on('data', (data) => {
            console.error(`Proceso ${index + 1} (${execName}): ${data}`)
        })

        // Manejar cierre del proceso
        childProcess.on('close', (code) => {
            console.log(`El proceso ${index + 1} (${execName}) se cerró con código: ${code}`)
        })
    })

    console.log(`Lanzados ${executables.length} procesos ejecutables`)
}

// Función para iniciar procesos Python
const launchPythonProcesses = (scripts) => {
    if (!Array.isArray(scripts) || scripts.length === 0) {
        console.error("Debes proporcionar un array con nombres de scripts")
        return
    }

    scripts.forEach((scriptName, index) => {
        // Determinar ruta según entorno
        const pythonDir = app.isPackaged 
            ? path.join(process.resourcesPath, 'python')
            : path.join(__dirname, '../../python')
        
        const scriptPath = path.join(pythonDir, scriptName)
        const pythonProcess = spawn('python', [scriptPath]) // Iniciar proceso Python

        // Registrar el proceso
        pythonProcesses.push({ name: scriptName, process: pythonProcess })

        // Manejar salida estándar
        pythonProcess.stdout.on('data', (data) => {
            console.log(`Proceso ${index + 1} (${scriptName}): ${data}`)
        })

        // Manejar errores
        pythonProcess.stderr.on('data', (data) => {
            console.error(`Proceso ${index + 1} (${scriptName}): ${data}`)
        })

        // Manejar cierre del proceso
        pythonProcess.on('close', (code) => {
            console.log(`El proceso ${index + 1} (${scriptName}) se cerro con el codigo: ${code}`)
        })
    })

    console.log(`Lanzados ${scripts.length} procesos Python`)
}

// Función para cerrar todos los procesos
const closePythonProcesses = () => {
    pythonProcesses.forEach(({ name, process }, index) => {
        console.log(`Cerrando proceso ${index + 1} (${name})...`)
        process.kill() // Terminar proceso
    })

    pythonProcesses.length = 0 // Limpiar array
    console.log("Todos los procesos Python han sido cerrados")
}

// Cuando la aplicación está lista
app.whenReady().then(async () => {
    try {
        if (isDev) {
            launchPythonProcesses(scriptNames) // Usar scripts Python en desarrollo
        } else {
            launchExecutableProcesses(['server/serverSIO', 'client/started_ClientSIO']) // Usar ejecutables en producción
        }
        createWindow() // Crear ventana principal
    } catch (error) {
        console.error("Error:", error)
        return
    }
})

// Manejador para cargar archivos JSON
ipcMain.handle('load-json', (event, relativeFilePath) => {
    try {
        const jsonDir = app.isPackaged 
            ? path.join(process.resourcesPath, 'resources')
            : path.join(__dirname, '../../resources')
        
        const fullPath = path.join(jsonDir, relativeFilePath)
        console.log(fullPath)
        
        if (!fs.existsSync(fullPath)) {
            throw new Error(`El archivo no existe: ${fullPath}`)
        }
        
        const data = fs.readFileSync(fullPath, 'utf8')
        return JSON.parse(data) // Devolver contenido del JSON
    } catch (error) {
        console.error('Error al cargar el archivo JSON:', error)
        return { error: error.message } // Devolver error
    }
})

// Manejador para apagar el equipo
ipcMain.handle('shutdown-computer', () => {
    return new Promise((resolve, reject) => {
        let command
        
        // Comando según sistema operativo
        switch (process.platform) {
            case 'win32': // Windows
                command = 'shutdown /s /t 0'
                break
            case 'darwin': // macOS
                command = 'osascript -e "tell app \\"System Events\\" to shut down"'
                break
            case 'linux': // Linux
                command = 'shutdown now'
                break
            default:
                reject(new Error('Sistema operativo no soportado'))
                return
        }
        
        // Ejecutar comando
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error al apagar: ${error.message}`)
                reject(error)
                return
            }
            if (stderr) {
                console.error(`Stderr: ${stderr}`)
                reject(new Error(stderr))
                return
            }
            console.log(`Apagado iniciado: ${stdout}`)
            resolve(stdout)
        })
    })
})

// Función de prueba para apagado (comentada)
/*
function testShutdown() {
    console.log("Iniciando prueba de apagado...")
    
    new Promise((resolve, reject) => {
        let command
        
        switch (process.platform) {
            case 'win32':
                command = 'shutdown /s /t 10'
                console.log("Comando Windows:", command)
                break
            case 'darwin':
                command = 'osascript -e "tell app \\"System Events\\" to shut down"'
                console.log("Comando macOS:", command)
                break
            case 'linux':
                command = 'echo "Prueba: shutdown now"'
                console.log("Comando Linux:", command)
                break
            default:
                console.error("Sistema operativo no soportado")
                return
        }
        
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error en prueba: ${error.message}`)
                return
            }
            if (stderr) {
                console.error(`Stderr: ${stderr}`)
                return
            }
            console.log(`Prueba exitosa. Salida: ${stdout}`)
        })
    })
}
*/

// Evento cuando se cierran todas las ventanas
app.on('window-all-closed', () => {
    closePythonProcesses() // Cerrar procesos
    if (process.platform !== 'windows') {
        app.quit() // Salir de la aplicación
    }
})