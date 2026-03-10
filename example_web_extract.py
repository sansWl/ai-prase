"""
网页内容提取使用示例
展示如何使用 LLMUtils 工具类从网站提取信息
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from utils.llm_prompt.llm_utils import (
    WebContentExtractor,
    LLMUtils,
    LLMBuilder,
    fetch_webpage,
    extract_job_info
)


def example_1_basic_extraction():
    """示例1: 基本网页内容提取"""
    print("=" * 60)
    print("示例1: 基本网页内容提取")
    print("=" * 60)
    
    url = "https://www.zhipin.com/web/geek/jobs?query=&city=101220100&position=100101"
    
    # 使用 WebContentExtractor 直接提取
    extractor = WebContentExtractor()
    result = extractor.extract(url)
    
    print(f"URL: {result['url']}")
    print(f"域名: {result['domain']}")
    print(f"提取的数据项: {list(result.get('extracted_data', {}).keys())}")
    
    # 显示提取的职位标题（前5个）
    titles = result.get('extracted_data', {}).get('title', [])
    print(f"\n提取的职位标题数量: {len(titles)}")
    if titles:
        print(f"前5个职位标题:")
        for i, title in enumerate(titles[:5], 1):
            print(f"  {i}. {title}")
    else:
        print("  (注: BOSS直聘网站使用JavaScript动态加载内容，需要特殊处理)")


def example_2_llm_utils_extraction():
    """示例2: 使用 LLMUtils 提取信息"""
    print("\n" + "=" * 60)
    print("示例2: 使用 LLMUtils 提取信息")
    print("=" * 60)
    
    url = "https://www.zhipin.com/web/geek/jobs?query=&city=101220100&position=100101"
    
    # 创建 LLMUtils 实例
    llm_utils = LLMUtils()
    
    # 提取网页信息
    result = llm_utils.extract_webpage_info(url)
    
    print(f"URL: {result['url']}")
    print(f"域名: {result['domain']}")
    
    # 显示提取的数据
    data = result.get('extracted_data', {})
    print(f"\n提取的数据概览:")
    for key, values in data.items():
        print(f"  {key}: {len(values)} 条数据")


def example_3_tool_invocation():
    """示例3: 使用工具函数"""
    print("\n" + "=" * 60)
    print("示例3: 使用工具函数")
    print("=" * 60)
    
    url = "https://www.zhipin.com/web/geek/jobs?query=&city=101220100&position=100101"
    
    # 使用工具函数提取职位信息
    print(f"正在从 {url} 提取职位信息...")
    
    try:
        # 工具函数需要通过 invoke 方法调用
        result = extract_job_info.invoke({'url': url})
        
        print(f"\n成功提取 {len(result)} 个职位信息")
        
        # 显示前3个职位
        if result and 'error' not in result[0]:
            for i, job in enumerate(result[:3], 1):
                print(f"\n  职位 {i}:")
                print(f"    标题: {job.get('title', 'N/A')}")
                print(f"    薪资: {job.get('salary', 'N/A')}")
                print(f"    公司: {job.get('company', 'N/A')}")
                print(f"    地点: {job.get('location', 'N/A')}")
        else:
            print("  (注: 该网站使用JavaScript动态加载，静态抓取无法获取内容)")
            
    except Exception as e:
        print(f"提取失败: {e}")


def example_4_builder_pattern():
    """示例4: 使用构建器模式创建 LLMUtils"""
    print("\n" + "=" * 60)
    print("示例4: 使用构建器模式创建 LLMUtils")
    print("=" * 60)
    
    # 使用 LLMBuilder 构建 LLMUtils（不初始化LLM，只配置工具）
    builder = LLMBuilder()
    builder.set_llm_type('openai')
    builder.set_llm_react(False)
    builder.add_tool(fetch_webpage)
    builder.add_tool(extract_job_info)
    
    print("成功配置 LLMUtils 构建器")
    print(f"  - LLM类型: openai")
    print(f"  - ReAct模式: False")
    print(f"  - 工具数量: {len(builder._tools)}")
    
    # 使用提取功能（不依赖LLM）
    url = "https://www.zhipin.com/web/geek/jobs?query=&city=101220100&position=100101"
    llm_utils = LLMUtils()
    result = llm_utils.extract_webpage_info(url)
    
    print(f"\n从 {result['domain']} 提取信息成功")


def example_5_domain_isolation():
    """示例5: 域名隔离功能"""
    print("\n" + "=" * 60)
    print("示例5: 域名隔离功能")
    print("=" * 60)
    
    # 不同域名的URL
    urls = [
        "https://www.zhipin.com/web/geek/jobs",
        "https://www.lagou.com/jobs/list_Java",
        "https://example.com/jobs",
        "https://www.51job.com"
    ]
    
    print("不同域名的提取规则:")
    for url in urls:
        rules = WebContentExtractor.get_domain_rules(url)
        print(f"  {url:40s} -> {rules['name']}")


def example_6_custom_extraction():
    """示例6: 自定义提取特定区域"""
    print("\n" + "=" * 60)
    print("示例6: 自定义提取特定区域")
    print("=" * 60)
    
    url = "https://www.zhipin.com/web/geek/jobs?query=&city=101220100&position=100101"
    
    # 只提取职位标题
    extractor = WebContentExtractor()
    result = extractor.extract(url, target_region='title')
    
    print(f"只提取职位标题区域:")
    titles = result.get('extracted_data', {}).get('title', [])
    print(f"  共提取 {len(titles)} 个标题")
    if titles:
        for i, title in enumerate(titles[:5], 1):
            print(f"  {i}. {title}")


def example_7_static_website():
    """示例7: 从静态网站提取内容"""
    print("\n" + "=" * 60)
    print("示例7: 从静态网站提取内容")
    print("=" * 60)
    
    # 使用一个静态网站示例
    url = "https://httpbin.org/html"
    
    print(f"从 {url} 提取内容...")
    
    try:
        # 使用 fetch_webpage 工具
        html = fetch_webpage.invoke({'url': url})
        
        if not html.startswith("获取网页失败"):
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取标题
            title = soup.find('title')
            print(f"  页面标题: {title.get_text() if title else 'N/A'}")
            
            # 提取正文
            body = soup.find('body')
            if body:
                text = body.get_text(strip=True)
                print(f"  正文内容: {text[:200]}...")
        else:
            print(f"  错误: {html}")
            
    except Exception as e:
        print(f"  提取失败: {e}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("LLMUtils 网页内容提取示例")
    print("=" * 60)
    
    try:
        # 运行所有示例
        example_1_basic_extraction()
        example_2_llm_utils_extraction()
        example_3_tool_invocation()
        example_4_builder_pattern()
        example_5_domain_isolation()
        example_6_custom_extraction()
        example_7_static_website()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
