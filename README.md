# WebCrawler

## 概述

WebCrawler 是一个基于 Python 的网页抓取工具，利用 Playwright 库自动化浏览器交互并从网页中提取数据。该工具旨在通过网页导航、提取文本内容、图片和链接，并将收集到的数据导出到 Excel 文件中。

## 功能

- **自动化浏览**：使用 Playwright 自动化浏览器操作，包括页面导航和元素交互。
- **内容提取**：从网页中提取文本内容、图片和链接。
- **数据去重**：确保提取的数据是唯一且相关的。
- **Excel 导出**：将收集到的数据导出到 `output.xlsx` 文件中，便于分析和共享。

## 安装

1. 克隆仓库：
   ```bash
   git clone <repository-url>
   cd WebCrawler
   ```

2. 安装所需依赖：
   ```bash
   uv sync
   ```

## 使用方法

运行网页抓取工具，执行以下命令：

```bash
uv run main.py <url>
```

将 `<url>` 替换为你希望抓取的目标网站 URL。

## 工作原理

1. **初始化**：抓取工具使用浏览器上下文和起始 URL 进行初始化。
2. **页面抓取**：抓取工具导航到初始 URL，提取内容，并跟随链接到子页面。
3. **内容提取**：使用 BeautifulSoup 和 Playwright 的 API 提取文本、图片和链接。
4. **数据导出**：将提取的数据编译成 Excel 文件（`output.xlsx`）。

## 依赖

- Python 3.12
- Playwright
- BeautifulSoup
- Pandas