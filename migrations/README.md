# Prompt管理系统数据库设计文档

## 一、设计理念

本数据库采用**最小设计原则**，仅保留核心功能所需的表和字段，避免过度设计。整体架构围绕"工作空间-用户-Prompt"的三层关系构建，支持个人使用和团队协作两种场景。

## 二、数据库表结构详解

### 1. workspaces 表 - 工作空间表

**表用途**：管理用户的工作环境，支持个人空间和协作空间，是系统的顶层组织单位。

| 字段名 | 类型 | 说明 | 设计理由 |
|--------|------|------|----------|
| `id` | BIGINT UNSIGNED | 主键，自增 | 唯一标识每个工作空间 |
| `name` | VARCHAR(100) | 空间名称 | 用于显示和识别工作空间，如"个人空间"、"产品团队空间" |
| `description` | TEXT | 空间描述 | 详细说明空间用途，便于成员了解空间定位 |
| `type` | VARCHAR(20) | 空间类型 | personal(个人)/shared(共享)，区分使用场景和权限模型 |
| `owner_id` | BIGINT UNSIGNED | 创建者ID | 标识空间所有者，拥有最高管理权限 |
| `create_time` | DATETIME | 创建时间 | 记录空间创建时间，用于审计和排序 |
| `update_time` | DATETIME | 更新时间 | 自动更新，追踪最后修改时间 |

**使用场景**：
- 用户登录后，系统查询其所属的所有工作空间
- 创建Prompt时需要指定所属工作空间
- 切换工作空间查看不同的Prompt集合

### 2. workspace_members 表 - 工作空间成员表

**表用途**：管理工作空间与用户的多对多关系，实现协作功能。

| 字段名 | 类型 | 说明 | 设计理由 |
|--------|------|------|----------|
| `id` | BIGINT UNSIGNED | 主键，自增 | 唯一标识每条成员关系 |
| `workspace_id` | BIGINT UNSIGNED | 工作空间ID | 关联到workspaces表，标识所属空间 |
| `user_id` | BIGINT UNSIGNED | 用户ID | 标识成员用户（用户表由外部系统提供） |
| `role` | VARCHAR(20) | 角色 | owner(所有者)/member(成员)，控制权限级别 |
| `join_time` | DATETIME | 加入时间 | 记录成员加入时间，用于成员管理 |

**使用场景**：
- 判断用户是否有权访问某个工作空间
- 获取工作空间的所有成员列表
- 验证用户在空间中的权限级别（owner可以管理成员和删除空间）

### 3. prompts 表 - Prompt基础信息表

**表用途**：存储Prompt的不变基础信息，内容等变化部分存储在版本表中。

| 字段名 | 类型 | 说明 | 设计理由 |
|--------|------|------|----------|
| `id` | BIGINT UNSIGNED | 主键，自增 | 内部唯一标识 |
| `uuid` | VARCHAR(36) | UUID | 外部引用标识，用于API调用和分享链接，避免暴露内部ID |
| `title` | VARCHAR(100) | 标题 | Prompt的名称，用于列表显示和搜索 |
| `description` | TEXT | 描述说明 | 详细说明Prompt用途和使用场景，帮助用户理解 |
| `category` | VARCHAR(50) | 分类 | 预定义分类(marketing/customer-service/product/code/creative/analysis)，便于筛选和统计 |
| `user_id` | BIGINT UNSIGNED | 创建者ID | 记录原始作者，用于权限判断和显示 |
| `workspace_id` | BIGINT UNSIGNED | 工作空间ID | 所属空间，决定可见性和协作范围 |
| `status` | TINYINT | 状态 | 0:删除(软删除) 1:正常，支持回收站功能 |
| `create_time` | DATETIME | 创建时间 | 记录首次创建时间，不会变更 |
| `update_time` | DATETIME | 更新时间 | 任何修改都会更新，用于排序和同步 |

**设计说明**：
- **为什么分离基础信息和版本内容**：Prompt的标题、分类等元信息相对稳定，而内容会频繁修改并需要版本管理
- **UUID的必要性**：未来做API开放或分享功能时，使用UUID比暴露自增ID更安全
- **软删除设计**：status=0表示删除，保留数据便于恢复和审计

### 4. prompt_versions 表 - Prompt版本管理表

**表用途**：存储Prompt的不同版本内容，实现版本控制功能。

| 字段名 | 类型 | 说明 | 设计理由 |
|--------|------|------|----------|
| `id` | BIGINT UNSIGNED | 主键，自增 | 版本唯一标识 |
| `prompt_id` | BIGINT UNSIGNED | Prompt ID | 关联主表，标识属于哪个Prompt |
| `version` | VARCHAR(20) | 版本号 | 如v1.0, v1.1，便于用户识别和管理 |
| `content` | TEXT | Prompt内容 | 实际的Prompt文本内容 |
| `change_log` | TEXT | 变更说明 | 记录此版本的修改内容，便于追溯 |
| `is_current` | TINYINT | 是否当前版本 | 0:否 1:是，快速定位当前使用版本 |
| `published_at` | DATETIME | 发布时间 | 记录版本发布时间，区别于创建时间 |
| `author_id` | BIGINT UNSIGNED | 版本作者ID | 记录谁创建了此版本，支持多人协作 |
| `create_time` | DATETIME | 创建时间 | 版本创建时间 |
| `update_time` | DATETIME | 更新时间 | 版本内容更新时间 |

**设计说明**：
- **is_current字段**：避免每次查询都要排序找最新版本，提高查询效率
- **版本号规则**：采用v1.0格式，主版本.次版本，便于理解
- **change_log的重要性**：团队协作时，其他成员需要了解版本间的差异

### 5. prompt_tags 表 - Prompt标签表

**表用途**：灵活的标签系统，支持用户自定义标签对Prompt进行分类。

| 字段名 | 类型 | 说明 | 设计理由 |
|--------|------|------|----------|
| `id` | BIGINT UNSIGNED | 主键，自增 | 标签关系唯一标识 |
| `prompt_id` | BIGINT UNSIGNED | Prompt ID | 关联到prompts表 |
| `tag_name` | VARCHAR(50) | 标签名称 | 标签文本，如"客户邮件"、"产品介绍" |
| `create_time` | DATETIME | 创建时间 | 记录标签添加时间 |

**设计说明**：
- **为什么不用单独的tags表**：简化设计，避免过度规范化，标签名直接存储
- **联合唯一索引**：(prompt_id, tag_name)保证同一个Prompt不会有重复标签

## 三、表关系设计

### 实体关系图

```
workspaces (1) ──────┬──── (n) workspace_members
                     │              │
                     │              │ user_id
                     │              ↓
                     │          (外部用户系统)
                     │
                     └──── (n) prompts (1) ────┬──── (n) prompt_versions
                                                │
                                                └──── (n) prompt_tags
```

### 关系说明

1. **workspaces : workspace_members = 1 : n**（一对多）
   - 一个工作空间可以有多个成员
   - 通过workspace_id关联
   - 删除工作空间时需要同时删除成员关系

2. **workspaces : prompts = 1 : n**（一对多）
   - 一个工作空间包含多个Prompt
   - 通过workspace_id关联
   - Prompt必须属于某个工作空间

3. **prompts : prompt_versions = 1 : n**（一对多）
   - 一个Prompt可以有多个版本
   - 通过prompt_id关联
   - 删除Prompt时级联删除所有版本

4. **prompts : prompt_tags = 1 : n**（一对多）
   - 一个Prompt可以有多个标签
   - 通过prompt_id关联
   - 标签与Prompt是弱关联，可独立管理

5. **用户关系**（外部系统）
   - user_id存在于多个表中（workspaces.owner_id, workspace_members.user_id, prompts.user_id, prompt_versions.author_id）
   - 假设存在外部用户系统提供用户信息
   - 本系统不维护用户基础信息表

## 四、索引设计

### 主要索引及用途

1. **workspaces表索引**
   - `idx_owner_id`：快速查询用户创建的所有空间
   - `idx_type`：按类型筛选空间

2. **workspace_members表索引**
   - `uk_workspace_user`：防止重复添加成员
   - `idx_user_id`：查询用户所属的所有空间
   - `idx_workspace_id`：查询空间的所有成员

3. **prompts表索引**
   - `uk_uuid`：UUID唯一性保证
   - `idx_user_id`：查询用户创建的Prompt
   - `idx_workspace_id`：查询空间内的所有Prompt
   - `idx_category`：按分类筛选
   - `idx_workspace_status`：复合索引，优化常用查询

4. **prompt_versions表索引**
   - `uk_prompt_version`：版本号唯一性
   - `idx_prompt_id`：查询Prompt的所有版本
   - `idx_is_current`：快速定位当前版本

5. **prompt_tags表索引**
   - `uk_prompt_tag`：防止重复标签
   - `idx_tag_name`：按标签搜索Prompt

## 五、数据完整性保证

1. **必填字段控制**：通过NOT NULL约束确保关键数据完整
2. **唯一性约束**：UUID、版本号等通过UNIQUE KEY保证唯一
3. **软删除机制**：通过status字段实现，保留历史数据
4. **时间戳自动维护**：create_time默认当前时间，update_time自动更新

## 六、扩展性考虑

1. **预留字段空间**：使用BIGINT作为ID，支持大数据量
2. **灵活的标签系统**：支持无限扩展的标签分类
3. **版本管理机制**：支持无限版本历史
4. **工作空间隔离**：天然支持多租户架构

## 七、使用建议

1. **初始化顺序**：先创建工作空间 → 添加成员 → 创建Prompt → 添加版本和标签
2. **查询优化**：利用复合索引，避免全表扫描
3. **权限判断**：始终检查用户的workspace_members记录
4. **版本管理**：修改内容时创建新版本，保留历史记录

## 八、维护说明

- 数据库初始化脚本：`init.sql`
- 执行方式：`mysql -h<host> -u<user> -p<password> < migrations/init.sql`
- 字符集：UTF8MB4，支持emoji等特殊字符
- 存储引擎：InnoDB，支持事务和外键