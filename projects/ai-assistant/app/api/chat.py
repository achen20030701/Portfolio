"""
问答接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.rag.chain import ask_question

router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    collection_name: str = "default"


class ChatResponse(BaseModel):
    """聊天响应"""
    reply: str
    sources: list


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    问答接口

    根据文档内容回答问题
    """
    try:
        result = ask_question(
            question=request.message,
            collection_name=request.collection_name
        )

        return ChatResponse(
            reply=result["answer"],
            sources=result["sources"]
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败：{str(e)}")
