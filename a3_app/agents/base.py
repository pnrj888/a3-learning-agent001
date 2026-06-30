import os
import json
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    name: str = "BaseAgent"
    description: str = ""
    system_prompt: str = ""

    def __init__(self):
        self._total_tokens_used = 0
        self._total_requests = 0
        self._total_errors = 0

    def _parse_bool_env(self, key: str, default: bool = False) -> bool:
        value = os.getenv(key, "").strip().lower()
        return value in {"1", "true", "yes", "on"}

    def _get_api_config(self) -> Dict:
        return {
            "api_key": os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
            "base_url": os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1",
            "model": os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo",
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "2048")),
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
            "timeout": int(os.getenv("LLM_TIMEOUT", "30")),
            "max_retries": int(os.getenv("LLM_MAX_RETRIES", "3")),
        }

    def _count_tokens(self, text: str) -> int:
        return len(text) // 4

    def _call_llm(self, prompt: str, system_prompt: str = None, messages: Optional[List[Dict]] = None) -> str:
        config = self._get_api_config()
        
        if self._parse_bool_env("USE_MOCK_LLM", False):
            logger.info(f"[{self.name}] Using mock LLM mode")
            return self._mock_llm(prompt)

        if not config["api_key"]:
            logger.warning(f"[{self.name}] No API key provided, falling back to mock mode")
            return self._mock_llm(prompt)

        try:
            import requests
            
            if messages is None:
                messages = []
            
            if system_prompt or self.system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt or self.system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": config["model"],
                "messages": messages,
                "max_tokens": config["max_tokens"],
                "temperature": config["temperature"],
            }

            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
            }

            backoff = 1.0
            last_error = None
            
            for attempt in range(config["max_retries"]):
                try:
                    self._total_requests += 1
                    logger.info(f"[{self.name}] LLM request attempt {attempt + 1}/{config['max_retries']}")
                    
                    resp = requests.post(
                        f"{config['base_url']}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=config["timeout"],
                    )
                    
                    if resp.status_code == 200:
                        result = resp.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        prompt_tokens = result.get("usage", {}).get("prompt_tokens", self._count_tokens(prompt))
                        completion_tokens = result.get("usage", {}).get("completion_tokens", self._count_tokens(content))
                        self._total_tokens_used += prompt_tokens + completion_tokens
                        
                        logger.info(f"[{self.name}] LLM request succeeded - prompt_tokens={prompt_tokens}, completion_tokens={completion_tokens}, total_used={self._total_tokens_used}")
                        return content
                    
                    elif resp.status_code in [429, 500, 502, 503, 504]:
                        last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
                        logger.warning(f"[{self.name}] LLM request failed ({last_error}), retrying in {backoff}s")
                        time.sleep(backoff)
                        backoff *= 2
                        
                    else:
                        last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
                        logger.error(f"[{self.name}] LLM request failed: {last_error}")
                        break
                        
                except requests.exceptions.Timeout:
                    last_error = "Request timed out"
                    logger.warning(f"[{self.name}] LLM request timed out, retrying in {backoff}s")
                    time.sleep(backoff)
                    backoff *= 2
                    
                except requests.exceptions.ConnectionError as e:
                    last_error = f"Connection error: {str(e)}"
                    logger.warning(f"[{self.name}] LLM connection error, retrying in {backoff}s")
                    time.sleep(backoff)
                    backoff *= 2
                    
                except Exception as e:
                    last_error = f"Unexpected error: {str(e)}"
                    logger.error(f"[{self.name}] LLM request exception: {last_error}")
                    break

            self._total_errors += 1
            logger.error(f"[{self.name}] All {config['max_retries']} retries failed, falling back to mock: {last_error}")
            return self._mock_llm(prompt)
            
        except ImportError:
            logger.warning(f"[{self.name}] requests library not available, falling back to mock mode")
            return self._mock_llm(prompt)

    def _mock_llm(self, prompt: str) -> str:
        return json.dumps({"reply": "我是一个基础Agent，请使用具体的子类。"})

    def get_stats(self) -> Dict:
        return {
            "agent_name": self.name,
            "total_requests": self._total_requests,
            "total_errors": self._total_errors,
            "total_tokens_used": self._total_tokens_used,
        }

    @abstractmethod
    async def process(self, user_input: str, context: dict = None) -> dict:
        pass

    def reset(self):
        self._total_tokens_used = 0
        self._total_requests = 0
        self._total_errors = 0
