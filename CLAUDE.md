# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个Prompt管理系统，使用Flask框架构建，MySQL作为数据库，部署在Docker环境中。

## 项目架构

```
app/
├── config.py          # 环境配置（从.env读取）
├── common/           # 公共模块
│   ├── logger.py     # 日志系统（支持debug/production模式，按日期切分）
│   ├── database.py   # 数据库连接管理
│   └── exceptions.py # 自定义异常
├── models/          # 数据模型
├── services/        # 业务逻辑层
├── routes/          # API路由
├── templates/       # 前端模板
└── static/         # 静态资源
```

## 开发规范

1. **代码审美原则**：代码是艺术品，追求"刚刚好"的设计，避免过度设计和粗暴实现
2. **架构原则**：高内聚低耦合，DRY原则，文件粒度适中
3. **注释要求**：
   - 所有函数必须有中文注释
   - 关键逻辑需要详细注释
   - 对Python特殊语法（如**kwargs）进行解释
4. **扩展性**：数据库表必须包含create_time和update_time字段

## 常用命令

### 本地开发
```bash
# 安装依赖
pip install -r requirements.txt

# 复制环境配置
cp .env.template .env
# 编辑.env文件，配置数据库等信息

# 运行应用
python run.py

# 运行测试（使用真实数据库连接，不使用mock）
python -m pytest tests/
```

### Docker部署
```bash
# 构建镜像
docker-compose -f docker/docker-compose.yml build

# 启动服务
docker-compose -f docker/docker-compose.yml up -d

# 查看日志
docker-compose -f docker/docker-compose.yml logs -f
```

### 数据库初始化
```bash
# 执行初始化脚本
mysql -h<host> -u<user> -p<password> < migrations/init.sql
```

## 日志说明

- 日志文件位置：`logs/`
- 日志文件命名：`prompt_project_log.YYYY/MM/DD`
- 错误日志单独存储
- Debug模式：详细日志用于调试
- Production模式：只记录重要信息用于监控

## 环境配置

通过.env文件控制，主要配置项：
- ENV：环境标识（development/production）
- DB_*：数据库连接配置
- LOG_LEVEL：日志级别
- FLASK_DEBUG：Flask调试模式

## 注意事项

- 不要提交.env文件到版本控制
- 所有测试使用真实数据库连接
- 修改数据库结构时更新migrations/init.sql