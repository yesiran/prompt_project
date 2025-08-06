/**
 * 主应用JavaScript文件
 * 作者: Claude
 * 创建时间: 2025-08-06
 * 功能: 提供全局的JavaScript功能，包括导航交互、搜索功能等
 */

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * 初始化应用
 * 设置全局事件监听器和初始化功能
 */
function initializeApp() {
    // 初始化侧边栏导航
    initializeSidebar();
    
    // 初始化搜索功能
    initializeSearch();
    
    // 初始化用户菜单
    initializeUserMenu();
    
    // 初始化通知功能
    initializeNotifications();
}

/**
 * 初始化侧边栏导航
 * 处理导航项的点击和高亮状态
 */
function initializeSidebar() {
    const navItems = document.querySelectorAll('.nav-item');
    
    // 为每个导航项添加点击事件
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // 如果是当前页面的链接，阻止默认行为
            if (this.classList.contains('active')) {
                e.preventDefault();
                return;
            }
            
            // 移除所有active类
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // 添加active类到当前项
            this.classList.add('active');
        });
    });
    
    // 新建Prompt按钮点击事件
    const newPromptBtn = document.querySelector('.btn-new-prompt');
    if (newPromptBtn) {
        newPromptBtn.addEventListener('click', function() {
            // TODO: 打开新建Prompt对话框或跳转到编辑器
            console.log('新建Prompt按钮被点击');
        });
    }
}

/**
 * 初始化搜索功能
 * 处理搜索框的输入和搜索逻辑
 */
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    if (!searchInput) return;
    
    let searchTimeout;
    
    // 监听搜索输入
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        
        // 清除之前的定时器
        clearTimeout(searchTimeout);
        
        // 延迟搜索，避免频繁请求
        searchTimeout = setTimeout(() => {
            if (query.length >= 2) {
                performSearch(query);
            }
        }, 300);
    });
    
    // 监听回车键
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = e.target.value.trim();
            if (query) {
                performSearch(query);
            }
        }
    });
}

/**
 * 执行搜索
 * @param {string} query - 搜索关键词
 */
function performSearch(query) {
    console.log('执行搜索:', query);
    // TODO: 实现搜索API调用
    // 这里可以调用后端API进行搜索
}

/**
 * 初始化用户菜单
 * 处理用户头像点击和下拉菜单
 */
function initializeUserMenu() {
    const userAvatar = document.querySelector('.user-avatar');
    if (!userAvatar) return;
    
    userAvatar.addEventListener('click', function(e) {
        e.stopPropagation();
        // TODO: 显示用户下拉菜单
        console.log('用户头像被点击');
    });
    
    // 点击页面其他地方关闭菜单
    document.addEventListener('click', function() {
        // TODO: 关闭用户菜单
    });
}

/**
 * 初始化通知功能
 * 处理通知图标点击和通知显示
 */
function initializeNotifications() {
    const notificationBtns = document.querySelectorAll('.header-icon-btn');
    
    notificationBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            // TODO: 显示通知或设置面板
            console.log('图标按钮被点击');
        });
    });
}

/**
 * 工具函数：格式化时间
 * @param {Date} date - 日期对象
 * @returns {string} 格式化后的时间字符串
 */
function formatTime(date) {
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 7) {
        return date.toLocaleDateString('zh-CN');
    } else if (days > 0) {
        return `${days}天前`;
    } else if (hours > 0) {
        return `${hours}小时前`;
    } else if (minutes > 0) {
        return `${minutes}分钟前`;
    } else {
        return '刚刚';
    }
}

/**
 * 工具函数：显示提示消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    // TODO: 实现toast提示功能
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// 导出全局函数供其他模块使用
window.AppUtils = {
    formatTime,
    showToast,
    performSearch
};