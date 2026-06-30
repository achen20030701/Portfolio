"""
文本分割器
将长文档分割成小块，便于向量化
"""
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
    documents: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Document]:
    """
    分割文档

    参数：
        documents: 文档列表
        chunk_size: 每块的最大字符数
        chunk_overlap: 块之间的重叠字符数

    返回：
        分割后的文档列表
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " "]
    )

    chunks = splitter.split_documents(documents)
    return chunks


# 测试代码
if __name__ == "__main__":
    # 创建测试文档
    test_doc = Document(
        page_content="这是一段很长的文本。" * 100,
        metadata={"source": "test.txt"}
    )

    chunks = split_documents([test_doc])
    print(f"✅ 分割成功")
    print(f"  原始文档：1 个")
    print(f"  分割后：{len(chunks)} 块")
    print(f"  第一块大小：{len(chunks[0].page_content)} 字符")
