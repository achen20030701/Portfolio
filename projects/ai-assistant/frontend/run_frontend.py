"""
启动前端脚本
"""
import subprocess
import sys

def main():
    """启动 Streamlit 前端"""
    print("🚀 启动前端界面...")
    print("📍 访问地址：http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止")
    print()

    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "frontend/app.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    main()
