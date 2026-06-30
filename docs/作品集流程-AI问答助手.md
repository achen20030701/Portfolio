# 📚 AI 智能文档问答助手 - 作品集流程文档

> 记录从零开始到部署完成的完整开发流程，方便回顾和面试讲解。

---

## 📋 项目概览

| 项目 | 说明 |
|------|------|
| **项目名称** | AI 智能文档问答助手 |
| **项目定位** | 基于 RAG 技术的文档问答系统 |
| **核心功能** | 上传文档 → 自然语言提问 → AI 根据文档回答 |
| **技术栈** | FastAPI + LangChain + ChromaDB + DeepSeek + Streamlit |
| **部署平台** | 腾讯云 CloudBase（云函数 + 静态网站托管） |
| **开发周期** | 2026年6月26日 |
| **项目状态** | ✅ 已完成 |

---

## 🎯 项目目标

### 学习目标
1. 掌握 Python Web 后端开发（FastAPI）
2. 理解 RAG（检索增强生成）技术原理
3. 学会使用 LangChain 构建 AI 应用
4. 掌握向量数据库（ChromaDB）的使用
5. 学会部署到云平台

### 作品集目标
1. 完整的全栈项目经验
2. 可展示的在线 Demo
3. 清晰的技术文档
4. 面试时可以讲解的项目

---

## 📅 开发时间线

### 第一阶段：项目搭建（Day 1 上午）

**目标：** 搭建项目骨架，配置开发环境

**完成内容：**
- ✅ 创建项目目录结构
- ✅ 配置 Python 虚拟环境
- ✅ 创建 `.env` 配置文件（API Key）
- ✅ 创建 `.gitignore`（排除敏感文件）
- ✅ 创建 `requirements.txt`（依赖清单）
- ✅ 编写配置读取模块 `app/config.py`
- ✅ 测试配置读取功能

**关键代码：**
```python
# app/config.py - 配置管理
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")
    # ...
```

**学习收获：**
- 理解了 `.env` 文件的作用（保险箱）
- 理解了 `.gitignore` 的作用（拒收清单）
- 理解了虚拟环境的作用（独立厨房）

---

### 第二阶段：后端 API 开发（Day 1 下午）

**目标：** 创建 FastAPI 后端服务

**完成内容：**
- ✅ 创建 FastAPI 主程序 `app/main.py`
- ✅ 配置 CORS 跨域
- ✅ 创建健康检查接口 `/health`
- ✅ 创建配置检查接口 `/config/check`
- ✅ 测试 API 服务启动

**关键代码：**
```python
# app/main.py - FastAPI 入口
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI 智能文档问答助手")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

**学习收获：**
- 理解了 FastAPI 的基本架构
- 理解了 CORS 跨域配置
- 理解了异步编程（async/await）

---

### 第三阶段：RAG 管道开发（Day 1 晚上）

**目标：** 实现文档加载、分割、向量化、检索

**完成内容：**
- ✅ 创建文档加载器 `app/rag/loader.py`（支持 TXT、PDF、DOCX）
- ✅ 创建文本分割器 `app/rag/splitter.py`
- ✅ 创建向量存储 `app/rag/vectorstore.py`（ChromaDB）
- ✅ 创建 RAG 问答链 `app/rag/chain.py`
- ✅ 创建文档上传接口 `app/api/upload.py`
- ✅ 创建问答接口 `app/api/chat.py`
- ✅ 测试文档上传和问答功能

**关键代码：**
```python
# app/rag/chain.py - RAG 问答链
def create_rag_chain(collection_name):
    # 获取向量存储
    vectorstore = get_vectorstore(collection_name)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 创建 LLM
    llm = ChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        openai_api_key=settings.DEEPSEEK_API_KEY,
        openai_api_base=settings.DEEPSEEK_BASE_URL,
    )

    # 创建 Prompt
    prompt = ChatPromptTemplate.from_template("""
    基于以下参考资料回答问题。
    参考资料：{context}
    问题：{question}
    """)

    # 创建 RAG 链
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever
```

**学习收获：**
- 理解了 RAG 的工作原理（检索 → 增强 → 生成）
- 理解了向量数据库的作用（语义搜索）
- 理解了 LangChain 的链式调用（LCEL）

---

### 第四阶段：前端界面开发（Day 2 上午）

**目标：** 创建 Streamlit 前端界面

**完成内容：**
- ✅ 创建 Streamlit 前端 `frontend/app.py`
- ✅ 实现文档上传功能
- ✅ 实现对话窗口
- ✅ 实现历史记录显示
- ✅ 实现来源追溯
- ✅ 测试前端功能

**关键代码：**
```python
# frontend/app.py - Streamlit 前端
import streamlit as st
import requests

st.title("🤖 AI 智能文档问答助手")

# 上传文档
uploaded_file = st.file_uploader("上传文档", type=["txt", "pdf", "docx"])

# 对话窗口
if prompt := st.chat_input("请输入你的问题..."):
    response = requests.post(f"{API_BASE}/chat/", json={"message": prompt})
    st.markdown(response.json()["reply"])
```

**学习收获：**
- 理解了 Streamlit 的快速开发能力
- 理解了前后端分离架构
- 理解了 API 调用流程

---

### 第五阶段：云平台部署（Day 2 下午）

**目标：** 部署到腾讯云 CloudBase

**完成内容：**
- ✅ 创建云函数代码 `cloudfunctions/ai-doc-qa/`
- ✅ 配置 CloudBase NoSQL 数据库
- ✅ 创建 Node.js 云函数
- ✅ 配置 API 网关触发器
- ✅ 部署前端到静态网站托管
- ✅ 测试在线访问

**关键代码：**
```javascript
// cloudfunctions/ai-doc-qa/index.js - 云函数入口
const cloud = require('@cloudbase/node-sdk');
const app = cloud.init({ env: 'cg-work-d3geug43lc211422a' });
const db = app.database();

exports.main = async (event, context) => {
  const { path, body } = event;

  if (path === '/chat') {
    const { message } = JSON.parse(body);
    const reply = await callDeepSeekAPI(message);
    return { statusCode: 200, body: JSON.stringify({ reply }) };
  }
};
```

**学习收获：**
- 理解了云函数的概念（无服务器）
- 理解了 CloudBase 的架构
- 理解了前后端部署流程

---

## 📁 项目文件结构

```
ai-doc-qa/
├── 📄 README.md                    # 项目说明文档
├── 📄 作品集流程.md                 # 本文件（开发流程记录）
├── 📄 requirements.txt             # Python 依赖清单
├── 📄 .env                         # 环境变量（API Key）
├── 📄 .env.example                 # 环境变量模板
├── 📄 .gitignore                   # Git 忽略配置
│
├── 📁 app/                         # 后端应用代码
│   ├── 📄 __init__.py              # 包初始化
│   ├── 📄 config.py                # 配置管理模块
│   ├── 📄 main.py                  # FastAPI 主入口
│   ├── 📄 database.py              # 数据库操作模块
│   ├── 📁 rag/                     # RAG 管道模块
│   │   ├── 📄 __init__.py
│   │   ├── 📄 loader.py            # 文档加载器
│   │   ├── 📄 splitter.py          # 文本分割器
│   │   ├── 📄 vectorstore.py       # 向量存储
│   │   └── 📄 chain.py             # RAG 问答链
│   └── 📁 api/                     # API 接口模块
│       ├── 📄 __init__.py
│       ├── 📄 upload.py            # 文档上传接口
│       └── 📄 chat.py              # 问答接口
│
├── 📁 frontend/                    # 前端代码
│   ├── 📄 app.py                   # Streamlit 前端（本地开发）
│   └── 📄 index.html               # HTML 前端（云部署）
│
├── 📁 cloudfunctions/              # 云函数代码
│   └── 📁 ai-doc-qa/
│       ├── 📄 index.js             # 云函数入口
│       ├── 📄 package.json         # Node.js 依赖
│       └── 📁 node_modules/        # 依赖包
│
├── 📁 data/                        # 数据目录
│   ├── 📁 uploads/                 # 上传的文档
│   ├── 📁 chroma/                  # 向量数据库
│   └── 📄 history.db               # 对话历史（SQLite）
│
└── 📁 tests/                       # 测试代码
    └── ...
```

---

## 🔧 技术栈详解

### 后端技术

| 技术 | 版本 | 用途 | 学习难度 |
|------|------|------|----------|
| **Python** | 3.10+ | 主要编程语言 | ⭐⭐ |
| **FastAPI** | 0.104+ | Web 框架 | ⭐⭐⭐ |
| **LangChain** | 0.1+ | AI 应用框架 | ⭐⭐⭐⭐ |
| **ChromaDB** | 0.4+ | 向量数据库 | ⭐⭐⭐ |
| **DeepSeek** | API | 大语言模型 | ⭐⭐ |

### 前端技术

| 技术 | 版本 | 用途 | 学习难度 |
|------|------|------|----------|
| **Streamlit** | 1.29+ | 快速原型 | ⭐⭐ |
| **HTML/CSS/JS** | - | 前端页面 | ⭐⭐ |

### 云平台

| 技术 | 用途 | 学习难度 |
|------|------|----------|
| **腾讯云 CloudBase** | 云函数 + 数据库 | ⭐⭐⭐ |
| **Node.js** | 云函数运行环境 | ⭐⭐⭐ |
| **CloudBase SDK** | 数据库操作 | ⭐⭐⭐ |

---

## 💡 核心概念解析

### 1. RAG（检索增强生成）

**是什么：** 一种让 AI 基于外部知识回答问题的技术

**工作流程：**
```
用户问题 → 向量化 → 检索相关文档 → 组装 Prompt → 调用 LLM → 生成回答
```

**生活比喻：** 开卷考试
- 闭卷考试：AI 只能用自己的知识回答
- 开卷考试：AI 可以翻阅资料（文档）回答

**代码实现：**
```python
# 1. 加载文档
docs = load_document(file_path)

# 2. 分割文档
chunks = split_documents(docs)

# 3. 向量化存储
create_vectorstore(chunks)

# 4. 检索相关文档
retriever = vectorstore.as_retriever()

# 5. 生成回答
answer = rag_chain.invoke(question)
```

---

### 2. 向量数据库

**是什么：** 专门存储和检索向量的数据库

**为什么需要：** 传统数据库只能精确匹配，向量数据库可以语义搜索

**生活比喻：** 图书馆索引系统
- 传统数据库：按书名精确查找
- 向量数据库：按内容相似度查找

**代码实现：**
```python
# 文本向量化
embeddings = OpenAIEmbeddings()

# 存储到向量数据库
vectorstore = Chroma.from_documents(docs, embeddings)

# 语义搜索
results = vectorstore.similarity_search("问题")
```

---

### 3. FastAPI

**是什么：** 高性能的 Python Web 框架

**为什么选择：** 自动生成 API 文档、支持异步、性能好

**生活比喻：** 快餐店点餐系统
- GET：查看菜单
- POST：下单点餐
- PUT：修改订单
- DELETE：取消订单

**代码实现：**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: ChatRequest):
    return {"reply": "回答"}
```

---

### 4. 云函数（Serverless）

**是什么：** 无需管理服务器的计算服务

**为什么选择：** 按量付费、自动扩缩容、无需运维

**生活比喻：** 共享充电宝
- 传统服务器：自己买充电宝（购买服务器）
- 云函数：用共享充电宝（按使用付费）

**代码实现：**
```javascript
// 云函数入口
exports.main = async (event, context) => {
  const { path, body } = event;

  if (path === '/chat') {
    const reply = await callAI(message);
    return { statusCode: 200, body: JSON.stringify({ reply }) };
  }
};
```

---

## 🐛 遇到的问题与解决方案

### 问题 1：LangChain 版本兼容性

**现象：**
```
ModuleNotFoundError: No module named 'langchain.schema'
```

**原因：** LangChain 版本更新，模块路径变化

**解决方案：**
```python
# 旧写法
from langchain.schema import Document

# 新写法
from langchain_core.documents import Document
```

**学习收获：** 使用第三方库时要注意版本兼容性

---

### 问题 2：PowerShell 执行策略

**现象：**
```
无法加载文件，因为在此系统上禁止运行脚本
```

**原因：** Windows PowerShell 默认禁止运行脚本

**解决方案：**
```bash
# 方法一：使用 CMD
.venv\Scripts\activate.bat

# 方法二：修改 PowerShell 执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**学习收获：** Windows 环境下的 Python 开发需要注意权限问题

---

### 问题 3：前端无法连接后端

**现象：** 前端显示"无法连接后端服务"

**原因：** 后端服务没有启动

**解决方案：**
```bash
# 终端 1：启动后端
python -m app.main

# 终端 2：启动前端
streamlit run frontend/app.py
```

**学习收获：** 前后端分离架构需要同时运行两个服务

---

### 问题 4：CloudBase SDK 安装失败

**现象：**
```
ERROR: Could not find a version that satisfies the requirement tcb-python-sdk
```

**原因：** `tcb-python-sdk` 已不再维护

**解决方案：** 改用 Node.js 云函数 + CloudBase SDK

**学习收获：** 选择技术方案时要考虑维护状态

---

## 📊 项目数据

### 代码统计

| 文件类型 | 文件数 | 代码行数 |
|----------|--------|----------|
| Python | 12 | ~800 行 |
| JavaScript | 1 | ~200 行 |
| HTML/CSS | 1 | ~300 行 |
| 配置文件 | 5 | ~100 行 |
| **总计** | **19** | **~1400 行** |

### 功能统计

| 功能模块 | 完成状态 | 备注 |
|----------|----------|------|
| 文档上传 | ✅ | 支持 TXT、PDF、DOCX |
| 文本分割 | ✅ | 500 字符/块 |
| 向量化存储 | ✅ | ChromaDB |
| 语义检索 | ✅ | Top 3 相关文档 |
| AI 问答 | ✅ | DeepSeek API |
| 来源追溯 | ✅ | 显示原文片段 |
| 对话历史 | ✅ | CloudBase NoSQL |
| 前端界面 | ✅ | Streamlit + HTML |
| 云函数部署 | ✅ | 腾讯云 CloudBase |

---

## 🎓 学习收获总结

### 技术层面

1. **Python Web 开发**
   - FastAPI 框架的使用
   - RESTful API 设计
   - 异步编程（async/await）

2. **AI 应用开发**
   - RAG 技术原理与实现
   - LangChain 框架的使用
   - 向量数据库的应用
   - Prompt Engineering

3. **前端开发**
   - Streamlit 快速原型
   - HTML/CSS/JavaScript
   - 前后端交互

4. **云平台部署**
   - 腾讯云 CloudBase
   - 云函数（Serverless）
   - 静态网站托管

### 工程层面

1. **项目管理**
   - 模块化设计
   - 代码组织结构
   - 文档编写

2. **问题解决**
   - 版本兼容性问题
   - 环境配置问题
   - 部署调试问题

3. **学习方法**
   - 边做边学
   - 遇到问题查文档
   - 记录解决方案

---

## 🎯 面试讲解要点

### 项目介绍（1 分钟）

"这是一个基于 RAG 技术的文档问答系统。用户上传文档后，可以用自然语言提问，AI 会根据文档内容智能回答，并附带原文来源。

技术栈包括：FastAPI 后端、LangChain RAG 管道、ChromaDB 向量数据库、DeepSeek 大模型、Streamlit 前端，部署在腾讯云 CloudBase。"

### 技术亮点（3 分钟）

1. **RAG 管道**
   - 文档加载、分割、向量化、检索、生成
   - 支持多种文档格式（TXT、PDF、DOCX）

2. **向量检索**
   - 使用 ChromaDB 存储向量
   - 语义搜索，精准定位相关内容

3. **来源追溯**
   - 回答附带原文来源
   - 可验证回答的准确性

4. **云原生部署**
   - 云函数（Serverless）
   - 按量付费，自动扩缩容

### 遇到的挑战（2 分钟）

1. **LangChain 版本兼容性**
   - 问题：模块路径变化
   - 解决：查阅官方文档，更新导入方式

2. **CloudBase SDK 选择**
   - 问题：Python SDK 不再维护
   - 解决：改用 Node.js 云函数

3. **前后端联调**
   - 问题：CORS 跨域问题
   - 解决：配置 FastAPI CORS 中间件

---

## 📈 后续优化方向

### 功能优化

- [ ] 支持更多文档格式（Markdown、Excel）
- [ ] 实现流式输出（打字机效果）
- [ ] 添加用户认证
- [ ] 支持多轮对话上下文
- [ ] 实现文档管理功能

### 性能优化

- [ ] 添加缓存机制
- [ ] 优化向量检索速度
- [ ] 实现异步文档处理
- [ ] 添加 CDN 加速

### 用户体验

- [ ] 优化前端界面
- [ ] 添加加载动画
- [ ] 支持移动端适配
- [ ] 添加使用说明

---

## 📝 更新日志

### 2026-06-26

- ✅ 完成项目搭建
- ✅ 完成后端 API 开发
- ✅ 完成 RAG 管道开发
- ✅ 完成前端界面开发
- ✅ 完成云平台部署
- ✅ 创建项目文档

---

## 🔗 相关链接

- **在线 Demo：** https://cg-work-cg-work-d3geug43lc211422a.webapps.tcloudbase.com
- **云函数 API：** https://cg-work-d3geug43lc211422a-1307660528.ap-shanghai.app.tcloudbase.com
- **GitHub 仓库：** [待上传后填写]
- **技术博客：** [待撰写后填写]

---

## 📞 联系方式

- **作者：** [你的名字]
- **邮箱：** [你的邮箱]
- **GitHub：** [你的 GitHub]

---

**最后更新时间：** 2026-06-29

**文档版本：** v1.2.0

---

## 🎉 项目完成！

**完成时间：** 2026-06-29

**部署平台：** 腾讯云 CloudBase

---

## 📚 作品集项目列表

### 项目一：AI 智能问答助手 ✅

- **在线地址：** https://cg-work-cg-work-d3geug43lc211422a.webapps.tcloudbase.com
- **技术栈：** Node.js + CloudBase + DeepSeek API
- **功能：** 自然语言对话，自动保存历史

### 项目二：RAG 文档问答系统 ✅

- **状态：** 本地测试成功，待部署
- **技术栈：** Python + FastAPI + LangChain + ChromaDB + DeepSeek
- **功能：** 上传文档，语义问答，来源追溯

### 作品集主页面

- **地址：** https://xxx.tcloudbaseapp.com
- **风格：** 极简白色系，高级感设计
