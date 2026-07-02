"""
查询优化模块
包含 Query Rewrite 和 HyDE 功能
"""
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings


class QueryOptimizer:
    """
    查询优化器

    功能：
    1. Query Rewrite: 将用户问题重写为更适合检索的形式
    2. HyDE: 生成假设性文档，用于检索
    3. 多轮对话上下文处理

    为什么需要查询优化？
    - 用户问题可能模糊、口语化
    - 直接检索可能效果不好
    - 优化后的查询能提升检索质量
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            openai_api_key=settings.DEEPSEEK_API_KEY,
            openai_api_base=settings.DEEPSEEK_BASE_URL,
            temperature=0.3
        )

    def rewrite_query(self, query: str, chat_history: List[dict] = None) -> str:
        """
        Query Rewrite（查询重写）

        原理：
        - 将用户问题重写为更适合检索的形式
        - 处理指代消解（"它" → 具体实体）
        - 补充上下文信息
        - 简化复杂问题

        示例：
        - 原始: "它的价格是多少？"
        - 重写: "DeepSeek API 的价格是多少？"

        - 原始: "怎么用？"
        - 重写: "如何使用 RAG 文档问答系统？"
        """
        if not chat_history:
            # 没有历史对话，直接返回原查询
            return query

        prompt = ChatPromptTemplate.from_template("""
你是一个查询重写专家。请根据对话历史，将用户的问题重写为一个独立、完整、更适合搜索的形式。

要求：
1. 解决指代问题（"它"、"这个" 等替换为具体实体）
2. 补充必要的上下文信息
3. 保持原意不变
4. 使问题更适合向量检索

对话历史：
{chat_history}

用户问题：{query}

重写后的查询（只输出重写后的查询，不要解释）：""")

        chain = prompt | self.llm | StrOutputParser()

        # 格式化对话历史
        history_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in chat_history[-5:]  # 只取最近5轮
        ])

        rewritten = chain.invoke({
            "chat_history": history_text,
            "query": query
        })

        return rewritten.strip()

    def generate_hyde(self, query: str) -> str:
        """
        HyDE (Hypothetical Document Embedding)

        原理：
        1. 让 LLM 生成一个"假设性文档"作为回答
        2. 用这个假设性文档去检索，而不是用原始查询
        3. 假设性文档与真实文档更相似，检索效果更好

        为什么有效？
        - 用户问题和文档的表述方式不同
        - 假设性文档的表述更接近真实文档
        - 提升检索的语义匹配度

        示例：
        - 查询: "什么是 RAG？"
        - 假设性文档: "RAG（Retrieval-Augmented Generation）是一种结合检索和生成的技术..."
        - 用假设性文档去检索，效果更好
        """
        prompt = ChatPromptTemplate.from_template("""
请根据以下问题，生成一个简短的假设性文档（约100-200字）。
这个文档应该像是一个技术文档中对这个问题的回答。

要求：
1. 使用专业、正式的语言
2. 包含关键词和术语
3. 结构清晰
4. 不要使用"可能"、"也许"等不确定词语

问题：{query}

假设性文档：""")

        chain = prompt | self.llm | StrOutputParser()
        hyde_doc = chain.invoke({"query": query})

        return hyde_doc.strip()

    def decompose_query(self, query: str) -> List[str]:
        """
        查询分解

        将复杂问题分解为多个简单子问题

        示例：
        - 原始: "RAG 和 Agent 的区别是什么？各自的应用场景有哪些？"
        - 分解: ["RAG 的定义是什么？", "Agent 的定义是什么？", "RAG 的应用场景？", "Agent 的应用场景？"]
        """
        prompt = ChatPromptTemplate.from_template("""
请将以下复杂问题分解为 2-4 个简单的子问题。
每个子问题应该独立可答。

复杂问题：{query}

子问题（每行一个）：""")

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"query": query})

        # 解析子问题
        sub_queries = [q.strip() for q in result.strip().split("\n") if q.strip()]

        return sub_queries if sub_queries else [query]
