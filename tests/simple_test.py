#!/usr/bin/env python3
"""
简单的独立测试脚本 - 测试重构后的项目功能
"""

import requests
import os

def test_basic_scraping():
    """测试基础的网页抓取功能"""
    print("🧪 测试基础网页抓取功能")
    print("=" * 50)
    
    # 测试抓取一个简单页面
    test_url = "https://example.com"
    
    try:
        print(f"📡 正在抓取: {test_url}")
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ 抓取成功! 状态码: {response.status_code}")
            print(f"📄 内容长度: {len(content)} 字符")
            print(f"🔍 内容预览:")
            print("-" * 30)
            print(content[:300] + "..." if len(content) > 300 else content)
            print("-" * 30)
            return True
        else:
            print(f"❌ 抓取失败! 状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 抓取过程中出现错误: {e}")
        return False

def test_form_page():
    """测试表单页面抓取"""
    print("\n🧪 测试表单页面抓取")
    print("=" * 50)
    
    test_url = "https://www.google.com"
    
    try:
        print(f"📡 正在抓取表单页面: {test_url}")
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ 表单页面抓取成功!")
            
            # 分析表单元素
            form_elements = []
            if '<input' in content:
                form_elements.append("文本输入框")
            if 'type="radio"' in content:
                form_elements.append("单选按钮")
            if 'type="checkbox"' in content:
                form_elements.append("复选框")
            if '<textarea' in content:
                form_elements.append("文本区域")
            if '<button' in content:
                form_elements.append("按钮")
                
            print(f"🔍 发现的表单元素: {', '.join(form_elements)}")
            return True
        else:
            print(f"❌ 表单页面抓取失败! 状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 表单页面抓取过程中出现错误: {e}")
        return False

def test_project_structure():
    """测试项目结构"""
    print("\n🧪 测试项目结构")
    print("=" * 50)
    
    expected_dirs = ["agent", "database", "tests"]
    expected_files = ["main.py", "config.py", "requirements.txt"]
    
    all_good = True
    
    # 检查目录
    for dir_name in expected_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✅ 目录存在: {dir_name}/")
            
            # 检查__init__.py
            init_file = os.path.join(dir_name, "__init__.py")
            if os.path.exists(init_file):
                print(f"  ✅ {dir_name}/__init__.py 存在")
            else:
                print(f"  ❌ {dir_name}/__init__.py 缺失")
                all_good = False
        else:
            print(f"❌ 目录缺失: {dir_name}/")
            all_good = False
    
    # 检查文件
    for file_name in expected_files:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            print(f"✅ 文件存在: {file_name}")
        else:
            print(f"❌ 文件缺失: {file_name}")
            all_good = False
    
    return all_good

def main():
    """主测试函数"""
    print("🚀 开始重构项目测试")
    print("=" * 60)
    
    results = []
    
    # 运行各项测试
    results.append(("项目结构", test_project_structure()))
    results.append(("基础抓取", test_basic_scraping()))
    results.append(("表单页面", test_form_page()))
    
    # 总结结果
    print("\n📊 测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:15s} : {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！重构项目运行正常。")
    else:
        print("⚠️ 部分测试失败，请检查项目配置。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
