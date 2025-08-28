from typing import List
import re
from urllib.parse import urlparse

#文本去重
def deduplicate_text(textList: List[str]) -> List[str]:
    return list(dict.fromkeys(textList))

# 检查两个链接的一级域名是否相同
def check_main_domain(crawl_url: str, check_url: str) -> bool|str:
    if not check_url:
        return False
    # 如果url2是以/开头的相对路径，直接返回True
    if check_url.startswith('/'):
        #提取crawl_url的域名和协议
        domain = urlparse(crawl_url).scheme + "://" + urlparse(crawl_url).hostname
        return domain + check_url
    # 如果url2是mailto协议，返回False
    if check_url.startswith("mailto:"):
        return False
    domain1 = urlparse(crawl_url).hostname.split('.')[-2:]
    hostname2 = urlparse(check_url).hostname
    if hostname2 is None:
        return False
    domain2 = hostname2.split('.')[-2:]
    return check_url if domain1 == domain2 else False

def remove_html_tags(text: str) -> str:
    """
    去掉HTML标签以及标签内的文字，只保留标签外的纯文本内容
    
    Args:
        text: 包含HTML标签的文本
        
    Returns:
        去掉所有HTML标签和标签内文字后的纯文本
    """
    if not text:
        return text
    
    # 使用正则表达式去掉所有HTML标签及其内容
    # 这个正则表达式会匹配：
    # 1. <tag>content</tag> - 开始标签、内容和结束标签
    # 2. <tag/> - 自闭合标签
    # 3. <tag> - 单独的标签（没有结束标签的情况）
    # 4. 标签内的属性
    # 5. 标签内的所有文字内容
    clean_text = re.sub(r'<[^>]*>.*?</[^>]*>|<[^>]*/>|<[^>]*>', '', text)
    
    # 去掉多余的空白字符
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    return clean_text.strip()

if __name__ == "__main__":
    # print(check_main_domain("https://cerlo.com//", "https://x.com/CerLo_team"))
    
    # 测试HTML标签去除功能
    test_html = '<span class=" text-[#4B6EFF]">CerLo:</span>AI 助力社媒营销'
    print("原始HTML:")
    print(test_html)
    print("\n清理后的文本:")
    print(remove_html_tags(test_html))
    
    # 更多测试用例
    test_cases = [
        '<div class="container">标题</div>内容',
        '<p>段落文字</p>',
        '<img src="image.jpg" alt="图片"/>',
        '<span style="color: red;">红色文字</span>普通文字',
        '<h1>标题</h1><p>段落</p>正文'
    ]
    
    print("\n更多测试用例:")
    for test_case in test_cases:
        print(f"原始: {test_case}")
        print(f"清理后: {remove_html_tags(test_case)}")
        print("-" * 30)