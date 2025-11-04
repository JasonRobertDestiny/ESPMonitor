# Railway部署指南

ESPMonitor在Railway上一键部署教程

---

## 为什么选择Railway?

- ✅ **零代码改动** - Flask应用直接部署
- ✅ **持久化存储** - 支持SQLite数据库持久化
- ✅ **免费额度** - 500小时/月免费运行时间
- ✅ **自动HTTPS** - 提供免费SSL证书
- ✅ **固定域名** - ESP32可直接配置使用

---

## 部署步骤

### 1. 准备工作
- [x] GitHub账号
- [x] Railway账号(使用GitHub登录)
- [x] 代码已推送到GitHub

### 2. 在Railway上部署

#### 方法1: 一键部署(推荐)

1. 访问 [Railway.app](https://railway.app)
2. 点击 "Start a New Project"
3. 选择 "Deploy from GitHub repo"
4. 授权Railway访问GitHub
5. 选择 `JasonRobertDestiny/ESPMonitor` 仓库
6. Railway自动检测Python项目并开始构建

#### 方法2: 使用Railway CLI

```bash
# 安装Railway CLI
npm i -g @railway/cli

# 登录Railway
railway login

# 在项目目录初始化
cd /path/to/ESPMonitor
railway init

# 部署
railway up
```

### 3. 配置持久化存储(重要!)

SQLite数据库需要持久化存储才能保存数据:

1. 在Railway项目中,点击 "Variables"
2. 添加卷(Volume):
   - 点击 "New Volume"
   - Mount Path: `/app/database`
   - 保存

### 4. 获取部署URL

部署完成后,Railway会提供一个域名:
```
https://espmonitor-production-xxxx.up.railway.app
```

### 5. 配置ESP32

修改 `esp32/config.h`:

```cpp
#define SERVER_URL "https://espmonitor-production-xxxx.up.railway.app"
```

**重要**: Railway域名使用HTTPS,ESP32需要支持SSL。

---

## 环境变量配置

Railway会自动设置 `PORT` 环境变量,无需手动配置。

如需自定义配置,在Railway Dashboard添加:

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| PORT | 服务器端口 | 自动分配 |
| PYTHON_VERSION | Python版本 | 3.11 |

---

## 验证部署

### 1. 检查服务器状态

访问: `https://your-app.up.railway.app`

应该看到Web控制面板。

### 2. 测试API端点

```bash
# 获取阈值
curl https://your-app.up.railway.app/api/thresholds

# 应该返回:
# {"temperature":30.0,"humidity":70.0,"water_level":80.0}
```

### 3. 查看日志

Railway Dashboard → Deployments → View Logs

看到类似输出:
```
=== ESPMonitor Server Starting ===
Database initialized
Current thresholds: {...}
 * Running on http://0.0.0.0:XXXX
```

---

## ESP32 HTTPS支持

Railway使用HTTPS,ESP32需要SSL支持:

### 方法1: 修改ESP32代码支持HTTPS

```cpp
#include <WiFiClientSecure.h>

WiFiClientSecure client;
client.setInsecure(); // 跳过证书验证(仅测试用)

// 或者添加证书验证
const char* rootCA = "-----BEGIN CERTIFICATE-----\n...";
client.setCACert(rootCA);
```

### 方法2: 使用HTTP反向代理(推荐)

如果ESP32不支持HTTPS,可以:
1. 在Railway部署时添加HTTP端点
2. 或使用其他支持HTTP的托管服务(如Render)

---

## 数据库管理

### 查看数据库内容

Railway提供数据库浏览功能:

1. Railway Dashboard → Volumes
2. 下载database/espmonitor.db
3. 使用SQLite工具打开

### 备份数据库

```bash
# 使用Railway CLI下载
railway run python -c "import shutil; shutil.copy('database/espmonitor.db', 'backup.db')"
```

---

## 监控与维护

### 查看运行时间

Railway Dashboard → Metrics

显示:
- CPU使用率
- 内存使用
- 网络流量
- 运行时间(免费500小时/月)

### 重启服务

Railway Dashboard → Settings → Restart

或使用CLI:
```bash
railway restart
```

---

## 成本估算

### 免费版限额

- **运行时间**: 500小时/月(约20天)
- **存储**: 1GB持久化存储
- **流量**: 无限制

### 优化建议

如果超出免费额度:
1. 优化数据库查询减少CPU占用
2. 定期清理历史数据
3. 升级到付费版($5/月起)

---

## 故障排查

### 部署失败

**症状**: Build failed

**解决**:
1. 检查requirements.txt是否在根目录
2. 检查Python版本兼容性
3. 查看Railway部署日志

### 数据库无法写入

**症状**: 数据不保存

**解决**:
1. 确认已添加Volume挂载到 `/app/database`
2. 检查数据库路径是否正确
3. 查看app.py日志错误信息

### ESP32连接失败

**症状**: ESP32显示HTTP -1错误

**解决**:
1. 检查SERVER_URL是否包含正确的Railway域名
2. 如使用HTTPS,确保ESP32支持SSL
3. 测试Railway服务是否正常运行

---

## 升级到付费版

如果免费额度不够用:

**Hobby Plan ($5/月)**:
- 无限运行时间
- 8GB RAM
- 100GB存储

**Pro Plan ($20/月)**:
- 多个项目
- 团队协作
- 优先支持

---

## 相关链接

- [Railway官方文档](https://docs.railway.app)
- [ESPMonitor GitHub](https://github.com/JasonRobertDestiny/ESPMonitor)
- [问题反馈](https://github.com/JasonRobertDestiny/ESPMonitor/issues)

---

**部署完成!** 你的ESPMonitor现在已经运行在云端了。

下一步: 配置ESP32连接到Railway服务器。
