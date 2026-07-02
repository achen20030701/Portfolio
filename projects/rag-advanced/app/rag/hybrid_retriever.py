"""
混合检索器
结合向量检索和 BM25 关键词检索
使用 RRF (Reciprocal Rank Fusion) 算法融合结果
"""
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
import numpy as np


class HybridRetriever:
    """
    混合检索器

    原理：
    1. 向量检索：通过 Embedding 模型将文档和查询转换为向量，计算相似度
    2. BM25 检索：基于词频的关键词匹配算法
    3. RRF 融合：将两种检索结果按排名融合

    优势：
    - 向量检索擅长语义匹配（"报销" 能匹配到 "费用申请"）
    - BM25 擅长精确匹配（"DeepSeek" 能精确匹配到 "DeepSeek"）
    - 两者结合，兼顾语义和关键词
    """

    def __init__(
        self,
        vectorstore,
        bm25_corpus: List[str] = None,
        bm25_documents: List[Document] = None,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3,
        top_k: int = 5
    ):
        """
        初始化混合检索器

        参数：
            vectorstore: 向量数据库实例
            bm25_corpus: BM25 语料库（用于分词）
            bm25_documents: BM25 对应的文档列表
            vector_weight: 向量检索权重
            bm25_weight: BM25 检索权重
            top_k: 返回文档数量
        """
        self.vectorstore = vectorstore
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.top_k = top_k

        # 初始化 BM25
        if bm25_corpus and bm25_documents:
            self.bm25 = BM25Okapi(bm25_corpus)
            self.bm25_documents = bm25_documents
        else:
            self.bm25 = None
            self.bm25_documents = []

    def _bm25_search(self, query: str, top_k: int = None) -> List[Tuple[Document, float]]:
        """
        BM25 检索

        原理：
        - BM25 是一种基于词频的检索算法
        - 计算查询中每个词在文档中的出现频率
        - 考虑词频饱和度和文档长度归一化

        优点：
        - 精确匹配效果好
        - 不需要训练
        - 计算速度快

        缺点：
        - 无法处理同义词
        - 无法理解语义
        """
        if not self.bm25:
            return []

        top_k = top_k or self.top_k

        # 对查询进行分词（简单按字符分割）
        query_tokens = list(query)

        # 计算 BM25 分数
        scores = self.bm25.get_scores(query_tokens)

        # 获取 top_k 结果
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # 只返回有相关性的结果
                results.append((self.bm25_documents[idx], float(scores[idx])))

        return results

    def _vector_search(self, query: str, top_k: int = None) -> List[Tuple[Document, float]]:
        """
        向量检索

        原理：
        - 使用 Embedding 模型将查询和文档转换为向量
        - 计算向量之间的余弦相似度
        - 返回最相似的文档

        优点：
        - 能理解语义（"报销" 能匹配到 "费用申请"）
        - 支持多语言

        缺点：
        - 对精确匹配不够敏感
        - 需要训练 Embedding 模型
        """
        top_k = top_k or self.top_k

        # 使用向量数据库的相似度搜索
        results = self.vectorstore.similarity_search_with_score(query, k=top_k)

        # 转换为 (Document, score) 格式
        # Chroma 返回的距离越小越相似，需要转换
        return [(doc, 1 - score) for doc, score in results]

    def _rrf_fusion(
        self,
        vector_results: List[Tuple[Document, float]],
        bm25_results: List[Tuple[Document, float]],
        k: int = 60
    ) -> List[Document]:
        """
        RRF (Reciprocal Rank Fusion) 融合算法

        原理：
        - 将多个检索结果按排名融合
        - 排名越靠前，分数越高
        - 公式：score = Σ (1 / (k + rank_i))

        优点：
        - 简单有效
        - 不需要归一化分数
        - 对异常值鲁棒

        参数：
            vector_results: 向量检索结果
            bm25_results: BM25 检索结果
            k: 平滑参数（通常取 60）
        """
        # 创建文档到排名的映射
        doc_rank_scores: Dict[str, float] = {}
        doc_map: Dict[str, Document] = {}

        # 处理向量检索结果
        for rank, (doc, _) in enumerate(vector_results):
            doc_id = doc.page_content[:100]  # 使用内容前100字符作为ID
            doc_rank_scores[doc_id] = doc_rank_scores.get(doc_id, 0) + 1 / (k + rank + 1)
            doc_map[doc_id] = doc

        # 处理 BM25 检索结果
        for rank, (doc, _) in enumerate(bm25_results):
            doc_id = doc.page_content[:100]
            doc_rank_scores[doc_id] = doc_rank_scores.get(doc_id, 0) + 1 / (k + rank + 1)
            doc_map[doc_id] = doc

        # 按 RRF 分数排序
        sorted_docs = sorted(doc_rank_scores.items(), key=lambda x: x[1], reverse=True)

        # 返回 top_k 文档
        return [doc_map[doc_id] for doc_id, _ in sorted_docs[:self.top_k]]

    def search(self, query: str) -> List[Document]:
        """
        混合检索

        流程：
        1. 同时执行向量检索和 BM25 检索
        2. 使用 RRF 算法融合结果
        3. 返回融合后的文档列表
        """
        # 并行执行两种检索
        vector_results = self._vector_search(query)
        bm25_results = self._bm25_search(query)

        # 如果只有一种检索有结果，直接返回
        if not vector_results:
            return [doc for doc, _ in bm25_results[:self.top_k]]
        if not bm25_results:
            return [doc for doc, _ in vector_results[:self.top_k]]

        # RRF 融合
        return self._rrf_fusion(vector_results, bm25_results)

    def search_with_scores(self, query: str) -> List[Tuple[Document, float]]:
        """
        带分数的混合检索

        返回：
            [(Document, rrf_score), ...]
        """
        vector_results = self._vector_search(query)
        bm25_results = self._bm25_search(query)

        if not vector_results:
            return [(doc, score) for doc, score in bm25_results[:self.top_k]]
        if not bm25_results:
            return [(doc, score) for doc, score in vector_results[:self.top_k]]

        # RRF 融合（带分数）
        k = 60
        doc_rank_scores: Dict[str, float] = {}
        doc_map: Dict[str, Document] = {}

        for rank, (doc, _) in enumerate(vector_results):
            doc_id = doc.page_content[:100]
            doc_rank_scores[doc_id] = doc_rank_scores.get(doc_id, 0) + 1 / (k + rank + 1)
            doc_map[doc_id] = doc

        for rank, (doc, _) in enumerate(bm25_results):
            doc_id = doc.page_content[:100]
            doc_rank_scores[doc_id] = doc_rank_scores.get(doc_id, 0) + 1 / (k + rank + 1)
            doc_map[doc_id] = doc

        sorted_docs = sorted(doc_rank_scores.items(), key=lambda x: x[1], reverse=True)

        return [(doc_map[doc_id], score) for doc_id, score in sorted_docs[:self.top_k]]
