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

if __name__ == "__main__":
    print(check_main_domain("https://cerlo.com//", "https://x.com/CerLo_team"))