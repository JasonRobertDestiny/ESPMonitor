# ESPMonitor 快速启动指南

5分钟快速部署ESPMonitor系统

---

## 准备工作

### 硬件清单
- [ ] ESP32开发板
- [ ] DHT11或DHT22传感器
- [ ] 水位传感器(可选)
- [ ] LED(可用内置LED)
- [ ] USB数据线
- [ ] 面包板和杜邦线

### 软件清单
- [ ] Arduino IDE (已安装ESP32支持)
- [ ] Python 3.8+ (Windows/Linux/Mac)
- [ ] 电脑和ESP32在同一WiFi网络

---

## Step 1: 硬件连接 (2分钟)

```
DHT传感器接线:
  DHT VCC  --> ESP32 3.3V
  DHT GND  --> ESP32 GND
  DHT DATA --> ESP32 GPIO4

水位传感器接线(可选):
  SENSOR VCC  --> ESP32 3.3V
  SENSOR GND  --> ESP32 GND
  SENSOR AOUT --> ESP32 GPIO34

LED接线(可直接用板载LED):
  使用GPIO2即可,无需外接
```

---

## Step 2: ESP32固件配置 (1分钟)

```bash
# 1. 复制配置模板
cd esp32
cp config.example.h config.h

# 2. 编辑config.h,只需修改3项:
#    - WIFI_SSID: 你的WiFi名称
#    - WIFI_PASSWORD: 你的WiFi密码
#    - SERVER_URL: 你的电脑IP,格式 http://192.168.1.XXX:5000

# 3. 如何找到电脑IP?
#    Windows: ipconfig
#    Linux/Mac: ifconfig 或 ip addr
```

### config.h 示例:
```cpp
#define WIFI_SSID "MyHome_WiFi"
#define WIFI_PASSWORD "mypassword123"
#define SERVER_URL "http://192.168.1.105:5000"
#define DEVICE_ID "ESP32_01"
```

---

## Step 3: 上传ESP32固件 (1分钟)

```
1. 用Arduino IDE打开 esp32/ESPMonitor.ino
2. 选择开发板: 工具 -> 开发板 -> ESP32 Dev Module
3. 选择端口: 工具 -> 端口 -> (你的ESP32端口)
4. 点击"上传"按钮(→图标)
5. 等待上传完成
6. 打开串口监视器(波特率115200)查看运行状态
```

**如果Arduino库缺失,安装以下库:**
- DHT sensor library (Adafruit)
- ArduinoJson

---

## Step 4: 启动Flask服务器 (1分钟)

```bash
# 1. 进入服务器目录
cd server

# 2. 安装Python依赖(仅首次需要)
pip install -r requirements.txt

# 3. 启动服务器
python app.py

# 看到以下信息表示成功:
# === ESPMonitor Server Starting ===
# Database initialized
# Current thresholds: {...}
#  * Running on http://0.0.0.0:5000
```

---

## Step 5: 访问Web界面

```
打开浏览器访问: http://localhost:5000

如从其他设备访问: http://你的电脑IP:5000
```

**成功标志:**
- 界面显示"在线"
- 能看到实时温度、湿度、水位数据
- 数据每5秒自动更新

---

## 测试阈值报警

1. 在Web界面"阈值设置"区域,将温度阈值设为20°C
2. 点击"更新阈值"
3. 如果当前温度>20°C,你会看到:
   - 温度卡片变为警告色并闪烁
   - ESP32的LED亮起
   - 串口监视器显示ALERT信息

---

## 常见问题速查

### Q: ESP32串口显示"WiFi connection failed"
**A:**
- 检查SSID和密码是否正确
- 确保是2.4GHz WiFi(不是5GHz)
- 检查WiFi信号强度

### Q: ESP32串口显示"POST failed: -1"
**A:**
- 检查SERVER_URL的IP是否正确
- 确保Flask服务器已启动
- ping 服务器IP确认网络连通

### Q: Web界面显示"离线"
**A:**
- 查看ESP32串口,确认是否正常发送数据
- 检查Flask服务器是否运行
- 刷新浏览器

### Q: DHT传感器读取失败
**A:**
- 检查接线是否正确
- 确认DHT类型(DHT11还是DHT22)
- 在代码中修改 `#define DHT_TYPE DHT11` 或 `DHT22`

---

## 下一步

### 基础功能验证
- [ ] 温度读数正常
- [ ] 湿度读数正常
- [ ] 水位读数正常(如有传感器)
- [ ] 阈值报警功能正常
- [ ] 历史数据记录正常

### 进阶操作
- [ ] 调整传感器采样频率
- [ ] 添加更多ESP32设备
- [ ] 自定义报警逻辑
- [ ] 数据导出和分析

---

## 串口输出示例

**正常运行的ESP32串口输出:**
```
=== ESPMonitor Starting ===
Connecting to WiFi........
WiFi connected
IP: 192.168.1.123
Thresholds updated: Temp=30.0, Hum=70.0, Water=80.0
Setup complete

Temp: 25.3°C, Humidity: 55.2%, Water: 42.0%
Data sent, response: 200
Temp: 25.4°C, Humidity: 55.1%, Water: 43.0%
Data sent, response: 200
```

---

## 性能指标

- 传感器采样间隔: 5秒
- 数据传输延迟: <100ms
- Web界面更新: 5秒自动刷新
- 阈值同步: 10秒轮询
- 数据库查询: <50ms

---

## 调试技巧

### 1. 查看ESP32状态
```cpp
// 在Arduino串口监视器中查看:
// - WiFi连接状态
// - 传感器读数
// - HTTP响应代码
// - 阈值更新日志
```

### 2. 查看Flask日志
```bash
# Flask控制台会显示:
# - 收到的数据
# - API请求
# - 数据库操作
```

### 3. 检查数据库
```bash
# 使用SQLite工具查看数据:
sqlite3 database/espmonitor.db
sqlite> SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10;
```

---

**完成! 现在你已经拥有一个完整的物联网环境监控系统。**

如有问题,查看完整的README.md或提交Issue。
