# Prompt管理系统开发日志 - 2025/08/06

## 项目概述

这是一个Prompt管理系统，使用Flask框架构建，MySQL作为数据库，部署在Docker环境中。

### 核心技术栈
- **服务器**: 阿里云ubuntu 24.02
- **环境部署**: Docker
- **数据库**: MySQL
- **程序语言**: Python
- **网站框架**: Flask

## 设计原则与理念

### 代码审美原则
1. **艺术品理念**: 代码是艺术品，每一个模块、每一行指令都精雕细琢
2. **"刚刚好"的设计**: 既不过度设计，也不粗暴实现
3. **高内聚低耦合**: 架构设计遵循DRY原则
4. **文件粒度适中**: 拆分文件，任何修改都是最小改动

### 扩展性设计
1. **数据库表设计**: 必须包含create_time和update_time字段
2. **配置管理**: 使用.env.template模式便于生产环境部署
3. **日志系统**: 支持debug/production模式切换
4. **模块化架构**: 便于后续功能扩展

### 注释与文档规范
1. **所有函数必须有中文注释**
2. **关键逻辑需要详细注释**
3. **对Python特殊语法进行解释**（如**kwargs等）
4. **面向对象设计，合理的封装和抽象**

---

## 项目架构设计

### 文件目录结构

```
prompt_project/
│
├── app/                           # 应用主目录
│   ├── __init__.py               # Flask应用初始化
│   ├── config.py                 # 配置管理模块 ✅
│   │
│   ├── common/                   # 公共模块目录
│   │   ├── __init__.py
│   │   ├── logger.py            # 日志管理模块 ✅
│   │   ├── database.py          # 数据库连接管理 📝
│   │   ├── exceptions.py        # 自定义异常处理 📝
│   │   ├── decorators.py        # 通用装饰器
│   │   └── utils.py             # 工具函数集合
│   │
│   ├── models/                   # 数据模型层
│   │   ├── __init__.py
│   │   ├── base.py              # 基础模型类（包含create_time, update_time）
│   │   ├── user.py              # 用户模型
│   │   ├── prompt.py            # Prompt模型
│   │   ├── template.py          # 模板模型
│   │   ├── workspace.py         # 工作空间模型
│   │   ├── activity.py          # 活动记录模型
│   │   └── api_config.py        # API配置模型
│   │
│   ├── services/                 # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py      # 认证服务
│   │   ├── prompt_service.py    # Prompt业务逻辑
│   │   ├── template_service.py  # 模板业务逻辑
│   │   ├── activity_service.py  # 活动记录服务
│   │   ├── api_status_service.py # API状态检测服务
│   │   └── dashboard_service.py  # 首页数据聚合服务
│   │
│   ├── routes/                   # 路由层（API接口）
│   │   ├── __init__.py
│   │   ├── auth.py              # 认证相关路由
│   │   ├── dashboard.py         # 首页路由
│   │   ├── prompts.py           # Prompt相关路由
│   │   ├── templates.py         # 模板相关路由
│   │   ├── activities.py        # 活动记录路由
│   │   └── integrations.py      # API集成路由
│   │
│   ├── templates/                # HTML模板目录
│   │   ├── base.html            # 基础模板
│   │   ├── dashboard.html       # 首页模板
│   │   ├── components/          # 组件模板
│   │   │   ├── sidebar.html     # 侧边栏
│   │   │   ├── header.html      # 顶部导航
│   │   │   └── cards/           # 卡片组件
│   │   │       ├── prompt_card.html
│   │   │       ├── template_card.html
│   │   │       └── activity_item.html
│   │   └── partials/            # 部分模板
│   │       └── modals/          # 弹窗模板
│   │
│   └── static/                   # 静态资源
│       ├── css/
│       │   ├── main.css         # 主样式文件
│       │   └── dashboard.css    # 首页样式
│       ├── js/
│       │   ├── app.js           # 主应用JS
│       │   └── dashboard.js     # 首页交互JS
│       └── images/              # 图片资源
│
├── migrations/                   # 数据库迁移文件
│   ├── init.sql                 # 初始化SQL脚本
│   └── versions/                # 版本迁移目录
│
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── conftest.py             # pytest配置
│   ├── test_config.py          # 配置模块测试 ✅
│   ├── test_logger.py          # 日志模块测试 ✅
│   ├── test_database.py        # 数据库模块测试
│   ├── test_services/          # 服务层测试
│   └── test_routes/            # 路由层测试
│
├── logs/                        # 日志文件目录（自动生成）
│   ├── prompt_project_log.2024.12.01
│   └── error/                  # 错误日志单独存储
│
├── docker/                      # Docker相关配置
│   ├── Dockerfile              # Docker镜像配置
│   ├── docker-compose.yml     # Docker Compose配置
│   └── nginx/                 # Nginx配置（如需要）
│       └── nginx.conf
│
├── scripts/                    # 脚本目录
│   ├── init_db.py             # 数据库初始化脚本
│   └── seed_data.py           # 测试数据导入脚本
│
├── claude_coding_log/          # 开发日志目录
│   └── claude_coding_log_2025_08_06.md  # 今日开发日志
│
├── .env.template              # 环境变量模板 ✅
├── .gitignore                # Git忽略文件
├── requirements.txt          # Python依赖包 ✅
├── run.py                   # 应用启动入口
├── CLAUDE.md               # 项目说明文档 ✅
└── README.md               # 项目说明文档
```

### 架构设计理念

#### 1. 分层架构
- **Models层**: 纯数据模型，只负责数据结构定义
- **Services层**: 业务逻辑处理，复杂的数据组合和处理
- **Routes层**: API接口定义，只负责请求响应
- **Common层**: 跨层的公共功能模块

#### 2. 文件粒度设计
- 每个模型单独一个文件，便于维护和扩展
- 服务层按业务功能划分，避免单个文件过大
- 路由层按资源类型组织，RESTful风格

#### 3. 扩展性考虑
- `base.py`提供所有模型的基类，统一处理create_time和update_time
- 配置文件使用`.env.template`模式，便于部署
- 日志系统支持多环境切换
- Docker部署支持，便于环境一致性

---

## 已完成功能模块

### ✅ 1. 配置管理模块 (app/config.py)

#### 功能特性
- **环境配置管理**: 支持development/production环境切换
- **数据库配置**: MySQL连接参数和连接池配置
- **API密钥管理**: OpenAI、Claude、文心一言等多平台API配置
- **日志配置**: 可配置日志级别、文件路径、保留天数等
- **安全配置**: CORS、Session、请求限制等配置

#### 设计亮点
```python
class Config:
    """配置基类，定义所有环境通用的配置项"""
    
    def get_api_config(self, provider: str) -> Dict[str, Any]:
        """获取指定AI提供商的API配置"""
        
    def validate(self) -> tuple[bool, list[str]]:
        """验证配置的完整性和有效性"""
```

#### 关键特性
- 自动从.env文件加载环境变量
- 支持配置验证，防止生产环境配置错误
- 提供便捷的API配置获取接口
- 支持配置继承，开发/生产环境差异化配置

#### 测试覆盖
- ✅ 配置初始化测试
- ✅ 环境切换测试
- ✅ 数据库URI构建测试
- ✅ API配置获取测试
- ✅ 配置验证测试

### ✅ 2. 日志管理模块 (app/common/logger.py)

#### 功能特性
- **多环境支持**: debug模式详细日志，production模式监控日志
- **按日期切分**: 日志文件按天自动切分，格式为`prompt_project_log.YYYY.MM.DD`
- **错误日志分离**: ERROR级别以上日志单独存储在error目录
- **彩色控制台输出**: 开发环境支持彩色日志，便于调试
- **性能监控**: 提供函数调用和性能记录装饰器
- **异常记录**: 完整的异常堆栈记录功能

#### 设计亮点
```python
class LoggerManager:
    """日志管理器，负责创建和配置日志记录器"""
    
    def get_logger(self, name: str = 'app') -> logging.Logger:
        """获取或创建指定名称的日志器"""
    
    def log_exception(self, logger_name: str = 'app', exc_info = None):
        """记录异常信息，包含完整的堆栈跟踪"""
    
    def cleanup_old_logs(self):
        """清理过期的日志文件"""

# 装饰器支持
@log_function_call
@log_performance
def your_function():
    """支持函数调用和性能监控的装饰器"""
```

#### 关键特性
- 单例模式确保日志器唯一性
- 支持日志文件自动轮转和清理
- 开发环境彩色输出，生产环境标准格式
- 错误日志单独存储便于问题排查
- 装饰器模式简化性能监控

#### 测试覆盖
- ✅ 日志器创建和单例测试
- ✅ 多级别日志记录测试
- ✅ 日志文件创建测试
- ✅ 错误日志分离测试
- ✅ 异常记录测试
- ✅ 装饰器功能测试
- ✅ 多环境行为测试

---

## 依赖包管理 (requirements.txt)

### 核心框架
```txt
Flask==3.0.0              # Web框架
PyMySQL==1.1.0            # MySQL数据库驱动
SQLAlchemy==2.0.23        # ORM框架
python-dotenv==1.0.0      # 环境变量管理
```

### 日志和工具
```txt
colorlog==6.8.0           # 彩色日志输出
requests==2.31.0          # HTTP客户端
pytest==7.4.3            # 测试框架
```

### 生产环境
```txt
gunicorn==21.2.0          # WSGI服务器
redis==5.0.1              # 缓存支持
```

---

## 当前开发进度

### ✅ 已完成
1. **项目架构设计** - 完整的文件目录结构设计
2. **配置管理模块** - 支持多环境配置，API密钥管理
3. **日志管理模块** - 支持日期切分、错误分离、性能监控
4. **环境配置文件** - .env.template模板和依赖包配置
5. **单元测试** - config和logger模块的完整测试覆盖

### 📝 下一步计划
1. **数据库连接管理模块** - 连接池、事务管理
2. **异常处理模块** - 统一异常处理和错误响应
3. **数据库表结构设计** - 用户、Prompt、模板等表设计
4. **首页后端API实现** - Dashboard数据聚合接口
5. **首页前端模板实现** - 基于设计稿的像素级还原

---

## 技术亮点与创新

### 1. 配置管理的艺术性
- **渐进式配置**: 从.env.template到.env的无缝过渡
- **配置验证**: 防止生产环境配置错误的自动检查
- **API配置抽象**: 统一的多平台API配置管理接口

### 2. 日志系统的精巧设计
- **时间轮转**: 基于时间的自动日志切分，无需手动管理
- **层次分离**: 普通日志和错误日志的智能分离
- **开发体验**: 彩色输出和详细调试信息提升开发效率
- **装饰器模式**: 无侵入式的性能监控和函数调用跟踪

### 3. 架构设计的前瞻性
- **分层清晰**: Models-Services-Routes三层架构，职责明确
- **模块独立**: 每个模块单一职责，便于测试和维护
- **扩展友好**: 预留足够的扩展点，支持未来功能增长

---

## 开发规范和最佳实践

### 1. 代码质量
- 每个函数必须有中文注释说明
- 关键业务逻辑需要详细注释
- 对Python特殊语法进行解释（如*args, **kwargs）
- 遵循PEP 8编码规范

### 2. 测试策略
- 不使用Mock，所有测试基于真实环境
- 每个模块配套对应的单元测试
- 测试覆盖功能正确性和边界情况

### 3. 错误处理
- 统一的异常处理机制
- 详细的错误日志记录
- 优雅的错误降级策略

---

## 下次开发重点

### 即将实现的模块

#### 1. 数据库连接管理 (app/common/database.py)
- SQLAlchemy连接池配置
- 数据库连接生命周期管理
- 事务处理和回滚机制
- 连接健康检查

#### 2. 异常处理系统 (app/common/exceptions.py)
- 业务异常类定义
- HTTP状态码映射
- 统一错误响应格式
- 异常日志记录

#### 3. 数据库表结构设计 (migrations/init.sql)
- 用户表 (users)
- Prompt表 (prompts)
- 模板表 (templates)
- 工作空间表 (workspaces)
- 活动记录表 (activities)
- API配置表 (api_configs)

### 开发注意事项
1. 所有数据库表必须包含create_time和update_time字段
2. 保持当前的代码质量和注释标准
3. 每个模块完成后编写对应的单元测试
4. 遵循现有的架构设计原则

---

## 项目质量保证

### 测试验证
- ✅ 配置模块 - 所有测试通过
- ✅ 日志模块 - 所有测试通过
- ✅ 日志文件正确生成 (logs/prompt_project_log.YYYY.MM.DD)
- ✅ 错误日志正确分离 (logs/error/error.YYYY.MM.DD)

### 文件结构验证
- ✅ 项目目录结构完整创建
- ✅ 配置文件模板可用
- ✅ 依赖包清单完整
- ✅ 测试框架搭建完成

---

**日志记录时间**: 2025-08-06  
**下次更新**: 明日继续数据库相关模块开发  
**当前状态**: 基础架构完成，公共模块60%进度