"""
RAG 问答链
将检索和生成组合在一起
"""
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.config import settings
from app.rag.vectorstore import get_vectorstore


def format_docs(docs: List[Document]) -> str:
    """将文档列表格式化为字符串"""
    return "\n\n".join(doc.page_content for doc in docs)


def create_rag_chain(collection_name: str = "default"):
    """
    创建 RAG 问答链

    参数：
        collection_name: 集合名称

    返回：
        RAG 链
    """
    # 获取向量存储
    vectorstore = get_vectorstore(collection_name)
    if not vectorstore:
        raise ValueError(f"向量库 '{collection_name}' 不存在，请先上传文档")

    # 创建检索器
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}  # 返回最相关的3个文档
    )

    # 创建 LLM
    llm = ChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        openai_api_key=settings.DEEPSEEK_API_KEY,
        openai_api_base=settings.DEEPSEEK_BASE_URL,
        temperature=0.3,  # 低温度，更稳定
    )

    # 创建 Prompt 模板
    prompt = ChatPromptTemplate.from_template("""
你是一个专业的文档问答助手。请基于以下参考资料回答问题。

要求：
1. 只使用参考资料中的信息回答
2. 如果资料中没有相关信息，请说"抱歉，我无法根据现有资料回答这个问题"
3. 回答要简洁明了，直接回答问题
4. 可以适当总结，不要直接复制粘贴

参考资料：
{context}

问题：{question}

回答：""")

    # 创建 RAG 链
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever


def ask_question(question: str, collection_name: str = "default") -> Dict[str, Any]:
    """
    问问题

    参数：
        question: 问题
        collection_name: 集合名称

    返回：
        包含回答和来源的字典
    """
    # 创建 RAG 链
    rag_chain, retriever = create_rag_chain(collection_name)

    # 获取相关文档
    relevant_docs = retriever.invoke(question)

    # 生成回答
    answer = rag_chain.invoke(question)

    # 格式化来源
    sources = []
    for doc in relevant_docs:
        sources.append({
            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            "metadata": doc.metadata
        })

    return {
        "answer": answer,
        "sources": sources
    }


# 测试代码
if __name__ == "__main__":
    try:
        result = ask_question("什么是人工智能？")
        print("✅ 问答成功！")
        print(f"回答：{result['answer']}")
        print(f"来源数量：{len(result['sources'])}")
    except Exception as e:
        print(f"❌ 错误：{e}")
