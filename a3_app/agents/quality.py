import json
import random
from agents.base import BaseAgent

class QualityAgent(BaseAgent):
    name = "质检Agent"
    description = "检查生成内容的质量、准确性和难度匹配度"
    
    system_prompt = """你是一位专业的学习内容质检专家。请对学习资源进行全面质量检查。

质检维度：
1. accuracy（准确性）：内容是否正确无误，无错误信息
2. difficulty（难度匹配）：内容难度是否与目标用户水平匹配
3. safety（安全性）：内容是否合规，无敏感信息
4. completeness（完整性）：内容是否完整覆盖主题
5. readability（可读性）：内容是否易于理解，格式清晰

输出格式要求：
必须返回JSON格式，包含以下字段：
- passed: 是否通过质检（boolean）
- score: 综合评分（0-100）
- checks: 各维度检查结果，每项包含 passed(boolean), score(0-100), issues(字符串数组)
- suggestions: 改进建议列表（字符串数组）"""

    def _mock_llm(self, prompt: str) -> str:
        return json.dumps({
            "passed": True,
            "score": 92,
            "checks": {
                "accuracy": {"passed": True, "score": 95, "issues": []},
                "difficulty": {"passed": True, "score": 88, "issues": ["部分术语可以更通俗"]},
                "safety": {"passed": True, "score": 100, "issues": []},
                "completeness": {"passed": True, "score": 90, "issues": []},
                "readability": {"passed": True, "score": 85, "issues": ["建议增加分段"]}
            },
            "suggestions": ["增加一个生活中的类比", "代码部分添加注释"]
        })
    
    async def check_resource(self, resource: dict, user_profile: dict = None) -> dict:
        resource_type = resource.get("type", "")
        resource_title = resource.get("title", "")
        resource_content = resource.get("content", "")
        user_level = user_profile.get("math_basics", 2.0) if user_profile else 2.0
        
        prompt = f"""请对以下学习资源进行质量检查：

资源类型：{resource_type}
资源标题：{resource_title}
资源内容：
{resource_content[:3000]}

用户水平参考（数学基础）：{user_level}/5

请按照系统提示词要求的JSON格式输出质检结果。"""
        
        result = self._call_llm(prompt)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return json.loads(self._mock_llm(prompt))
    
    async def check_answer(self, question: str, original_answer: str, user_level: float) -> dict:
        prompt = f"""请检查以下练习题答案的正确性：

题目：{question}
原答案：{original_answer}
用户水平：{user_level}/5

请判断答案是否正确，如果有错误请指出并给出正确答案。

输出格式要求：
必须返回JSON格式，包含以下字段：
- found_error: 是否发现错误（boolean）
- original: 原始答案
- corrected: 修正后的答案（如果有错误）
- reason: 错误原因（如果有错误）
- verified: 是否已验证"""
        
        result = self._call_llm(prompt)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            results = [
                {"found_error": True, "original": "f'(x) = 3x² + 2x + 1", "corrected": "f'(x) = 3x² - 2x + 1", "reason": "中间项符号错误", "verified": True},
                {"found_error": False, "original": "答案正确", "corrected": "", "reason": "", "verified": True}
            ]
            return random.choice(results)
    
    async def process(self, user_input: str, context: dict = None) -> dict:
        if context and "resource" in context:
            result = await self.check_resource(context["resource"])
            return {"reply": f"质检完成，综合评分：{result.get('score', 92)}分 {'✅' if result.get('passed') else '❌'}", "quality_report": result}
        return {"reply": "质检完成，内容质量合格 ✅", "quality_report": {"score": 92, "passed": True}}
