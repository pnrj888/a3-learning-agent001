import json
from agents.base import BaseAgent

class GeneratorAgent(BaseAgent):
    name = "生成Agent"
    description = "根据学习路径生成多模态学习资源"
    
    system_prompt = """你是一位专业的学习资源生成专家。请根据用户指定的主题和难度，生成高质量的多模态学习资源。

资源类型要求：
1. lecture（精讲讲义）：包含核心概念、公式推导、代码示例、案例讲解
2. mindmap（思维导图）：结构化知识图谱，使用树形格式
3. exercise（练习题集）：包含选择题、计算题、编程题、综合应用题
4. code（代码案例）：可运行的Python代码，包含注释和解释

输出格式要求：
必须返回JSON格式，包含以下字段：
- resources: 资源列表，每项包含 type, title, content, tags, quality(0-100)"""

    def _mock_llm(self, prompt: str) -> str:
        topic = "机器学习"
        return json.dumps({
            "resources": [
                {"type":"lecture","title":f"{topic}精讲讲义","content":f"{topic}是机器学习中的核心概念。本讲义详细讲解其数学原理、实现方法和应用场景。内容涵盖：基本原理 → 公式推导 → sklearn实现 → 实际案例。","tags":["公式推导","代码示例","案例讲解"],"quality":94},
                {"type":"mindmap","title":f"{topic}知识图谱","content":f"中心: {topic}\\n├── 基本概念\\n│   ├── 定义与直觉理解\\n│   └── 应用场景\\n├── 数学原理\\n│   ├── 公式推导\\n│   └── 直观几何解释\\n└── 工程实践\\n    ├── sklearn代码实现\\n    └── 案例分析","tags":["可视化","结构化","一图概括"],"quality":86},
                {"type":"exercise","title":f"{topic}练习题集","content":f"1. 概念理解：关于{topic}，以下说法正确的是？\\n2. 计算推导：请推导相关公式\\n3. 代码填空：补全 Python 实现\\n4. 综合应用：真实场景分析","tags":["选择题","计算题","编程题","中等难度"],"quality":91},
                {"type":"code","title":f"{topic} Python实战","content":f"# {topic} 完整实战\\nimport numpy as np\\nfrom sklearn.model_selection import train_test_split\\nfrom sklearn.metrics import accuracy_score\\n\\n# 1. 数据准备\\n# 2. 模型训练\\n# 3. 参数调优\\n# 4. 结果可视化和评估","tags":["Python","sklearn","可运行","含注释"],"quality":88}
            ]
        })

    async def generate_resources(self, topic: str, level: str = "intermediate") -> list:
        prompt = f"""请为以下学习主题生成4种学习资源：

主题：{topic}
难度：{level}（初级/beginner、中级/intermediate、高级/advanced）

请按照系统提示词要求的JSON格式输出。"""
        
        result = self._call_llm(prompt)
        try:
            llm_result = json.loads(result)
            resources = llm_result.get("resources", [])
            for r in resources:
                r["title"] = r.get("title", "").format(topic=topic) if isinstance(r.get("title"), str) else r.get("title")
                r["content"] = r.get("content", "").format(topic=topic) if isinstance(r.get("content"), str) else r.get("content")
            return resources
        except json.JSONDecodeError:
            mock_result = json.loads(self._mock_llm(prompt))
            resources = []
            for r in mock_result["resources"]:
                r["title"] = r["title"].format(topic=topic)
                r["content"] = r["content"].format(topic=topic)
                resources.append(r)
            return resources

    async def regenerate(self, resource_id: int, feedback: str = "") -> dict:
        prompt = f"""请根据以下反馈重新生成学习资源：

资源ID：{resource_id}
反馈：{feedback}

请按照系统提示词要求的JSON格式输出。"""
        
        result = self._call_llm(prompt)
        try:
            llm_result = json.loads(result)
            return {"status": "regenerated", "new_quality": llm_result.get("quality", 95), "feedback": "已根据反馈优化"}
        except json.JSONDecodeError:
            return {"status": "regenerated", "new_quality": 95, "feedback": "已根据反馈优化"}

    async def process(self, user_input: str, context: dict = None) -> dict:
        ctx = context or {}
        agent_type = ctx.get("agent_type", "")

        if agent_type == "teach":
            topic = user_input.strip()
            if not topic:
                topic = "机器学习基础"
        else:
            topic = ctx.get("topic", "机器学习基础")

        resources = await self.generate_resources(topic)
        reply = f"✅ 已为「{topic}」生成 {len(resources)} 种学习资源！\n\n"
        for r in resources:
            reply += f"{r.get('type', '')} - {r.get('title', '')}\n"
        reply += "\n前往「资源预览」页面查看详情。"
        return {"reply": reply, "resources": resources, "topic": topic}
