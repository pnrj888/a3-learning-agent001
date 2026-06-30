import json
import hmac
import hashlib
import base64
import urllib.parse
import time
import ssl
import websocket
import threading
from typing import List, Dict, Optional, Callable
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import SparkConfig
from .profile_model import StudentProfile, ProfileStorage


class SparkClient:
    def __init__(self):
        self.app_id = SparkConfig.APP_ID
        self.api_key = SparkConfig.API_KEY
        self.api_secret = SparkConfig.API_SECRET
        self.api_url = SparkConfig.API_URL
        self.ws = None
        self.lock = threading.Lock()
        self.response_text = ""
        self.is_connected = False

    def _build_auth_url(self) -> str:
        parsed = urllib.parse.urlparse(self.api_url)
        host = parsed.hostname
        path = parsed.path
        now = int(time.time())
        signature_origin = f"host: {host}\ndate: {now}\nGET {path} HTTP/1.1"
        signature_sha = hmac.new(self.api_secret.encode(), signature_origin.encode(), hashlib.sha256).digest()
        signature_b64 = base64.b64encode(signature_sha).decode()
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_b64}"'
        authorization_b64 = base64.b64encode(authorization_origin.encode()).decode()
        params = {
            "authorization": authorization_b64,
            "date": str(now),
            "host": host
        }
        return f"{self.api_url}?{urllib.parse.urlencode(params)}"

    def _on_message(self, ws, message):
        data = json.loads(message)
        if data.get("header", {}).get("code") == 0:
            choices = data.get("payload", {}).get("choices", {})
            for choice in choices.get("text", []):
                self.response_text += choice.get("content", "")
            if choices.get("status") == 2:
                self.is_connected = False

    def _on_error(self, ws, error):
        self.is_connected = False

    def _on_close(self, ws, close_status_code, close_msg):
        self.is_connected = False

    def _on_open(self, ws):
        self.is_connected = True

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 2000) -> str:
        self.response_text = ""
        auth_url = self._build_auth_url()
        
        self.ws = websocket.WebSocketApp(
            auth_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        def send_data():
            while not self.is_connected:
                time.sleep(0.1)
            payload = {
                "header": {"app_id": self.app_id},
                "parameter": {
                    "chat": {
                        "domain": "generalv3.5",
                        "temperature": 0.7,
                        "max_tokens": max_tokens
                    }
                },
                "payload": {"message": {"text": messages}}
            }
            self.ws.send(json.dumps(payload))
        
        threading.Thread(target=send_data, daemon=True).start()
        self.ws.run_forever(sslopt={"ssl_context": ssl_context})
        return self.response_text.strip()


class ProfileAgent:
    def __init__(self):
        self.spark_client = SparkClient()
        self.storage = ProfileStorage()
        self.conversation_history: List[Dict[str, str]] = []

    def _extract_json(self, text: str) -> Optional[dict]:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
        return None

    def _generate_initial_prompt(self, student_id: str, name: str) -> str:
        return f"""你是一个专业的教育测评助手。请通过多轮对话收集学生信息，生成结构化的学生画像。

学生信息：
- 学号：{student_id}
- 姓名：{name}

请依次询问以下6个维度的信息：
1. 前置知识基础：学生已掌握的知识范围和水平
2. 认知学习风格：视觉型、听觉型、动觉型、阅读型等
3. 薄弱知识点：学生在当前科目中的薄弱环节
4. 易错题型：学生经常出错的题型类别
5. 学习目标：学生近期的学习目标和期望
6. 每日学习节奏：学生每天的学习时间段和习惯

请用自然、友好的语言开始第一轮提问。"""

    def _generate_summary_prompt(self) -> str:
        return f"""基于以下对话历史，请生成结构化的学生画像JSON数据：

对话历史：
{json.dumps(self.conversation_history, ensure_ascii=False, indent=2)}

请输出严格的JSON格式，包含以下字段：
{{
  "prerequisites": ["知识点1", "知识点2", ...],
  "learning_style": "学习风格描述",
  "weak_points": ["薄弱点1", "薄弱点2", ...],
  "error_prone_types": ["题型1", "题型2", ...],
  "learning_goals": ["目标1", "目标2", ...],
  "daily_rhythm": {{"时间段": "学习内容/习惯", ...}}
}}

只输出JSON，不要包含其他文字。"""

    def start_conversation(self, student_id: str, name: str) -> str:
        self.conversation_history = []
        prompt = self._generate_initial_prompt(student_id, name)
        response = self.spark_client.chat([{"role": "user", "content": prompt}])
        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def continue_conversation(self, user_input: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_input})
        response = self.spark_client.chat(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def generate_profile(self, student_id: str, name: str) -> StudentProfile:
        prompt = self._generate_summary_prompt()
        response = self.spark_client.chat([{"role": "user", "content": prompt}])
        
        profile_data = self._extract_json(response)
        if not profile_data:
            profile_data = {
                "prerequisites": [],
                "learning_style": "",
                "weak_points": [],
                "error_prone_types": [],
                "learning_goals": [],
                "daily_rhythm": {}
            }
        
        profile = StudentProfile(
            student_id=student_id,
            name=name,
            prerequisites=profile_data.get("prerequisites", []),
            learning_style=profile_data.get("learning_style", ""),
            weak_points=profile_data.get("weak_points", []),
            error_prone_types=profile_data.get("error_prone_types", []),
            learning_goals=profile_data.get("learning_goals", []),
            daily_rhythm=profile_data.get("daily_rhythm", {})
        )
        self.storage.save(profile)
        return profile

    def update_with_exam_record(self, student_id: str, exam_record: Dict) -> StudentProfile:
        profile = self.storage.get(student_id)
        if not profile:
            raise ValueError(f"学生 {student_id} 不存在")
        
        prompt = f"""请分析以下做题记录，更新学生画像的薄弱知识点和易错题型。

当前学生画像：
{profile.to_json()}

做题记录：
{json.dumps(exam_record, ensure_ascii=False, indent=2)}

请输出严格的JSON格式，包含需要新增或更新的字段：
{{
  "weak_points": ["新增薄弱点1", "新增薄弱点2", ...],
  "error_prone_types": ["新增易错题型1", "新增易错题型2", ...]
}}

只输出JSON，不要包含其他文字。"""
        
        response = self.spark_client.chat([{"role": "user", "content": prompt}])
        update_data = self._extract_json(response)
        
        if update_data:
            for point in update_data.get("weak_points", []):
                profile.add_weak_point(point)
            for q_type in update_data.get("error_prone_types", []):
                profile.add_error_prone_type(q_type)
        
        self.storage.save(profile)
        return profile

    def get_profile(self, student_id: str) -> Optional[StudentProfile]:
        return self.storage.get(student_id)
