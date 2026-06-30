"""
文档上传接口
"""
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.rag.loader import load_document
from app.rag.splitter import split_documents
from app.rag.vectorstore import create_vectorstore

router = APIRouter()


@router.post("/")
async def upload_document(
    file: UploadFile = File(...),
    collection_name: str = "default"
):
    """
    上传文档并建立向量索引

    支持格式：.txt, .pdf, .docx
    """
    # 检查文件类型
    allowed_extensions = {".txt", ".pdf", ".docx"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式：{file_ext}，支持：{', '.join(allowed_extensions)}"
        )

    # 保存文件
    upload_dir = settings.UPLOAD_DIR / collection_name
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        # 加载文档
        documents = load_document(file_path)

        # 分割文档
        chunks = split_documents(documents)

        # 创建向量存储
        create_vectorstore(chunks, collection_name)

        return {
            "filename": file.filename,
            "chunks": len(chunks),
            "collection_name": collection_name,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理文档失败：{str(e)}")
