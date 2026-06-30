"""
向量存储
使用 ChromaDB 存储和检索向量
"""
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

from app.config import settings


def get_embedding_model() -> DashScopeEmbeddings:
    """获取 Embedding 模型"""
    return DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key=settings.DASHSCOPE_API_KEY
    )


def create_vectorstore(
    documents: List[Document],
    collection_name: str = "default"
) -> Chroma:
    """
    创建向量存储

    参数：
        documents: 文档列表
        collection_name: 集合名称

    返回：
        Chroma 向量存储实例
    """
    embeddings = get_embedding_model()

    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(settings.CHROMA_DIR / collection_name),
        collection_name=collection_name,
    )

    return vectorstore


def get_vectorstore(collection_name: str = "default") -> Optional[Chroma]:
    """
    获取已存在的向量存储

    参数：
        collection_name: 集合名称

    返回：
        Chroma 向量存储实例，如果不存在返回 None
    """
    persist_dir = settings.CHROMA_DIR / collection_name

    if not persist_dir.exists():
        return None

    embeddings = get_embedding_model()

    vectorstore = Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings,
        collection_name=collection_name,
    )

    return vectorstore


# 测试代码
if __name__ == "__main__":
    print("✅ 向量存储模块加载成功")
    print(f"  向量库目录：{settings.CHROMA_DIR}")
