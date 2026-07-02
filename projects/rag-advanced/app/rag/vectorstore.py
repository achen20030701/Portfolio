"""
向量存储模块
管理 Chroma 向量数据库
"""
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from app.config import settings


def get_vectorstore(collection_name: str = "default") -> Optional[Chroma]:
    """
    获取向量存储

    参数：
        collection_name: 集合名称

    返回：
        Chroma 向量存储实例
    """
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=settings.DASHSCOPE_API_KEY,
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

    return vectorstore


def get_bm25_corpus(documents: List[Document]) -> Tuple[List[List[str]], List[Document]]:
    """
    准备 BM25 语料库

    BM25 需要将文档分词后才能建立索引。
    这里使用简单的字符级分词。

    参数：
        documents: 文档列表

    返回：
        (bm25_corpus, bm25_documents)
        - bm25_corpus: 分词后的语料库
        - bm25_documents: 对应的文档列表
    """
    bm25_corpus = []
    bm25_documents = []

    for doc in documents:
        # 简单的字符级分词
        # 对于中文，按字符分割效果不错
        tokens = list(doc.page_content)
        bm25_corpus.append(tokens)
        bm25_documents.append(doc)

    return bm25_corpus, bm25_documents


def add_documents(
    collection_name: str,
    documents: List[Document]
) -> int:
    """
    添加文档到向量数据库

    参数：
        collection_name: 集合名称
        documents: 文档列表

    返回：
        添加的文档数量
    """
    vectorstore = get_vectorstore(collection_name)
    vectorstore.add_documents(documents)
    return len(documents)


def search_documents(
    collection_name: str,
    query: str,
    top_k: int = 5
) -> List[Tuple[Document, float]]:
    """
    搜索文档

    参数：
        collection_name: 集合名称
        query: 查询文本
        top_k: 返回数量

    返回：
        [(Document, score), ...]
    """
    vectorstore = get_vectorstore(collection_name)
    return vectorstore.similarity_search_with_score(query, k=top_k)
