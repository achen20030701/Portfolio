"""
RAG 进阶版配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # DeepSeek API
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # DashScope Embedding
    DASHSCOPE_API_KEY: str = ""

    # 应用配置
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # RAG 配置
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5

    # 检索策略配置
    USE_HYBRID_SEARCH: bool = True
    USE_RERANK: bool = True
    BM25_WEIGHT: float = 0.3
    VECTOR_WEIGHT: float = 0.7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
