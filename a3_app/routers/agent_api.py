# Agent对话 + 画像API v1.1
# 修复: 1) 诊断Agent per-session隔离  2) 真实token认证  3) process_answer调用bug修复
import json
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from typing import Optional

from database import get_db
from models.db_models import User, UserProfile, ChatMessage
from schemas.pydantic_models import ChatRequest, ChatResponse, UserProfileResponse, RadarData
from agents.diagnose import DiagnoseAgent
from agents.planner import PlannerAgent
from agents.generator import GeneratorAgent
from agents.quality import QualityAgent
from agents.tutor import TutorAgent
from config import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/agent", tags=["智能体"])

# ── Session-级别的诊断Agent池（key: session_id） ──
# 修复v1.0全局单例问题，每个session独立一个DiagnoseAgent实例
_diagnose_sessions: dict[str, DiagnoseAgent] = {}

# 其他Agent是无状态的，全局单例即可
_planner = PlannerAgent()
_generator = GeneratorAgent()
_quality = QualityAgent()
_tutor = TutorAgent()


def get_diagnose_agent(session_id: str) -> DiagnoseAgent:
    if session_id not in _diagnose_sessions:
        _diagnose_sessions[session_id] = DiagnoseAgent()
    return _diagnose_sessions[session_id]


def get_current_user_id(authorization: Optional[str] = Header(None)) -> int:
    """从 Authorization: Bearer <token> 提取用户ID，失败则返回1（演示模式）"""
    if not authorization or not authorization.startswith("Bearer "):
        return 1  # 演示模式默认用户
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="无效token，请重新登录")


@router.post("/chat")
async def agent_chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Agent对话接口 - 支持诊断/规划/教学/辅导四种模式"""
    user_id = get_current_user_id(authorization)
    session_id = req.session_id or f"user_{user_id}_default"

    # ── 诊断Agent ──
    if req.agent_type == "diagnose":
        agent = get_diagnose_agent(session_id)
        result = agent.process_answer(req.message)  # v1.1修复：只传answer

        # 保存对话记录
        for role, content in [("user", req.message), ("agent", result["reply"])]:
            msg = ChatMessage(
                user_id=user_id, session_id=session_id,
                agent_type=req.agent_type, role=role, content=content
            )
            db.add(msg)

        # 诊断完成 → 持久化画像
        if result.get("is_done") and result.get("profile"):
            p = result["profile"]
            up_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
            profile = up_result.scalar_one_or_none()
            if profile:
                profile.math_basics = p["math_basics"]
                profile.programming_basics = p["programming_basics"]
                profile.domain_knowledge = p["domain_knowledge"]
                profile.cognitive_style = p["cognitive_style"]
                profile.daily_study_hours = p["daily_study_hours"]
                profile.self_discipline = p["self_discipline"]
                profile.goal_description = p["goal"]
                profile.weak_points = json.dumps(p["weak_points"], ensure_ascii=False)
                profile.strong_points = json.dumps(p["strong_points"], ensure_ascii=False)
            # 诊断完成后清除session，释放内存
            _diagnose_sessions.pop(session_id, None)

        await db.commit()
        return ChatResponse(
            session_id=session_id,
            reply=result["reply"],
            agent_type=req.agent_type,
            quick_options=result.get("options", []),
            metadata={
                "step": result.get("step", 0),
                "total_steps": result.get("total_steps", 5),
                "is_done": result.get("is_done", False),
                "profile": result.get("profile")
            }
        )

    # ── 规划Agent ──
    elif req.agent_type == "plan":
        up_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        profile = up_result.scalar_one_or_none()
        profile_data = {
            "goal": profile.goal_description if profile else "",
            "math_basics": profile.math_basics if profile else 2.0,
            "programming_basics": profile.programming_basics if profile else 2.0,
            "daily_study_hours": profile.daily_study_hours if profile else 2.0,
        }
        path = await _planner.generate_path(profile_data)

        # 保存对话
        for role, content in [("user", req.message), ("agent", f"已为你生成学习路径：{path['title']}")]:
            db.add(ChatMessage(user_id=user_id, session_id=session_id,
                               agent_type=req.agent_type, role=role, content=content))
        await db.commit()

        return ChatResponse(
            session_id=session_id,
            reply=f"📚 已根据你的画像生成【{path['title']}】，共{len(path['nodes'])}周计划。点击「学习路径」查看详情。",
            agent_type=req.agent_type,
            metadata={"path": path}
        )

    # ── 辅导/教学/其他Agent ──
    else:
        agent = _tutor if req.agent_type == "tutor" else _generator
        result = await agent.process(req.message, {"agent_type": req.agent_type})

        for role, content in [("user", req.message), ("agent", result.get("reply", ""))]:
            db.add(ChatMessage(user_id=user_id, session_id=session_id,
                               agent_type=req.agent_type, role=role, content=content))
        await db.commit()

        return ChatResponse(
            session_id=session_id,
            reply=result.get("reply", "已收到你的问题，正在处理..."),
            agent_type=req.agent_type,
            metadata=result
        )


@router.get("/diagnose/init/{session_id}")
async def init_diagnose(session_id: str):
    """初始化诊断会话，返回第一个问题"""
    agent = get_diagnose_agent(session_id)
    agent.reset()
    q = agent.get_initial_question()
    return {
        "session_id": session_id,
        "reply": q["question"],
        "options": q["options"],
        "step": 0,
        "total_steps": len(agent.dialogue_flow)
    }


@router.get("/profile/{user_id}")
async def get_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取用户画像"""
    up = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = up.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "画像不存在，请先完成诊断对话")

    weak = json.loads(profile.weak_points) if profile.weak_points else []
    strong = json.loads(profile.strong_points) if profile.strong_points else []

    return UserProfileResponse(
        math_basics=profile.math_basics,
        programming_basics=profile.programming_basics,
        domain_knowledge=profile.domain_knowledge,
        learning_efficiency=profile.learning_efficiency,
        self_discipline=profile.self_discipline,
        weakness_awareness=profile.weakness_awareness,
        cognitive_style=profile.cognitive_style,
        daily_study_hours=profile.daily_study_hours,
        goal=profile.goal_description or "",
        weak_points=weak,
        strong_points=strong
    )


@router.get("/radar/{user_id}")
async def get_radar(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取雷达图数据（前后对比）"""
    up = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = up.scalar_one_or_none()
    if not profile:
        raise HTTPException(404, "画像不存在")

    before = [1.5, 2.0, 1.0, 2.5, 2.5, 1.5]
    after = [
        min(5.0, profile.math_basics),
        min(5.0, profile.programming_basics),
        min(5.0, profile.domain_knowledge + 0.5),
        min(5.0, profile.learning_efficiency),
        min(5.0, profile.self_discipline),
        min(5.0, profile.weakness_awareness + 1.0)
    ]

    return RadarData(
        before=before,
        after=after,
        labels=["数学基础", "编程能力", "领域知识", "学习效率", "自律程度", "薄弱认知"]
    )
