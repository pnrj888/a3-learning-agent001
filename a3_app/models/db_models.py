# 数据模型
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    display_name = Column(String(50), default="新同学")
    avatar = Column(String(255), default="")
    role = Column(String(20), default="student")  # student / teacher
    created_at = Column(DateTime, default=datetime.utcnow)
    
    profile = relationship("UserProfile", uselist=False, back_populates="user")
    paths = relationship("LearningPath", back_populates="user")
    messages = relationship("ChatMessage", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # 6维画像 (1-5评分)
    math_basics = Column(Float, default=2.0)        # 数学基础
    programming_basics = Column(Float, default=2.0)  # 编程基础
    domain_knowledge = Column(Float, default=1.0)    # 领域知识(ML/DL)
    learning_efficiency = Column(Float, default=3.0) # 学习效率
    self_discipline = Column(Float, default=3.0)     # 自律性
    weakness_awareness = Column(Float, default=2.0)  # 薄弱点认知
    
    cognitive_style = Column(String(20), default="mixed")  # visual/reading/hands-on/mixed
    daily_study_hours = Column(Float, default=2.0)
    goal_description = Column(Text, default="")
    weak_points = Column(Text, default="")  # JSON array string
    strong_points = Column(Text, default="")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="profile")

class LearningPath(Base):
    __tablename__ = "learning_paths"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200))
    total_weeks = Column(Integer, default=8)
    current_week = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active/completed/paused
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="paths")
    nodes = relationship("PathNode", back_populates="path", cascade="all, delete-orphan")

class PathNode(Base):
    __tablename__ = "path_nodes"
    id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"))
    week_number = Column(Integer)
    title = Column(String(200))
    status = Column(String(20), default="pending")  # pending/in_progress/completed
    estimated_hours = Column(Float, default=4.0)
    actual_hours = Column(Float, default=0.0)
    resources_completed = Column(Integer, default=0)
    resources_total = Column(Integer, default=4)
    sort_order = Column(Integer, default=0)
    
    path = relationship("LearningPath", back_populates="nodes")

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    path_node_id = Column(Integer, ForeignKey("path_nodes.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200))
    resource_type = Column(String(20))  # lecture/exercise/mindmap/code/video
    content = Column(Text, default="")
    quality_score = Column(Integer, default=0)  # 质检评分0-100
    quality_status = Column(String(20), default="pending")  # pending/passed/rejected
    meta_tags = Column(Text, default="")  # JSON array
    is_favorited = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(50), index=True)
    agent_type = Column(String(20))  # diagnose/plan/teach/quiz
    role = Column(String(10))  # user/agent
    content = Column(Text)
    metadata_json = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="messages")

class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    mastery = Column(Integer, default=0)  # 0-100
    status = Column(String(20), default="not_started")  # not_started/in_progress/mastered
    category = Column(String(50), default="")
    prerequisites = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
