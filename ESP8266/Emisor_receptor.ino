const int inputPin = 4;         // D2 - Pin para recibir señal externa
const int outputPin = 5;        // D1 - Pin para enviar señal
const int ledPin = LED_BUILTIN; // LED integrado (GPIO2)

// Configuración de pulsos para el modo emisor
unsigned long pulseDuration = 500;  // 500ms de pulso
unsigned long pulseInterval = 3000; // 3 segundos entre pulsos
unsigned long lastPulseTime = 0;
bool pulseActive = false;

// Para el modo receptor
unsigned long lastSignalTime = 0;
bool externalSignalActive = false;

void setup() {
  Serial.begin(9600);
  
  // Configuración de pines
  pinMode(ledPin, OUTPUT);
  pinMode(outputPin, OUTPUT);
  pinMode(inputPin, INPUT);
  
  // Estado inicial
  digitalWrite(outputPin, LOW);  // Inicia en HIGH (pulso inactivo)
  digitalWrite(ledPin, HIGH);     // LED apagado
  
  Serial.println("\nSistema iniciado - Modo Emisor/Receptor Simultaneo");
  Serial.println("Emisor: Generando pulsos cada " + String(pulseInterval) + "ms");
  Serial.println("Receptor: Monitoreando señal en pin D2");
}

void loop() {
  unsigned long currentTime = millis();
  
  // --- MODO EMISOR ---
  // Genera pulsos periódicos
  if (!pulseActive && (currentTime - lastPulseTime >= (pulseInterval + pulseDuration))) {
    // Inicia nuevo pulso
    digitalWrite(outputPin, HIGH);  // Activa el pulso (LOW para activar)
    pulseActive = true;
    lastPulseTime = currentTime;
    Serial.println("Emisor: Pulso INICIADO");
  }
  
  if (pulseActive && (currentTime - lastPulseTime >= pulseDuration)) {
    // Termina el pulso
    digitalWrite(outputPin, LOW); // Desactiva el pulso
    pulseActive = false;
    Serial.println("Emisor: Pulso TERMINADO");
  }
  
  // --- MODO RECEPTOR ---
  // Detecta señales externas
  int signalState = digitalRead(inputPin);
  
  if (signalState == HIGH && !externalSignalActive) {
    // Señal externa detectada
    externalSignalActive = true;
    lastSignalTime = currentTime;
    digitalWrite(ledPin, LOW);  // Enciende el LED (activo bajo)
    Serial.println("Receptor: Señal EXTERNA detectada - LED ON");
  }
  else if (signalState == LOW && externalSignalActive) {
    // Señal externa terminó
    externalSignalActive = false;
    digitalWrite(ledPin, HIGH); // Apaga el LED
    Serial.println("Receptor: Señal externa terminada - LED OFF");
  }
  
  // Pequeña pausa para evitar fluctuaciones
  delay(10);
}