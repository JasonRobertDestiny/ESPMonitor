/*
 * ESPMonitor - Environment Monitoring System
 * ESP8266 Firmware
 *
 * Reads temperature, humidity, and water level sensors
 * Sends data to Flask server via HTTP
 * Receives threshold updates and controls alerts
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ==================== Configuration ====================
// Copy config.example.h to config.h and edit your settings
#include "config.h"

// Pin Definitions for ESP8266
#define DHT_PIN D4          // DHT sensor data pin (GPIO2)
#define WATER_LEVEL_PIN A0  // Analog pin for water level sensor (only A0 available)
#define ALERT_LED_PIN D0    // Built-in LED (GPIO16) or external LED

// DHT Sensor Type (DHT11 or DHT22)
#define DHT_TYPE DHT11

// Timing
#define SEND_INTERVAL 5000        // Send data every 5 seconds
#define THRESHOLD_CHECK_INTERVAL 10000  // Check thresholds every 10 seconds

// ==================== Global Objects ====================
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient client;
HTTPClient http;

// ==================== Global Variables ====================
unsigned long lastSendTime = 0;
unsigned long lastThresholdCheck = 0;

// Current sensor readings
float temperature = 0.0;
float humidity = 0.0;
float waterLevel = 0.0;

// Thresholds (defaults)
float tempThreshold = 30.0;
float humidityThreshold = 70.0;
float waterThreshold = 80.0;

bool alertActive = false;

// ==================== WiFi Functions ====================
void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

// ==================== Sensor Functions ====================
void readSensors() {
  // Read DHT sensor
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  // Check if reading failed
  if (isnan(t) || isnan(h)) {
    Serial.println("DHT read failed");
    return;
  }

  temperature = t;
  humidity = h;

  // Read water level (0-100%)
  // ESP8266 ADC is 10-bit (0-1023)
  int rawValue = analogRead(WATER_LEVEL_PIN);
  waterLevel = map(rawValue, 0, 1023, 0, 100);

  Serial.printf("Temp: %.1f°C, Humidity: %.1f%%, Water: %.1f%%\n",
                temperature, humidity, waterLevel);
}

// ==================== HTTP Communication ====================
bool sendDataToServer() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected");
    return false;
  }

  // Create JSON payload
  StaticJsonDocument<256> doc;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["water_level"] = waterLevel;
  doc["device_id"] = DEVICE_ID;

  String payload;
  serializeJson(doc, payload);

  // Send POST request
  String url = String(SERVER_URL) + "/api/sensor-data";
  http.begin(client, url);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(payload);

  if (httpCode > 0) {
    Serial.printf("Data sent, response: %d\n", httpCode);

    if (httpCode == HTTP_CODE_OK) {
      String response = http.getString();
      Serial.println("Response: " + response);
      http.end();
      return true;
    }
  } else {
    Serial.printf("POST failed: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
  return false;
}

bool fetchThresholds() {
  if (WiFi.status() != WL_CONNECTED) {
    return false;
  }

  String url = String(SERVER_URL) + "/api/thresholds";
  http.begin(client, url);

  int httpCode = http.GET();

  if (httpCode == HTTP_CODE_OK) {
    String response = http.getString();

    // Parse JSON response
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, response);

    if (!error) {
      tempThreshold = doc["temperature"] | tempThreshold;
      humidityThreshold = doc["humidity"] | humidityThreshold;
      waterThreshold = doc["water_level"] | waterThreshold;

      Serial.printf("Thresholds updated: Temp=%.1f, Hum=%.1f, Water=%.1f\n",
                    tempThreshold, humidityThreshold, waterThreshold);
      http.end();
      return true;
    } else {
      Serial.println("JSON parse failed");
    }
  } else {
    Serial.printf("GET thresholds failed: %d\n", httpCode);
  }

  http.end();
  return false;
}

// ==================== Alert Functions ====================
void checkThresholdsAndAlert() {
  bool shouldAlert = false;

  if (temperature > tempThreshold) {
    Serial.printf("ALERT: Temperature %.1f > %.1f\n", temperature, tempThreshold);
    shouldAlert = true;
  }

  if (humidity > humidityThreshold) {
    Serial.printf("ALERT: Humidity %.1f > %.1f\n", humidity, humidityThreshold);
    shouldAlert = true;
  }

  if (waterLevel > waterThreshold) {
    Serial.printf("ALERT: Water level %.1f > %.1f\n", waterLevel, waterThreshold);
    shouldAlert = true;
  }

  // Control LED
  if (shouldAlert != alertActive) {
    alertActive = shouldAlert;
    digitalWrite(ALERT_LED_PIN, alertActive ? HIGH : LOW);
  }
}

// ==================== Setup & Loop ====================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=== ESPMonitor (ESP8266) Starting ===");

  // Initialize pins
  pinMode(ALERT_LED_PIN, OUTPUT);
  digitalWrite(ALERT_LED_PIN, LOW);

  // Initialize DHT sensor
  dht.begin();

  // Connect to WiFi
  connectWiFi();

  // Initial threshold fetch
  if (WiFi.status() == WL_CONNECTED) {
    fetchThresholds();
  }

  Serial.println("Setup complete\n");
}

void loop() {
  unsigned long currentTime = millis();

  // Reconnect WiFi if disconnected
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, reconnecting...");
    connectWiFi();
  }

  // Read sensors and send data
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    readSensors();
    sendDataToServer();
    checkThresholdsAndAlert();
    lastSendTime = currentTime;
  }

  // Fetch threshold updates
  if (currentTime - lastThresholdCheck >= THRESHOLD_CHECK_INTERVAL) {
    fetchThresholds();
    lastThresholdCheck = currentTime;
  }

  delay(100);  // Small delay to prevent tight loop
}
