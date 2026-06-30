"""
智能体服务层 - 五大智能体的核心业务逻辑
"""
from typing import Dict, List, Any
from services.llm_service import llm
from services.database import DatabaseService

db = DatabaseService()

class ProfileAgent:
    def __init__(self):
        self.name = "ProfileAgent"
        self.description = "学生画像采集与分析"
    
    def collect_profile(self, student_id: str, answers: List[str]) -> Dict:
        profile = {
            "student_id": student_id,
            "answers": answers,
            "dimensions": {
                "learning_style": self._analyze_learning_style(answers),
                "knowledge_level": self._assess_knowledge_level(answers),
                "interests": self._extract_interests(answers),
                "weak_points": self._identify_weak_points(answers),
                "learning_goals": self._extract_goals(answers),
                "time_habit": self._analyze_time_habit(answers),
            }
        }
        db.save_student_profile(student_id, profile)
        return profile
    
    def _analyze_learning_style(self, answers: List[str]) -> str:
        return llm.generate(f"从以下回答分析学习风格：{answers}")
    
    def _assess_knowledge_level(self, answers: List[str]) -> str:
        return llm.generate(f"从以下回答评估知识水平：{answers}")
    
    def _extract_interests(self, answers: List[str]) -> List[str]:
        return ["网络安全", "系统编程"]
    
    def _identify_weak_points(self, answers: List[str]) -> List[str]:
        return ["TCP拥塞控制", "IP路由算法"]
    
    def _extract_goals(self, answers: List[str]) -> str:
        return "掌握计算机网络基础知识"
    
    def _analyze_time_habit(self, answers: List[str]) -> str:
        return "每晚2小时"

class PlannerAgent:
    def __init__(self):
        self.name = "PlannerAgent"
        self.description = "学习路径规划"
    
    def generate_plan(self, student_id: str, profile: Dict) -> Dict:
        plan = {
            "student_id": student_id,
            "phases": [
                {"name": "基础巩固", "duration": "2周", "topics": ["OSI模型", "TCP/IP基础"]},
                {"name": "深度提升", "duration": "3周", "topics": ["TCP拥塞控制", "路由算法"]},
                {"name": "综合应用", "duration": "1周", "topics": ["网络安全", "实践项目"]},
            ],
            "recommendations": ["建议每天学习1-2小时", "重点关注薄弱环节"]
        }
        db.save_generation_log(student_id, "plan", "综合学习路径", "success", 4.5, 5)
        return plan

class ResourceAgent:
    def __init__(self):
        self.name = "ResourceAgent"
        self.description = "学习资源生成"
    
    def generate_resource(self, student_id: str, task_type: str, topic: str) -> Dict:
        content = llm.generate(f"生成{task_type}：{topic}")
        resource = {
            "student_id": student_id,
            "type": task_type,
            "topic": topic,
            "content": content,
            "meta": {"length": len(content), "chunks": 5}
        }
        db.save_learning_resource(student_id, resource)
        db.save_generation_log(student_id, task_type, topic, "success", 3.2, 5)
        return resource

class QuizAgent:
    def __init__(self):
        self.name = "QuizAgent"
        self.description = "习题生成与批改"
    
    def generate_quiz(self, topic: str, num_questions: int = 10) -> Dict:
        questions = llm.generate(f"生成{num_questions}道关于{topic}的选择题")
        return {"topic": topic, "questions": questions, "count": num_questions}
    
    def grade_quiz(self, student_id: str, answers: List[str], correct_answers: List[str]) -> Dict:
        score = sum(1 for a, c in zip(answers, correct_answers) if a == c) / len(correct_answers) * 100
        db.update_knowledge_mastery(student_id, {"score": score})
        return {"score": score, "correct": sum(1 for a, c in zip(answers, correct_answers) if a == c)}

class ReviewAgent:
    def __init__(self):
        self.name = "ReviewAgent"
        self.description = "质量审核与评估"
    
    def review_resource(self, resource: Dict) -> Dict:
        review = llm.generate(f"评估以下资源质量：{resource['content'][:200]}")
        return {
            "resource_id": resource.get("id", ""),
            "quality_score": 85,
            "feedback": review,
            "approved": True
        }
    
    def evaluate_student_progress(self, student_id: str) -> Dict:
        records = db.get_qa_records(student_id)
        return {
            "student_id": student_id,
            "total_questions": len(records),
            "correct_rate": 0.75,
            "recommendations": ["继续保持", "重点复习薄弱环节"]
        }

class AgentManager:
    def __init__(self):
        self.agents = {
            "profile": ProfileAgent(),
            "planner": PlannerAgent(),
            "resource": ResourceAgent(),
            "quiz": QuizAgent(),
            "review": ReviewAgent(),
        }
    
    def get_agent(self, agent_name: str):
        return self.agents.get(agent_name.lower())
    
    def run_workflow(self, student_id: str, task_type: str, topic: str) -> Dict:
        results = {}
        
        results["profile"] = self.agents["profile"].collect_profile(student_id, ["计算机专业", "喜欢动手实践"])
        results["plan"] = self.agents["planner"].generate_plan(student_id, results["profile"])
        results["resource"] = self.agents["resource"].generate_resource(student_id, task_type, topic)
        
        if task_type in ["exam", "习题"]:
            results["quiz"] = self.agents["quiz"].generate_quiz(topic)
        
        results["review"] = self.agents["review"].review_resource(results["resource"])
        
        return results
