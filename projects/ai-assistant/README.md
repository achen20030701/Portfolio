# 🤖 AI 智能文档问答助手

> 基于 RAG 技术的文档问答系统，上传文档后可以用自然语言提问，AI 会根据文档内容回答。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-latest-orange)
![ChromaDB](https://img.shields.io/badge/ChromaDB-latest-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ 项目亮点

- 📄 **多格式支持**：支持 TXT、PDF、DOCX 文档上传
- 🔍 **智能检索**：基于向量语义搜索，精准定位相关内容
- 💬 **自然对话**：多轮对话，记住上下文
- 📚 **来源追溯**：回答附带原文来源，可验证
- 🚀 **云原生部署**：腾讯云 CloudBase，按量付费

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户界面（HTML/Streamlit）              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  文档上传    │  │  对话窗口    │  │  历史记录    │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         └────────────────┼────────────────┘             │
│                          │ HTTPS                         │
│                          ▼                               │
├─────────────────────────────────────────────────────────┤
│                    云函数（Node.js）                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ /chat       │  │ /history    │  │ /clear      │     │
│  │ 问答接口    │  │ 历史查询    │  │ 清空历史    │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         ▼                ▼                ▼             │
│  ┌─────────────────────────────────────────────────┐   │
│  │              CloudBase NoSQL 数据库               │   │
│  │  ┌─────────────┐                                 │   │
│  │  │ messages    │  存储对话历史                     │   │
│  │  └─────────────┘                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                               │
│                          ▼                               │
│  ┌─────────────┐                                        │
│  │ DeepSeek    │  调用大语言模型                         │
│  │ API         │                                        │
│  └─────────────┘                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **前端** | HTML/CSS/JavaScript | 用户界面 |
| **后端** | Node.js 云函数 | 业务逻辑 |
| **数据库** | CloudBase NoSQL | 对话历史 |
| **AI 模型** | DeepSeek API | 问答生成 |
| **云平台** | 腾讯云 CloudBase | 部署托管 |

---

## 📁 项目结构

```
ai-doc-qa/
├── 📄 README.md                    # 项目说明文档
├── 📄 作品集流程.md                 # 开发流程记录
├── 📄 requirements.txt             # Python 依赖清单
├── 📄 .env                         # 环境变量（API Key）
├── 📄 .env.example                 # 环境变量模板
├── 📄 .gitignore                   # Git 忽略配置
│
├── 📁 app/                         # 后端应用代码（本地开发）
│   ├── 📄 __init__.py
│   ├── 📄 config.py                # 配置管理
│   ├── 📄 main.py                  # FastAPI 入口
│   ├── 📄 database.py              # 数据库操作
│   ├── 📁 rag/                     # RAG 管道
│   │   ├── 📄 loader.py            # 文档加载器
│   │   ├── 📄 splitter.py          # 文本分割器
│   │   ├── 📄 vectorstore.py       # 向量存储
│   │   └── 📄 chain.py             # RAG 问答链
│   └── 📁 api/                     # API 接口
│       ├── 📄 upload.py            # 文档上传
│       └── 📄 chat.py              # 问答接口
│
├── 📁 frontend/                    # 前端代码
│   ├── 📄 app.py                   # Streamlit 前端
│   └── 📄 index.html               # HTML 前端
│
├── 📁 cloudfunctions/              # 云函数代码
│   └── 📁 ai-doc-qa/
│       ├── 📄 index.js             # 云函数入口
│       ├── 📄 package.json         # Node.js 依赖
│       └── 📁 node_modules/        # 依赖包
│
└── 📁 data/                        # 数据目录
    ├── 📁 uploads/                 # 上传的文档
    ├── 📁 chroma/                  # 向量数据库
    └── 📄 history.db               # 对话历史
```

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ai-doc-qa.git
cd ai-doc-qa
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的 API Key
# DEEPSEEK_API_KEY=sk-xxx
```

### 3. 安装依赖（本地开发）

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 启动本地服务

```bash
# 启动后端
python -m app.main

# 新终端，启动前端
streamlit run frontend/app.py
```

### 5. 访问应用

- **本地前端：** http://localhost:8501
- **本地后端：** http://localhost:8000
- **API 文档：** http://localhost:8000/docs

---

## 🌐 云平台部署

### 部署到腾讯云 CloudBase

1. **创建云函数**
   - 进入腾讯云控制台
   - 选择 CloudBase
   - 创建云函数 `ai-doc-qa`
   - 上传 `cloudfunctions/ai-doc-qa/` 目录

2. **配置环境变量**
   ```
   DEEPSEEK_API_KEY=sk-e7abd2ee989e4c0cb92f748a94dd1fa1
   ```

3. **创建数据库集合**
   - 进入数据库管理
   - 创建集合 `messages`

4. **部署前端**
   - 进入静态网站托管
   - 上传 `frontend/index.html`

5. **访问应用**
   - 前端地址：`https://xxx.tcloudbaseapp.com`

---

## 📖 API 接口

### 问答接口

```bash
POST /chat
Content-Type: application/json

{
  "message": "什么是人工智能？",
  "collection_name": "default"
}
```

**响应：**
```json
{
  "reply": "人工智能（Artificial Intelligence）是...",
  "sources": []
}
```

### 获取历史

```bash
GET /history?limit=50
```

**响应：**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "什么是人工智能？",
      "timestamp": "2026-06-26T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "人工智能是...",
      "timestamp": "2026-06-26T10:00:01Z"
    }
  ]
}
```

### 清空历史

```bash
POST /clear
```

**响应：**
```json
{
  "message": "历史已清空"
}
```

---

## 💡 核心概念

### RAG（检索增强生成）

**是什么：** 一种让 AI 基于外部知识回答问题的技术

**工作流程：**
```
用户问题 → 向量化 → 检索相关文档 → 组装 Prompt → 调用 LLM → 生成回答
```

**生活比喻：** 开卷考试
- 闭卷考试：AI 只能用自己的知识回答
- 开卷考试：AI 可以翻阅资料（文档）回答

### 向量数据库

**是什么：** 专门存储和检索向量的数据库

**为什么需要：** 传统数据库只能精确匹配，向量数据库可以语义搜索

**生活比喻：** 图书馆索引系统
- 传统数据库：按书名精确查找
- 向量数据库：按内容相似度查找

---

## 🎯 作品集展示要点

### 面试时可以这样介绍

**项目背景：**
"这是一个基于 RAG 技术的文档问答系统，用户上传文档后可以用自然语言提问，系统会根据文档内容智能回答。"

**技术亮点：**
1. **RAG 管道**：使用 LangChain 构建完整的文档处理管道
2. **向量检索**：使用 ChromaDB 实现语义搜索
3. **来源追溯**：回答附带原文来源，可验证准确性
4. **云原生部署**：使用腾讯云 CloudBase，按量付费

**遇到的挑战：**
"文档分块大小对检索效果影响很大，太大会丢失细节，太小会丢失上下文。通过实验找到了 500 字符、50 字符重叠的最佳配置。"

**优化方向：**
- 添加 Reranker 重排序提升检索精度
- 支持更多文档格式
- 实现流式输出提升用户体验

---

## 📚 学习资源

- [LangChain 官方文档](https://python.langchain.com/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [ChromaDB 官方文档](https://docs.trychroma.com/)
- [DeepSeek API 文档](https://platform.deepseek.com/)
- [腾讯云 CloudBase 文档](https://cloud.tencent.com/product/tcb)

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - AI 应用框架
- [FastAPI](https://github.com/tiangolo/fastapi) - Web 框架
- [Streamlit](https://github.com/streamlit/streamlit) - 前端框架
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库
- [DeepSeek](https://www.deepseek.com/) - 大语言模型
- [腾讯云 CloudBase](https://cloud.tencent.com/product/tcb) - 云平台

---

## 📞 联系方式

- **作者：** [你的名字]
- **邮箱：** [你的邮箱]
- **GitHub：** [你的 GitHub]

---

## 🔗 相关链接

- **在线 Demo：** https://cg-work-cg-work-d3geug43lc211422a.webapps.tcloudbase.com
- **云函数 API：** https://cg-work-d3geug43lc211422a-1307660528.ap-shanghai.app.tcloudbase.com
- **GitHub 仓库：** [待上传后填写]
- **技术博客：** [待撰写后填写]

---

**最后更新时间：** 2026-06-28

**项目状态：** ✅ 已完成并部署上线
