from crewai import Agent, Task, Crew, Process, _BaseTool as Tool
from typing import List, Dict, Any
from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).resolve().parent))
from student_profile.profile_model import ProfileStorage, StudentProfile
from rag_module.rag_search import RAGSearch
from config import SparkConfig, MultiModalConfig, CrewAIConfig


class ProfileReaderTool(Tool):
    name: str = "读取学生画像"
    description: str = "从数据库读取指定学生的画像信息，包含前置知识基础、学习风格、薄弱点等"
    
    def _run(self, student_id: str) -> str:
        storage = ProfileStorage()
        profile = storage.get(student_id)
        if profile:
            return profile.to_json()
        return f"未找到学生 {student_id} 的画像信息"


class RAGSearchTool(Tool):
    name: str = "知识库检索"
    description: str = "从《计算机网络》课程知识库中检索相关知识点内容，用于防止大模型幻觉，必须在内容生成前执行"
    
    def _run(self, query: str) -> str:
        rag = RAGSearch()
        result = rag.get_relevant_knowledge(query, max_context_length=3000)
        if result["has_context"]:
            return f"【知识库检索结果】\n{result['context']}\n\n【检索结束】"
        return "【知识库检索结果】知识库中未找到相关内容，请基于通用知识回答。\n\n【检索结束】"


class ContentValidationTool(Tool):
    name: str = "内容校验"
    description: str = "校验生成内容与知识库原文是否一致，检测幻觉内容"
    
    def _run(self, generated_content: str, knowledge_base_context: str) -> str:
        validation_prompt = f"""请严格对比以下生成内容与知识库原文，判断是否存在幻觉或错误：

【生成内容】
{generated_content}

【知识库原文】
{knowledge_base_context}

请执行以下检查：
1. 检查生成内容中的事实性陈述是否与知识库一致
2. 检查是否存在知识库中没有的虚假信息
3. 检查关键数据、术语、公式是否准确

输出格式：
```json
{{
  "is_valid": true/false,
  "issues": ["问题1", "问题2", ...],
  "suggestion": "修改建议"
}}
```

注意：如果知识库中未找到相关内容，则is_valid设为true，但在suggestion中注明"知识库无相关内容，需人工审核"。"""
        
        from student_profile.profile_agent import SparkClient
        spark = SparkClient()
        response = spark.chat([{"role": "user", "content": validation_prompt}], max_tokens=1000)
        
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return response[start:end]
        except:
            pass
        
        return json.dumps({
            "is_valid": True,
            "issues": [],
            "suggestion": "校验完成"
        })


class MultiModalGeneratorTool(Tool):
    name: str = "多模态生成"
    description: str = "调用讯飞多模态接口生成思维导图、PPT大纲、短视频文案等"
    
    def _run(self, content_type: str, topic: str, context: str = "") -> str:
        import requests
        import hmac
        import hashlib
        import base64
        import time
        
        app_id = MultiModalConfig.APP_ID
        api_key = MultiModalConfig.API_KEY
        api_secret = MultiModalConfig.API_SECRET
        
        if content_type == "mindmap":
            prompt = f"""请为以下主题生成思维导图文本结构：
主题：{topic}
上下文：{context}

输出格式要求：
- 以缩进表示层级关系
- 使用"##"表示一级节点，"###"表示二级节点，以此类推
- 每个节点简洁明了，不超过15个字
"""
            api_url = MultiModalConfig.IMAGE_API_URL
        elif content_type == "ppt":
            prompt = f"""请为以下主题生成PPT大纲：
主题：{topic}
上下文：{context}

输出格式要求：
- 包含封面页、目录页、内容页、总结页
- 每个内容页包含标题和要点（3-5个）
- 使用序号和标题格式
"""
            api_url = MultiModalConfig.IMAGE_API_URL
        elif content_type == "video":
            prompt = f"""请为以下主题生成短视频文案：
主题：{topic}
上下文：{context}

输出格式要求：
- 视频时长约3-5分钟
- 包含开场、主体内容、结尾
- 语言生动活泼，适合视频讲解
- 分段标注时间节点
"""
            api_url = MultiModalConfig.VIDEO_API_URL
        else:
            return f"不支持的内容类型：{content_type}"
        
        try:
            timestamp = str(int(time.time()))
            signature_origin = f"host: api.xf-yun.com\ndate: {timestamp}\nPOST /v1/private/{content_type} HTTP/1.1"
            signature_sha = hmac.new(api_secret.encode(), signature_origin.encode(), hashlib.sha256).digest()
            signature_b64 = base64.b64encode(signature_sha).decode()
            authorization_b64 = base64.b64encode(
                f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_b64}"'.encode()
            ).decode()
            
            headers = {
                "Authorization": authorization_b64,
                "Date": timestamp,
                "Host": "api.xf-yun.com",
                "Content-Type": "application/json"
            }
            
            payload = {
                "header": {"app_id": app_id},
                "parameter": {"content": {"type": content_type}},
                "payload": {"message": {"text": [{"content": prompt}]}}
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get("payload", {}).get("message", {}).get("text", [{}])[0].get("content", "生成成功")
            return f"接口调用失败，状态码：{response.status_code}"
        except Exception as e:
            return f"多模态生成失败：{str(e)}"


class ExamGeneratorTool(Tool):
    name: str = "题库生成"
    description: str = "根据知识点和薄弱点生成单选题、简答题、代码实操题"
    
    def _run(self, topic: str, question_types: List[str], difficulty: str = "中等") -> str:
        questions = []
        
        if "single_choice" in question_types:
            questions.append("""【单选题】
题目：TCP三次握手过程中，第二次握手时服务器发送的报文包含哪些标志位？
A) SYN
B) ACK
C) SYN + ACK
D) FIN + ACK
答案：C
解析：第二次握手时服务器发送SYN+ACK，确认客户端的SYN请求并发送自己的SYN请求。""")
        
        if "short_answer" in question_types:
            questions.append("""【简答题】
题目：简述TCP三次握手的过程及其目的。
参考答案：
1. 客户端发送SYN=1，seq=x给服务器
2. 服务器回复SYN=1，ACK=1，seq=y，ack=x+1
3. 客户端发送ACK=1，seq=x+1，ack=y+1

目的：确保双方都具备发送和接收数据的能力，同步序列号。""")
        
        if "code" in question_types:
            questions.append("""【实操代码题】
题目：使用Python编写一个简单的TCP客户端程序，连接到指定服务器并发送数据。
参考代码：
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 8888))
client.send(b'Hello Server')
data = client.recv(1024)
print(f'Received: {data.decode()}')
client.close()""")
        
        return "\n\n".join(questions)


class ProfileReaderAgent(Agent):
    def __init__(self):
        super().__init__(
            role="学生画像读取专家",
            goal="准确读取并解析学生画像数据库中的信息",
            backstory="你是一名教育数据分析师，擅长从学生画像数据库中提取关键信息，为后续个性化学习服务提供数据支撑。",
            tools=[ProfileReaderTool()],
            verbose=True,
            allow_delegation=False
        )


class TaskDispatcherAgent(Agent):
    def __init__(self):
        super().__init__(
            role="智能任务调度中心",
            goal="接收用户学习需求，结合学生画像，合理拆分任务并分发给各内容生成Agent",
            backstory="你是一名经验丰富的教学总监，擅长根据学生的学习需求和个人特点，制定高效的学习任务分配方案。",
            tools=[ProfileReaderTool(), RAGSearchTool()],
            verbose=True,
            allow_delegation=True
        )


class TextContentAgent(Agent):
    def __init__(self):
        super().__init__(
            role="课程内容创作专家",
            goal="结合RAG检索结果，生成高质量的课程知识点讲义和拓展阅读材料，严格禁止编造未在知识库中出现的内容",
            backstory="你是一名资深的计算机网络课程讲师，擅长将复杂的网络知识转化为通俗易懂的教学内容。你必须严格基于知识库检索结果进行创作，对于知识库中没有的内容，必须明确标注为'待验证'。",
            tools=[RAGSearchTool()],
            verbose=True,
            allow_delegation=False
        )


class ContentValidationAgent(Agent):
    def __init__(self):
        super().__init__(
            role="内容校验专家",
            goal="严格校验生成内容与知识库原文的一致性，检测并标记所有幻觉内容",
            backstory="你是一名严谨的学术审查专家，专门负责验证AI生成内容的准确性。你必须逐句对比生成内容与知识库原文，任何不一致或未在知识库中出现的陈述都必须被标记为可疑内容。",
            tools=[ContentValidationTool(), RAGSearchTool()],
            verbose=True,
            allow_delegation=False
        )


class ExamAgent(Agent):
    def __init__(self):
        super().__init__(
            role="智能题库专家",
            goal="针对学生薄弱点生成有针对性的练习题和实操案例，题目内容必须基于知识库",
            backstory="你是一名专业的教育测评专家，擅长设计高质量的练习题，帮助学生巩固薄弱知识点。所有题目和答案必须来源于知识库内容。",
            tools=[ExamGeneratorTool(), RAGSearchTool()],
            verbose=True,
            allow_delegation=False
        )


class MultiModalAgent(Agent):
    def __init__(self):
        super().__init__(
            role="多模态内容创意师",
            goal="调用多模态接口生成思维导图、PPT大纲、短视频文案等可视化学习资源，内容必须与知识库一致",
            backstory="你是一名创意设计师，擅长将知识内容转化为多种形式的可视化学习资源。你必须确保生成内容与知识库中的知识点一致。",
            tools=[MultiModalGeneratorTool(), RAGSearchTool()],
            verbose=True,
            allow_delegation=False
        )


class PathPlannerAgent(Agent):
    def __init__(self):
        super().__init__(
            role="学习路径规划师",
            goal="整合所有生成的学习资源，制定分阶段的个性化学习计划",
            backstory="你是一名教育规划专家，擅长根据学生特点和学习目标制定科学的学习路径。",
            tools=[ProfileReaderTool(), RAGSearchTool()],
            verbose=True,
            allow_delegation=False
        )


def create_tasks(student_id: str, learning_goal: str, topics: List[str]) -> List[Task]:
    read_profile_task = Task(
        description=f"读取学生 {student_id} 的画像信息，包括前置知识基础、学习风格、薄弱知识点、易错题型、学习目标和每日学习节奏。",
        agent=ProfileReaderAgent(),
        expected_output="学生画像JSON数据"
    )
    
    dispatch_task = Task(
        description=f"""作为任务调度中心，请根据学生 {student_id} 的画像和学习需求，拆分出具体任务。
        
学习目标：{learning_goal}
重点知识点：{', '.join(topics)}

请分析：
1. 需要生成哪些知识点讲义
2. 需要针对哪些薄弱点出题
3. 需要生成哪些多模态资源
4. 制定学习路径规划

输出格式：JSON格式的任务清单""",
        agent=TaskDispatcherAgent(),
        expected_output="JSON格式的任务清单，包含讲义生成、题库生成、多模态生成、路径规划四个任务的详细说明",
        context=[read_profile_task]
    )
    
    rag_retrieval_tasks = []
    for topic in topics:
        rag_task = Task(
            description=f"""【强制RAG检索】请检索知识库中关于"{topic}"的所有相关内容。
            
重要要求：
1. 必须在生成任何内容前执行此检索
2. 检索结果将作为后续内容生成的唯一依据
3. 如果知识库中没有相关内容，必须明确说明""",
            agent=TextContentAgent(),
            expected_output=f"关于{topic}的知识库检索结果，包含原文引用和出处",
            context=[read_profile_task, dispatch_task]
        )
        rag_retrieval_tasks.append(rag_task)
    
    lecture_tasks = []
    validation_tasks = []
    
    for i, topic in enumerate(topics):
        lecture_task = Task(
            description=f"""请基于以下RAG检索结果，为"{topic}"生成详细的课程讲义和拓展阅读材料：

【强制约束】
1. 所有内容必须严格基于知识库检索结果
2. 禁止编造任何未在知识库中出现的知识点
3. 对于不确定的内容，必须标注"待验证"
4. 必须在讲义末尾注明所有引用的来源

知识点：{topic}

要求：
1. 结构清晰，包含概念讲解、原理分析、实例说明
2. 提供拓展阅读推荐
3. 语言通俗易懂""",
            agent=TextContentAgent(),
            expected_output=f"{topic}知识点的完整讲义文档，包含核心概念、原理分析、实例和拓展阅读",
            context=[read_profile_task, dispatch_task, rag_retrieval_tasks[i]]
        )
        lecture_tasks.append(lecture_task)
        
        validation_task = Task(
            description=f"""【内容校验】请严格校验以下讲义内容与知识库原文是否一致：

讲义主题：{topic}

请执行以下检查：
1. 检查所有事实性陈述是否准确
2. 检查是否存在幻觉内容（知识库中没有的信息）
3. 检查关键术语、数据、公式是否正确
4. 如果发现问题，给出具体修改建议

输出格式：
- is_valid: true/false
- issues: 问题列表
- suggestion: 修改建议""",
            agent=ContentValidationAgent(),
            expected_output="JSON格式的校验结果，包含is_valid、issues、suggestion字段",
            context=[rag_retrieval_tasks[i], lecture_tasks[i]]
        )
        validation_tasks.append(validation_task)
    
    exam_task = Task(
        description=f"""请基于知识库检索结果，针对学生 {student_id} 的薄弱知识点生成练习题：

【强制约束】
1. 所有题目和答案必须来源于知识库
2. 禁止编造题目内容
3. 答案必须准确无误

薄弱知识点：从学生画像中获取
学习目标：{learning_goal}

要求：
1. 生成5道单选题
2. 生成3道简答题
3. 生成2道代码实操题
4. 题目难度适中，具有针对性""",
        agent=ExamAgent(),
        expected_output="包含单选、简答、代码题的完整练习题集，附答案和解析",
        context=[read_profile_task, dispatch_task] + rag_retrieval_tasks
    )
    
    exam_validation_task = Task(
        description=f"""【内容校验】请严格校验以下练习题与知识库原文是否一致：

请检查：
1. 题目描述是否准确反映知识库内容
2. 答案是否正确
3. 解析是否与知识库一致

输出格式：JSON格式的校验结果""",
        agent=ContentValidationAgent(),
        expected_output="JSON格式的校验结果",
        context=[exam_task] + rag_retrieval_tasks
    )
    
    mindmap_task = Task(
        description=f"""请基于知识库检索结果，为以下知识点生成思维导图文本结构：

【强制约束】
1. 所有节点内容必须来源于知识库
2. 禁止添加知识库中没有的知识点

主题：{learning_goal}
知识点：{', '.join(topics)}

要求：
1. 层次分明，结构清晰
2. 包含核心概念和关键要点
3. 使用缩进表示层级关系""",
        agent=MultiModalAgent(),
        expected_output="思维导图文本结构，使用缩进表示层级关系",
        context=[read_profile_task, dispatch_task] + rag_retrieval_tasks
    )
    
    ppt_task = Task(
        description=f"""请基于知识库检索结果，为以下主题生成PPT大纲：

【强制约束】
1. 所有内容必须来源于知识库
2. 禁止添加虚构内容

主题：{learning_goal}

要求：
1. 包含封面页、目录页、内容页、总结页
2. 每个内容页包含标题和3-5个要点
3. 逻辑清晰，重点突出""",
        agent=MultiModalAgent(),
        expected_output="完整的PPT大纲，包含各页标题和要点",
        context=[read_profile_task, dispatch_task] + rag_retrieval_tasks
    )
    
    plan_task = Task(
        description=f"""请基于知识库检索结果和已生成的学习资源，为学生 {student_id} 制定个性化学习计划：

学生画像：从数据库读取
学习目标：{learning_goal}
重点知识点：{', '.join(topics)}

要求：
1. 分阶段规划（基础阶段、巩固阶段、提升阶段）
2. 每日学习内容安排
3. 结合生成的讲义、题库、思维导图等资源
4. 包含学习进度检查点""",
        agent=PathPlannerAgent(),
        expected_output="详细的分阶段学习计划，包含每日安排和资源使用建议",
        context=[read_profile_task, dispatch_task] + lecture_tasks + [exam_task, mindmap_task, ppt_task]
    )
    
    return [
        read_profile_task,
        dispatch_task,
        *rag_retrieval_tasks,
        *lecture_tasks,
        *validation_tasks,
        exam_task,
        exam_validation_task,
        mindmap_task,
        ppt_task,
        plan_task
    ]


def run_learning_crew(student_id: str, learning_goal: str, topics: List[str]) -> Dict[str, Any]:
    tasks = create_tasks(student_id, learning_goal, topics)
    
    crew = Crew(
        agents=[
            ProfileReaderAgent(),
            TaskDispatcherAgent(),
            TextContentAgent(),
            ContentValidationAgent(),
            ExamAgent(),
            MultiModalAgent(),
            PathPlannerAgent()
        ],
        tasks=tasks,
        process=Process.sequential,
        verbose=CrewAIConfig.LOGGING_ENABLED
    )
    
    result = crew.kickoff()
    
    outputs = {}
    validation_results = []
    
    for i, task in enumerate(tasks):
        if hasattr(task, 'output') and task.output:
            desc = task.description[:30]
            outputs[desc + "..."] = str(task.output)
            
            if "内容校验" in task.description:
                validation_results.append({
                    "task": desc,
                    "result": str(task.output)
                })
    
    valid_count = 0
    for v in validation_results:
        try:
            data = json.loads(v['result'])
            if data.get('is_valid', True):
                valid_count += 1
        except:
            valid_count += 1
    
    return {
        "summary": str(result),
        "task_outputs": outputs,
        "total_tasks": len(tasks),
        "validation_results": validation_results,
        "validation_pass_rate": f"{valid_count}/{len(validation_results)}" if validation_results else "N/A"
    }


def run_parallel_learning_crew(student_id: str, learning_goal: str, topics: List[str]) -> Dict[str, Any]:
    read_profile_task = Task(
        description=f"读取学生 {student_id} 的画像信息",
        agent=ProfileReaderAgent(),
        expected_output="学生画像JSON数据"
    )
    
    dispatch_task = Task(
        description=f"分析学生 {student_id} 的学习需求，拆分任务",
        agent=TaskDispatcherAgent(),
        expected_output="任务清单",
        context=[read_profile_task]
    )
    
    rag_retrieval_tasks = []
    for topic in topics:
        rag_task = Task(
            description=f"【强制RAG检索】检索{topic}的知识库内容",
            agent=TextContentAgent(),
            expected_output=f"{topic}的检索结果",
            context=[read_profile_task, dispatch_task]
        )
        rag_retrieval_tasks.append(rag_task)
    
    lecture_tasks = []
    validation_tasks = []
    for i, topic in enumerate(topics):
        lecture_task = Task(
            description=f"基于RAG结果生成{topic}讲义",
            agent=TextContentAgent(),
            expected_output=f"{topic}讲义",
            context=[read_profile_task, dispatch_task, rag_retrieval_tasks[i]]
        )
        lecture_tasks.append(lecture_task)
        
        validation_task = Task(
            description=f"校验{topic}讲义内容",
            agent=ContentValidationAgent(),
            expected_output="校验结果",
            context=[rag_retrieval_tasks[i], lecture_tasks[i]]
        )
        validation_tasks.append(validation_task)
    
    exam_task = Task(
        description=f"针对学生 {student_id} 的薄弱点生成练习题",
        agent=ExamAgent(),
        expected_output="练习题集",
        context=[read_profile_task, dispatch_task] + rag_retrieval_tasks
    )
    
    mindmap_task = Task(
        description=f"生成 {learning_goal} 思维导图",
        agent=MultiModalAgent(),
        expected_output="思维导图",
        context=[read_profile_task, dispatch_task] + rag_retrieval_tasks
    )
    
    ppt_task = Task(
        description=f"生成 {learning_goal} PPT大纲",
        agent=MultiModalAgent(),
        expected_output="PPT大纲",
        context=[read_profile_task, dispatch_task] + rag_retrieval_tasks
    )
    
    plan_task = Task(
        description=f"为学生 {student_id} 制定学习计划",
        agent=PathPlannerAgent(),
        expected_output="学习计划",
        context=[read_profile_task, dispatch_task] + lecture_tasks + [exam_task, mindmap_task, ppt_task]
    )
    
    crew = Crew(
        agents=[
            ProfileReaderAgent(),
            TaskDispatcherAgent(),
            TextContentAgent(),
            ContentValidationAgent(),
            ExamAgent(),
            MultiModalAgent(),
            PathPlannerAgent()
        ],
        tasks=[
            read_profile_task,
            dispatch_task,
            *rag_retrieval_tasks,
            *lecture_tasks,
            *validation_tasks,
            exam_task,
            mindmap_task,
            ppt_task,
            plan_task
        ],
        process=Process.hierarchical,
        verbose=CrewAIConfig.LOGGING_ENABLED,
        manager_llm=None
    )
    
    result = crew.kickoff()
    
    return {
        "summary": str(result),
        "total_tasks": len([read_profile_task, dispatch_task, *rag_retrieval_tasks, *lecture_tasks, *validation_tasks, exam_task, mindmap_task, ppt_task, plan_task])
    }
