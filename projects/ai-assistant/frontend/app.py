"""
Streamlit 前端界面
AI 智能文档问答助手
"""
import streamlit as st
import requests
from pathlib import Path

# 后端 API 地址
API_BASE = "http://localhost:8000"

# 页面配置
st.set_page_config(
    page_title="AI 智能文档问答助手",
    page_icon="🤖",
    layout="wide"
)

# 标题
st.title("🤖 AI 智能文档问答助手")
st.markdown("上传文档，用自然语言提问，AI 会根据文档内容回答。")

# 侧边栏
with st.sidebar:
    st.header("📁 文档管理")

    # 上传文档
    uploaded_file = st.file_uploader(
        "上传文档",
        type=["txt", "pdf", "docx"],
        help="支持 TXT、PDF、DOCX 格式"
    )

    if uploaded_file:
        if st.button("📤 上传并处理", type="primary"):
            with st.spinner("正在处理文档..."):
                try:
                    # 上传文件
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    response = requests.post(
                        f"{API_BASE}/upload/",
                        files=files,
                        params={"collection_name": "default"}
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ 上传成功！")
                        st.info(f"📄 文件：{result['filename']}")
                        st.info(f"📊 分块数：{result['chunks']}")
                    else:
                        st.error(f"❌ 上传失败：{response.text}")

                except Exception as e:
                    st.error(f"❌ 错误：{str(e)}")

    st.divider()

    # 系统状态
    st.header("⚙️ 系统状态")
    try:
        health_response = requests.get(f"{API_BASE}/health")
        if health_response.status_code == 200:
            st.success("✅ 服务运行中")
        else:
            st.error("❌ 服务异常")
    except:
        st.error("❌ 无法连接后端服务")

    # 配置检查
    try:
        config_response = requests.get(f"{API_BASE}/config/check")
        if config_response.status_code == 200:
            config = config_response.json()
            if config["status"] == "complete":
                st.success("✅ 配置完整")
            else:
                st.warning(f"⚠️ {config['message']}")
    except:
        pass

# 主界面
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 对话")

    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示历史消息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📚 查看来源"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**来源 {i}:**")
                        st.text(source["content"])

    # 用户输入
    if prompt := st.chat_input("请输入你的问题..."):
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 添加到历史
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 调用 API
        with st.chat_message("assistant"):
            with st.spinner("正在思考..."):
                try:
                    response = requests.post(
                        f"{API_BASE}/chat/",
                        json={
                            "message": prompt,
                            "collection_name": "default"
                        }
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.markdown(result["reply"])

                        # 显示来源
                        if result["sources"]:
                            with st.expander("📚 查看来源"):
                                for i, source in enumerate(result["sources"], 1):
                                    st.markdown(f"**来源 {i}:**")
                                    st.text(source["content"])

                        # 添加到历史
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result["reply"],
                            "sources": result["sources"]
                        })
                    else:
                        st.error(f"❌ 问答失败：{response.text}")

                except Exception as e:
                    st.error(f"❌ 错误：{str(e)}")

with col2:
    st.header("📋 使用说明")

    st.markdown("""
    ### 🚀 快速开始

    1. **上传文档**
       - 在左侧边栏点击"上传文档"
       - 支持 TXT、PDF、DOCX 格式
       - 点击"上传并处理"

    2. **开始问答**
       - 在下方输入框输入问题
       - AI 会根据文档内容回答
       - 可以查看答案来源

    3. **多轮对话**
       - 支持连续提问
       - AI 会记住对话历史

    ### 💡 提问技巧

    - 问题要具体明确
    - 可以问"文档中提到了什么？"
    - 可以问"XXX 是什么？"
    - 可以问"总结一下主要内容"
    """)

    st.divider()

    st.header("🔧 技术栈")
    st.markdown("""
    - **前端**: Streamlit
    - **后端**: FastAPI
    - **AI 框架**: LangChain
    - **向量库**: ChromaDB
    - **LLM**: DeepSeek
    """)
