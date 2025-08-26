from playwright.sync_api import BrowserContext, Page
from typing import Optional,List,Set
from bs4 import BeautifulSoup
from src.utils.functions import deduplicate_text,check_main_domain
from dataclasses import field,dataclass,asdict
import pandas as pd
import time
import re

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

class Crawler:

    browserContext: Optional[BrowserContext] = None

    init_url: str = ''

    table:CrawlerTable = field(default_factory={})

    __clicked_elements:Set[str] = field(default_factory=set)

    __crawled_urls:Set[str] = field(default_factory=set)

    def __init__(self, browserContext:BrowserContext,url:str):
        self.browserContext = browserContext
        self.init_url = url
        self.table = CrawlerTable()
        self.__clicked_elements = set()
        self.__crawled_urls = set()

    #获取网页内容
    def get_content(self,page:Page)->webContent:
        page_content = page.content()
        soup = BeautifulSoup(page_content, 'html.parser')
        content_list = soup.get_text(separator='<|>',strip=True).split('<|>')
        #文本去重
        content_list = deduplicate_text(content_list)
        #过滤掉纯符号文本
        content_list = [text for text in content_list if not re.match(r'^[^\w\s]+$', text)]
        title = soup.title.string if soup.title else "无标题"
        return webContent(title,contents=content_list)
    
    #获取所有链接
    def get_link_urls(self,page:Page):
        links = page.query_selector_all('a')
        linkUrls = []
        for link in links:
            href = link.get_attribute('href')
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
    def get_image_urls(self, page: Page):
        images = page.query_selector_all('img')
        imageUrls = []
        for image in images:
            src = image.get_attribute('src')
            if src:
                # 过滤掉包含特定关键词的图片
                if any(keyword in src for keyword in ["background", "icon", "sprite"]):
                    continue
                
                # 获取图片的宽度和高度
                width = image.get_attribute('width')
                height = image.get_attribute('height')
                
                # 过滤掉尺寸非常小的图片
                if width and height and (int(width) < 50 or int(height) < 50):
                    continue
                
                imageUrls.append(src)
        
        imageUrls = deduplicate_text(imageUrls)
        return imageUrls
    
    #爬取子链接页面
    def crawSubLinkPage(self,page:Page):
        linkUrls = self.get_link_urls(page)
        for linkUrl in linkUrls:
            new_page = self.browserContext.new_page()
            new_page.goto(linkUrl)
            new_page.wait_for_load_state('networkidle')
            self.craw_page(linkUrl,new_page)
            self.__crawled_urls.add(linkUrl)
            new_page.close()

    #爬取点击元素页面
    # def crawSubClickPage(self,page:Page):
    #      # 查找并点击可点击的 <div> 元素
    #     clickable_divs = page.query_selector_all('div[style*="cursor:pointer"], div.clickable')
    #     #记录所有可点击div 供下次进入链接点击
    #     for div in clickable_divs:
    #         try:
    #             div_outer_html = div.evaluate("(element) => element.outerHTML")
    #             if div_outer_html in self.__clicked_elements:
    #                 print("已经点击过:"+div_outer_html)
    #                 continue
    #         except Exception as e:
    #             print("获取div元素失败:"+str(e))
    #             continue
    #         div.evaluate("(element) => element.click()")
    #         self.__clicked_elements.add(div_outer_html)
    #         # 等待页面加载完成
    #         page.wait_for_load_state('networkidle')
    #         #等待1秒
    #         time.sleep(1)
    #         # 获取当前页面url
    #         current_url = page.evaluate("() => window.location.href")
    #         if current_url not in self.__crawled_urls:
    #             self.__crawled_urls.add(current_url)
    #             self.craw_page(current_url,page)
    #         else:
    #             print("已经抓取过:"+current_url)
    #         page.goto(self.init_url)
    #         page.wait_for_load_state('networkidle')
    #         self.crawSubClickPage(page)
    #         break

    #爬取点击元素页面
    def crawSubClickPage(self, page: Page):
        # 使用栈来模拟递归
        stack = [page]
        while stack:
            current_page = stack.pop()
            clickable_divs = current_page.query_selector_all('div[style*="cursor:pointer"], div.clickable')

            for div in clickable_divs:
                try:
                    div_outer_html = div.evaluate("(element) => element.outerHTML")
                    if div_outer_html in self.__clicked_elements:
                        print("已经点击过:" + div_outer_html)
                        continue
                except Exception as e:
                    print("获取div元素失败:" + str(e))
                    continue

                div.evaluate("(element) => element.click()")
                self.__clicked_elements.add(div_outer_html)
                current_page.wait_for_load_state('networkidle')
                time.sleep(1)

                current_url = current_page.evaluate("() => window.location.href")
                if current_url not in self.__crawled_urls:
                    self.__crawled_urls.add(current_url)
                    self.craw_page(current_url, current_page)
                else:
                    print("已经抓取过:" + current_url)

                # 将当前页面重新加入栈中以便继续处理
                stack.append(current_page)
                current_page.goto(self.init_url)
                current_page.wait_for_load_state('networkidle')   
                break         

    def add_table_row(self,webContent:webContent,url:str,images:List[str]):
        self.table.title.append(webContent.title)
        self.table.url.append(url)
        self.table.content.append("\n".join(webContent.contents))
        self.table.images.append("\n".join(images))

    def export_table(self):
        df = pd.DataFrame(asdict(self.table))
        df.to_excel('output.xlsx', index=False)

    def craw_page(self,url:str,page:Page):
        print("开始爬取页面:",url)
        # 获取所有的button并点击
        if "faq" in url:
            buttons = page.query_selector_all('button')
            for button in buttons:
                button.evaluate("(element) => element.click()")
        # 提取网页的所有文本内容
        webContent = self.get_content(page)
        # 提取所有图片链接
        imageUrls = self.get_image_urls(page)
        # 添加表格行
        self.add_table_row(webContent,url,imageUrls)

    def run(self):
        page = self.browserContext.new_page()
        # 打开目标网页
        page.goto(self.init_url)
        # 等待页面加载完成
        page.wait_for_load_state('networkidle')
        self.craw_page(self.init_url,page)
        self.__crawled_urls.add(self.init_url)
        # 爬取子页面
        self.crawSubLinkPage(page)
        self.crawSubClickPage(page)
        # 导出表格
        self.export_table()
