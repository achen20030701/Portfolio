"""
RAG 进阶版主应用
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.api.chat import router as chat_router, init_rag_chain
from app.rag.vectorstore import get_vectorstore, add_documents
from app.rag.loader import load_document
from app.rag.splitter import split_documents

import os

# 创建 FastAPI 应用
app = FastAPI(
    title="RAG 进阶版",
    description="支持混合检索、Rerank、Query Rewrite 的 RAG 系统",
    version="2.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router)


@app.on_event("startup")
async def startup():
    """应用启动时初始化"""
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    os.makedirs("chroma_db", exist_ok=True)

    # 初始化 RAG 链
    try:
        vectorstore = get_vectorstore()
        init_rag_chain(vectorstore)
        print("✅ RAG 链初始化成功")
    except Exception as e:
        print(f"⚠️ RAG 链初始化失败: {e}")


@app.get("/")
async def root():
    """首页"""
    return FileResponse("static/index.html")


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "hybrid_search": settings.USE_HYBRID_SEARCH,
            "rerank": settings.USE_RERANK,
            "query_rewrite": True,
            "hyde": False
        }
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档

    支持格式：TXT, PDF
    """
    # 检查文件类型
    allowed_types = [".txt", ".pdf"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_ext}，支持: {allowed_types}"
        )

    # 保存文件
    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        # 加载文档
        docs = load_document(file_path)

        # 分块
        chunks = split_documents(
            docs,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

        # 添加到向量数据库
        count = add_documents("default", chunks)

        # 重新初始化 RAG 链
        vectorstore = get_vectorstore()
        init_rag_chain(vectorstore, chunks)

        return {
            "message": "文档上传成功",
            "filename": file.filename,
            "chunks": count,
            "file_size": len(content)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """获取当前配置"""
    return {
        "chunk_size": settings.CHUNK_SIZE,
        "chunk_overlap": settings.CHUNK_OVERLAP,
        "top_k": settings.TOP_K,
        "use_hybrid_search": settings.USE_HYBRID_SEARCH,
        "use_rerank": settings.USE_RERANK,
        "bm25_weight": settings.BM25_WEIGHT,
        "vector_weight": settings.VECTOR_WEIGHT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
