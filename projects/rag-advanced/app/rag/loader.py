"""
文档加载器
支持 TXT 和 PDF 文件
"""
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader


def load_document(file_path: str) -> List[Document]:
    """
    加载文档

    参数：
        file_path: 文件路径

    返回：
        文档列表
    """
    if file_path.endswith('.txt'):
        loader = TextLoader(file_path, encoding='utf-8')
    elif file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_path}")

    return loader.load()
