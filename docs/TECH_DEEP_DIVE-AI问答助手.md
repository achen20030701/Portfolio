# 🔬 AI 智能问答助手 - 技术深度解析

> 本文档详细解析 AI 问答助手的架构、云函数部署和前后端交互原理
> 适合：想了解 Serverless 架构和云函数开发的开发者

---

## 📑 目录

1. [项目概述](#1-项目概述)
2. [架构设计](#2-架构设计)
3. [云函数原理](#3-云函数原理)
4. [代码逐行解析](#4-代码逐行解析)
5. [关键技术详解](#5-关键技术详解)
6. [部署流程](#6-部署流程)
7. [面试问答](#7-面试问答)

---

## 1. 项目概述

### 1.1 项目定位

**AI 智能问答助手** 是一个基于云函数的轻量级 AI 对话应用

```
核心特点：
✅ Serverless 架构，无需管理服务器
✅ 云函数 + 云数据库，全托管
✅ 支持多轮对话
✅ 自动保存历史记录
```

### 1.2 技术栈

| 层级 | 技术 | 作用 |
|------|------|------|
| 前端 | HTML + JavaScript | 用户界面 |
| 后端 | 腾讯云云函数 | 处理请求 |
| 数据库 | 腾讯云数据库 | 存储对话 |
| AI | DeepSeek API | 生成回答 |

### 1.3 与 RAG 项目的区别

| 对比项 | AI 问答助手 | RAG 文档问答 |
|--------|------------|--------------|
| 知识来源 | LLM 通用知识 | 上传的文档 |
| 检索机制 | 无 | 向量检索 |
| 部署方式 | 云函数 | FastAPI |
| 适用场景 | 通用问答 | 文档问答 |

---

## 2. 架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI 问答助手架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   前端页面    │────→│  云函数      │────→│  DeepSeek   │   │
│  │  (HTML/JS)   │←────│  (Node.js)  │←────│   API       │   │
│  └──────────────┘     └──────────────┘     └──────────────┘   │
│                              │                                  │
│                              ↓                                  │
│                       ┌──────────────┐                         │
│                       │  云数据库    │                         │
│                       │  (MongoDB)  │                         │
│                       └──────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Serverless vs 传统架构

```
传统架构：
┌─────────────────────────────────────────────────────────┐
│  开发者需要管理：                                        │
│  - 服务器购买/租赁                                       │
│  - 操作系统安装                                          │
│  - 运行环境配置                                          │
│  - 负载均衡                                              │
│  - 自动扩缩容                                            │
│  - 安全防护                                              │
│  - 监控告警                                              │
└─────────────────────────────────────────────────────────┘

Serverless 架构：
┌─────────────────────────────────────────────────────────┐
│  云厂商管理：                                            │
│  - 服务器 ✓                                              │
│  - 操作系统 ✓                                            │
│  - 运行环境 ✓                                            │
│  - 负载均衡 ✓                                            │
│  - 自动扩缩容 ✓                                          │
│  - 安全防护 ✓                                            │
│  - 监控告警 ✓                                            │
│                                                         │
│  开发者只需关注：                                        │
│  - 业务代码                                              │
│  - 配置参数                                              │
└─────────────────────────────────────────────────────────┘
```

### 2.3 请求流程图

```
用户输入: "什么是人工智能？"
       │
       ↓
┌─────────────────────────────────────────────────────────┐
│  Step 1: 前端发送请求                                    │
│  POST /chat                                             │
│  Body: { "message": "什么是人工智能？" }                 │
└─────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────┐
│  Step 2: 云函数接收请求                                  │
│  解析请求体 → 提取 message                               │
└─────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────┐
│  Step 3: 保存用户消息                                    │
│  数据库.insert({ role: "user", content: "..." })        │
└─────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────┐
│  Step 4: 调用 DeepSeek API                              │
│  POST https://api.deepseek.com/v1/chat/completions      │
│  Body: {                                                │
│    model: "deepseek-chat",                              │
│    messages: [                                          │
│      { role: "system", content: "你是AI助手" },         │
│      { role: "user", content: "什么是人工智能？" }       │
│    ]                                                    │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────┐
│  Step 5: 保存 AI 回复                                    │
│  数据库.insert({ role: "assistant", content: "..." })   │
└─────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────┐
│  Step 6: 返回响应                                        │
│  { "reply": "人工智能是..." }                           │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 云函数原理

### 3.1 什么是云函数？

**云函数（Cloud Function）** = 在云端运行的函数，无需管理服务器

```
传统方式：
开发者 → 编写代码 → 部署到服务器 → 服务器运行代码

云函数方式：
开发者 → 编写函数 → 上传到云平台 → 云平台自动运行
```

### 3.2 云函数特点

```
┌─────────────────────────────────────────────────────────┐
│                    云函数特点                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 事件驱动                                             │
│     - HTTP 请求触发                                      │
│     - 数据库变更触发                                     │
│     - 定时触发                                           │
│                                                         │
│  2. 按需执行                                             │
│     - 有请求才运行                                       │
│     - 无请求不收费                                       │
│                                                         │
│  3. 自动扩缩容                                           │
│     - 并发高时自动扩容                                   │
│     - 并发低时自动缩容                                   │
│                                                         │
│  4. 免运维                                               │
│     - 无需管理服务器                                     │
│     - 无需关心操作系统                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.3 云函数 vs 传统后端

| 对比项 | 云函数 | 传统后端 |
|--------|--------|---------|
| 服务器管理 | 无需 | 需要 |
| 扩缩容 | 自动 | 手动 |
| 计费方式 | 按调用次数 | 按服务器时长 |
| 冷启动 | 有 | 无 |
| 适用场景 | 轻量级、事件驱动 | 复杂业务 |

### 3.4 冷启动问题

**什么是冷启动？**

```
第一次请求：
┌─────────────────────────────────────────────────────────┐
│  用户请求 → 加载运行环境 → 执行函数 → 返回结果          │
│              ↑                                          │
│              这一步需要时间（100ms-3s）                  │
└─────────────────────────────────────────────────────────┘

后续请求：
┌─────────────────────────────────────────────────────────┐
│  用户请求 → 执行函数 → 返回结果                          │
│              ↑                                          │
│              环境已加载，直接执行                         │
└─────────────────────────────────────────────────────────┘
```

**优化方案**：

```javascript
// 方案 1：保持函数温热（定时触发）
// 每 5 分钟触发一次，保持函数活跃

// 方案 2：使用预留实例
// 腾讯云支持预留实例，避免冷启动

// 方案 3：减少依赖
// 减少 npm 包数量，加快加载速度
```

---

## 4. 代码逐行解析

### 4.1 项目结构

```
projects/ai-assistant/
├── cloudfunctions/
│   └── ai-doc-qa/
│       ├── index.js        # 云函数入口 ⭐
│       ├── package.json    # 依赖配置
│       └── package-lock.json
├── frontend/
│   ├── index_new.html      # 前端页面
│   └── app.py              # 本地测试用
├── .env                    # 环境变量
├── .env.example            # 环境变量示例
└── requirements.txt        # Python 依赖
```

### 4.2 index.js 逐行解析

```javascript
/**
 * 腾讯云 CloudBase 云函数
 * AI 智能文档问答助手
 */
const cloud = require('@cloudbase/node-sdk');

// 初始化 CloudBase
const app = cloud.init({
  env: 'cg-work-d3geug43lc211422a'
});

// 获取数据库引用
const db = app.database();
const messagesCollection = db.collection('messages');
```

**代码解析**：

```javascript
// 1. 导入 CloudBase SDK
const cloud = require('@cloudbase/node-sdk');
// @cloudbase/node-sdk 是腾讯云 CloudBase 的 Node.js SDK
// 提供数据库、存储、云函数等功能

// 2. 初始化 CloudBase
const app = cloud.init({
  env: 'cg-work-d3geug43lc211422a'  // 环境 ID
});
// env 是 CloudBase 环境的唯一标识
// 每个环境有独立的数据库、存储等资源

// 3. 获取数据库引用
const db = app.database();
// 获取 CloudBase 数据库实例

// 4. 获取集合引用
const messagesCollection = db.collection('messages');
// 集合类似于 MySQL 中的表
// messages 集合存储所有对话消息
```

**数据库结构**：

```
messages 集合
┌─────────────────────────────────────────────────────────┐
│  {                                                      │
│    _id: "auto_generated_id",    // 自动生成的 ID        │
│    role: "user",                // 消息角色              │
│    content: "什么是人工智能？",  // 消息内容              │
│    timestamp: "2024-01-01..."   // 时间戳                │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
```

---

```javascript
/**
 * 云函数主入口
 */
exports.main = async (event, context) => {
  try {
    const { httpMethod, path, body, queryStringParameters } = event;

    // 解析请求体
    let requestData = {};
    if (body) {
      requestData = typeof body === 'string' ? JSON.parse(body) : body;
    }

    // 路由处理
    switch (path) {
      case '/health':
        return successResponse({ status: 'healthy', version: '1.0.0' });

      case '/chat':
        if (httpMethod !== 'POST') {
          return errorResponse(405, 'Method not allowed');
        }
        return await handleChat(requestData);

      case '/history':
        if (httpMethod !== 'GET') {
          return errorResponse(405, 'Method not allowed');
        }
        return await handleGetHistory(queryStringParameters);

      case '/clear':
        if (httpMethod !== 'POST') {
          return errorResponse(405, 'Method not allowed');
        }
        return await handleClearHistory();

      default:
        return errorResponse(404, '接口不存在');
    }

  } catch (error) {
    console.error('云函数错误：', error);
    return errorResponse(500, error.message);
  }
};
```

**代码解析**：

```javascript
// exports.main 是云函数的入口函数
// 当有 HTTP 请求到达时，云平台会调用这个函数

// event 参数包含请求信息：
event = {
  httpMethod: 'POST',           // 请求方法
  path: '/chat',                // 请求路径
  body: '{"message": "你好"}',   // 请求体
  queryStringParameters: {}     // URL 查询参数
}

// context 参数包含运行环境信息
context = {
  requestId: 'xxx',    // 请求 ID
  functionName: 'xxx', // 函数名
  memory_limit_in_mb: 256  // 内存限制
}
```

**路由设计**：

```
┌─────────────────────────────────────────────────────────┐
│                    API 路由表                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  GET  /health   → 健康检查                              │
│  POST /chat     → 发送消息，获取 AI 回复                 │
│  GET  /history  → 获取历史消息                           │
│  POST /clear    → 清空历史消息                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

```javascript
/**
 * 处理聊天请求
 */
async function handleChat(body) {
  const { message, collection_name = 'default' } = body;

  if (!message) {
    return errorResponse(400, '消息不能为空');
  }

  // 保存用户消息到数据库
  await saveMessage('user', message);

  // 调用 DeepSeek API 获取回答
  const reply = await callDeepSeekAPI(message);

  // 保存 AI 回复到数据库
  await saveMessage('assistant', reply);

  return successResponse({
    reply: reply,
    sources: [] // 简化版本，不包含来源
  });
}
```

**代码解析**：

```javascript
// 1. 解构请求体
const { message, collection_name = 'default' } = body;
// 从请求体中提取 message 和 collection_name
// collection_name 有默认值 'default'

// 2. 参数校验
if (!message) {
  return errorResponse(400, '消息不能为空');
}
// 如果消息为空，返回 400 错误

// 3. 保存用户消息
await saveMessage('user', message);
// 将用户消息保存到数据库

// 4. 调用 AI API
const reply = await callDeepSeekAPI(message);
// 调用 DeepSeek API 获取 AI 回复

// 5. 保存 AI 回复
await saveMessage('assistant', reply);
// 将 AI 回复保存到数据库

// 6. 返回响应
return successResponse({
  reply: reply,
  sources: []
});
// 返回 AI 回复给前端
```

---

```javascript
/**
 * 调用 DeepSeek API
 */
async function callDeepSeekAPI(message) {
  const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;
  const DEEPSEEK_BASE_URL = 'https://api.deepseek.com';

  try {
    const response = await fetch(`${DEEPSEEK_BASE_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEEPSEEK_API_KEY}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          {
            role: 'system',
            content: '你是一个专业的 AI 助手，请用中文回答问题。'
          },
          {
            role: 'user',
            content: message
          }
        ],
        temperature: 0.7,
        max_tokens: 2000
      })
    });

    const data = await response.json();

    if (data.choices && data.choices[0]) {
      return data.choices[0].message.content;
    } else {
      throw new Error('API 返回格式错误');
    }

  } catch (error) {
    console.error('调用 DeepSeek API 失败：', error);
    throw new Error('调用 AI 服务失败，请稍后重试');
  }
}
```

**代码解析**：

```javascript
// 1. 获取 API Key
const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;
// process.env 是 Node.js 的环境变量
// 在云函数配置中设置环境变量

// 2. 构建请求
const response = await fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${DEEPSEEK_API_KEY}`
    // Authorization 头用于身份验证
    // Bearer 是认证类型
  },
  body: JSON.stringify({
    model: 'deepseek-chat',
    messages: [
      {
        role: 'system',
        content: '你是一个专业的 AI 助手，请用中文回答问题。'
      },
      {
        role: 'user',
        content: message
      }
    ],
    temperature: 0.7,  // 控制随机性
    max_tokens: 2000   // 最大输出长度
  })
});

// 3. 解析响应
const data = await response.json();
// 响应格式：
// {
//   choices: [
//     {
//       message: {
//         content: "AI 的回答"
//       }
//     }
//   ]
// }

// 4. 提取回答
if (data.choices && data.choices[0]) {
  return data.choices[0].message.content;
}
```

**API 请求格式**：

```json
{
  "model": "deepseek-chat",
  "messages": [
    {
      "role": "system",
      "content": "你是一个专业的 AI 助手，请用中文回答问题。"
    },
    {
      "role": "user",
      "content": "什么是人工智能？"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**messages 角色说明**：

| 角色 | 作用 | 示例 |
|------|------|------|
| `system` | 系统提示，设定 AI 行为 | "你是一个专业的 AI 助手" |
| `user` | 用户消息 | "什么是人工智能？" |
| `assistant` | AI 回复 | "人工智能是..." |

---

```javascript
/**
 * 保存消息到数据库
 */
async function saveMessage(role, content) {
  try {
    await messagesCollection.add({
      data: {
        role: role,
        content: content,
        timestamp: db.serverDate()
      }
    });
  } catch (error) {
    console.error('保存消息失败：', error);
  }
}
```

**代码解析**：

```javascript
// messagesCollection.add() 向集合中添加一条记录
await messagesCollection.add({
  data: {
    role: role,           // "user" 或 "assistant"
    content: content,     // 消息内容
    timestamp: db.serverDate()  // 服务器时间
  }
});

// db.serverDate() 返回服务器时间
// 避免客户端时间不准确的问题
```

**数据库记录示例**：

```json
{
  "_id": "auto_generated_id",
  "role": "user",
  "content": "什么是人工智能？",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

---

```javascript
/**
 * 获取历史消息
 */
async function handleGetHistory(queryParams) {
  const limit = parseInt(queryParams?.limit) || 50;

  try {
    const result = await messagesCollection
      .orderBy('timestamp', 'desc')
      .limit(limit)
      .get();

    const messages = result.data.reverse(); // 按时间正序

    return successResponse({ messages });
  } catch (error) {
    console.error('获取历史失败：', error);
    return errorResponse(500, '获取历史失败');
  }
}
```

**代码解析**：

```javascript
// 1. 获取查询参数
const limit = parseInt(queryParams?.limit) || 50;
// 从 URL 查询参数中获取 limit
// 默认返回 50 条记录

// 2. 查询数据库
const result = await messagesCollection
  .orderBy('timestamp', 'desc')  // 按时间倒序
  .limit(limit)                   // 限制返回数量
  .get();                         // 执行查询

// 3. 反转顺序
const messages = result.data.reverse();
// 数据库返回的是倒序（最新的在前）
// 反转后变成正序（最早的在前）

// 4. 返回结果
return successResponse({ messages });
```

**查询链**：

```
messagesCollection
    .orderBy('timestamp', 'desc')  // 排序
    .limit(50)                      // 限制数量
    .get();                         // 执行查询

等价于 SQL：
SELECT * FROM messages 
ORDER BY timestamp DESC 
LIMIT 50
```

---

```javascript
/**
 * 清空历史消息
 */
async function handleClearHistory() {
  try {
    // 获取所有消息 ID
    const result = await messagesCollection.get();
    const ids = result.data.map(item => item._id);

    // 批量删除
    if (ids.length > 0) {
      await messagesCollection.where({
        _id: db.command.in(ids)
      }).remove();
    }

    return successResponse({ message: '历史已清空' });
  } catch (error) {
    console.error('清空历史失败：', error);
    return errorResponse(500, '清空历史失败');
  }
}
```

**代码解析**：

```javascript
// 1. 获取所有消息 ID
const result = await messagesCollection.get();
const ids = result.data.map(item => item._id);
// 获取所有记录的 _id 字段

// 2. 构建删除条件
db.command.in(ids)
// 等价于 SQL: WHERE _id IN ('id1', 'id2', ...)

// 3. 批量删除
await messagesCollection.where({
  _id: db.command.in(ids)
}).remove();
// 删除所有匹配的记录
```

---

```javascript
/**
 * 成功响应
 */
function successResponse(data) {
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    },
    body: JSON.stringify(data)
  };
}
```

**代码解析**：

```javascript
// 返回 HTTP 响应格式
{
  statusCode: 200,  // HTTP 状态码
  headers: {
    'Content-Type': 'application/json',  // 响应类型
    'Access-Control-Allow-Origin': '*',  // 允许跨域
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  },
  body: JSON.stringify(data)  // 响应体
}
```

**CORS 跨域配置**：

```
问题：前端和后端不在同一个域名
     前端：https://xxx.webapps.tcloudbase.com
     后端：https://xxx.ap-shanghai.app.tcloudbase.com

解决：设置 CORS 头
Access-Control-Allow-Origin: *  // 允许所有域名访问
```

---

## 5. 关键技术详解

### 5.1 Serverless 架构

**传统架构 vs Serverless**：

```
传统架构：
┌─────────────────────────────────────────────────────────┐
│  开发者负责：                                            │
│  - 购买/租赁服务器                                       │
│  - 安装操作系统                                          │
│  - 配置运行环境（Node.js、Python）                       │
│  - 部署代码                                              │
│  - 配置负载均衡                                          │
│  - 监控和告警                                            │
│  - 安全防护                                              │
│                                                         │
│  成本：按服务器时长付费（即使没有请求）                   │
└─────────────────────────────────────────────────────────┘

Serverless 架构：
┌─────────────────────────────────────────────────────────┐
│  云厂商负责：                                            │
│  - 服务器 ✓                                              │
│  - 操作系统 ✓                                            │
│  - 运行环境 ✓                                            │
│  - 负载均衡 ✓                                            │
│  - 监控告警 ✓                                            │
│  - 安全防护 ✓                                            │
│                                                         │
│  开发者负责：                                            │
│  - 编写业务代码                                          │
│  - 配置环境变量                                          │
│                                                         │
│  成本：按调用次数付费（无请求不收费）                     │
└─────────────────────────────────────────────────────────┘
```

### 5.2 云函数触发方式

```
┌─────────────────────────────────────────────────────────┐
│                    云函数触发方式                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. HTTP 触发                                           │
│     - API 网关触发                                      │
│     - 适合 Web 应用                                     │
│                                                         │
│  2. 定时触发                                            │
│     - Cron 表达式                                       │
│     - 适合定时任务                                       │
│                                                         │
│  3. 数据库触发                                          │
│     - 数据变更时触发                                     │
│     - 适合实时处理                                       │
│                                                         │
│  4. 对象存储触发                                        │
│     - 文件上传时触发                                     │
│     - 适合文件处理                                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.3 环境变量管理

**为什么需要环境变量？**

```
问题：API Key 不能硬编码在代码中
     - 安全风险：代码泄露会导致 Key 泄露
     - 灵活性：更换 Key 需要改代码

解决方案：环境变量
     - 存储在云平台配置中
     - 代码通过 process.env 读取
     - 不同环境使用不同配置
```

**配置方式**：

```
腾讯云云函数控制台：
┌─────────────────────────────────────────────────────────┐
│  环境变量配置                                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  变量名                    变量值                        │
│  ─────────────────────────────────────────────────────  │
│  DEEPSEEK_API_KEY         sk-xxx                        │
│  DEEPSEEK_BASE_URL        https://api.deepseek.com     │
│  DEEPSEEK_MODEL           deepseek-chat                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**代码中读取**：

```javascript
const apiKey = process.env.DEEPSEEK_API_KEY;
const baseUrl = process.env.DEEPSEEK_BASE_URL;
const model = process.env.DEEPSEEK_MODEL;
```

### 5.4 数据库设计

**集合设计**：

```
messages 集合
┌─────────────────────────────────────────────────────────┐
│  字段名        类型          说明                        │
│  ─────────────────────────────────────────────────────  │
│  _id          String       自动生成的唯一 ID             │
│  role          String       消息角色（user/assistant）    │
│  content       String       消息内容                     │
│  timestamp     Date         消息时间戳                   │
└─────────────────────────────────────────────────────────┘
```

**查询示例**：

```javascript
// 查询最近 50 条消息
const result = await messagesCollection
  .orderBy('timestamp', 'desc')
  .limit(50)
  .get();

// 查询用户消息
const userMessages = await messagesCollection
  .where({ role: 'user' })
  .get();

// 查询特定时间范围的消息
const messages = await messagesCollection
  .where({
    timestamp: db.command.gte(startTime)
  })
  .get();
```

---

## 6. 部署流程

### 6.1 云函数部署步骤

```
┌─────────────────────────────────────────────────────────┐
│                    云函数部署流程                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: 创建云函数                                     │
│  - 登录腾讯云控制台                                      │
│  - 进入 CloudBase 管理                                   │
│  - 创建云函数                                           │
│                                                         │
│  Step 2: 上传代码                                       │
│  - 打包 cloudfunctions/ai-doc-qa/ 目录                  │
│  - 上传 ZIP 文件                                        │
│  - 或使用 CLI 工具上传                                   │
│                                                         │
│  Step 3: 配置环境变量                                    │
│  - 添加 DEEPSEEK_API_KEY                                │
│  - 添加 DEEPSEEK_BASE_URL                               │
│  - 添加 DEEPSEEK_MODEL                                  │
│                                                         │
│  Step 4: 配置触发器                                      │
│  - 选择 HTTP 触发                                       │
│  - 配置路径和方法                                        │
│                                                         │
│  Step 5: 测试                                            │
│  - 使用 Postman 或 curl 测试                            │
│  - 检查日志和错误                                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 6.2 前端部署步骤

```
┌─────────────────────────────────────────────────────────┐
│                    前端部署流程                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: 修改 API 地址                                   │
│  - 打开 index_new.html                                  │
│  - 修改 API_BASE_URL 为云函数域名                        │
│                                                         │
│  Step 2: 上传到静态网站托管                               │
│  - 登录腾讯云控制台                                      │
│  - 进入 CloudBase 管理                                   │
│  - 开启静态网站托管                                      │
│  - 上传 HTML 文件                                        │
│                                                         │
│  Step 3: 配置域名                                        │
│  - 使用默认域名或绑定自定义域名                           │
│  - 配置 HTTPS 证书                                       │
│                                                         │
│  Step 4: 测试                                            │
│  - 访问网站                                              │
│  - 测试对话功能                                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 7. 面试问答

### Q1: 什么是 Serverless？

**标准答案**：
> Serverless（无服务器）是一种云计算架构，开发者无需管理服务器，只需编写业务代码。云厂商负责服务器的 provisioning、scaling、patching 等运维工作。Serverless 的核心特点包括：事件驱动、按需执行、自动扩缩容、按调用次数计费。

### Q2: 云函数和传统后端有什么区别？

**标准答案**：
> | 对比项 | 云函数 | 传统后端 |
> |--------|--------|---------|
> | 服务器管理 | 无需 | 需要 |
> | 扩缩容 | 自动 | 手动 |
> | 计费方式 | 按调用次数 | 按服务器时长 |
> | 冷启动 | 有 | 无 |
> | 适用场景 | 轻量级、事件驱动 | 复杂业务 |

### Q3: 什么是冷启动？如何优化？

**标准答案**：
> 冷启动是指云函数第一次被调用时，需要加载运行环境（如 Node.js），导致响应时间增加。优化方案包括：
> 1. **保持函数温热**：定时触发，保持函数活跃
> 2. **使用预留实例**：云厂商提供的预留实例，避免冷启动
> 3. **减少依赖**：减少 npm 包数量，加快加载速度
> 4. **选择轻量运行时**：如 Node.js 比 Java 冷启动更快

### Q4: 如何管理云函数的环境变量？

**标准答案**：
> 环境变量存储在云平台配置中，代码通过 `process.env` 读取。优点：
> 1. **安全性**：API Key 不硬编码在代码中
> 2. **灵活性**：不同环境使用不同配置
> 3. **易维护**：更换配置无需改代码

### Q5: 什么是 CORS？为什么需要配置？

**标准答案**：
> CORS（跨域资源共享）是浏览器的安全策略。当前端和后端不在同一个域名时，浏览器会阻止请求。解决方案是在后端响应中添加 CORS 头：
> ```
> Access-Control-Allow-Origin: *
> Access-Control-Allow-Methods: GET, POST, OPTIONS
> Access-Control-Allow-Headers: Content-Type
> ```

### Q6: 云函数适合什么场景？

**标准答案**：
> 云函数适合以下场景：
> 1. **API 服务**：轻量级 REST API
> 2. **事件处理**：文件上传、数据库变更
> 3. **定时任务**：数据备份、报表生成
> 4. **Webhook**：第三方回调处理
> 
> 不适合的场景：
> 1. **长连接**：WebSocket、长轮询
> 2. **长时间运行**：超过执行时间限制
> 3. **有状态服务**：需要本地存储

---

## 📚 扩展阅读

- [腾讯云 CloudBase 文档](https://cloud.tencent.com/document/product/876)
- [Serverless 架构详解](https://www.serverless.com/)
- [Node.js 云函数开发指南](https://cloud.tencent.com/document/product/876/43578)
- [DeepSeek API 文档](https://platform.deepseek.com/docs)

---

**最后更新：** 2026-06-30
