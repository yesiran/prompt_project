/**
 * Prompt编辑器前端逻辑
 * 处理编辑器的所有交互功能
 */

// 全局变量
let currentPromptId = null;
let currentVersionId = null;
let hasUnsavedChanges = false;
let autoSaveTimer = null;
let testRunning = false;

/**
 * 初始化Prompt编辑器
 */
function initPromptEditor(promptData, isNew) {
    currentPromptId = promptData ? promptData.id : null;
    currentVersionId = promptData && promptData.current_version ? promptData.current_version.id : null;
    
    // 设置自动保存
    setupAutoSave();
    
    // 监听内容变化
    setupChangeListeners();
    
    // 加载测试历史
    if (currentPromptId) {
        loadTestHistory();
    }
    
    // 设置快捷键
    setupKeyboardShortcuts();
}

/**
 * 设置自动保存
 */
function setupAutoSave() {
    const autoSave = () => {
        if (hasUnsavedChanges) {
            saveToAutosave();
        }
    };
    
    // 每3秒检查一次
    setInterval(() => {
        if (autoSaveTimer) {
            clearTimeout(autoSaveTimer);
        }
        autoSaveTimer = setTimeout(autoSave, 3000);
    }, 1000);
}

/**
 * 设置变化监听器
 */
function setupChangeListeners() {
    // 标题变化
    document.getElementById('promptTitle').addEventListener('input', function() {
        hasUnsavedChanges = true;
    });
    
    // 内容变化
    document.getElementById('promptContent').addEventListener('input', function() {
        hasUnsavedChanges = true;
    });
    
    // 分类变化
    document.getElementById('promptCategory').addEventListener('change', function() {
        hasUnsavedChanges = true;
    });
}


/**
 * 保存Prompt
 */
async function savePrompt() {
    const title = document.getElementById('promptTitle').value;
    const content = document.getElementById('promptContent').value;
    const category = document.getElementById('promptCategory').value;
    const tags = collectTags();
    
    if (!title) {
        showNotification('请输入Prompt标题', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const url = currentPromptId 
            ? `/prompt/api/${currentPromptId}/update`
            : '/prompt/api/create';
        
        const method = currentPromptId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title,
                content,
                category,
                tags,
                create_new_version: false
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            hasUnsavedChanges = false;
            if (!currentPromptId) {
                currentPromptId = result.prompt_id;
                currentVersionId = result.version_id;
                // 更新URL
                window.history.replaceState({}, '', `/prompt/editor/${currentPromptId}`);
            }
            showNotification('保存成功', 'success');
        } else {
            showNotification(result.error || '保存失败', 'error');
        }
    } catch (error) {
        console.error('Save error:', error);
        showNotification('保存失败', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * 运行测试
 */
async function runTest() {
    if (testRunning) return;
    
    const content = document.getElementById('promptContent').value;
    if (!content) {
        showNotification('请先编写Prompt内容', 'error');
        return;
    }
    
    
    // 获取模型配置
    const modelSelect = document.getElementById('modelProvider').value;
    const [provider, model] = modelSelect.split('/');
    const temperature = parseFloat(document.getElementById('temperatureSlider').value);
    const maxTokens = parseInt(document.getElementById('maxTokens').value);
    
    // 更新按钮状态
    const btn = document.getElementById('runTestBtn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>测试中...';
    testRunning = true;
    
    try {
        // 如果还没有保存，先保存
        if (!currentPromptId) {
            await savePrompt();
            if (!currentPromptId) {
                throw new Error('请先保存Prompt');
            }
        }
        
        const response = await fetch(`/prompt/api/${currentPromptId}/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content,
                model_provider: provider,
                model_name: model,
                parameters: {
                    temperature,
                    max_tokens: maxTokens
                }
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayTestResult(result.data);
            // 刷新测试历史
            loadTestHistory();
        } else {
            showNotification(result.error || '测试失败', 'error');
        }
    } catch (error) {
        console.error('Test error:', error);
        showNotification('测试失败: ' + error.message, 'error');
    } finally {
        testRunning = false;
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play mr-2"></i>运行测试';
    }
}

/**
 * 显示测试结果
 */
function displayTestResult(result) {
    const resultDiv = document.getElementById('testResult');
    
    resultDiv.innerHTML = `
        <div class="space-y-4">
            <div class="bg-green-50 border border-green-200 rounded p-4">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-green-800 font-medium">测试成功</span>
                    <span class="text-sm text-gray-600">${new Date().toLocaleTimeString()}</span>
                </div>
                <div class="text-sm text-gray-600 space-y-1">
                    <p>模型: ${result.model_provider} / ${result.model_name}</p>
                    <p>Token使用: ${result.total_tokens} (输入: ${result.prompt_tokens}, 输出: ${result.completion_tokens})</p>
                    <p>响应时间: ${result.response_time_ms}ms</p>
                    ${result.estimated_cost ? `<p>预估成本: $${result.estimated_cost}</p>` : ''}
                </div>
            </div>
            
            <div class="bg-gray-50 rounded p-4">
                <h4 class="font-medium mb-2">输出结果:</h4>
                <div class="whitespace-pre-wrap text-sm text-gray-700">${escapeHtml(result.output_text)}</div>
            </div>
        </div>
    `;
}

/**
 * 加载测试历史
 */
async function loadTestHistory() {
    if (!currentPromptId) return;
    
    try {
        const response = await fetch(`/prompt/api/${currentPromptId}/test-history?page=1&page_size=10`);
        const result = await response.json();
        
        if (result.success && result.history) {
            displayTestHistory(result.history);
        }
    } catch (error) {
        console.error('Load history error:', error);
    }
}

/**
 * 显示测试历史
 */
function displayTestHistory(history) {
    const historyDiv = document.getElementById('testHistory');
    
    if (!history.data || history.data.length === 0) {
        historyDiv.innerHTML = '<p class="text-gray-500">暂无测试记录</p>';
        return;
    }
    
    historyDiv.innerHTML = history.data.map(test => `
        <div class="border border-gray-200 rounded p-3 cursor-pointer hover:bg-gray-50"
             onclick="viewTestDetail(${test.id})">
            <div class="flex items-center justify-between mb-1">
                <span class="text-sm font-medium">${test.model_provider} / ${test.model_name}</span>
                <span class="text-xs text-gray-500">${formatDateTime(test.create_time)}</span>
            </div>
            <div class="text-xs text-gray-600">
                <span>Token: ${test.total_tokens}</span>
                <span class="mx-2">|</span>
                <span>响应: ${test.response_time_ms}ms</span>
                ${test.evaluation_score ? `<span class="mx-2">|</span><span>评分: ${test.evaluation_score}/5</span>` : ''}
            </div>
        </div>
    `).join('');
}

/**
 * 添加标签
 */
function addTag() {
    const input = document.getElementById('newTagInput');
    const tag = input.value.trim();
    
    if (!tag) return;
    
    // 检查重复
    const existingTags = collectTags();
    if (existingTags.includes(tag)) {
        showNotification('标签已存在', 'warning');
        return;
    }
    
    // 添加到列表
    const tagList = document.getElementById('tagList');
    const tagSpan = document.createElement('span');
    tagSpan.className = 'px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm cursor-pointer hover:bg-gray-200';
    tagSpan.onclick = () => removeTag(tag);
    tagSpan.innerHTML = `${tag} <i class="fas fa-times ml-1 text-xs"></i>`;
    
    tagList.appendChild(tagSpan);
    input.value = '';
    hasUnsavedChanges = true;
}

/**
 * 移除标签
 */
function removeTag(tag) {
    const tagList = document.getElementById('tagList');
    const tags = tagList.querySelectorAll('span');
    
    tags.forEach(span => {
        if (span.textContent.trim().startsWith(tag)) {
            span.remove();
        }
    });
    
    hasUnsavedChanges = true;
}

/**
 * 收集所有标签
 */
function collectTags() {
    const tagList = document.getElementById('tagList');
    const tags = tagList.querySelectorAll('span');
    
    return Array.from(tags).map(span => {
        const text = span.textContent.trim();
        return text.substring(0, text.lastIndexOf(' '));
    });
}

/**
 * 切换Tab
 */
function switchTab(tab) {
    const outputTab = document.getElementById('outputTab');
    const historyTab = document.getElementById('historyTab');
    const tabs = document.querySelectorAll('.border-b-2');
    
    tabs.forEach(t => {
        t.classList.remove('border-blue-600', 'text-blue-600');
        t.classList.add('border-transparent', 'text-gray-600');
    });
    
    if (tab === 'output') {
        outputTab.classList.remove('hidden');
        historyTab.classList.add('hidden');
        tabs[0].classList.add('border-blue-600', 'text-blue-600');
        tabs[0].classList.remove('border-transparent', 'text-gray-600');
    } else {
        outputTab.classList.add('hidden');
        historyTab.classList.remove('hidden');
        tabs[1].classList.add('border-blue-600', 'text-blue-600');
        tabs[1].classList.remove('border-transparent', 'text-gray-600');
    }
}

/**
 * 保存到自动保存
 */
async function saveToAutosave() {
    const data = {
        prompt_id: currentPromptId,
        title: document.getElementById('promptTitle').value,
        content: document.getElementById('promptContent').value,
        metadata: {
            category: document.getElementById('promptCategory').value,
            tags: collectTags()
        },
        variables: extractedVariables
    };
    
    try {
        await fetch('/prompt/api/autosave', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
    } catch (error) {
        console.error('Autosave error:', error);
    }
}

/**
 * 设置键盘快捷键
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Cmd/Ctrl + S: 保存
        if ((e.metaKey || e.ctrlKey) && e.key === 's') {
            e.preventDefault();
            savePrompt();
        }
        
        // Cmd/Ctrl + Enter: 运行测试
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            e.preventDefault();
            runTest();
        }
    });
}

/**
 * 显示加载提示
 */
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

/**
 * 显示通知
 */
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-4 px-4 py-3 rounded shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'warning' ? 'bg-yellow-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // 3秒后自动消失
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

/**
 * 转义HTML
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * 格式化日期时间
 */
function formatDateTime(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN');
}

/**
 * 显示版本历史
 */
function showVersionHistory() {
    // TODO: 实现版本历史弹窗
    showNotification('版本历史功能开发中...', 'info');
}

/**
 * 分享Prompt
 */
function sharePrompt() {
    // TODO: 实现分享功能
    showNotification('分享功能开发中...', 'info');
}

/**
 * 查看测试详情
 */
function viewTestDetail(testId) {
    // TODO: 实现测试详情弹窗
    showNotification('测试详情功能开发中...', 'info');
}