# Arduino库依赖安装指南

ESPMonitor项目需要的Arduino库及安装方法

---

## 方法1: 通过Arduino IDE库管理器安装(推荐)

### 1. DHT Sensor Library

**作用**: 读取DHT11/DHT22温湿度传感器

**安装步骤**:
1. 打开Arduino IDE
2. Sketch → Include Library → Manage Libraries
3. 搜索: `DHT sensor library`
4. 选择 `DHT sensor library by Adafruit`
5. 点击"Install"
6. 同时安装依赖库: `Adafruit Unified Sensor`

**版本要求**: 1.4.4 或更高

---

### 2. ArduinoJson

**作用**: JSON数据解析和生成

**安装步骤**:
1. 打开Arduino IDE
2. Sketch → Include Library → Manage Libraries
3. 搜索: `ArduinoJson`
4. 选择 `ArduinoJson by Benoit Blanchon`
5. 点击"Install"

**版本要求**: 6.21.0 或更高

---

### 3. ESP32 Core

**作用**: ESP32开发板支持

**安装步骤**:
1. 打开Arduino IDE
2. File → Preferences
3. 在"Additional Boards Manager URLs"中添加:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Tools → Board → Boards Manager
5. 搜索: `esp32`
6. 安装 `esp32 by Espressif Systems`

**版本要求**: 2.0.0 或更高

---

## 方法2: 手动下载安装

### DHT Library
```bash
# 下载地址
https://github.com/adafruit/DHT-sensor-library

# 安装方法
1. 下载ZIP文件
2. Sketch → Include Library → Add .ZIP Library
3. 选择下载的ZIP文件
```

### ArduinoJson
```bash
# 下载地址
https://github.com/bblanchon/ArduinoJson

# 安装方法
1. 下载ZIP文件
2. Sketch → Include Library → Add .ZIP Library
3. 选择下载的ZIP文件
```

---

## 验证安装

### 测试代码
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

void setup() {
  Serial.begin(115200);
  Serial.println("All libraries loaded successfully!");
}

void loop() {}
```

**成功标志**: 代码编译无错误

---

## 常见安装问题

### Q: 找不到DHT.h
**A**: 确保安装的是 "DHT sensor library by Adafruit",不是其他同名库

### Q: ArduinoJson编译错误
**A**: 检查版本,必须是6.x版本(不是5.x或7.x)

### Q: ESP32开发板不在列表中
**A**:
1. 检查Boards Manager URL是否正确添加
2. 重启Arduino IDE
3. 重新搜索并安装ESP32支持包

### Q: HTTPClient.h找不到
**A**: HTTPClient是ESP32 Core的一部分,确保ESP32 Core已正确安装

---

## 库文件位置

### Windows
```
C:\Users\你的用户名\Documents\Arduino\libraries\
```

### Linux
```
~/Arduino/libraries/
```

### Mac
```
~/Documents/Arduino/libraries/
```

---

## 推荐IDE设置

```
File → Preferences
- Compiler warnings: Default
- Upload speed: 115200
- Flash Mode: QIO
- Flash Frequency: 80MHz
- Flash Size: 4MB
```

---

## 完整库列表

| 库名称 | 版本 | 用途 |
|--------|------|------|
| ESP32 Core | 2.0.0+ | ESP32基础支持 |
| DHT sensor library | 1.4.4+ | 温湿度传感器 |
| ArduinoJson | 6.21.0+ | JSON处理 |
| WiFi | (内置) | WiFi连接 |
| HTTPClient | (内置) | HTTP通信 |

**注**: WiFi和HTTPClient是ESP32 Core的内置库,无需单独安装

---

## 更新库

定期更新库以获取bug修复和新功能:

```
Sketch → Include Library → Manage Libraries
搜索已安装的库 → 点击"Update"
```

---

## 使用PlatformIO(替代方案)

如果你使用PlatformIO而不是Arduino IDE,在`platformio.ini`中添加:

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
lib_deps =
    adafruit/DHT sensor library @ ^1.4.4
    bblanchon/ArduinoJson @ ^6.21.0
```

然后运行:
```bash
pio lib install
```

---

**安装完成后,你就可以编译和上传ESPMonitor固件了!**
