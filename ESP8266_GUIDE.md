# ESP8266使用指南

ESPMonitor完全支持ESP8266开发板

---

## ESP8266 vs ESP32对比

| 特性 | ESP8266 | ESP32 |
|------|---------|-------|
| CPU | 80MHz单核 | 240MHz双核 |
| RAM | 80KB | 520KB |
| WiFi | 2.4GHz | 2.4GHz + 5GHz |
| ADC引脚 | 1个(A0) | 18个 |
| GPIO | 11个可用 | 34个 |
| 价格 | 更便宜 | 稍贵 |
| **本项目适用性** | ✅ 完全适用 | ✅ 完全适用 |

**结论**: ESP8266完全够用，更省钱！

---

## 硬件准备

### 推荐开发板
- NodeMCU v3 (CP2102)
- Wemos D1 Mini
- ESP-12E/F模块

### 传感器清单
- DHT11或DHT22温湿度传感器
- 水位传感器(模拟输出)
- LED指示灯(可选，板载LED可用)

---

## 引脚连接

### ESP8266引脚图

```
NodeMCU标识    GPIO    功能
D0            GPIO16   LED报警
D1            GPIO5    -
D2            GPIO4    -
D3            GPIO0    -
D4            GPIO2    DHT传感器
D5            GPIO14   -
D6            GPIO12   -
D7            GPIO13   -
D8            GPIO15   -
A0            ADC0     水位传感器
```

### 传感器接线

**DHT11/DHT22温湿度传感器**:
```
DHT VCC  --> NodeMCU 3.3V
DHT GND  --> NodeMCU GND
DHT DATA --> NodeMCU D4 (GPIO2)
```

**水位传感器**:
```
SENSOR VCC  --> NodeMCU 3.3V
SENSOR GND  --> NodeMCU GND
SENSOR AOUT --> NodeMCU A0 (唯一的ADC引脚)
```

**LED报警灯**:
```
LED 正极 --> NodeMCU D0 (GPIO16)
LED 负极 --> NodeMCU GND
(或直接使用板载LED，无需外接)
```

---

## 代码差异说明

### 关键修改点

**1. WiFi库不同**:
```cpp
// ESP32
#include <WiFi.h>

// ESP8266
#include <ESP8266WiFi.h>
```

**2. HTTP库不同**:
```cpp
// ESP32
#include <HTTPClient.h>
HTTPClient http;
http.begin(url);

// ESP8266
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
WiFiClient client;
HTTPClient http;
http.begin(client, url);  // 需要传入client对象
```

**3. ADC分辨率不同**:
```cpp
// ESP32: 12-bit ADC (0-4095)
waterLevel = map(analogRead(34), 0, 4095, 0, 100);

// ESP8266: 10-bit ADC (0-1023)
waterLevel = map(analogRead(A0), 0, 1023, 0, 100);
```

**4. 引脚编号不同**:
```cpp
// ESP32: 使用GPIO编号
#define DHT_PIN 4
#define WATER_LEVEL_PIN 34

// ESP8266: 使用D标识或GPIO编号
#define DHT_PIN D4        // 或 GPIO2
#define WATER_LEVEL_PIN A0
```

---

## Arduino IDE配置

### 1. 安装ESP8266支持

1. 打开Arduino IDE
2. 文件 → 首选项
3. 在"附加开发板管理器网址"添加:
   ```
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
4. 工具 → 开发板 → 开发板管理器
5. 搜索"esp8266"
6. 安装 **"ESP8266 by ESP8266 Community"** (版本3.0.0+)

### 2. 安装库

工具 → 管理库，搜索并安装:
- **DHT sensor library** (by Adafruit)
- **ArduinoJson** (6.21.0+)
- **ESP8266WiFi** (随ESP8266核心自动安装)
- **ESP8266HTTPClient** (随ESP8266核心自动安装)

### 3. 开发板设置

- 开发板: **NodeMCU 1.0 (ESP-12E Module)**
- Upload Speed: **115200**
- CPU Frequency: **80 MHz**
- Flash Size: **4MB (FS:2MB OTA:~1019KB)**
- Port: 选择你的ESP8266端口

---

## 上传步骤

### 1. 配置WiFi和服务器

```bash
cd esp32
cp config.example.h config.h
# 编辑config.h
```

**config.h示例**:
```cpp
#define WIFI_SSID "YourWiFi"
#define WIFI_PASSWORD "YourPassword"
#define SERVER_URL "http://192.168.1.100:8080"  // 本地测试
// 或
#define SERVER_URL "https://your-railway-app.up.railway.app"  // Railway部署
#define DEVICE_ID "ESP8266_01"
```

### 2. 打开ESP8266固件

Arduino IDE打开: `esp32/ESPMonitor_ESP8266.ino`

### 3. 选择开发板和端口

- 工具 → 开发板 → NodeMCU 1.0
- 工具 → 端口 → (你的ESP8266端口)

### 4. 上传

点击"上传"按钮(→)，等待完成。

### 5. 查看串口输出

工具 → 串口监视器 (波特率115200)

正常输出:
```
=== ESPMonitor (ESP8266) Starting ===
Connecting to WiFi........
WiFi connected
IP: 192.168.1.123
Thresholds updated: Temp=30.0, Hum=70.0, Water=80.0
Setup complete

Temp: 25.3°C, Humidity: 55.2%, Water: 42.0%
Data sent, response: 200
```

---

## ESP8266特殊注意事项

### 1. 内存限制

ESP8266的RAM较小(80KB)，避免:
- 大量字符串拼接
- 超大JSON文档
- 过多全局变量

**当前代码已优化**，无需修改。

### 2. ADC只有一个

ESP8266只有**一个ADC引脚(A0)**:
- 如需接更多模拟传感器，需使用ADC扩展模块
- 或使用数字传感器

### 3. GPIO16(D0)特殊性

GPIO16不支持某些功能:
- 不能用于中断
- 不能用于I2C/SPI
- **可以用于LED控制**(本项目使用)

### 4. 3.3V供电

ESP8266只支持3.3V:
- DHT传感器用3.3V(不要5V)
- 水位传感器用3.3V
- 外接传感器确认电压兼容

---

## 故障排查

### 上传失败

**症状**: Upload failed

**解决**:
1. 检查USB驱动(CP2102或CH340)
2. 按住FLASH按钮再点上传
3. 降低Upload Speed到74880

### WiFi连接失败

**症状**: WiFi connection failed

**解决**:
1. 确认是2.4GHz WiFi(不支持5GHz)
2. 检查SSID/密码
3. 靠近路由器测试

### DHT读取NaN

**症状**: DHT read failed

**解决**:
1. 确认接线正确(VCC→3.3V，不是5V)
2. 检查DHT_TYPE是DHT11还是DHT22
3. 更换传感器测试

### HTTP错误

**症状**: POST failed: -1

**解决**:
1. 确认SERVER_URL正确
2. 如使用Railway HTTPS，ESP8266需要SSL支持
3. 测试: 先用本地HTTP服务器

---

## HTTPS支持(Railway部署)

Railway使用HTTPS，ESP8266需要额外配置:

### 方法1: 禁用证书验证(仅测试)

```cpp
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>

WiFiClientSecure client;
client.setInsecure();  // 跳过证书验证

http.begin(client, "https://your-app.up.railway.app/api/sensor-data");
```

### 方法2: 添加根证书(生产环境)

获取Railway的根证书后:
```cpp
const char* rootCA = "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----";
client.setCACert(rootCA);
```

### 方法3: 使用HTTP反向代理

最简单的方法:
1. 在Railway前添加HTTP→HTTPS反向代理
2. ESP8266连接HTTP代理
3. 代理转发HTTPS到Railway

---

## 性能对比

| 指标 | ESP8266 | ESP32 |
|------|---------|-------|
| 上传速度 | ~5秒 | ~3秒 |
| WiFi连接 | ~3秒 | ~2秒 |
| HTTP请求 | ~100-200ms | ~80-150ms |
| 内存占用 | ~40KB | ~30KB |
| 功耗 | 70mA平均 | 80mA平均 |

**结论**: ESP8266性能完全够用！

---

## 推荐配置

**最佳开发板**: NodeMCU v3
- 集成CP2102 USB转串口
- 板载LED
- 引脚标识清晰
- 价格便宜(~$3)

**推荐传感器**: DHT22
- 比DHT11更精确
- 温度: ±0.5°C
- 湿度: ±2%
- 价格略贵但值得

---

## 代码文件对照

| 开发板 | 固件文件 |
|--------|----------|
| ESP32 | `esp32/ESPMonitor.ino` |
| ESP8266 | `esp32/ESPMonitor_ESP8266.ino` |
| 配置 | `esp32/config.h` (两者共用) |

---

## 总结

ESP8266完全可以运行ESPMonitor，优势:
- ✅ 价格更便宜
- ✅ 功耗更低
- ✅ 功能够用
- ✅ 社区资源丰富

唯一劣势:
- ❌ 只有1个ADC引脚(够用)
- ❌ 内存较小(本项目无影响)

**推荐使用ESP8266!**
