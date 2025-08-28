from playwright.async_api import BrowserContext, Page
from typing import Optional,List,Set
from src.utils.functions import deduplicate_text,check_main_domain,remove_html_tags
from dataclasses import field,dataclass,asdict
import pandas as pd
import json
import asyncio
import re
import os
from config.config import EXPORT_PATH

@dataclass
class CrawlerTable:
    title:List[str] = field(default_factory=list)
    url:List[str] = field(default_factory=list)
    content:List[str] = field(default_factory=list)
    images:List[str] = field(default_factory=list)

@dataclass
class webContent:
    title:str = ''
    contents:List[str] = field(default_factory=list)

class AsyncCrawlerPro:

    browserContext: Optional[BrowserContext] = None

    init_url: str = ''

    table:CrawlerTable

    output_file:str = ''

    __clicked_elements:Set[str]

    __crawled_urls:Set[str]

    def __init__(self, browserContext:BrowserContext,url:str,output_file:str):
        self.browserContext = browserContext
        self.init_url = url
        self.output_file = output_file
        self.table = CrawlerTable()
        self.__clicked_elements = set[str]()
        self.__crawled_urls = set[str]()

    #获取网页内容(带文字坐标位置和字号)
    async def get_content(self,page:Page)->webContent:
        elements = await page.locator('body *').element_handles()
        data = {}
        for element in elements:
            # 检查元素是否是 HTMLElement
            is_html_element = await element.evaluate("node => node instanceof HTMLElement")
            if is_html_element:
                tag_name = await element.evaluate("node => node.tagName.toLowerCase()")
                if tag_name in ['script', 'iframe', 'style']:
                    continue
                text = await element.inner_text()
                text = text.strip()
                if re.match(r'^[^\w\s]+$', text) or not text:
                    continue
                # 检查是否有子元素，如果有则跳过
                has_children = await element.evaluate("node => node.children.length > 0")
                if has_children:
                    innerHtml = await element.inner_html()
                    text = remove_html_tags(innerHtml)
                    if not text:
                        continue
                bounding_box = await element.bounding_box()
                # 获取文本的字号
                if bounding_box:
                    font_size = await element.evaluate("node => window.getComputedStyle(node).fontSize")
                    data[text] = json.dumps({"text":text,"font_size":font_size}|bounding_box,ensure_ascii=False)
        title = await page.title()
        return webContent(title,contents=list(data.values()))
    
    #获取所有链接
    async def get_link_urls(self,page:Page):
        links = await page.query_selector_all('a')
        linkUrls = []
        for link in links:
            href = await link.get_attribute('href')
            if href:
                linkUrls.append(href)
        linkUrls = deduplicate_text(linkUrls)
        newLinkUrls = []
        for linkUrl in linkUrls:
            url = check_main_domain(self.init_url,linkUrl)
            if url:
                newLinkUrls.append(url)
        return newLinkUrls
    
    #获取所有图片链接
    async def get_image_urls(self, page: Page):
        images = await page.query_selector_all('img')
        imageUrls = []
        for image in images:
            src = await image.get_attribute('src')
            if src:
                # 过滤掉包含特定关键词的图片
                if any(keyword in src for keyword in ["background", "icon", "sprite"]):
                    continue
                
                # 获取图片的宽度和高度
                width = await image.get_attribute('width')
                height = await image.get_attribute('height')
                
                # 过滤掉尺寸非常小的图片
                if width and height and (int(width) < 50 or int(height) < 50):
                    continue
                
                bounding_box = await image.bounding_box()
                image_data = {"src":src}
                if bounding_box:
                    image_data |= bounding_box
                imageUrls.append(json.dumps(image_data,ensure_ascii=False))
        
        # imageUrls = deduplicate_text(imageUrls)
        return imageUrls
    
    #爬取子链接页面
    async def crawSubLinkPage(self,page:Page):
        linkUrls = await self.get_link_urls(page)
        tasks = []
        for linkUrl in linkUrls:
            tasks.append(self.craw_single_page(linkUrl))
        #并行获取
        await asyncio.gather(*tasks)

    async def craw_single_page(self, linkUrl: str):
        new_page = await self.browserContext.new_page()
        await new_page.goto(linkUrl)
        await new_page.wait_for_load_state('networkidle')
        await self.craw_page(linkUrl, new_page)
        self.__crawled_urls.add(linkUrl)
        await new_page.close()

    #爬取点击元素页面
    async def crawSubClickPage(self, page: Page):
        # 使用栈来模拟递归
        stack = [page]
        while stack:
            current_page = stack.pop()
            clickable_divs = await current_page.query_selector_all('div[style*="cursor:pointer"], div.clickable')

            for div in clickable_divs:
                try:
                    div_outer_html = await div.evaluate("(element) => element.outerHTML")
                    if div_outer_html in self.__clicked_elements:
                        print("已经点击过:" + div_outer_html)
                        continue
                except Exception as e:
                    print("获取div元素失败:" + str(e))
                    continue

                await div.evaluate("(element) => element.click()")
                self.__clicked_elements.add(div_outer_html)
                await current_page.wait_for_load_state('networkidle')
                await asyncio.sleep(1)

                current_url = await current_page.evaluate("() => window.location.href")
                if current_url not in self.__crawled_urls:
                    self.__crawled_urls.add(current_url)
                    await self.craw_page(current_url, current_page)
                else:
                    print("已经抓取过:" + current_url)

                # 将当前页面重新加入栈中以便继续处理
                stack.append(current_page)
                await current_page.goto(self.init_url)
                await current_page.wait_for_load_state('networkidle')   
                break         

    def add_table_row(self,webContent:webContent,url:str,images:List[str]):
        self.table.title.append(webContent.title)
        self.table.url.append(url)
        self.table.content.append("\n".join(webContent.contents))
        self.table.images.append("\n".join(images))

    def export_table(self):
        df = pd.DataFrame(asdict(self.table))
        df.to_excel(os.path.join(EXPORT_PATH,self.output_file), index=False)

    async def craw_page(self,url:str,page:Page):
        print("开始爬取页面:",url)
        # 获取所有的button并点击
        if "faq" in url:
            buttons = await page.query_selector_all('button')
            for button in buttons:
                await button.evaluate("(element) => element.click()")
        # 提取网页的所有文本内容
        webContent = await self.get_content(page)
        # 提取所有图片链接
        imageUrls = await self.get_image_urls(page)
        # 添加表格行
        self.add_table_row(webContent,url,imageUrls)

    async def arun(self):
        page = await self.browserContext.new_page()
        # 打开目标网页
        await page.goto(self.init_url)
        # 等待页面加载完成
        await page.wait_for_load_state('networkidle')
        await self.craw_page(self.init_url,page)
        self.__crawled_urls.add(self.init_url)
        # 爬取子页面
        await self.crawSubLinkPage(page)
        await self.crawSubClickPage(page)
        # 导出表格
        self.export_table()
