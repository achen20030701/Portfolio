"""
配置管理模块
从 .env 文件读取 API Key 等配置
"""
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

class Settings:
    """应用配置类"""

    # DeepSeek 配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # DashScope 配置
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")

    # 应用配置
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

# 全局配置实例
settings = Settings()

# 测试代码
if __name__ == "__main__":
    print("✅ 配置读取成功！")
    print(f"  DeepSeek Key：{settings.DEEPSEEK_API_KEY[:10]}...")
    print(f"  DeepSeek 模型：{settings.DEEPSEEK_MODEL}")
    print(f"  DashScope Key：{settings.DASHSCOPE_API_KEY[:10]}...")




    """
配置管理模块
从 .env 文件读取 API Key 等配置
"""
from dotenv import load_dotenv
import os
from pathlib import Path

# 加载 .env 文件
load_dotenv()


class Settings:
    """应用配置类"""

    # DeepSeek 配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # DashScope 配置
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")

    # 应用配置
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

    # 文件路径
    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    CHROMA_DIR: Path = BASE_DIR / "data" / "chroma"


# 全局配置实例
settings = Settings()


# 测试代码
if __name__ == "__main__":
    print("✅ 配置读取成功！")
    print(f"  DeepSeek Key：{settings.DEEPSEEK_API_KEY[:10]}...")
    print(f"  DeepSeek 模型：{settings.DEEPSEEK_MODEL}")
    print(f"  DashScope Key：{settings.DASHSCOPE_API_KEY[:10]}...")
    print(f"  上传目录：{settings.UPLOAD_DIR}")
    print(f"  向量库目录：{settings.CHROMA_DIR}")