#!/usr/bin/env python
"""
测试字数统计功能删除后系统是否正常
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.prompt import PromptVersion

def test_prompt_version_model():
    """测试PromptVersion模型不再有字数统计字段"""
    print("测试PromptVersion模型...")
    
    version = PromptVersion()
    version.content = "这是测试内容"
    
    # 检查是否还有字数统计属性
    has_char_count = hasattr(version, 'character_count')
    has_word_count = hasattr(version, 'word_count')
    has_token_count = hasattr(version, 'estimated_tokens')
    
    if has_char_count or has_word_count or has_token_count:
        print("❌ 模型仍有字数统计字段")
        if has_char_count:
            print("  - character_count 仍存在")
        if has_word_count:
            print("  - word_count 仍存在")
        if has_token_count:
            print("  - estimated_tokens 仍存在")
    else:
        print("✅ 字数统计字段已成功删除")
    
    # 检查是否还有calculate_metrics方法
    has_calc_method = hasattr(version, 'calculate_metrics')
    if has_calc_method:
        print("❌ calculate_metrics方法仍存在")
    else:
        print("✅ calculate_metrics方法已删除")

if __name__ == "__main__":
    print("=" * 50)
    print("测试字数统计功能删除")
    print("=" * 50)
    test_prompt_version_model()
    print("\n测试完成！")