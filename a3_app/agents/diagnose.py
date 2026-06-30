import json
from agents.base import BaseAgent

class DiagnoseAgent(BaseAgent):
    name = "诊断Agent"
    description = "通过对话评估用户水平和薄弱点，生成6维画像"
    
    system_prompt = """你是一位专业的学习诊断师。请根据用户的回答，分析其学习状态并生成6维学习画像：
1. math_basics (1-5): 数学基础水平
2. programming_basics (1-5): 编程基础水平
3. domain_knowledge (1-5): 领域知识水平
4. learning_efficiency (1-5): 学习效率
5. self_discipline (1-5): 自律程度
6. weakness_awareness (1-5): 薄弱点认知

输出格式要求：
必须返回JSON格式，包含以下字段：
- profile: 包含上述6维评分的字典
- weak_points: 薄弱点列表（字符串数组）
- strong_points: 强项列表（字符串数组）
- analysis: 简要分析（2-3句话）
- suggested_focus: 建议重点（字符串数组）"""

    profile_template = {
        "math_basics": 2.0,
        "programming_basics": 2.0,
        "domain_knowledge": 1.0,
        "learning_efficiency": 3.0,
        "self_discipline": 3.0,
        "weakness_awareness": 2.0,
        "cognitive_style": "mixed",
        "daily_study_hours": 2.0,
        "goal": "",
        "weak_points": [],
        "strong_points": []
    }

    dialogue_flow = [
        {"key": "goal",        "question": "你好！我是你的学习诊断师。你这次想学习什么？或者有什么学习目标？",
         "options": ["考研数学", "机器学习入门", "Python编程", "数据结构与算法"]},
        {"key": "math",        "question": "你的数学基础怎么样？",
         "options": ["学过高等数学 ✅", "线性代数记得一些", "概率论忘光了 🫣", "数学基础不错"]},
        {"key": "programming", "question": "编程基础呢？有写过代码吗？",
         "options": ["Python熟练", "学过C语言", "零基础", "有过项目经验"]},
        {"key": "time",        "question": "你每天大概能花多少时间学习？",
         "options": ["1小时以内", "1-2小时", "2-3小时", "3小时以上"]},
        {"key": "style",       "question": "你更喜欢哪种学习方式？",
         "options": ["看视频 🎬", "阅读文字 📖", "动手实践 🔧", "混合方式"]},
        {"key": "done",        "question": "", "options": []}
    ]

    def __init__(self):
        self.reset()

    def _mock_llm(self, prompt: str) -> str:
        return json.dumps({
            "profile": {
                "math_basics": 3.0,
                "programming_basics": 2.5,
                "domain_knowledge": 1.5,
                "learning_efficiency": 3.0,
                "self_discipline": 3.5,
                "weakness_awareness": 2.5,
            },
            "analysis": "用户数学基础一般，编程有一定基础，目标明确但需要系统规划。",
            "suggested_focus": ["基础概念", "数学推导", "代码实践"],
            "weak_points": ["数学基础", "领域知识"],
            "strong_points": ["学习态度积极", "自律性强"]
        })

    def get_current_question(self) -> dict:
        if self.step < len(self.dialogue_flow):
            return self.dialogue_flow[self.step]
        return {"key": "done", "question": "诊断已完成！正在生成你的学习画像...", "options": []}

    def get_initial_question(self) -> dict:
        return self.dialogue_flow[0]

    def _analyze_profile_with_llm(self) -> dict:
        dialogue_history = "\n".join([
            f"Q: {self.dialogue_flow[i]['question']}\nA: {self.profile.get(self.dialogue_flow[i]['key'], '')}"
            for i in range(min(self.step, len(self.dialogue_flow)))
        ])
        
        prompt = f"""请根据以下对话历史，分析用户的学习状态并生成6维学习画像：

对话历史：
{dialogue_history}

当前用户目标：{self.profile.get('goal', '')}
数学基础自评：{self.profile.get('math_basics', 2.0)}/5
编程基础自评：{self.profile.get('programming_basics', 2.0)}/5
每日学习时长：{self.profile.get('daily_study_hours', 2.0)}小时
认知风格：{self.profile.get('cognitive_style', 'mixed')}

请按照系统提示词要求的JSON格式输出分析结果。"""
        
        result = self._call_llm(prompt)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return json.loads(self._mock_llm(prompt))

    def process_answer(self, answer: str) -> dict:
        if self.step >= len(self.dialogue_flow):
            return {
                "reply": "诊断已完成！请查看你的学习画像。",
                "options": [],
                "is_done": True,
                "profile": self.profile,
                "step": self.step,
                "total_steps": len(self.dialogue_flow)
            }

        key = self.dialogue_flow[self.step]["key"]

        if key == "goal":
            self.profile["goal"] = answer
            if "考研" in answer:
                self.profile["domain_knowledge"] = 1.5
        elif key == "math":
            if "学过" in answer or "不错" in answer:
                self.profile["math_basics"] = 3.5
            elif "记得" in answer:
                self.profile["math_basics"] = 2.5
            else:
                self.profile["math_basics"] = 1.5
        elif key == "programming":
            if "熟练" in answer or "项目" in answer:
                self.profile["programming_basics"] = 4.0
            elif "学过" in answer:
                self.profile["programming_basics"] = 2.5
            else:
                self.profile["programming_basics"] = 1.0
        elif key == "time":
            if "3小时" in answer:
                self.profile["daily_study_hours"] = 3.5
                self.profile["self_discipline"] = 4.0
            elif "2-3" in answer:
                self.profile["daily_study_hours"] = 2.5
                self.profile["self_discipline"] = 3.5
            elif "1-2" in answer:
                self.profile["daily_study_hours"] = 1.5
            else:
                self.profile["daily_study_hours"] = 1.0
                self.profile["self_discipline"] = 2.5
        elif key == "style":
            style_map = {"视频": "visual", "阅读": "reading", "动手": "hands-on", "混合": "mixed"}
            for k, v in style_map.items():
                if k in answer:
                    self.profile["cognitive_style"] = v
                    break

        self.step += 1
        is_done = (self.step >= len(self.dialogue_flow))

        if is_done:
            llm_result = self._analyze_profile_with_llm()
            
            self.profile["weak_points"] = llm_result.get("weak_points", [])
            self.profile["strong_points"] = llm_result.get("strong_points", [])
            
            for dim in ["math_basics", "programming_basics", "domain_knowledge", 
                        "learning_efficiency", "self_discipline", "weakness_awareness"]:
                if dim in llm_result.get("profile", {}):
                    self.profile[dim] = llm_result["profile"][dim]
            
            next_reply = f"✅ 诊断完成！{llm_result.get('analysis', '我已根据你的情况生成了个性化学习画像，正在为你规划学习路径...')}"
            next_options = []
        else:
            next_q = self.dialogue_flow[self.step]
            next_reply = next_q["question"]
            next_options = next_q["options"]

        return {
            "reply": next_reply,
            "options": next_options,
            "is_done": is_done,
            "profile": self.profile if is_done else None,
            "step": self.step,
            "total_steps": len(self.dialogue_flow)
        }

    async def process(self, user_input: str, context: dict = None) -> dict:
        return self.process_answer(user_input)

    def reset(self):
        super().reset()
        self.step = 0
        self.profile = dict(self.profile_template)
        self.profile["weak_points"] = []
        self.profile["strong_points"] = []
