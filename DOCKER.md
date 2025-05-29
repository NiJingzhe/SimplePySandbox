# Docker 部署指南

## 快速启动

```bash
# 构建镜像
./docker.sh build

# 启动服务
./docker.sh start

# 查看状态
./docker.sh status

# 查看日志
./docker.sh logs

# 停止服务
./docker.sh stop
```

## 开发模式

```bash
# 启动开发模式（支持代码热重载）
docker-compose -f docker-compose.dev.yml up -d

# 查看开发模式日志
docker-compose -f docker-compose.dev.yml logs -f
```

## 服务访问

启动后可通过以下地址访问：

- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 数据持久化

服务会自动创建并挂载以下目录：

- `./data` - 环境数据存储
- `./logs` - 日志文件（如果存在）

## 常用命令

```bash
# 重新构建并启动
./docker.sh restart --build

# 运行测试
./docker.sh test

# 清理所有资源
./docker.sh clean

# 查看帮助
./docker.sh help
```

## 故障排除

### 服务无法启动

1. 检查Docker是否运行
2. 检查端口8000是否被占用
3. 查看日志：`./docker.sh logs`

### 构建失败

1. 确保网络连接正常
2. 清理Docker缓存：`docker system prune -f`
3. 重新构建：`./docker.sh build`
