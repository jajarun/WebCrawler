import os

# 基础配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_PATH = os.path.join(BASE_DIR, 'export')

# 确保导出目录存在
os.makedirs(EXPORT_PATH, exist_ok=True)

__all__ = [
    BASE_DIR,
    EXPORT_PATH
]