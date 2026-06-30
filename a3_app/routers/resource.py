# 资源管理路由
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.db_models import Resource, KnowledgeNode
from schemas.pydantic_models import ResourceResponse, ResourceListResponse, KnowledgeGraphResponse, KnowledgeNodeData
from agents.generator import GeneratorAgent
from agents.quality import QualityAgent

router = APIRouter(prefix="/api/resource", tags=["资源"])

@router.get("/list/{user_id}")
async def list_resources(user_id: int, topic: str = Query(""), db: AsyncSession = Depends(get_db)):
    """获取资源列表"""
    stmt = select(Resource).where(Resource.user_id == user_id).order_by(Resource.created_at.desc())
    if topic:
        stmt = stmt.where(Resource.title.like(f"%{topic}%"))
    result = await db.execute(stmt)
    resources = result.scalars().all()
    
    items = []
    for r in resources:
        tags = json.loads(r.meta_tags) if r.meta_tags else []
        items.append(ResourceResponse(
            id=r.id, title=r.title, resource_type=r.resource_type,
            content=r.content[:200] + "..." if len(r.content) > 200 else r.content,
            quality_score=r.quality_score, quality_status=r.quality_status,
            meta_tags=tags, is_favorited=r.is_favorited,
            created_at=r.created_at.strftime("%Y-%m-%d %H:%M")
        ))
    
    avg = sum(r.quality_score for r in resources) / max(len(resources), 1)
    return ResourceListResponse(resources=items, avg_quality=round(avg, 1), total=len(items))

@router.post("/generate/{user_id}")
async def generate_resources(user_id: int, topic: str, db: AsyncSession = Depends(get_db)):
    """生成指定主题的学习资源"""
    gen = GeneratorAgent()
    qc = QualityAgent()
    
    gen_resources = await gen.generate_resources(topic)
    saved = []
    
    for r in gen_resources:
        # 质检
        qc_result = await qc.check_resource(r)
        quality = qc_result.get("score", qc_result.get("checks", {}).get("accuracy", {}).get("score", 85))
        
        resource = Resource(
            user_id=user_id, title=r["title"],
            resource_type=r["type"], content=r["content"],
            quality_score=quality,
            quality_status="passed" if qc_result.get("passed", True) else "rejected",
            meta_tags=json.dumps(r.get("tags", []), ensure_ascii=False)
        )
        db.add(resource)
        await db.flush()
        saved.append({
            "id": resource.id, "title": resource.title, "type": resource.resource_type,
            "quality": quality, "status": resource.quality_status
        })
    
    await db.commit()
    return {"resources": saved, "count": len(saved)}

@router.post("/favorite/{resource_id}")
async def toggle_favorite(resource_id: int, db: AsyncSession = Depends(get_db)):
    """收藏/取消收藏"""
    r = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = r.scalar_one_or_none()
    if not resource:
        raise HTTPException(404, "资源不存在")
    resource.is_favorited = not resource.is_favorited
    await db.commit()
    return {"id": resource_id, "is_favorited": resource.is_favorited}

@router.get("/knowledge/{user_id}")
async def get_knowledge_graph(user_id: int, db: AsyncSession = Depends(get_db)):
    """获取知识图谱"""
    result = await db.execute(select(KnowledgeNode).where(KnowledgeNode.user_id == user_id))
    nodes = result.scalars().all()
    
    if not nodes:
        # 返回默认数据
        default_nodes = [
            KnowledgeNodeData(name="Python基础", mastery=92, status="mastered", category="基础"),
            KnowledgeNodeData(name="线性代数回顾", mastery=88, status="mastered", category="数学"),
            KnowledgeNodeData(name="概率论基础", mastery=75, status="mastered", category="数学"),
            KnowledgeNodeData(name="线性回归", mastery=70, status="in_progress", category="算法"),
            KnowledgeNodeData(name="逻辑回归", mastery=55, status="in_progress", category="算法"),
            KnowledgeNodeData(name="代价函数", mastery=82, status="mastered", category="算法"),
            KnowledgeNodeData(name="梯度下降", mastery=65, status="in_progress", category="算法"),
            KnowledgeNodeData(name="反向传播", mastery=20, status="not_started", category="算法"),
            KnowledgeNodeData(name="神经网络", mastery=10, status="not_started", category="算法"),
            KnowledgeNodeData(name="过拟合与正则化", mastery=5, status="not_started", category="算法"),
            KnowledgeNodeData(name="决策树", mastery=0, status="not_started", category="算法"),
            KnowledgeNodeData(name="集成学习", mastery=0, status="not_started", category="算法"),
        ]
        mastered = sum(1 for n in default_nodes if n.status == "mastered")
        return KnowledgeGraphResponse(nodes=default_nodes, mastered_count=mastered, total_count=len(default_nodes))
    
    items = [KnowledgeNodeData(name=n.name, mastery=n.mastery, status=n.status, category=n.category) for n in nodes]
    mastered = sum(1 for n in items if n.status == "mastered")
    return KnowledgeGraphResponse(nodes=items, mastered_count=mastered, total_count=len(items))
