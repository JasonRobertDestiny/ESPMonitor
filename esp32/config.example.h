/*
 * ESPMonitor Configuration Template
 *
 * Instructions:
 * 1. Copy this file to config.h
 * 2. Edit the values below with your settings
 * 3. DO NOT commit config.h to version control (add to .gitignore)
 */

#ifndef CONFIG_H
#define CONFIG_H

// ==================== WiFi Configuration ====================
#define WIFI_SSID "your_wifi_ssid"       // Your WiFi network name
#define WIFI_PASSWORD "your_wifi_password"   // Your WiFi password

// ==================== Server Configuration ====================
#define SERVER_URL "http://192.168.1.100:5000"  // Flask server URL (change IP to your server)

// ==================== Device Configuration ====================
#define DEVICE_ID "ESP32_01"  // Unique identifier for this device

#endif
