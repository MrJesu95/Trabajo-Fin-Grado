const { contextBridge, ipcRenderer} = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
    // Función cargar JSON
    loadJSON:  (filePath) => {
        try {
            // Solicita la carga del archivo JSON al proceso principal
            const jsonData =  ipcRenderer.invoke('load-json', filePath)
            if (jsonData.error) {
                console.error('Error desde el proceso principal:', jsonData.error)
                return null;
            }
            return jsonData;
        } catch (error) {
            console.error('Error al comunicarse con el proceso principal:', error)
            return null;
        }
    },
    // Función para apagar el equipo
    shutdownComputer: () => {
        try {
            return ipcRenderer.invoke('shutdown-computer')
        } catch (error) {
            console.error('Error al solicitar apagado:', error)
            return Promise.reject(error)
        }
    }
});