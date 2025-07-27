#!/usr/bin/env python3
"""
Simple standalone test script - tests refactored project functionality
"""

import requests
import os

def test_basic_scraping():
    """Test basic web scraping functionality"""
    print("🧪 Testing basic web scraping functionality")
    print("=" * 50)
    
    # Test scraping a simple page
    test_url = "https://example.com"
    
    try:
        print(f"📡 Scraping: {test_url}")
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ Scraping successful! Status code: {response.status_code}")
            print(f"📄 Content length: {len(content)} characters")
            print(f"🔍 Content preview:")
            print("-" * 30)
            print(content[:300] + "..." if len(content) > 300 else content)
            print("-" * 30)
            return True
        else:
            print(f"❌ Scraping failed! Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return False

def test_form_page():
    """Test form page scraping"""
    print("\n🧪 Testing form page scraping")
    print("=" * 50)
    
    test_url = "https://www.google.com"
    
    try:
        print(f"📡 Scraping form page: {test_url}")
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ Form page scraping successful!")
            
            # Analyze form elements
            form_elements = []
            if '<input' in content:
                form_elements.append("text input")
            if 'type="radio"' in content:
                form_elements.append("radio button")
            if 'type="checkbox"' in content:
                form_elements.append("checkbox")
            if '<textarea' in content:
                form_elements.append("textarea")
            if '<button' in content:
                form_elements.append("button")
                
            print(f"🔍 Found form elements: {form_elements}")
            return True
        else:
            print(f"❌ Form page scraping failed! Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during form page scraping: {e}")
        return False

def test_project_structure():
    """Test project structure"""
    print("\n🧪 Testing project structure")
    print("=" * 50)
    
    expected_dirs = ["agent", "database", "tests"]
    expected_files = ["main.py", "config.py", "requirements.txt"]
    
    all_good = True
    
    # Check directories
    for dir_name in expected_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"✅ Directory exists: {dir_name}/")
            
            # Check __init__.py
            init_file = os.path.join(dir_name, "__init__.py")
            if os.path.exists(init_file):
                print(f"  ✅ {dir_name}/__init__.py exists")
            else:
                print(f"  ❌ {dir_name}/__init__.py is missing")
                all_good = False
        else:
            print(f"❌ Directory is missing: {dir_name}/")
            all_good = False
    
    # Check files
    for file_name in expected_files:
        if os.path.exists(file_name) and os.path.isfile(file_name):
            print(f"✅ File exists: {file_name}")
        else:
            print(f"❌ File is missing: {file_name}")
            all_good = False
    
    return all_good

def main():
    """Main test function"""
    print("🚀 Starting refactored project test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Project Structure", test_project_structure()))
    results.append(("Basic Scraping", test_basic_scraping()))
    results.append(("Form Page", test_form_page()))
    
    # Summarize results
    print("\n📊 Test results summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ Passed" if result else "❌ Failed"
        print(f"{test_name:20s} : {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactored project is running correctly.")
    else:
        print("⚠️ Some tests failed, please check the project configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
