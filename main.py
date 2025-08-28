from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import asyncio
import sys
from src.services.crawler import Crawler
from src.services.async_crawler import AsyncCrawler
from src.services.async_crawler_pro import AsyncCrawlerPro
        
async def main():
    #获取命令行第一个参数
    url = sys.argv[1] if len(sys.argv) > 1 else None
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output"
    if not url:
        print("请输入url")
        return
    
    width = 1440
    height = 720
    output_file = output_file + f"_{width}_{height}.xlsx"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": width, "height": height})
        crawer = AsyncCrawlerPro(context,url,output_file)
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