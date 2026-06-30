import json
from agents.base import BaseAgent

class PlannerAgent(BaseAgent):
    name = "规划Agent"
    description = "根据画像生成个性化学习路径"
    
    system_prompt = """你是一位专业的学习路径规划师。请根据用户的学习画像和目标，生成个性化的学习路径。

路径规划要求：
1. 根据用户基础水平和目标，合理安排学习进度
2. 每周学习时长要合理，不宜过多或过少
3. 学习内容要循序渐进，前后衔接合理
4. 包含多种资源类型（讲义、练习、思维导图、代码案例等）

输出格式要求：
必须返回JSON格式，包含以下字段：
- path: 路径列表，每项包含 week, title, hours, resources（字符串数组）"""

    def _mock_llm(self, prompt: str) -> str:
        return json.dumps({
            "path": [
                {"week": 1, "title": "Python基础 + 数学基础", "hours": 4, "resources": ["讲义", "练习", "思维导图", "代码案例"]},
                {"week": 2, "title": "线性回归", "hours": 4, "resources": ["讲义", "练习", "思维导图", "代码案例"]},
                {"week": 3, "title": "逻辑回归与分类问题", "hours": 5, "resources": ["讲义", "练习", "思维导图", "代码案例"]},
                {"week": 4, "title": "决策树与集成学习", "hours": 5, "resources": ["讲义", "练习", "思维导图", "拓展阅读"]},
                {"week": 5, "title": "神经网络基础", "hours": 6, "resources": ["讲义", "练习", "思维导图", "代码案例"]},
                {"week": 6, "title": "项目实战:房价预测", "hours": 6, "resources": ["项目文档", "代码模板", "数据", "评测"]},
                {"week": 7, "title": "综合复习与进阶", "hours": 5, "resources": ["复习讲义", "综合练习", "错题集", "模拟题"]},
                {"week": 8, "title": "结课评估与下一步", "hours": 3, "resources": ["结课测试", "学习报告", "路径推荐", "证书"]}
            ]
        })
    
    async def generate_path(self, profile: dict) -> dict:
        goal = profile.get("goal", "")
        math_level = profile.get("math_basics", 2.0)
        programming_level = profile.get("programming_basics", 2.0)
        daily_hours = profile.get("daily_study_hours", 2.0)
        weak_points = profile.get("weak_points", [])
        
        prompt = f"""请根据以下用户画像生成个性化学习路径：

用户目标：{goal}
数学基础：{math_level}/5
编程基础：{programming_level}/5
每日学习时长：{daily_hours}小时
薄弱点：{', '.join(weak_points) if weak_points else '无'}

请考虑：
1. 如果数学基础较弱，前几周要加强数学基础
2. 如果编程基础较弱，要安排编程入门内容
3. 目标如果是考研，要侧重理论和公式推导
4. 目标如果是入门，要侧重实践和代码

请按照系统提示词要求的JSON格式输出。"""
        
        result = self._call_llm(prompt)
        try:
            llm_result = json.loads(result)
            path = llm_result.get("path", [])
            return {"nodes": path, "title": f"{goal}学习路线" if goal else "个性化学习路径"}
        except json.JSONDecodeError:
            mock_result = json.loads(self._mock_llm(prompt))
            return {"nodes": mock_result["path"], "title": f"{goal}学习路线" if goal else "个性化学习路径"}
    
    async def handle_query(self, question: str, path_context: dict = None) -> str:
        prompt = f"""用户对学习路径有疑问，请给出友好的回答：

问题：{question}
当前路径上下文：{json.dumps(path_context or {})}

请给出简洁、有帮助的回答。"""
        
        result = self._call_llm(prompt)
        try:
            llm_result = json.loads(result)
            return llm_result.get("reply", "")
        except json.JSONDecodeError:
            responses = {
                "为什么要先学": "因为这是前置知识，掌握了这些后面学得更轻松。",
                "可以跳过": "建议按顺序学习，如果已有基础可以在测验后跳过。",
                "太难了": "我会适当降低难度，增加基础练习的比重。"
            }
            for key, resp in responses.items():
                if key in question:
                    return resp
            return "好的，我来调整学习计划，确保更适合你的节奏。"
    
    async def process(self, user_input: str, context: dict = None) -> dict:
        return {"reply": await self.handle_query(user_input), "path_update": None}
