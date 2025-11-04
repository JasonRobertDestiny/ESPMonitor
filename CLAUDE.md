# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 项目概述

ESPMonitor是一个物联网环境监控系统,由三个核心部分组成:

1. **ESP32固件** (Arduino C++) - 读取传感器,发送数据,控制报警
2. **Flask服务器** (Python) - 接收数据,存储到SQLite,提供REST API
3. **Web界面** (HTML/CSS/JavaScript) - 实时展示数据,远程控制阈值

**数据流**: 传感器 → ESP32 → Flask API → SQLite → Web界面 → 用户调整阈值 → ESP32获取更新

---

## 系统架构关键点

### 1. 双向通信机制
- **上行**: ESP32每5秒POST传感器数据到 `/api/sensor-data`
- **下行**: ESP32每10秒GET阈值更新从 `/api/thresholds`
- **报警逻辑**: ESP32本地比较读数与阈值,超阈值时LED亮起(不依赖服务器)

### 2. 数据存储设计
- SQLite两张表: `sensor_data`(历史记录) + `thresholds`(单行配置)
- 阈值采用**内存缓存+数据库持久化**模式(server/app.py:18-23)
- 无自动清理机制,长期运行需手动维护数据库

### 3. 容错机制
- ESP32: WiFi断线自动重连,传感器读取失败不崩溃
- Flask: 参数化查询防SQL注入,异常处理返回HTTP 500
- Web: 5秒轮询更新,超15秒无新数据显示"离线"

---

## 开发命令

### ESP32固件开发

```bash
# 配置WiFi和服务器(首次必须)
cd esp32
cp config.example.h config.h
# 编辑config.h填写WIFI_SSID, WIFI_PASSWORD, SERVER_URL

# 使用Arduino IDE上传固件
# 1. 打开ESPMonitor.ino
# 2. 工具 → 开发板 → ESP32 Dev Module
# 3. 工具 → 端口 → (选择ESP32端口)
# 4. 点击上传按钮

# 监控串口输出(调试必备)
# 波特率: 115200
# 可看到: WiFi连接状态、传感器读数、HTTP响应代码、阈值更新日志
```

### Flask服务器开发

```bash
# 安装依赖(首次)
cd server
pip install -r requirements.txt

# 启动开发服务器
python app.py
# 默认监听: http://0.0.0.0:8080
# 注意: 代码中硬编码端口8080(app.py:328),与README中的5000不一致

# 数据库操作(调试/维护)
sqlite3 ../database/espmonitor.db
# 查看最新数据
sqlite> SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10;
# 重置阈值
sqlite> UPDATE thresholds SET temperature=30, humidity=70, water_level=80 WHERE id=1;
# 清空历史数据
sqlite> DELETE FROM sensor_data;
```

### Web前端开发

```bash
# 前端为纯静态文件,修改后直接刷新浏览器
# 访问: http://localhost:8080

# 文件位置:
# - server/templates/dashboard.html  (主页面)
# - server/static/css/style.css      (样式)
# - server/static/js/dashboard.js    (交互逻辑)

# 调试前端:
# 1. 浏览器F12打开开发者工具
# 2. Console查看JavaScript错误
# 3. Network查看API请求/响应
```

---

## 关键配置说明

### ESP32配置 (esp32/config.h)
```cpp
#define WIFI_SSID "your_wifi"         // 必须2.4GHz WiFi
#define WIFI_PASSWORD "password"
#define SERVER_URL "http://192.168.1.X:8080"  // 注意端口是8080
#define DEVICE_ID "ESP32_01"          // 多设备时用于区分
```

### 引脚定义 (esp32/ESPMonitor.ino:19-22)
```cpp
#define DHT_PIN 4           // DHT传感器DATA引脚
#define WATER_LEVEL_PIN 34  // 水位传感器AOUT引脚(ADC1通道)
#define ALERT_LED_PIN 2     // LED报警(GPIO2是内置LED)
#define DHT_TYPE DHT11      // 或DHT22(根据实际传感器修改)
```

### 时间间隔 (esp32/ESPMonitor.ino:28-29)
```cpp
#define SEND_INTERVAL 5000              // 数据发送间隔(毫秒)
#define THRESHOLD_CHECK_INTERVAL 10000  // 阈值检查间隔(毫秒)
```

---

## API端点快速参考

| 方法 | 路径 | 功能 | 使用者 |
|------|------|------|--------|
| POST | `/api/sensor-data` | 接收传感器数据 | ESP32 |
| GET  | `/api/thresholds` | 获取当前阈值 | ESP32 + Web |
| POST | `/api/thresholds` | 更新阈值 | Web |
| GET  | `/api/latest-data?limit=20` | 获取最新N条数据 | Web |
| GET  | `/api/stats` | 获取24小时统计 | Web |
| GET  | `/api/history?device_id=X&limit=100` | 获取历史数据 | Web |

**数据格式示例**(POST /api/sensor-data):
```json
{
  "device_id": "ESP32_01",
  "temperature": 26.5,
  "humidity": 58.2,
  "water_level": 45.0
}
```

---

## 常见修改场景

### 添加新传感器(如光照传感器)

1. **ESP32端**:
   - 定义新引脚: `#define LIGHT_SENSOR_PIN 35`
   - 在`readSensors()`中读取: `lightLevel = analogRead(LIGHT_SENSOR_PIN)`
   - 在`sendDataToServer()`中添加到JSON: `doc["light"] = lightLevel`

2. **Flask端**:
   - 修改数据库schema(app.py:33-42): 添加`light REAL`列
   - 修改`save_sensor_data()`参数: 添加`light`参数
   - 修改API验证(app.py:154): 添加`'light'`到`required`列表

3. **Web端**:
   - 添加显示卡片(dashboard.html)
   - 更新JavaScript更新逻辑(dashboard.js)

### 修改采样频率
- ESP32: 修改`SEND_INTERVAL`(当前5000ms)
- 注意: 频率过高会增加数据库压力,建议>=3秒

### 更换服务器端口
1. 修改Flask启动端口(app.py:328): `port=8080` → `port=5000`
2. 修改ESP32配置(config.h): `SERVER_URL`中的端口号
3. 重新上传ESP32固件

### 添加多个ESP32设备
- 每个设备使用不同的`DEVICE_ID`(config.h)
- 服务器自动支持多设备(通过`device_id`字段区分)
- Web端可通过`/api/history?device_id=XXX`查询特定设备

---

## 故障排查流程

### ESP32无法连接WiFi
```bash
# 1. 检查串口输出(115200波特率)
# 2. 确认WiFi是2.4GHz(ESP32不支持5GHz)
# 3. 验证SSID/密码无特殊字符
# 4. 测试: 手机热点连接验证硬件正常
```

### ESP32显示"POST failed: -1"
```bash
# 1. 检查SERVER_URL是否正确
# 2. ping服务器IP确认网络连通
# 3. 确认Flask已启动且端口正确(8080)
# 4. 关闭防火墙测试: sudo ufw disable (Linux)
# 5. 查看Flask日志是否有请求记录
```

### Web界面显示"离线"
```bash
# 1. 检查ESP32串口是否正常发送数据
# 2. 测试API: curl http://localhost:8080/api/latest-data
# 3. 浏览器F12查看Network面板是否有API错误
# 4. 检查CORS配置(app.py:13)
```

### 传感器读数NaN
```bash
# 1. 检查DHT传感器接线(VCC/GND/DATA)
# 2. 确认DHT_TYPE匹配实际传感器(DHT11/DHT22)
# 3. 测试: 用万用表测量传感器VCC是否3.3V
# 4. 更换传感器排除硬件故障
```

---

## 代码风格规范

### Python代码(遵循PEP8)
- 函数使用snake_case: `save_sensor_data()`
- 常量大写: `DB_PATH`
- 参数化查询防SQL注入: `cursor.execute(sql, (param1, param2))`
- 异常处理: 所有API路由必须try-except

### Arduino C++代码
- 函数使用camelCase: `readSensors()`
- 常量/宏大写: `#define DHT_PIN 4`
- 全局变量驼峰命名: `lastSendTime`
- 串口调试信息清晰: `Serial.printf("Temp: %.1f°C", temperature)`

### JavaScript代码(前端)
- 使用现代ES6+语法: `const`, `let`, 箭头函数
- 异步请求使用`fetch()` API
- DOM操作使用`querySelector()`而非jQuery

---

## 安全注意事项

1. **config.h已加入.gitignore** - 绝不提交WiFi密码到Git
2. **生产环境建议**:
   - 添加API认证(JWT Token)
   - 使用HTTPS加密通信
   - 实施rate limiting防API滥用
   - 更换默认数据库路径权限
3. **当前安全措施**:
   - CORS已启用(可限制域名)
   - 参数化SQL查询
   - 输入验证(JSON必需字段检查)

---

## 性能基准

| 指标 | 当前值 | 优化建议 |
|------|--------|----------|
| 数据采样频率 | 5秒 | 可调整SEND_INTERVAL,建议>=3秒 |
| 数据传输延迟 | <100ms (局域网) | 无需优化 |
| Web刷新间隔 | 5秒 | 可改用WebSocket实时推送 |
| 数据库查询 | <50ms | 长期运行需定期清理历史数据 |
| 并发支持 | 10+ | Flask单线程,生产环境用Gunicorn |

---

## 扩展方向

### 短期扩展(1周内)
- 添加图表可视化(Chart.js/ECharts)
- 邮件/微信报警通知
- 数据导出CSV功能

### 中期扩展(1月内)
- WebSocket实时推送(替代轮询)
- 用户认证系统
- Docker容器化部署
- 多设备管理界面

### 长期扩展(3月内)
- 时序数据库(InfluxDB)替代SQLite
- 机器学习预测异常
- 移动APP(Flutter)
- 云端部署(AWS/阿里云)

---

## 重要文件清单

| 文件 | 作用 | 修改频率 |
|------|------|----------|
| `esp32/ESPMonitor.ino` | ESP32主程序 | 高 |
| `esp32/config.h` | WiFi/服务器配置(不提交) | 每次部署 |
| `server/app.py` | Flask主应用+API路由 | 高 |
| `server/requirements.txt` | Python依赖 | 低 |
| `server/templates/dashboard.html` | Web主页面 | 中 |
| `server/static/js/dashboard.js` | 前端交互逻辑 | 中 |
| `database/espmonitor.db` | SQLite数据库(自动创建) | 系统生成 |

---

## 部署前检查

1. **硬件连接**: DHT传感器正确接线,LED可用
2. **配置文件**: `config.h`已创建并填写正确信息
3. **Arduino库**: DHT sensor library + ArduinoJson已安装
4. **Python依赖**: `pip install -r requirements.txt`已执行
5. **网络环境**: ESP32和服务器在同一局域网
6. **端口冲突**: 8080端口未被占用

完整检查清单见: `DEPLOYMENT_CHECKLIST.md`

---

## 关键技术决策记录

### 为什么用轮询而非WebSocket?
- **原因**: ESP32 WebSocket库不够稳定,HTTP更可靠
- **权衡**: 实时性稍差(5-10秒延迟),但容错性强
- **未来**: Web端可改用WebSocket,ESP32保持HTTP

### 为什么用SQLite而非MySQL?
- **原因**: 单设备系统无需复杂数据库,SQLite零配置
- **适用**: <10个ESP32设备,<10万条/天数据
- **升级**: 超过此规模建议迁移到PostgreSQL/InfluxDB

### 为什么Flask运行在8080而非5000?
- **代码实现**: app.py:328硬编码`port=8080`
- **文档说明**: README中误写为5000
- **建议**: 统一为5000(Flask默认端口)避免混淆

---

## 已知问题

1. **端口不一致**: 代码使用8080,文档写5000 - 建议统一为5000
2. **无数据清理**: 长期运行会导致数据库膨胀 - 需添加定期清理任务
3. **无认证机制**: API完全开放 - 生产环境必须添加认证
4. **单线程Flask**: 并发能力有限 - 生产环境用Gunicorn+Nginx

---

## 联系与支持

- **快速启动**: 见 `QUICKSTART.md`
- **完整文档**: 见 `README.md`
- **Arduino库安装**: 见 `ARDUINO_LIBS.md`
- **部署检查**: 见 `DEPLOYMENT_CHECKLIST.md`
