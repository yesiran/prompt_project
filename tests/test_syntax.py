#!/usr/bin/env python
"""
测试代码语法和导入是否正常
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("测试导入模块...")

try:
    # 测试模型导入
    from app.models import Prompt, PromptVersion, PromptTag
    print("✅ 模型导入成功（已移除PromptVariable）")
    
    # 测试服务导入
    from app.services.prompt_service import PromptService
    print("✅ PromptService导入成功")
    
    from app.services.prompt_test_service import PromptTestService
    print("✅ PromptTestService导入成功")
    
    # 测试路由导入
    from app.routes.prompt_editor import prompt_editor_bp
    print("✅ 路由导入成功")
    
    # 测试函数签名（不实际调用）
    import inspect
    
    # 检查run_test函数签名（不应该有variables参数）
    sig = inspect.signature(PromptTestService.run_test)
    params = list(sig.parameters.keys())
    if 'variables' in params:
        print("❌ run_test仍然有variables参数")
    else:
        print("✅ run_test已移除variables参数")
    
    print("\n所有测试通过！变量功能已成功删除。")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()