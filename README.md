# ESPMonitor - 物联网环境监控系统

一个基于ESP32的完整环境监控解决方案,实现温度、湿度和水位的实时监测,数据可视化和远程阈值控制。

---

## 系统架构

```
ESP32 (传感器) --WiFi--> Flask服务器 --HTTP--> Web浏览器
    ↓                        ↓                     ↓
  读取数据                存储到SQLite            实时显示
  控制LED                 处理API请求             调整阈值
```

---

## 功能特性

### ESP32端
- WiFi连接(STA模式)
- DHT11/DHT22温湿度传感器读取
- 水位传感器读取(模拟输入)
- HTTP POST发送数据到服务器
- HTTP GET获取阈值更新
- 超阈值LED报警

### 服务器端
- Flask RESTful API
- SQLite数据库存储
- 实时数据接收和处理
- 阈值管理
- 历史数据查询
- 统计分析(24小时)

### Web界面
- 实时数据展示(每5秒更新)
- 温度/湿度/水位可视化卡片
- 阈值远程调整
- 24小时统计数据
- 历史记录表格
- 响应式设计

---

## 硬件需求

### ESP32端
- ESP32开发板 (ESP-WROOM-32或类似)
- DHT11或DHT22温湿度传感器
- 水位传感器(可选,模拟输出)
- LED指示灯
- 杜邦线和面包板

### 引脚连接
```
DHT传感器:
  - VCC  -> 3.3V
  - GND  -> GND
  - DATA -> GPIO 4

水位传感器:
  - VCC  -> 3.3V
  - GND  -> GND
  - AOUT -> GPIO 34 (ADC1_CH6)

LED报警灯:
  - 正极 -> GPIO 2 (内置LED)
  - 负极 -> GND
```

---

## 软件依赖

### ESP32 (Arduino IDE)
```
- Arduino ESP32 Core (2.0.0+)
- DHT sensor library (1.4.4+)
- ArduinoJson (6.21.0+)
```

### 服务器 (Python 3.8+)
```
- Flask 3.0.0
- flask-cors 4.0.0
```

---

## 安装步骤

### 1. ESP32固件部署

1. 安装Arduino IDE和ESP32支持包
2. 安装所需库:
   - Sketch -> Include Library -> Manage Libraries
   - 搜索并安装: DHT sensor library, ArduinoJson

3. 配置WiFi和服务器:
   ```bash
   cd esp32
   cp config.example.h config.h
   # 编辑config.h,填入你的WiFi和服务器信息
   ```

4. 上传代码到ESP32:
   - 打开 `esp32/ESPMonitor.ino`
   - 选择开发板: Tools -> Board -> ESP32 Dev Module
   - 选择端口: Tools -> Port -> (你的ESP32端口)
   - 点击上传按钮

### 2. Flask服务器部署

1. 安装Python依赖:
   ```bash
   cd server
   pip install -r requirements.txt
   ```

2. 启动服务器:
   ```bash
   python app.py
   ```

   服务器将在 `http://0.0.0.0:5000` 启动

3. 访问Web界面:
   ```
   http://你的服务器IP:5000
   ```

### 3. 配置说明

#### ESP32配置 (esp32/config.h)
```cpp
#define WIFI_SSID "your_wifi_name"
#define WIFI_PASSWORD "your_password"
#define SERVER_URL "http://192.168.1.100:5000"
#define DEVICE_ID "ESP32_01"
```

#### 修改传感器引脚 (ESPMonitor.ino)
```cpp
#define DHT_PIN 4           // DHT传感器数据引脚
#define WATER_LEVEL_PIN 34  // 水位传感器引脚
#define ALERT_LED_PIN 2     // LED报警引脚
```

---

## API文档

### 1. 接收传感器数据
```http
POST /api/sensor-data
Content-Type: application/json

{
  "device_id": "ESP32_01",
  "temperature": 26.5,
  "humidity": 58.2,
  "water_level": 45.0
}
```

### 2. 获取最新数据
```http
GET /api/latest-data?limit=20
```

### 3. 获取阈值
```http
GET /api/thresholds

Response:
{
  "temperature": 30.0,
  "humidity": 70.0,
  "water_level": 80.0
}
```

### 4. 更新阈值
```http
POST /api/thresholds
Content-Type: application/json

{
  "temperature": 28.0,
  "humidity": 75.0,
  "water_level": 85.0
}
```

### 5. 获取历史数据
```http
GET /api/history?device_id=ESP32_01&limit=100
```

### 6. 获取统计数据
```http
GET /api/stats
```

---

## 使用说明

### 首次启动
1. 确保ESP32和Flask服务器在同一网络
2. 修改ESP32的`config.h`,填入正确的服务器IP
3. 上传固件到ESP32
4. 启动Flask服务器
5. ESP32会自动连接WiFi并开始发送数据

### 调整阈值
1. 打开Web界面 `http://服务器IP:5000`
2. 在"阈值设置"区域输入新的阈值
3. 点击"更新阈值"按钮
4. ESP32会在10秒内获取新阈值并应用

### 监控报警
- 当任何读数超过阈值时:
  - ESP32的LED会亮起
  - Web界面对应卡片会变为警告色并闪烁
  - 串口监视器会打印警告信息

---

## 故障排查

### ESP32无法连接WiFi
- 检查SSID和密码是否正确
- 确保WiFi是2.4GHz频段(ESP32不支持5GHz)
- 查看串口监视器的连接日志

### 数据无法发送到服务器
- 检查服务器IP是否正确
- 确保服务器已启动
- 检查防火墙是否阻止5000端口
- 查看串口监视器的HTTP响应代码

### Web界面显示"离线"
- 检查ESP32是否正常运行
- 确保ESP32能正常发送数据(查看串口)
- 刷新浏览器页面

### 数据库问题
- 数据库文件位于: `database/espmonitor.db`
- 如需重置,删除此文件后重启服务器
- 服务器会自动重建数据库

---

## 项目结构

```
ESPMonitor/
├── esp32/
│   ├── ESPMonitor.ino         # ESP32主程序
│   └── config.example.h       # 配置模板
├── server/
│   ├── app.py                 # Flask主应用
│   ├── requirements.txt       # Python依赖
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # 样式表
│   │   └── js/
│   │       └── dashboard.js   # 前端逻辑
│   └── templates/
│       └── dashboard.html     # 主页面
├── database/
│   └── espmonitor.db          # SQLite数据库(自动创建)
└── README.md                  # 本文档
```

---

## 扩展建议

### 硬件扩展
- 添加更多传感器(光照、气压、PM2.5等)
- 添加继电器控制(风扇、加湿器等)
- 使用OLED屏幕显示本地数据
- 添加蜂鸣器报警

### 软件扩展
- 实现WebSocket实时推送(替代轮询)
- 添加用户认证和授权
- 数据导出功能(CSV/Excel)
- 图表可视化(Chart.js)
- 微信/邮件报警通知
- 移动端APP

### 部署建议
- 使用Nginx反向代理Flask
- 使用Gunicorn/uWSGI部署生产环境
- 使用MySQL/PostgreSQL替代SQLite
- 容器化部署(Docker)

---

## 技术栈

- **硬件**: ESP32, DHT11/22, 水位传感器
- **固件**: Arduino C++
- **后端**: Python 3.8+, Flask 3.0
- **数据库**: SQLite 3
- **前端**: HTML5, CSS3, Vanilla JavaScript
- **通信**: HTTP REST API

---

## 许可证

MIT License - 自由使用、修改和分发

---

## 作者

ESPMonitor v1.0

如有问题或建议,欢迎提交Issue或Pull Request。

---

## 更新日志

### v1.0 (2025-10-29)
- 初始版本发布
- ESP32传感器读取和WiFi通信
- Flask RESTful API
- Web实时监控界面
- SQLite数据存储
- 阈值远程控制
- LED报警功能
