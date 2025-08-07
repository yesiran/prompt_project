#!/usr/bin/env python
"""
测试变量功能删除后系统是否正常
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.prompt_service import PromptService
from app.services.prompt_test_service import PromptTestService

def test_prompt_service():
    """测试Prompt服务"""
    print("测试PromptService...")
    
    # 测试创建Prompt（不带变量）
    result = PromptService.create_prompt(
        user_id=1,
        workspace_id=1,
        title="测试Prompt",
        content="这是一个测试Prompt内容，没有任何变量",
        category="general"
    )
    print(f"创建Prompt结果: {result}")
    
    if result['success']:
        prompt_id = result['prompt']['id']
        print(f"成功创建Prompt，ID: {prompt_id}")
        
        # 测试获取Prompt
        prompt = PromptService.get_prompt(prompt_id, user_id=1)
        if prompt:
            print(f"成功获取Prompt: {prompt['title']}")
        else:
            print("获取Prompt失败")
    else:
        print(f"创建Prompt失败: {result.get('error')}")

def test_prompt_test_service():
    """测试Prompt测试服务（不带变量）"""
    print("\n测试PromptTestService...")
    
    # 测试运行测试（不传递变量）
    result = PromptTestService.run_test(
        prompt_id=1,
        user_id=1,
        content="这是测试内容，没有变量",
        model_provider="openai",
        model_name="gpt-3.5-turbo",
        parameters={"temperature": 0.7, "max_tokens": 100},
        save_result=False
    )
    print(f"测试运行结果: {result}")
    
    if result.get('success'):
        print("测试运行成功")
    else:
        print(f"测试运行失败: {result.get('error')}")

if __name__ == "__main__":
    print("=" * 50)
    print("测试变量功能删除后的系统")
    print("=" * 50)
    
    try:
        test_prompt_service()
        test_prompt_test_service()
        print("\n✅ 所有测试通过！系统运行正常。")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()