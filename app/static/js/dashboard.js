/**
 * 首页JavaScript文件
 * 作者: Claude
 * 创建时间: 2025-08-06
 * 功能: 处理首页的所有交互逻辑，包括动态问候、模板点击、API状态检查等
 */

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

/**
 * 初始化首页
 * 设置所有首页相关的功能和事件监听器
 */
function initializeDashboard() {
    // 更新问候语
    updateGreeting();
    
    // 初始化快速模板
    initializeTemplates();
    
    // 初始化最近使用的Prompts
    initializeRecentPrompts();
    
    // 初始化协作动态
    initializeActivityFeed();
    
    // 初始化API状态
    initializeApiStatus();
    
    // 设置定时刷新
    setupAutoRefresh();
}

/**
 * 更新问候语
 * 根据当前时间显示不同的问候语
 */
function updateGreeting() {
    const greetingElement = document.getElementById('greeting');
    if (!greetingElement) return;
    
    const hour = new Date().getHours();
    let greeting = '早上好！';
    
    if (hour >= 5 && hour < 12) {
        greeting = '早上好！';
    } else if (hour >= 12 && hour < 18) {
        greeting = '下午好！';
    } else if (hour >= 18 && hour < 22) {
        greeting = '晚上好！';
    } else {
        greeting = '夜深了，注意休息！';
    }
    
    greetingElement.textContent = greeting;
}

/**
 * 初始化快速模板
 * 为模板卡片添加点击事件
 */
function initializeTemplates() {
    const templateCards = document.querySelectorAll('.template-card');
    
    templateCards.forEach(card => {
        card.addEventListener('click', function() {
            const templateType = this.dataset.template;
            handleTemplateClick(templateType);
        });
        
        // 添加键盘支持
        card.setAttribute('tabindex', '0');
        card.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const templateType = this.dataset.template;
                handleTemplateClick(templateType);
            }
        });
    });
}

/**
 * 处理模板点击
 * @param {string} templateType - 模板类型
 */
function handleTemplateClick(templateType) {
    console.log('模板被点击:', templateType);
    
    // 模板配置
    const templates = {
        conversation: {
            title: '对话助手模板',
            content: '你是一个专业的客服助手。请根据用户的问题，提供友好、准确的回答。\n\n用户问题：{{user_question}}\n\n回答要求：\n1. 态度友好、专业\n2. 回答准确、详细\n3. 必要时提供相关建议'
        },
        content: {
            title: '内容创作模板',
            content: '请为{{topic}}撰写一篇{{word_count}}字左右的文章。\n\n要求：\n1. 标题吸引人\n2. 结构清晰\n3. 内容原创\n4. SEO友好'
        },
        code: {
            title: '代码助手模板',
            content: '请帮我{{task_type}}以下代码：\n\n```{{language}}\n{{code}}\n```\n\n要求：\n1. 保持代码风格一致\n2. 添加必要的注释\n3. 优化性能'
        },
        ecommerce: {
            title: '电商运营模板',
            content: '为{{product_name}}撰写商品详情页文案。\n\n产品特点：{{features}}\n\n要求：\n1. 突出卖点\n2. 打动目标客户\n3. 包含行动号召'
        }
    };
    
    const template = templates[templateType];
    if (template) {
        // TODO: 跳转到编辑器并预填充模板
        window.AppUtils.showToast(`正在加载${template.title}...`, 'info');
    }
}

/**
 * 初始化最近使用的Prompts
 * 为Prompt卡片添加交互事件
 */
function initializeRecentPrompts() {
    const promptCards = document.querySelectorAll('.prompt-card');
    
    promptCards.forEach(card => {
        // 卡片点击事件
        card.addEventListener('click', function(e) {
            // 如果点击的是测试按钮，不触发卡片点击
            if (e.target.classList.contains('btn-test')) {
                return;
            }
            
            const promptId = this.dataset.promptId;
            handlePromptClick(promptId);
        });
        
        // 测试按钮点击事件
        const testBtn = card.querySelector('.btn-test');
        if (testBtn) {
            testBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                const promptId = card.dataset.promptId;
                handleTestPrompt(promptId);
            });
        }
    });
}

/**
 * 处理Prompt卡片点击
 * @param {string} promptId - Prompt ID
 */
function handlePromptClick(promptId) {
    console.log('Prompt被点击:', promptId);
    // TODO: 跳转到编辑器并加载该Prompt
    window.AppUtils.showToast('正在加载Prompt...', 'info');
}

/**
 * 处理测试Prompt
 * @param {string} promptId - Prompt ID
 */
function handleTestPrompt(promptId) {
    console.log('测试Prompt:', promptId);
    // TODO: 打开测试对话框或跳转到测试页面
    window.AppUtils.showToast('正在打开测试界面...', 'info');
}

/**
 * 初始化协作动态
 * 设置动态列表的交互
 */
function initializeActivityFeed() {
    // 模拟加载更多动态
    const activitySection = document.querySelector('.activity-section');
    if (!activitySection) return;
    
    // 可以添加加载更多按钮或无限滚动
    console.log('协作动态已初始化');
}

/**
 * 初始化API状态
 * 检查和显示API连接状态
 */
function initializeApiStatus() {
    checkApiStatus();
    
    // 为API状态项添加点击事件
    const apiStatusItems = document.querySelectorAll('.api-status-item');
    apiStatusItems.forEach(item => {
        item.addEventListener('click', function() {
            const apiName = this.querySelector('.api-name').textContent;
            handleApiStatusClick(apiName);
        });
    });
}

/**
 * 检查API状态
 * 向后端请求各API的连接状态
 */
async function checkApiStatus() {
    try {
        // TODO: 实际调用后端API
        // const response = await fetch('/api/integrations/status');
        // const data = await response.json();
        
        // 模拟API状态数据
        const mockStatus = {
            'OpenAI GPT-4': { connected: true, responseTime: 120 },
            'Claude 3': { connected: true, responseTime: 95 },
            '文心一言': { connected: false, error: 'API密钥未配置' }
        };
        
        updateApiStatusDisplay(mockStatus);
    } catch (error) {
        console.error('检查API状态失败:', error);
    }
}

/**
 * 更新API状态显示
 * @param {Object} statusData - API状态数据
 */
function updateApiStatusDisplay(statusData) {
    Object.entries(statusData).forEach(([apiName, status]) => {
        const apiItem = Array.from(document.querySelectorAll('.api-status-item'))
            .find(item => item.querySelector('.api-name').textContent === apiName);
        
        if (apiItem) {
            const statusDot = apiItem.querySelector('.status-dot');
            const statusBadge = apiItem.querySelector('.status-badge');
            
            if (status.connected) {
                statusDot.className = 'status-dot status-green';
                statusBadge.className = 'status-badge status-connected';
                statusBadge.textContent = '已连接';
            } else {
                statusDot.className = 'status-dot status-red';
                statusBadge.className = 'status-badge status-disconnected';
                statusBadge.textContent = '未连接';
            }
        }
    });
}

/**
 * 处理API状态点击
 * @param {string} apiName - API名称
 */
function handleApiStatusClick(apiName) {
    console.log('API状态被点击:', apiName);
    // TODO: 打开API配置对话框
    window.AppUtils.showToast(`打开${apiName}配置...`, 'info');
}

/**
 * 设置自动刷新
 * 定时刷新动态数据
 */
function setupAutoRefresh() {
    // 每分钟更新时间显示
    setInterval(() => {
        updateTimeDisplays();
    }, 60000);
    
    // 每5分钟检查API状态
    setInterval(() => {
        checkApiStatus();
    }, 300000);
}

/**
 * 更新时间显示
 * 更新所有相对时间显示
 */
function updateTimeDisplays() {
    const timeElements = document.querySelectorAll('.prompt-time span, .activity-time');
    
    timeElements.forEach(element => {
        // 这里需要根据实际的时间戳更新显示
        // 暂时跳过，因为现在是静态数据
    });
}

/**
 * 加载首页数据
 * 从后端获取首页所需的所有数据
 */
async function loadDashboardData() {
    try {
        // TODO: 实际调用后端API
        // const response = await fetch('/api/dashboard/data');
        // const data = await response.json();
        
        console.log('加载首页数据...');
        
        // 更新页面显示
        // updateDashboardDisplay(data);
    } catch (error) {
        console.error('加载首页数据失败:', error);
        window.AppUtils.showToast('加载数据失败，请刷新页面重试', 'error');
    }
}

// 页面加载时获取数据
window.addEventListener('load', function() {
    // 延迟加载数据，避免阻塞首屏渲染
    setTimeout(() => {
        loadDashboardData();
    }, 100);
});