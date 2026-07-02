"""
文本分割器
将长文档分成小块
"""
from typing import List
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def split_documents(
    docs: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Document]:
    """
    分割文档

    参数：
        docs: 文档列表
        chunk_size: 每块最大字符数
        chunk_overlap: 块之间重叠字符数

    返回：
        分割后的文档列表
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "，", " "]
    )

    return splitter.split_documents(docs)
