from playwright.sync_api import sync_playwright
import sys
from src.services.crawler import Crawler
        
def main():
    #获取命令行第一个参数
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        print("请输入url")
        return
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        crawer = Crawler(context,url)
        crawer.run()
        browser.close()

# 示例用法
if __name__ == '__main__':
    main()