# 🔬 RAG 文档问答系统 - 技术深度解析

> 本文档详细解析 RAG（检索增强生成）系统的原理、架构和实现细节
> 适合：想深入理解 RAG 技术的开发者

---

## 📑 目录

1. [什么是 RAG？](#1-什么是-rag)
2. [核心原理](#2-核心原理)
3. [系统架构](#3-系统架构)
4. [代码逐行解析](#4-代码逐行解析)
5. [关键技术详解](#5-关键技术详解)
6. [常见问题与优化](#6-常见问题与优化)
7. [面试问答](#7-面试问答)

---

## 1. 什么是 RAG？

### 1.1 定义

**RAG（Retrieval-Augmented Generation）** = 检索增强生成

```
用户问题 → 检索相关文档 → 将文档 + 问题给 LLM → 生成回答
```

### 1.2 为什么需要 RAG？

**问题：LLM 的局限性**

| 问题 | 说明 | 示例 |
|------|------|------|
| 知识截止 | 训练数据有时间限制 | "2024年发生了什么？" |
| 幻觉 | 编造不存在的信息 | 虚假的论文引用 |
| 私有数据 | 无法访问企业内部文档 | "公司的报销政策是什么？" |

**解决方案：RAG**

```
┌─────────────────────────────────────────────────────────┐
│                      RAG 工作流程                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   用户提问: "如何申请报销？"                              │
│         ↓                                               │
│   检索器: 从知识库找到相关文档                            │
│         ↓                                               │
│   上下文: "报销流程：1.填写申请表 2.提交发票..."          │
│         ↓                                               │
│   LLM: 基于上下文生成准确回答                            │
│         ↓                                               │
│   回答: "申请报销需要以下步骤：..."                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.3 RAG vs 微调 vs 长上下文

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **RAG** | 知识可更新、可追溯 | 检索质量影响回答 | 知识库问答 |
| **微调** | 深度理解领域知识 | 成本高、难更新 | 特定领域模型 |
| **长上下文** | 简单直接 | Token 成本高 | 少量文档 |

---

## 2. 核心原理

### 2.1 RAG 三阶段

```
┌──────────────────────────────────────────────────────────┐
│                    RAG 三阶段                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  阶段 1: 索引（Indexing）                                 │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 文档 → 分块 → 向量化 → 存入向量数据库                │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  阶段 2: 检索（Retrieval）                                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 用户问题 → 向量化 → 相似度搜索 → 返回 Top-K 文档    │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  阶段 3: 生成（Generation）                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 问题 + 检索文档 → Prompt 模板 → LLM → 生成回答      │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 2.2 向量相似度搜索

**核心思想**：将文本转换为向量，通过向量距离衡量语义相似度

```python
# 文本转向量示例
"如何申请报销" → [0.2, 0.5, -0.1, 0.8, ...]  # 768维向量
"报销申请流程" → [0.2, 0.5, -0.1, 0.7, ...]  # 相似向量
"今天天气真好" → [-0.3, 0.1, 0.6, -0.2, ...]  # 不相似向量
```

**相似度计算**：

```python
# 余弦相似度
similarity = cos(θ) = (A · B) / (||A|| × ||B||)

# 示例
向量A = [0.2, 0.5, -0.1]
向量B = [0.2, 0.5, -0.1]
相似度 = 1.0  # 完全相同

向量C = [-0.3, 0.1, 0.6]
相似度 = -0.2  # 不相似
```

### 2.3 Embedding 模型

**作用**：将文本转换为向量

```
文本 → Embedding 模型 → 向量

示例：
"AI 技术" → text-embedding-ada-002 → [0.1, 0.3, -0.2, ...]
```

**常用模型**：

| 模型 | 维度 | 特点 |
|------|------|------|
| text-embedding-ada-002 | 1536 | OpenAI，效果好 |
| BGE-large-zh | 1024 | 中文优化 |
| DashScope Embedding | 1536 | 阿里云，中文好 |

---

## 3. 系统架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG 文档问答系统架构                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   前端页面    │────→│  FastAPI     │────→│   RAG 引擎   │   │
│  │  (HTML/JS)   │←────│   后端       │←────│              │   │
│  └──────────────┘     └──────────────┘     └──────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    RAG 引擎详细                          │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                         │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐         │   │
│  │  │ 文档加载  │───→│ 文本分割  │───→│ 向量化   │         │   │
│  │  │ Loader   │    │ Splitter │    │ Embedding│         │   │
│  │  └──────────┘    └──────────┘    └──────────┘         │   │
│  │       │                                   │             │   │
│  │       ↓                                   ↓             │   │
│  │  ┌──────────┐                      ┌──────────┐        │   │
│  │  │ 文档解析  │                      │ 向量数据库│        │   │
│  │  │ PDF/TXT  │                      │ Chroma   │        │   │
│  │  └──────────┘                      └──────────┘        │   │
│  │                                           │             │   │
│  │                                           ↓             │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐         │   │
│  │  │ 生成回答  │←───│ Prompt   │←───│ 检索器   │         │   │
│  │  │ LLM      │    │ 模板     │    │ Retriever│         │   │
│  │  └──────────┘    └──────────┘    └──────────┘         │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 数据流图

```
                    ┌─────────────────────────────────────────┐
                    │              索引阶段（离线）            │
                    └─────────────────────────────────────────┘
                    
文档上传 (PDF/TXT)
       │
       ↓
┌──────────────┐
│ 文档加载器    │  读取文件内容
│ loader.py    │
└──────────────┘
       │
       ↓
┌──────────────┐
│ 文本分割器    │  按 chunk_size 分块
│ splitter.py  │  chunk_overlap 保持上下文
└──────────────┘
       │
       ↓
┌──────────────┐
│ Embedding    │  文本转向量
│ 模型         │
└──────────────┘
       │
       ↓
┌──────────────┐
│ 向量数据库    │  存储向量 + 元数据
│ Chroma       │
└──────────────┘


                    ┌─────────────────────────────────────────┐
                    │              查询阶段（在线）            │
                    └─────────────────────────────────────────┘

用户提问: "如何申请报销？"
       │
       ↓
┌──────────────┐
│ 问题向量化    │  将问题转为向量
└──────────────┘
       │
       ↓
┌──────────────┐
│ 相似度搜索    │  找到最相似的 K 个文档
│ Top-K        │
└──────────────┘
       │
       ↓
┌──────────────┐
│ 构建 Prompt  │  问题 + 检索到的文档
└──────────────┘
       │
       ↓
┌──────────────┐
│ LLM 生成     │  基于上下文生成回答
└──────────────┘
       │
       ↓
返回回答 + 来源
```

---

## 4. 代码逐行解析

### 4.1 核心文件结构

```
projects/rag-doc-qa/
├── app/
│   ├── main.py           # FastAPI 入口
│   ├── config.py         # 配置管理
│   ├── api/
│   │   ├── chat.py       # 对话接口
│   │   └── upload.py     # 上传接口
│   └── rag/
│       ├── loader.py     # 文档加载器
│       ├── splitter.py   # 文本分割器
│       ├── vectorstore.py # 向量存储
│       └── chain.py      # RAG 链 ⭐
└── requirements.txt
```

### 4.2 chain.py 逐行解析

```python
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
```

**导入说明**：

| 模块 | 作用 | 类比 |
|------|------|------|
| `Document` | 文档数据结构 | 一个文档 = 内容 + 元数据 |
| `ChatOpenAI` | LLM 调用封装 | 调用 DeepSeek API |
| `ChatPromptTemplate` | Prompt 模板 | 填空题模板 |
| `StrOutputParser` | 输出解析器 | 提取 LLM 回答文本 |
| `RunnablePassthrough` | 透传组件 | 直接传递用户问题 |

---

```python
def format_docs(docs: List[Document]) -> str:
    """将文档列表格式化为字符串"""
    return "\n\n".join(doc.page_content for doc in docs)
```

**作用**：将检索到的多个文档合并成一个字符串

**示例**：
```python
docs = [
    Document(page_content="报销流程：1. 填写申请表"),
    Document(page_content="2. 提交发票和收据"),
    Document(page_content="3. 等待审批")
]

format_docs(docs)
# 输出：
# "报销流程：1. 填写申请表
#
# 2. 提交发票和收据
#
# 3. 等待审批"
```

---

```python
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
```

**作用**：获取已创建的向量数据库

**原理**：
```
向量数据库 = 存储向量的仓库
集合(Collection) = 一组相关文档的向量
```

---

```python
    # 创建检索器
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}  # 返回最相关的3个文档
    )
```

**作用**：将向量数据库转换为检索器

**参数说明**：
- `k=3`：返回最相似的 3 个文档块
- `k` 越大：上下文越完整，但可能引入噪音
- `k` 越小：回答越精准，但可能遗漏信息

**检索过程**：
```
用户问题 → 向量化 → 与所有文档向量计算相似度 → 返回 Top-3
```

---

```python
    # 创建 LLM
    llm = ChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        openai_api_key=settings.DEEPSEEK_API_KEY,
        openai_api_base=settings.DEEPSEEK_BASE_URL,
        temperature=0.3,  # 低温度，更稳定
    )
```

**参数说明**：

| 参数 | 值 | 作用 |
|------|-----|------|
| `model` | deepseek-chat | 使用的模型 |
| `temperature` | 0.3 | 控制随机性（0-1） |

**temperature 解释**：
```
temperature = 0.0 → 最确定，每次回答相同
temperature = 0.3 → 较稳定，适合问答
temperature = 0.7 → 较随机，适合创作
temperature = 1.0 → 最随机，可能胡说
```

---

```python
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
```

**Prompt 设计解析**：

```
┌─────────────────────────────────────────────────────────┐
│                    Prompt 结构                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 角色设定: "你是一个专业的文档问答助手"               │
│     → 让 LLM 进入专业问答模式                           │
│                                                         │
│  2. 约束条件: "只使用参考资料中的信息"                   │
│     → 减少幻觉，强制基于检索内容回答                     │
│                                                         │
│  3. 兜底策略: "如果资料中没有..."                        │
│     → 处理无法回答的情况                                 │
│                                                         │
│  4. 输出要求: "简洁明了，直接回答"                       │
│     → 控制输出风格                                       │
│                                                         │
│  5. 变量占位符:                                          │
│     - {context} → 检索到的文档内容                       │
│     - {question} → 用户问题                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

```python
    # 创建 RAG 链
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever
```

**LangChain 表达式语言（LCEL）解析**：

```python
# 这是一个管道语法，数据从左到右流动

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    # ↑ 第1步：构建输入
    # context = 检索文档 | 格式化为字符串
    # question = 直接传递用户问题
    
    | prompt
    # ↑ 第2步：填充 Prompt 模板
    # 将 context 和 question 填入模板
    
    | llm
    # ↑ 第3步：调用 LLM
    # 发送给 DeepSeek API
    
    | StrOutputParser()
    # ↑ 第4步：解析输出
    # 提取 LLM 回答文本
)
```

**执行流程图**：

```
用户输入: "如何申请报销？"
            │
            ↓
┌─────────────────────────────────────────────────────────┐
│  Step 1: 构建输入                                        │
│  {                                                      │
│    "context": retriever("如何申请报销？") | format_docs, │
│    "question": "如何申请报销？"                          │
│  }                                                      │
│  ↓                                                      │
│  {                                                      │
│    "context": "报销流程：1.填写申请表\n\n2.提交发票...",  │
│    "question": "如何申请报销？"                          │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
            │
            ↓
┌─────────────────────────────────────────────────────────┐
│  Step 2: 填充 Prompt                                     │
│  "你是一个专业的文档问答助手...                          │
│   参考资料：报销流程：1.填写申请表...                     │
│   问题：如何申请报销？                                   │
│   回答："                                                │
└─────────────────────────────────────────────────────────┘
            │
            ↓
┌─────────────────────────────────────────────────────────┐
│  Step 3: 调用 LLM                                        │
│  DeepSeek API → 生成回答                                 │
└─────────────────────────────────────────────────────────┘
            │
            ↓
┌─────────────────────────────────────────────────────────┐
│  Step 4: 解析输出                                        │
│  "申请报销需要以下步骤：1.填写申请表 2.提交发票..."      │
└─────────────────────────────────────────────────────────┘
```

---

```python
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
```

**函数流程**：

```
ask_question("如何申请报销？")
       │
       ↓
┌─────────────────────────────────────┐
│ 1. 创建 RAG 链                      │
│    rag_chain, retriever = ...       │
└─────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│ 2. 检索相关文档                      │
│    relevant_docs = retriever.invoke │
│    → [Document1, Document2, ...]    │
└─────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│ 3. 生成回答                         │
│    answer = rag_chain.invoke        │
│    → "申请报销需要..."              │
└─────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────┐
│ 4. 格式化来源                       │
│    sources = [                      │
│      {"content": "...", "metadata": │
│       {"source": "file.pdf"}},      │
│      ...                            │
│    ]                                │
└─────────────────────────────────────┘
       │
       ↓
返回 {
    "answer": "申请报销需要...",
    "sources": [...]
}
```

### 4.3 loader.py 解析

```python
"""
文档加载器
支持 TXT 和 PDF 文件
"""
from langchain_community.document_loaders import TextLoader, PyPDFLoader

def load_document(file_path: str):
    """根据文件类型加载文档"""
    if file_path.endswith('.txt'):
        loader = TextLoader(file_path, encoding='utf-8')
    elif file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_path}")
    
    return loader.load()
```

**工作原理**：
```
TXT 文件 → TextLoader → 读取文本内容 → [Document]
PDF 文件 → PyPDFLoader → 解析 PDF → [Document]

Document 结构：
{
    "page_content": "文档内容...",
    "metadata": {"source": "file.pdf", "page": 1}
}
```

### 4.4 splitter.py 解析

```python
"""
文本分割器
将长文档分成小块
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_documents(docs, chunk_size=500, chunk_overlap=50):
    """分割文档"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,      # 每块最大字符数
        chunk_overlap=chunk_overlap, # 块之间重叠字符数
        separators=["\n\n", "\n", "。", "！", "？", "，", " "]
    )
    return splitter.split_documents(docs)
```

**参数说明**：

| 参数 | 值 | 作用 |
|------|-----|------|
| `chunk_size` | 500 | 每块最大 500 字符 |
| `chunk_overlap` | 50 | 块之间重叠 50 字符 |

**为什么需要分块？**

```
问题：LLM 有上下文长度限制
     - GPT-4: 128K tokens
     - DeepSeek: 64K tokens

方案：将长文档分成小块
     - 只检索相关块
     - 减少 Token 消耗
     - 提高检索精度
```

**分块示例**：

```
原文档（2000字符）:
┌─────────────────────────────────────────────────────────┐
│ 第一章：公司简介                                         │
│ 我们公司成立于2020年...（500字符）                       │
├─────────────────────────────────────────────────────────┤
│ 第二章：报销政策                                         │
│ 报销流程如下...（500字符）                               │
├─────────────────────────────────────────────────────────┤
│ 第三章：请假制度                                         │
│ 请假需要提前...（500字符）                               │
├─────────────────────────────────────────────────────────┤
│ 第四章：培训计划                                         │
│ 新员工培训...（500字符）                                 │
└─────────────────────────────────────────────────────────┘

分块后（chunk_size=500, chunk_overlap=50）:
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 块1: 公司简介 │ │ 块2: 报销政策 │ │ 块3: 请假制度 │ │ 块4: 培训计划 │
│ 500字符      │ │ 500字符      │ │ 500字符      │ │ 500字符      │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        ↑___________↑ 重叠50字符
```

**为什么需要重叠？**

```
问题：如果在块边界切断句子，语义会丢失

示例：
原文："报销流程如下：1.填写申请表 2.提交发票"
      ↓
块1："报销流程如下：1.填写申请表"  ← 缺少后续步骤
块2："2.提交发票"                ← 缺少上下文

解决方案：重叠
块1："报销流程如下：1.填写申请表"
块2："1.填写申请表 2.提交发票"   ← 包含完整上下文
```

### 4.5 vectorstore.py 解析

```python
"""
向量存储
管理 Chroma 向量数据库
"""
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

def get_vectorstore(collection_name: str):
    """获取向量存储"""
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",
        openai_api_key=settings.DASHSCOPE_API_KEY,
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )
    
    return vectorstore
```

**工作原理**：

```
┌─────────────────────────────────────────────────────────┐
│                  向量存储流程                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 创建 Embedding 模型                                 │
│     OpenAIEmbeddings → 调用 DashScope API               │
│                                                         │
│  2. 创建 Chroma 实例                                    │
│     Chroma(                                             │
│         collection_name="default",  # 集合名             │
│         embedding_function=embeddings,  # Embedding 模型 │
│         persist_directory="./chroma_db"  # 持久化目录    │
│     )                                                   │
│                                                         │
│  3. 添加文档                                            │
│     vectorstore.add_documents(docs)                     │
│     → 自动向量化并存储                                   │
│                                                         │
│  4. 检索                                                │
│     vectorstore.similarity_search(query)                │
│     → 返回相似文档                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Chroma 数据库结构**：

```
chroma_db/
├── chroma.sqlite3        # SQLite 数据库
└── [uuid]/               # 向量数据
    ├── data_level0.bin   # 向量数据
    ├── header.bin        # 头信息
    ├── length.bin        # 长度信息
    └── link_lists.bin    # 链接列表
```

---

## 5. 关键技术详解

### 5.1 Embedding 向量化

**什么是 Embedding？**

```
将文本转换为数值向量的过程

示例：
"报销" → [0.2, 0.5, -0.1, 0.8, ...]
"请假" → [0.1, 0.4, -0.2, 0.7, ...]
"天气" → [-0.3, 0.1, 0.6, -0.2, ...]

相似的文本 → 相似的向量
不相似的文本 → 不相似的向量
```

**Embedding 模型选择**：

| 模型 | 维度 | 中文效果 | 价格 |
|------|------|---------|------|
| text-embedding-ada-002 | 1536 | 好 | $0.0001/1K tokens |
| BGE-large-zh | 1024 | 很好 | 免费 |
| DashScope Embedding | 1536 | 很好 | ¥0.0007/1K tokens |

### 5.2 向量数据库

**为什么需要向量数据库？**

```
传统数据库（MySQL）：
- 存储结构化数据
- 支持精确查询
- 不支持相似度搜索

向量数据库（Chroma）：
- 存储向量
- 支持相似度搜索
- 专为 AI 设计
```

**向量数据库对比**：

| 数据库 | 特点 | 适用场景 |
|--------|------|---------|
| Chroma | 轻量、本地、易用 | 原型开发、小规模 |
| Milvus | 分布式、高性能 | 大规模生产 |
| Qdrant | Rust 实现、高性能 | 高性能需求 |
| Pinecone | 全托管、易用 | 快速上线 |

### 5.3 相似度搜索算法

**余弦相似度**：

```python
import numpy as np

def cosine_similarity(a, b):
    """计算余弦相似度"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 示例
a = [0.2, 0.5, -0.1]  # "报销"
b = [0.2, 0.5, -0.1]  # "报销"
c = [-0.3, 0.1, 0.6]  # "天气"

print(cosine_similarity(a, b))  # 1.0（完全相同）
print(cosine_similarity(a, c))  # -0.2（不相似）
```

**L2 距离（欧氏距离）**：

```python
def l2_distance(a, b):
    """计算 L2 距离"""
    return np.sqrt(np.sum((a - b) ** 2))

# 距离越小，越相似
```

### 5.4 Prompt Engineering

**Prompt 设计原则**：

```
┌─────────────────────────────────────────────────────────┐
│                  Prompt 设计原则                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 角色设定（Role）                                     │
│     "你是一个专业的文档问答助手"                         │
│     → 让 LLM 进入专业模式                               │
│                                                         │
│  2. 任务描述（Task）                                     │
│     "请基于参考资料回答问题"                             │
│     → 明确任务目标                                       │
│                                                         │
│  3. 约束条件（Constraints）                              │
│     "只使用参考资料中的信息"                             │
│     → 减少幻觉                                          │
│                                                         │
│  4. 输出格式（Format）                                   │
│     "回答要简洁明了"                                     │
│     → 控制输出风格                                       │
│                                                         │
│  5. 示例（Examples）                                     │
│     提供输入输出示例                                     │
│     → 引导 LLM 输出格式                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Prompt 模板示例**：

```python
# 基础模板
prompt = ChatPromptTemplate.from_template("""
请回答以下问题。

参考资料：{context}
问题：{question}
回答：""")

# 优化模板
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
```

---

## 6. 常见问题与优化

### 6.1 检索质量差

**问题**：检索到的文档不相关

**原因**：
1. 分块太大/太小
2. Embedding 模型效果差
3. 查询和文档表述不同

**解决方案**：

```python
# 1. 调整分块参数
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,  # 减小块大小
    chunk_overlap=100  # 增加重叠
)

# 2. 使用更好的 Embedding 模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# 3. Query Rewrite
def rewrite_query(question):
    """重写查询，提高检索效果"""
    prompt = f"将以下问题重写为更适合搜索的形式：{question}"
    return llm.invoke(prompt)
```

### 6.2 回答质量差

**问题**：回答不准确或幻觉

**原因**：
1. Prompt 设计不合理
2. 检索到的文档不相关
3. temperature 太高

**解决方案**：

```python
# 1. 优化 Prompt
prompt = ChatPromptTemplate.from_template("""
请严格基于参考资料回答问题。如果资料中没有相关信息，请明确说明。

参考资料：{context}
问题：{question}
回答：""")

# 2. 降低 temperature
llm = ChatOpenAI(temperature=0.1)

# 3. 增加检索数量
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
```

### 6.3 响应速度慢

**问题**：查询响应时间长

**原因**：
1. 向量数据库大
2. LLM 调用慢
3. 网络延迟

**解决方案**：

```python
# 1. 使用更快的向量数据库
# Chroma → Qdrant

# 2. 缓存常见问题
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_ask(question):
    return ask_question(question)

# 3. 异步处理
import asyncio

async def async_ask(question):
    return await rag_chain.ainvoke(question)
```

---

## 7. 面试问答

### Q1: 什么是 RAG？为什么需要 RAG？

**标准答案**：
> RAG（Retrieval-Augmented Generation）是检索增强生成的缩写。它通过检索外部知识库来增强 LLM 的回答能力。RAG 解决了 LLM 的三个核心问题：知识截止（训练数据有时间限制）、幻觉（编造信息）、无法访问私有数据。

### Q2: RAG 的核心流程是什么？

**标准答案**：
> RAG 分为三个阶段：
> 1. **索引阶段**：文档 → 分块 → 向量化 → 存入向量数据库
> 2. **检索阶段**：用户问题 → 向量化 → 相似度搜索 → 返回 Top-K 文档
> 3. **生成阶段**：问题 + 检索文档 → Prompt 模板 → LLM → 生成回答

### Q3: 为什么需要分块（Chunking）？

**标准答案**：
> 分块的原因有三个：
> 1. **上下文限制**：LLM 有最大上下文长度，无法处理整个文档
> 2. **检索精度**：小块更精确，大块可能包含无关信息
> 3. **成本控制**：只检索相关块，减少 Token 消耗

### Q4: 如何选择 chunk_size？

**标准答案**：
> chunk_size 的选择需要平衡：
> - **太小（<100）**：语义不完整，检索效果差
> - **太大（>1000）**：包含噪音，成本高
> - **推荐**：300-800 字符，根据文档类型调整
> 
> 技术文档可以大一些（800-1000），对话记录应该小一些（200-400）。

### Q5: 什么是 Embedding？

**标准答案**：
> Embedding 是将文本转换为数值向量的过程。相似的文本会生成相似的向量。通过计算向量之间的距离，可以衡量文本的语义相似度。常用的 Embedding 模型有 OpenAI text-embedding-ada-002、BGE 等。

### Q6: 向量数据库和传统数据库有什么区别？

**标准答案**：
> | 对比项 | 传统数据库 | 向量数据库 |
> |--------|-----------|-----------|
> | 数据类型 | 结构化数据 | 向量 |
> | 查询方式 | 精确查询 | 相似度搜索 |
> | 索引 | B+树 | HNSW/IVF |
> | 适用场景 | 事务处理 | AI 检索 |

### Q7: 如何评估 RAG 系统的效果？

**标准答案**：
> 常用的评估指标：
> 1. **准确率（Accuracy）**：回答是否正确
> 2. **召回率（Recall）**：是否找到所有相关文档
> 3. **相关性（Relevance）**：检索的文档是否相关
> 4. **忠实度（Faithfulness）**：回答是否基于检索内容
> 
> 可以使用 RAGAS、TruLens 等框架进行自动化评估。

### Q8: 如何优化 RAG 系统？

**标准答案**：
> 优化方向：
> 1. **检索优化**：混合检索（向量 + BM25）、Rerank 重排序
> 2. **查询优化**：Query Rewrite、HyDE
> 3. **分块优化**：调整 chunk_size、使用语义分块
> 4. **Prompt 优化**：更好的提示词模板
> 5. **模型优化**：使用更大的 Embedding 模型

---

## 📚 扩展阅读

- [LangChain RAG 文档](https://python.langchain.com/docs/tutorials/rag/)
- [Chroma 官方文档](https://docs.trychroma.com/)
- [RAGAS 评估框架](https://github.com/explodinggradients/ragas)
- [Prompt Engineering 指南](https://www.promptingguide.ai/)

---

**最后更新：** 2026-06-30
