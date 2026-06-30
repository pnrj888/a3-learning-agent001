"""
LLM 服务层 - 支持 Mock 和真实 API 模式切换
默认使用 Mock 模式，配置环境变量后自动切换为真实 API
"""
import os
import json
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict], **kwargs) -> str:
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

class MockLLMService(BaseLLMService):
    def chat(self, messages: List[Dict], **kwargs) -> str:
        last_message = messages[-1]['content'] if messages else ""
        
        mock_responses = {
            "TCP三次握手": "TCP三次握手是建立TCP连接的过程：1. 客户端发送SYN；2. 服务器返回SYN+ACK；3. 客户端发送ACK。完成三次握手后，TCP连接建立。",
            "OSI模型": "OSI七层模型从上到下依次是：应用层、表示层、会话层、传输层、网络层、数据链路层、物理层。每层负责不同的功能。",
            "HTTP和HTTPS": "HTTP是明文传输，端口80；HTTPS是加密传输，端口443。HTTPS通过SSL/TLS协议提供数据加密和身份认证。",
        }
        
        for key, response in mock_responses.items():
            if key in last_message:
                return response
        
        return f"这是一个模拟回答：{last_message[:50]}..."

    def generate(self, prompt: str, **kwargs) -> str:
        if "讲义" in prompt or "lecture" in prompt.lower():
            return "# 学习讲义\n\n## 一、核心概念\n\n本节介绍核心知识点的定义和基本原理。\n\n## 二、重点难点\n\n需要重点掌握的内容和常见易错点。\n\n## 三、例题解析\n\n通过例题加深理解。"
        
        if "习题" in prompt or "exercise" in prompt.lower():
            return "1. 选择题：TCP三次握手的目的是什么？\n   A) 加密数据\n   B) 建立连接\n   C) 传输数据\n   D) 断开连接\n\n2. 填空题：OSI模型共分为___层。\n\n答案：1.B 2.7"
        
        if "思维导图" in prompt or "mindmap" in prompt.lower():
            return "# 知识思维导图\n\n- 计算机网络\n  - OSI七层模型\n    - 应用层\n    - 传输层\n    - 网络层\n  - TCP/IP协议\n    - TCP\n    - IP"
        
        if "PPT" in prompt or "presentation" in prompt.lower():
            return "幻灯片1: 标题页\n幻灯片2: 目录\n幻灯片3: 核心概念\n幻灯片4: 原理讲解\n幻灯片5: 案例分析\n幻灯片6: 总结"
        
        return "这是生成的模拟内容..."

class SparkLLMService(BaseLLMService):
    def __init__(self):
        self.api_key = os.environ.get("SPARK_API_KEY", "")
        self.app_id = os.environ.get("SPARK_APP_ID", "")
        self.api_secret = os.environ.get("SPARK_API_SECRET", "")
        self.api_url = "wss://spark-api.xf-yun.com/v3.5/chat"
        self.domain = "generalv3.5"

    def _generate_signature(self) -> str:
        import hmac
        import hashlib
        import base64
        from datetime import datetime
        from urllib.parse import quote
        
        date = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
        signature_origin = f"host: spark-api.xf-yun.com\ndate: {date}\nGET /v3.5/chat HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature_sha).decode('utf-8')
        
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        return quote(authorization_origin)

    def chat(self, messages: List[Dict], **kwargs) -> str:
        if not self.api_key or not self.app_id or not self.api_secret:
            return "⚠️ 讯飞API密钥未配置，请在环境变量中设置 SPARK_API_KEY, SPARK_APP_ID, SPARK_API_SECRET"
        
        try:
            import websocket
            import json
            
            ws_url = f"{self.api_url}?authorization={self._generate_signature()}&date={datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}&host=spark-api.xf-yun.com"
            
            ws = websocket.create_connection(ws_url)
            
            payload = {
                "header": {
                    "app_id": self.app_id,
                    "uid": "user001"
                },
                "parameter": {
                    "chat": {
                        "domain": self.domain,
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 2000)
                    }
                },
                "payload": {
                    "message": {
                        "text": messages
                    }
                }
            }
            
            ws.send(json.dumps(payload))
            
            response = ""
            while True:
                result = ws.recv()
                data = json.loads(result)
                if data.get("header", {}).get("status") == 2:
                    break
                content = data.get("payload", {}).get("choices", {}).get("text", [{}])[0].get("content", "")
                response += content
            
            ws.close()
            return response
        except Exception as e:
            return f"API调用失败: {str(e)}"

    def generate(self, prompt: str, **kwargs) -> str:
        messages = [
            {"role": "system", "content": "你是一个专业的教育AI助手，擅长生成学习资料。"},
            {"role": "user", "content": prompt}
        ]
        return self.chat(messages, **kwargs)

class LLMService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            mode = os.environ.get("LLM_MODE", "mock").lower()
            if mode == "spark":
                cls._instance = SparkLLMService()
            else:
                cls._instance = MockLLMService()
        return cls._instance

    def chat(self, messages: List[Dict], **kwargs) -> str:
        return self._instance.chat(messages, **kwargs)

    def generate(self, prompt: str, **kwargs) -> str:
        return self._instance.generate(prompt, **kwargs)

    @staticmethod
    def get_mode() -> str:
        return os.environ.get("LLM_MODE", "mock").lower()

llm = LLMService()
