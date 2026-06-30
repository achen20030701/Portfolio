# 📚 RAG 文档问答系统

> 上传文档，用自然语言提问，AI 根据文档内容回答。

## ✨ 功能特点

- 📄 **多格式支持**：TXT、PDF、DOCX
- 🔍 **智能检索**：向量语义搜索
- 💬 **自然对话**：多轮对话
- 📚 **来源追溯**：显示原文来源
- ☁️ **云原生部署**：腾讯云 CloudBase

## 🛠️ 技术栈

- **后端**：Python + FastAPI
- **AI 框架**：LangChain
- **向量库**：ChromaDB
- **LLM**：DeepSeek API
- **部署**：腾讯云 CloudBase

## 📁 项目结构

```
ai-rag-doc-qa/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── loader.py        # 文档加载器
│   │   ├── splitter.py      # 文本分割器
│   │   ├── vectorstore.py   # 向量存储
│   │   └── chain.py         # RAG 问答链
│   └── api/
│       ├── __init__.py
│       ├── upload.py        # 文档上传
│       └── chat.py          # 问答接口
├── frontend/
│   └── index.html           # 前端页面
├── cloudfunctions/          # 云函数
├── deploy/                  # 部署文件
├── .env                     # 环境变量
├── .env.example             # 环境变量模板
├── .gitignore               # Git 忽略
└── requirements.txt         # 依赖清单
```

## 🚀 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 API Key
```

### 3. 启动服务

```bash
python -m app.main
```

### 4. 访问应用

- 前端：http://localhost:8501
- 后端：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 📝 开发日志

- [ ] Day 1：项目搭建 + 配置管理
- [ ] Day 2：文档加载器
- [ ] Day 3：文本分割器
- [ ] Day 4：向量存储
- [ ] Day 5：RAG 问答链
- [ ] Day 6：API 接口
- [ ] Day 7：前端界面
- [ ] Day 8：云函数部署
- [ ] Day 9：测试优化
- [ ] Day 10：文档完善
