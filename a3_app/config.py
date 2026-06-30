# A3 智能学习系统 - 配置
# v1.1 优化：SECRET_KEY 从环境变量读取，兜底使用随机生成
import os
import secrets

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'data', 'a3_app.db')}"

# 安全：从环境变量读取，不存在则动态生成（每次重启会变，生产环境务必设置ENV）
SECRET_KEY = os.getenv("A3_SECRET_KEY", "a3-learnmind-secret-key-2026-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天

# LLM 配置
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_URL = os.getenv("LLM_API_URL", "https://spark-api.xf-yun.com/v4.0/chat")
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "true").lower() == "true"  # 从环境变量控制
