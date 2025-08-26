from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio
import sys
from src.services.crawler import Crawler
from src.services.async_crawler import AsyncCrawler
        
async def main():
    #获取命令行第一个参数
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        print("请输入url")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        crawer = AsyncCrawler(context,url)
        await crawer.arun()
        await browser.close()

    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=True)
    #     context = browser.new_context()
    #     crawer = Crawler(context,url)
    #     crawer.run()
    #     browser.close()

# 示例用法
if __name__ == '__main__':
    asyncio.run(main())