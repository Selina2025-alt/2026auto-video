"""
后端启动脚本
启动 FastAPI 服务器
"""
import uvicorn
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 启动配置
    config = {
        "host": "0.0.0.0",
        "port": 8001,
        "reload": True,  # 开发模式自动重载
        "log_level": "info"
    }

    print("=" * 50)
    print("批量自动剪辑智能体 - 后端服务")
    print("=" * 50)
    print(f"服务地址: http://{config['host']}:{config['port']}")
    print(f"API文档: http://{config['host']}:{config['port']}/docs")
    print("=" * 50)

    # 启动服务器
    uvicorn.run("main:app", **config)
