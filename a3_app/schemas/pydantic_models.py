# 数据Schema
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ====== Auth ======
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str = "新同学"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    display_name: str

# ====== Profile ======
class UserProfileResponse(BaseModel):
    math_basics: float = 2.0
    programming_basics: float = 2.0
    domain_knowledge: float = 1.0
    learning_efficiency: float = 3.0
    self_discipline: float = 3.0
    weakness_awareness: float = 2.0
    cognitive_style: str = "mixed"
    daily_study_hours: float = 2.0
    goal: str = ""
    weak_points: List[str] = []
    strong_points: List[str] = []
    radar_labels: List[str] = ["高数", "编程", "ML领域", "效率", "自律", "薄弱认知"]

class RadarData(BaseModel):
    before: List[float]
    after: List[float]
    labels: List[str]

# ====== Chat ======
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    agent_type: str = "diagnose"  # diagnose/plan/teach/quiz
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    agent_type: str
    quick_options: List[str] = []
    profile_update: Optional[dict] = None
    metadata: dict = {}

# ====== Path ======
class PathNodeData(BaseModel):
    id: Optional[int] = None
    week_number: int
    title: str
    status: str = "pending"
    estimated_hours: float = 4.0
    resources: List[dict] = []

class LearningPathResponse(BaseModel):
    id: int
    title: str
    total_weeks: int
    current_week: int
    progress_percent: float
    nodes: List[PathNodeData]

# ====== Resource ======
class ResourceResponse(BaseModel):
    id: int
    title: str
    resource_type: str
    content: str
    quality_score: int
    quality_status: str
    meta_tags: List[str] = []
    is_favorited: bool = False
    created_at: str

class ResourceListResponse(BaseModel):
    resources: List[ResourceResponse]
    avg_quality: float
    total: int

# ====== Knowledge ======
class KnowledgeNodeData(BaseModel):
    name: str
    mastery: int
    status: str
    category: str

class KnowledgeGraphResponse(BaseModel):
    nodes: List[KnowledgeNodeData]
    mastered_count: int
    total_count: int

# ====== Report ======
class StudyReportResponse(BaseModel):
    today_hours: float
    total_hours: float
    progress: float
    accuracy: float
    streak_days: int
    questions_asked: int
    radar: RadarData
    knowledge_detail: List[dict]
    agent_suggestion: str
