"""
FastAPI 主入口
RAG 文档问答系统
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.upload import router as upload_router
from app.api.chat import router as chat_router


# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    missing = settings.validate()
    if missing:
        print(f"⚠️  警告：缺少配置 {', '.join(missing)}")
    else:
        print("✅ 配置验证通过")

    yield  # 应用运行期间

    # 关闭时执行（可选）
    print("👋 应用关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="RAG 文档问答系统",
    description="上传文档，用自然语言提问，AI 根据文档内容回答",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(upload_router, prefix="/upload", tags=["文档上传"])
app.include_router(chat_router, prefix="/chat", tags=["问答"])


@app.get("/")
async def root():
    """根路径"""
    return {"message": "RAG 文档问答系统 API"}


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/config/check")
async def check_config():
    """检查配置是否完整"""
    missing = settings.validate()
    if missing:
        return {
            "status": "incomplete",
            "missing": missing,
            "message": f"缺少配置：{', '.join(missing)}"
        }
    return {
        "status": "complete",
        "message": "配置验证通过"
    }


# 启动服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )
