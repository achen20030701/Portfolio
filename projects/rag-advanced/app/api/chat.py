"""
聊天 API 接口
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.rag.advanced_chain import AdvancedRAGChain


router = APIRouter(prefix="/api", tags=["chat"])


# 请求模型
class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    collection_name: str = "default"
    use_hybrid: bool = True
    use_rerank: bool = True
    use_query_rewrite: bool = True
    use_hyde: bool = False
    chat_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str
    sources: List[Dict[str, Any]]
    retrieval_info: Dict[str, Any]


# 全局 RAG 链实例
rag_chain: Optional[AdvancedRAGChain] = None


def init_rag_chain(vectorstore, documents: List = None):
    """初始化 RAG 链"""
    global rag_chain

    from app.rag.vectorstore import get_bm25_corpus

    # 准备 BM25 语料库
    bm25_corpus, bm25_docs = get_bm25_corpus(documents) if documents else (None, None)

    rag_chain = AdvancedRAGChain(
        vectorstore=vectorstore,
        bm25_corpus=bm25_corpus,
        bm25_documents=bm25_docs,
        use_hybrid=True,
        use_rerank=True,
        use_query_rewrite=True,
        use_hyde=False
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口

    支持的功能：
    - 混合检索（向量 + BM25）
    - Rerank 重排序
    - Query Rewrite 查询重写
    - HyDE 假设性文档嵌入
    """
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG 链未初始化")

    try:
        # 动态调整检索策略
        rag_chain.use_hybrid = request.use_hybrid
        rag_chain.use_rerank = request.use_rerank
        rag_chain.use_query_rewrite = request.use_query_rewrite
        rag_chain.use_hyde = request.use_hyde

        # 执行问答
        result = rag_chain.ask(
            question=request.message,
            chat_history=request.chat_history
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            retrieval_info=result["retrieval_info"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/debug")
async def chat_debug(request: ChatRequest):
    """
    带调试信息的聊天接口

    返回详细的检索过程，用于调试和优化
    """
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG 链未初始化")

    try:
        result = rag_chain.ask_with_debug(
            question=request.message,
            chat_history=request.chat_history
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
