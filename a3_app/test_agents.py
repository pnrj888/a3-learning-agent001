import asyncio
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_agents():
    print("=" * 60)
    print("Agent LLM 改造测试")
    print("=" * 60)
    
    os.environ["USE_MOCK_LLM"] = "true"
    
    from agents.diagnose import DiagnoseAgent
    from agents.tutor import TutorAgent
    from agents.generator import GeneratorAgent
    from agents.planner import PlannerAgent
    from agents.quality import QualityAgent
    
    print("\n1. 测试 DiagnoseAgent（诊断Agent）")
    print("-" * 40)
    diag = DiagnoseAgent()
    result = diag.process_answer("机器学习入门")
    print(f"   回答处理: step={result['step']}, is_done={result['is_done']}")
    result = diag.process_answer("学过高等数学")
    reply = result['reply'][:30] if len(result['reply']) > 30 else result['reply']
    print(f"   数学基础: {reply}...")
    diag.reset()
    print(f"   Stats: {diag.get_stats()}")
    
    print("\n2. 测试 TutorAgent（辅导Agent）")
    print("-" * 40)
    tutor = TutorAgent()
    result = await tutor.answer_question("什么是梯度下降？")
    reply = result['reply'][:50] if len(result['reply']) > 50 else result['reply']
    reply = reply.encode('utf-8', errors='replace').decode('utf-8')
    print(f"   匹配知识库回答: {reply}...")
    result = await tutor.answer_question("什么是深度学习？")
    reply = result['reply'][:50] if len(result['reply']) > 50 else result['reply']
    reply = reply.encode('utf-8', errors='replace').decode('utf-8')
    print(f"   LLM回答: {reply}...")
    print(f"   Stats: {tutor.get_stats()}")
    
    print("\n3. 测试 GeneratorAgent（生成Agent）")
    print("-" * 40)
    gen = GeneratorAgent()
    resources = await gen.generate_resources("线性回归", "beginner")
    print(f"   生成资源数: {len(resources)}")
    for r in resources[:2]:
        title = r['title'][:30] if len(r['title']) > 30 else r['title']
        print(f"   - {r['type']}: {title}... (quality={r.get('quality', 'N/A')})")
    print(f"   Stats: {gen.get_stats()}")
    
    print("\n4. 测试 PlannerAgent（规划Agent）")
    print("-" * 40)
    planner = PlannerAgent()
    profile = {
        "goal": "机器学习入门",
        "math_basics": 3.0,
        "programming_basics": 2.5,
        "daily_study_hours": 2.0,
        "weak_points": ["数学基础"]
    }
    path = await planner.generate_path(profile)
    print(f"   路径标题: {path['title']}")
    print(f"   周数: {len(path['nodes'])}")
    for node in path['nodes'][:3]:
        print(f"   - Week {node['week']}: {node['title']} ({node['hours']}h)")
    print(f"   Stats: {planner.get_stats()}")
    
    print("\n5. 测试 QualityAgent（质检Agent）")
    print("-" * 40)
    qa = QualityAgent()
    resource = {
        "type": "lecture",
        "title": "线性回归讲义",
        "content": "线性回归是一种用于预测连续值的机器学习算法。"
    }
    result = await qa.check_resource(resource)
    print(f"   质检结果: passed={result['passed']}, score={result['score']}")
    checks_str = ", ".join([f"{k}: {v['score']}" for k, v in result['checks'].items()])
    print(f"   各维度评分: {checks_str}")
    print(f"   Stats: {qa.get_stats()}")
    
    print("\n" + "=" * 60)
    print("所有 Agent 测试通过！")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agents())
