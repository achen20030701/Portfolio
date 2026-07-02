"""
Rerank 重排序模块
使用交叉编码器对检索结果进行重排序
"""
from typing import List, Tuple
from langchain_core.documents import Document


class Reranker:
    """
    Rerank 重排序器

    原理：
    - 初始检索（向量/BM25）使用双编码器（Bi-Encoder）
      - 查询和文档分别编码，计算相似度
      - 速度快，但精度有限
    - Rerank 使用交叉编码器（Cross-Encoder）
      - 将查询和文档拼接后一起编码
      - 速度慢，但精度高

    流程：
    1. 初始检索返回 top_k 个候选文档（如 k=20）
    2. Rerank 对这 20 个文档重新打分
    3. 返回重排序后的 top_n 个文档（如 n=5）

    优势：
    - 显著提升检索精度
    - 减少噪音文档
    - 提升最终回答质量
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        """
        初始化 Reranker

        参数：
            model_name: 重排序模型名称
                - BAAI/bge-reranker-base: 中文效果好，速度快
                - BAAI/bge-reranker-large: 效果更好，速度较慢
                - cross-encoder/ms-marco-MiniLM-L-6-v2: 英文效果好
        """
        self.model_name = model_name
        self.model = None

    def _load_model(self):
        """延迟加载模型"""
        if self.model is None:
            try:
                from sentence_transformers import CrossEncoder
                self.model = CrossEncoder(self.model_name)
                print(f"✅ Rerank 模型加载成功: {self.model_name}")
            except Exception as e:
                print(f"⚠️ Rerank 模型加载失败: {e}")
                self.model = None

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_n: int = 5
    ) -> List[Document]:
        """
        重排序

        参数：
            query: 查询文本
            documents: 候选文档列表
            top_n: 返回文档数量

        返回：
            重排序后的文档列表
        """
        if not documents:
            return []

        # 加载模型
        self._load_model()

        # 如果模型加载失败，返回原始结果
        if self.model is None:
            return documents[:top_n]

        # 构建查询-文档对
        pairs = [(query, doc.page_content) for doc in documents]

        # 计算相关性分数
        scores = self.model.predict(pairs)

        # 按分数排序
        doc_scores = list(zip(documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        # 返回 top_n
        return [doc for doc, _ in doc_scores[:top_n]]

    def rerank_with_scores(
        self,
        query: str,
        documents: List[Document],
        top_n: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        带分数的重排序

        返回：
            [(Document, rerank_score), ...]
        """
        if not documents:
            return []

        self._load_model()

        if self.model is None:
            return [(doc, 0.0) for doc in documents[:top_n]]

        pairs = [(query, doc.page_content) for doc in documents]
        scores = self.model.predict(pairs)

        doc_scores = list(zip(documents, scores))
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        return [(doc, float(score)) for doc, score in doc_scores[:top_n]]


class SimpleReranker:
    """
    简单重排序器（不依赖外部模型）

    使用简单的文本匹配分数进行重排序
    适合无法安装 sentence_transformers 的场景
    """

    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_n: int = 5
    ) -> List[Document]:
        """
        简单重排序

        使用查询词在文档中的出现次数作为分数
        """
        if not documents:
            return []

        query_chars = set(query)
        doc_scores = []

        for doc in documents:
            # 计算查询字符在文档中的覆盖率
            doc_chars = set(doc.page_content)
            overlap = len(query_chars & doc_chars)
            score = overlap / len(query_chars) if query_chars else 0
            doc_scores.append((doc, score))

        # 按分数排序
        doc_scores.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in doc_scores[:top_n]]
