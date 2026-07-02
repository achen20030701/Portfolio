"""
RAG 进阶版问答链
整合混合检索、Rerank、Query Rewrite
"""
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.config import settings
from app.rag.hybrid_retriever import HybridRetriever
from app.rag.reranker import Reranker, SimpleReranker
from app.rag.query_optimizer import QueryOptimizer


def format_docs(docs: List[Document]) -> str:
    """将文档列表格式化为字符串"""
    return "\n\n---\n\n".join([
        f"[来源 {i+1}] {doc.page_content}"
        for i, doc in enumerate(docs)
    ])


class AdvancedRAGChain:
    """
    RAG 进阶版问答链

    架构：
    ┌─────────────────────────────────────────────────────────┐
    │                    Advanced RAG Chain                   │
    ├─────────────────────────────────────────────────────────┤
    │                                                         │
    │  用户查询                                                │
    │      │                                                  │
    │      ↓                                                  │
    │  ┌──────────────┐                                       │
    │  │ Query Rewrite │  将问题重写为更适合检索的形式          │
    │  └──────────────┘                                       │
    │      │                                                  │
    │      ↓                                                  │
    │  ┌──────────────┐                                       │
    │  │ 混合检索      │  向量检索 + BM25 + RRF 融合           │
    │  └──────────────┘                                       │
    │      │                                                  │
    │      ↓                                                  │
    │  ┌──────────────┐                                       │
    │  │ Rerank       │  交叉编码器重排序                      │
    │  └──────────────┘                                       │
    │      │                                                  │
    │      ↓                                                  │
    │  ┌──────────────┐                                       │
    │  │ LLM 生成     │  基于检索结果生成回答                  │
    │  └──────────────┘                                       │
    │      │                                                  │
    │      ↓                                                  │
    │  返回回答 + 来源                                         │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    """

    def __init__(
        self,
        vectorstore,
        bm25_corpus: List[str] = None,
        bm25_documents: List[Document] = None,
        use_hybrid: bool = True,
        use_rerank: bool = True,
        use_query_rewrite: bool = True,
        use_hyde: bool = False
    ):
        """
        初始化 RAG 链

        参数：
            vectorstore: 向量数据库
            bm25_corpus: BM25 语料库
            bm25_documents: BM25 文档列表
            use_hybrid: 是否使用混合检索
            use_rerank: 是否使用 Rerank
            use_query_rewrite: 是否使用查询重写
            use_hyde: 是否使用 HyDE
        """
        self.vectorstore = vectorstore
        self.use_hybrid = use_hybrid
        self.use_rerank = use_rerank
        self.use_query_rewrite = use_query_rewrite
        self.use_hyde = use_hyde

        # 初始化组件
        if use_hybrid and bm25_corpus and bm25_documents:
            self.retriever = HybridRetriever(
                vectorstore=vectorstore,
                bm25_corpus=bm25_corpus,
                bm25_documents=bm25_documents,
                vector_weight=settings.VECTOR_WEIGHT,
                bm25_weight=settings.BM25_WEIGHT,
                top_k=settings.TOP_K * 2  # 检索更多文档用于 Rerank
            )
        else:
            # 仅使用向量检索
            self.retriever = vectorstore.as_retriever(
                search_kwargs={"k": settings.TOP_K * 2}
            )

        # Rerank
        if use_rerank:
            try:
                self.reranker = Reranker()
            except Exception:
                self.reranker = SimpleReranker()
        else:
            self.reranker = None

        # 查询优化
        if use_query_rewrite or use_hyde:
            self.query_optimizer = QueryOptimizer()
        else:
            self.query_optimizer = None

        # LLM
        self.llm = ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_BASE_URL,
            temperature=0.3
        )

        # Prompt 模板
        self.prompt = ChatPromptTemplate.from_template("""
你是一个专业的文档问答助手。请基于以下参考资料回答问题。

要求：
1. 只使用参考资料中的信息回答
2. 如果资料中没有相关信息，请说"抱歉，我无法根据现有资料回答这个问题"
3. 回答要简洁明了，直接回答问题
4. 引用来源时使用 [来源 N] 格式
5. 可以适当总结，不要直接复制粘贴

参考资料：
{context}

问题：{question}

回答：""")

    def _retrieve(self, query: str, chat_history: List[dict] = None) -> List[Document]:
        """
        执行检索

        流程：
        1. Query Rewrite（可选）
        2. HyDE（可选）
        3. 混合检索 / 向量检索
        4. Rerank（可选）
        """
        # Step 1: Query Rewrite
        if self.use_query_rewrite and self.query_optimizer and chat_history:
            query = self.query_optimizer.rewrite_query(query, chat_history)

        # Step 2: HyDE
        if self.use_hyde and self.query_optimizer:
            hyde_doc = self.query_optimizer.generate_hyde(query)
            # 使用假设性文档进行检索
            query = hyde_doc

        # Step 3: 检索
        if isinstance(self.retriever, HybridRetriever):
            docs = self.retriever.search(query)
        else:
            docs = self.retriever.invoke(query)

        # Step 4: Rerank
        if self.reranker and len(docs) > settings.TOP_K:
            docs = self.reranker.rerank(query, docs, top_n=settings.TOP_K)

        return docs

    def ask(
        self,
        question: str,
        chat_history: List[dict] = None
    ) -> Dict[str, Any]:
        """
        提问

        参数：
            question: 用户问题
            chat_history: 对话历史

        返回：
            {
                "answer": "回答内容",
                "sources": [...],
                "retrieval_info": {...}
            }
        """
        # 检索
        relevant_docs = self._retrieve(question, chat_history)

        # 生成回答
        context = format_docs(relevant_docs)
        chain = self.prompt | self.llm | StrOutputParser()

        answer = chain.invoke({
            "context": context,
            "question": question
        })

        # 格式化来源
        sources = []
        for i, doc in enumerate(relevant_docs):
            sources.append({
                "index": i + 1,
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            })

        # 检索信息
        retrieval_info = {
            "use_hybrid": self.use_hybrid,
            "use_rerank": self.use_rerank,
            "use_query_rewrite": self.use_query_rewrite,
            "use_hyde": self.use_hyde,
            "total_docs": len(relevant_docs)
        }

        return {
            "answer": answer,
            "sources": sources,
            "retrieval_info": retrieval_info
        }

    def ask_with_debug(
        self,
        question: str,
        chat_history: List[dict] = None
    ) -> Dict[str, Any]:
        """
        带调试信息的提问

        返回详细的检索过程信息，用于调试和优化
        """
        debug_info = {}

        # Query Rewrite
        rewritten_query = question
        if self.use_query_rewrite and self.query_optimizer and chat_history:
            rewritten_query = self.query_optimizer.rewrite_query(question, chat_history)
            debug_info["rewritten_query"] = rewritten_query

        # HyDE
        hyde_doc = None
        if self.use_hyde and self.query_optimizer:
            hyde_doc = self.query_optimizer.generate_hyde(rewritten_query)
            debug_info["hyde_doc"] = hyde_doc[:200] + "..."

        # 检索
        query = hyde_doc if hyde_doc else rewritten_query
        if isinstance(self.retriever, HybridRetriever):
            docs = self.retriever.search(query)
            debug_info["search_method"] = "hybrid"
        else:
            docs = self.retriever.invoke(query)
            debug_info["search_method"] = "vector"

        debug_info["initial_docs_count"] = len(docs)

        # Rerank
        if self.reranker and len(docs) > settings.TOP_K:
            docs = self.reranker.rerank(query, docs, top_n=settings.TOP_K)
            debug_info["after_rerank_count"] = len(docs)

        # 生成回答
        context = format_docs(docs)
        chain = self.prompt | self.llm | StrOutputParser()

        answer = chain.invoke({
            "context": context,
            "question": question
        })

        # 格式化来源
        sources = []
        for i, doc in enumerate(docs):
            sources.append({
                "index": i + 1,
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata
            })

        return {
            "answer": answer,
            "sources": sources,
            "debug_info": debug_info
        }
