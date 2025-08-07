-- ====================================
-- Prompt管理系统数据库初始化脚本
-- 作者: Claude  
-- 创建时间: 2025-08-07
-- 说明: 创建数据库表和初始数据
-- 使用方法: mysql -h<host> -u<user> -p<password> < migrations/init.sql
-- ====================================

CREATE DATABASE IF NOT EXISTS `prompt_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE prompt_db;

-- ====================================
-- 1. workspaces 表 - 工作空间表
-- ====================================
CREATE TABLE IF NOT EXISTS `workspaces` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '工作空间ID',
    `name` VARCHAR(100) NOT NULL COMMENT '空间名称',
    `description` TEXT COMMENT '空间描述',
    `type` VARCHAR(20) DEFAULT 'personal' COMMENT '空间类型（personal/shared）',
    `owner_id` BIGINT UNSIGNED NOT NULL COMMENT '创建者ID',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_owner_id` (`owner_id`),
    KEY `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工作空间表';

-- ====================================
-- 2. workspace_members 表 - 工作空间成员表
-- ====================================
CREATE TABLE IF NOT EXISTS `workspace_members` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '成员关系ID',
    `workspace_id` BIGINT UNSIGNED NOT NULL COMMENT '工作空间ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `role` VARCHAR(20) DEFAULT 'member' COMMENT '角色（owner/member）',
    `join_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_workspace_user` (`workspace_id`, `user_id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_workspace_id` (`workspace_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工作空间成员表';

-- ====================================
-- 3. prompts 表 - Prompt基础信息表
-- ====================================
CREATE TABLE IF NOT EXISTS `prompts` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'Prompt唯一标识',
    `uuid` VARCHAR(36) NOT NULL COMMENT 'UUID，用于外部引用',
    `title` VARCHAR(100) NOT NULL COMMENT 'Prompt标题',
    `description` TEXT COMMENT 'Prompt描述说明',
    `category` VARCHAR(50) DEFAULT 'general' COMMENT '分类（marketing/customer-service/product/code/creative/analysis）',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '创建用户ID',
    `workspace_id` BIGINT UNSIGNED NOT NULL COMMENT '所属工作空间ID',
    `status` TINYINT DEFAULT 1 COMMENT '状态（0:删除 1:正常）',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_uuid` (`uuid`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_workspace_id` (`workspace_id`),
    KEY `idx_category` (`category`),
    KEY `idx_status` (`status`),
    KEY `idx_create_time` (`create_time`),
    KEY `idx_workspace_status` (`workspace_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt基础信息表';

-- ====================================
-- 4. prompt_versions 表 - Prompt版本管理表
-- ====================================
CREATE TABLE IF NOT EXISTS `prompt_versions` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '版本ID',
    `prompt_id` BIGINT UNSIGNED NOT NULL COMMENT 'Prompt ID',
    `version` VARCHAR(20) NOT NULL COMMENT '版本号（如：v1.0, v1.1）',
    `content` TEXT NOT NULL COMMENT 'Prompt内容',
    `change_log` TEXT COMMENT '版本变更说明',
    `is_current` TINYINT DEFAULT 0 COMMENT '是否为当前版本（0:否 1:是）',
    `published_at` DATETIME DEFAULT NULL COMMENT '发布时间',
    `author_id` BIGINT UNSIGNED NOT NULL COMMENT '版本作者ID',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_prompt_version` (`prompt_id`, `version`),
    KEY `idx_prompt_id` (`prompt_id`),
    KEY `idx_is_current` (`is_current`),
    KEY `idx_author_id` (`author_id`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt版本管理表';

-- ====================================
-- 5. prompt_tags 表 - Prompt标签表
-- ====================================
CREATE TABLE IF NOT EXISTS `prompt_tags` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '标签ID',
    `prompt_id` BIGINT UNSIGNED NOT NULL COMMENT 'Prompt ID',
    `tag_name` VARCHAR(50) NOT NULL COMMENT '标签名称',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_prompt_tag` (`prompt_id`, `tag_name`),
    KEY `idx_prompt_id` (`prompt_id`),
    KEY `idx_tag_name` (`tag_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Prompt标签表';

-- ====================================
-- 创建索引优化查询性能
-- ====================================
CREATE INDEX idx_prompt_user_status ON prompts(user_id, status);
CREATE INDEX idx_version_prompt_current ON prompt_versions(prompt_id, is_current);

-- ====================================
-- 插入初始数据
-- ====================================

-- 创建默认工作空间
INSERT INTO `workspaces` (`id`, `name`, `description`, `type`, `owner_id`) VALUES
(1, '个人工作空间', '默认个人工作空间', 'personal', 1),
(2, '家庭协作空间', '家庭成员共享的协作空间', 'shared', 1)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 添加工作空间成员
INSERT INTO `workspace_members` (`workspace_id`, `user_id`, `role`) VALUES
(1, 1, 'owner'),  -- user1 是个人空间的所有者
(2, 1, 'owner'),  -- user1 是协作空间的所有者
(2, 2, 'member')  -- user2 是协作空间的成员
ON DUPLICATE KEY UPDATE role=VALUES(role);