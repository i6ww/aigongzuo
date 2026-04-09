# AI Art Workbench

一个简洁美观的 AI 画图工具，支持文生图和图生图功能。

## 功能特性

- **文生图** - 输入描述词，AI 生成精美图片
- **图生图** - 上传参考图片，AI 基于图片生成新作品
- **多分辨率** - 支持 1K、2K、4K 输出
- **多模型选择** - 支持 Pro、V2、V3 等多种模型
- **深色/浅色主题** - 一键切换
- **历史记录** - 保存最近使用的提示词
- **隐私保护** - API Key 不自动保存，保护用户隐私
- **图片下载** - 一键下载生成结果

## 支持模型

| 模型系列 | 说明 |
|---------|------|
| firefly-nano-banana-pro | 高质量专业模型 |
| firefly-nano-banana2 | nano-banana-2 系列 |
| firefly-nano-banana | nano-banana-3 系列 |

每个系列支持 1K、2K、4K 分辨率。

---

## 快速开始

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python app.py
```

访问 `http://localhost:8080`

### Docker 部署

```bash
# 构建镜像
docker build -t ai-art-workbench .

# 运行容器
docker run -d -p 8080:5000 --name ai-art-workbench ai-art-workbench
```

---

## 云服务器部署

### 环境要求

- 服务器安装了 Docker
- 开放端口 8080

### 部署步骤

```bash
# 1. 连接服务器
ssh root@你的服务器IP

# 2. 安装 Docker（如未安装）
apt update && apt install -y docker.io docker-compose

# 3. 克隆项目
git clone https://github.com/i6ww/aigongzuotai.git
cd aigongzuotai/ai-art-workbench

# 4. 构建并启动
docker build -t ai-art-workbench .
docker run -d -p 8080:5000 --name ai-art-workbench ai-art-workbench
```

### Docker Compose 部署（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: ai-art-workbench
    ports:
      - "8080:5000"
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
```

启动服务：

```bash
# 构建并启动
docker-compose up -d --build

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 更新部署
git pull origin main && docker-compose up -d --build
```

### 开放端口

在云服务器控制台的安全组中添加入站规则：

- 协议: TCP
- 端口: 8080
- 来源: 0.0.0.0/0

---

## 常见问题

### Q: 端口被占用？
```bash
# 查看端口占用
netstat -tlnp | grep 8080

# 改为其他端口，如 8090
docker run -d -p 8090:5000 --name ai-art-workbench ai-art-workbench
```

### Q: 容器启动失败？
```bash
# 查看错误日志
docker logs ai-art-workbench
```

### Q: 如何更新？
```bash
cd ai-art-workbench
git pull origin main
docker build -t ai-art-workbench .
docker stop ai-art-workbench
docker rm ai-art-workbench
docker run -d -p 8080:5000 --name ai-art-workbench ai-art-workbench
```

### Q: 如何备份？
```bash
# 导出镜像
docker save ai-art-workbench > ai-art-workbench.tar

# 导入镜像
docker load < ai-art-workbench.tar
```

---

## 项目结构

```
ai-art-workbench/
├── app.py              # Flask 后端
├── requirements.txt    # Python 依赖
├── Dockerfile          # Docker 配置
├── README.md           # 项目说明
└── static/
    ├── index.html      # 前端页面
    ├── styles.css      # 样式
    └── script.js       # 前端脚本
```

## API 配置

- **API 地址**: https://www.371181668.xyz
- **认证方式**: Bearer API Key

## 技术栈

- 后端: Flask (Python)
- 前端: HTML + CSS + JavaScript
- 部署: Docker
