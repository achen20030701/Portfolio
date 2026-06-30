# CLAUDB Portfolio Memories

> 作品集项目记忆文件，用于在新窗口中恢复上下文。

---

## 📋 项目概览

| 项目 | 状态 | 地址 |
|------|------|------|
| AI 智能问答助手 | ✅ 已上线 | https://cg-work-cg-work-d3geug43lc211422a.webapps.tcloudbase.com |
| RAG 文档问答系统 | ✅ 已部署 | 待填写云函数地址 |
| 作品集主页面 | ✅ 已上线 | 待填写静态网站地址 |

---

## 📁 项目结构

```
D:\Dev\Agent\Portfolio\
├── README.md
├── projects/
│   ├── ai-assistant/          # AI 问答助手
│   └── rag-doc-qa/            # RAG 文档问答
├── deploy/
│   ├── portfolio/             # 作品集主页面
│   │   ├── index.html
│   │   ├── ai-assistant.html
│   │   └── rag-doc-qa.html
│   ├── ai-assistant/
│   └── rag-doc-qa/
└── docs/
```

---

## ☁️ 腾讯云 CloudBase

- **环境 ID:** cg-work-d3geug43lc211422a
- **套餐:** 体验版（免费）

### 云函数

| 函数名 | 用途 | 状态 |
|--------|------|------|
| ai-doc-qa | AI 问答助手 | ✅ 已部署 |
| rag-doc-qa | RAG 文档问答 | ✅ 已部署 |

### 数据库集合

| 集合名 | 用途 |
|--------|------|
| messages | AI 问答助手对话历史 |
| rag_documents | RAG 文档存储 |
| rag_messages | RAG 对话历史 |

### HTTP 网关

- AI 问答助手域名：`cg-work-d3geug43lc211422a-1307660528.ap-shanghai.app.tcloudbase.com`
- RAG 文档问答域名：待填写

---

## 🎨 UI 风格

- **风格：** 极简白色系
- **字体：** Inter
- **主色调：** 黑白灰 + 蓝色点缀

---

## 📝 联系方式

- **邮箱：** 898480959@qq.com
- **GitHub：** https://github.com/achen20030701

---

## ✅ 已完成任务

1. ~~更新 RAG 前端页面的 API 地址~~ ✅ RAG 已上线
2. ~~上传 RAG 前端到静态网站托管~~ ✅ RAG 已上线
3. ~~删除空目录 `ai-doc-qa`~~ ✅ 已删除
4. ~~上传项目到 GitHub~~ ✅ 已上传

## ⏳ 待完成任务

1. 删除空目录 `ai-rag-doc-qa`（被进程占用，需手动删除）

---

## 📅 更新日志

- **2026-06-30:** 文件整理完成，项目迁移到 Portfolio 目录
- **2026-06-29:** RAG 文档问答系统开发完成
- **2026-06-28:** AI 问答助手部署上线
- **2026-06-26:** 项目启动

---

**最后更新：** 2026-06-30
