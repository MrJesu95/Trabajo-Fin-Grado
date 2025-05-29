import json

class HandleJSON:
    """Clase para manejar operaciones de lectura y escritura en archivos JSON."""
    
    def __init__(self, json_path):
        """
        Inicializa el manejador JSON con la ruta al archivo.
        
        Args:
            json_path (str): Ruta completa al archivo JSON que se va a manejar
        """
        self.json_path = json_path

    def editJson(self, key, value):
        """
        Modifica un valor específico en el archivo JSON.
        
        Args:
            key (str): Clave del valor a modificar
            value (any): Nuevo valor a asignar (debe ser serializable en JSON)
        """
        with open(self.json_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        datos[key] = value
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)

    def getJson(self):
        """
        Obtiene todos los datos del archivo JSON.
        
        Returns:
            dict: Diccionario con todos los datos del archivo JSON
        """
        with open(self.json_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return datos
    
    def getJsonValue(self, key):
        """
        Obtiene un valor específico del archivo JSON.
        
        Args:
            key (str): Clave del valor a recuperar
            
        Returns:
            any: Valor asociado a la clave solicitada
        """
        with open(self.json_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return datos[key]
    
    def editJsonDec(self, key):
        """
        Decrementa en 1 un valor numérico en el archivo JSON (si es mayor que 0).
        
        Args:
            key (str): Clave del valor numérico a decrementar
            
        Returns:
            int: Nuevo valor después del decremento, o 0 si ya era 0 o menor
        """
        with open(self.json_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        if datos[key] > 0: 
            datos[key] = datos[key]-1
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4)
            return datos[key]
        return 0