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

    # DashScope 配置（用于 Embedding）
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")

    # 应用配置
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

    # 文件路径
    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    CHROMA_DIR: Path = BASE_DIR / "data" / "chroma"

    def validate(self) -> list[str]:
        """验证配置，返回缺失的配置项"""
        missing = []
        if not self.DEEPSEEK_API_KEY:
            missing.append("DEEPSEEK_API_KEY")
        if not self.DASHSCOPE_API_KEY:
            missing.append("DASHSCOPE_API_KEY")
        return missing


# 全局配置实例
settings = Settings()


# 测试代码
if __name__ == "__main__":
    missing = settings.validate()
    if missing:
        print(f"❌ 缺少配置：{', '.join(missing)}")
        print("请检查 .env 文件")
    else:
        print("✅ 配置验证通过！")
        print(f"  DeepSeek 模型：{settings.DEEPSEEK_MODEL}")
        print(f"  DeepSeek 地址：{settings.DEEPSEEK_BASE_URL}")
        print(f"  上传目录：{settings.UPLOAD_DIR}")
        print(f"  向量库目录：{settings.CHROMA_DIR}")
