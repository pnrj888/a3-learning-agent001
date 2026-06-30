"""
A3 赛题全局统一设计规范 - 基于大模型的个性化资源生成与学习多智能体系统开发
AtomCode 项目开发手册标准 | TRAE Work Design
版本: v3.0 | 出题企业: 科大讯飞
"""
import streamlit as st
from typing import List, Dict, Optional
import uuid

# ============================================================================
# 第一部分: 色彩体系 (Color Tokens)
# ============================================================================
class ColorTokens:
    """固定色彩体系 - 全部页面严格遵循"""
    PRIMARY = "#2563EB"          # 科技深蓝 - 主色调(导航/主按钮/图表)
    PRIMARY_HOVER = "#1D4ED8"   # 深蓝hover
    LIGHT_BLUE = "#E8F0FE"      # 辅助浅蓝 - 卡片背景/hover状态
    AGENT_GREEN = "#10B981"     # 智能体强调绿 - Agent标识/成功/进度
    WARNING_RED = "#EF4444"     # 警示红 - 薄弱知识点/错误/高风险
    WARNING_RED_LIGHT = "#FEF2F2"  # 浅红背景
    DARK_GRAY = "#111827"       # 文本深灰 - 标题/正文
    MID_GRAY = "#374151"        # 中灰 - 辅助文字/正文说明
    LIGHT_GRAY = "#6B7280"      # 浅灰 - 技术标注/次要文字
    BG_WHITE = "#FFFFFF"        # 背景纯白
    BG_GRAY = "#F9FAFB"         # 浅灰背景
    CARD_BORDER = "#E5E7EB"     # 卡片边框
    GLOW_BLUE = "rgba(37,99,235,0.15)"    # 蓝色微光
    GLOW_GREEN = "rgba(16,185,129,0.15)"  # 绿色微光

# ============================================================================
# 第二部分: 全局CSS (Global Stylesheet)
# ============================================================================
GLOBAL_CSS = f"""
<style>
/* === Google Fonts === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* === CSS Reset & Base === */
* {{ box-sizing: border-box; }}
body {{ font-family: 'Inter', 'Source Han Sans SC', -apple-system, sans-serif; background: {ColorTokens.BG_WHITE}; color: {ColorTokens.DARK_GRAY}; }}

/* === Typography === */
h1, h2, h3, h4 {{ font-family: 'Inter', sans-serif; font-weight: 700; letter-spacing: -0.025em; }}
h1 {{ font-size: 28px; color: {ColorTokens.DARK_GRAY}; }}
h2 {{ font-size: 22px; color: {ColorTokens.DARK_GRAY}; }}
h3 {{ font-size: 18px; color: {ColorTokens.DARK_GRAY}; }}
p  {{ font-size: 14px; line-height: 1.7; color: {ColorTokens.MID_GRAY}; }}

/* === Markdown 正文/列表统一颜色（解决浅色背景下看不清的问题） === */
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
.element-container .stMarkdown {{ color: {ColorTokens.MID_GRAY} !important; }}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
.stMarkdown strong, .stMarkdown b {{ color: {ColorTokens.DARK_GRAY} !important; }}
.stMarkdown ul, .stMarkdown ol {{ color: {ColorTokens.MID_GRAY} !important; }}
.stMarkdown code {{ color: {ColorTokens.PRIMARY}; background: {ColorTokens.LIGHT_BLUE}; padding: 2px 6px; border-radius: 4px; font-size: 13px; }}

/* === Streamlit Overrides === */
.stApp {{ background: {ColorTokens.BG_WHITE}; }}
header[data-testid="stHeader"] {{ display: none !important; }}
button[data-testid="stAppDeployButton"] {{ display: none !important; }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0B1120 0%, #111827 100%) !important; }}
section[data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.95) !important; }}
section[data-testid="stSidebar"] svg {{ fill: rgba(255,255,255,0.95) !important; }}

section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {{
    background: rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.95) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    margin: 4px 0 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}}
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {{
    background: rgba(255,255,255,0.15) !important;
    border-color: rgba(255,255,255,0.2) !important;
}}
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:active {{
    background: {ColorTokens.PRIMARY} !important;
    color: white !important;
}}
.stButton > button, .stDownloadButton > button {{ 
    font-family: 'Inter', sans-serif; font-weight: 600; font-size: 14px;
    border-radius: 10px !important; border: none; cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); padding: 10px 24px;
}}

/* === 全局按钮规范: 10px圆角 === */
.ds-btn {{
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 20px; border-radius: 10px; font-family: 'Inter', sans-serif;
    font-weight: 600; font-size: 14px; cursor: pointer; border: none;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    text-decoration: none; white-space: nowrap;
}}
.ds-btn-primary {{ background: {ColorTokens.PRIMARY}; color: white; }}
.ds-btn-primary:hover {{ background: {ColorTokens.PRIMARY_HOVER}; box-shadow: 0 4px 12px rgba(37,99,235,0.3); transform: translateY(-1px); }}
.ds-btn-green {{ background: {ColorTokens.AGENT_GREEN}; color: white; }}
.ds-btn-green:hover {{ background: #059669; box-shadow: 0 4px 12px rgba(16,185,129,0.3); }}
.ds-btn-outline {{ background: transparent; border: 2px solid {ColorTokens.PRIMARY}; color: {ColorTokens.PRIMARY}; }}
.ds-btn-outline:hover {{ background: {ColorTokens.LIGHT_BLUE}; }}

/* === AI流光按钮 === */
.ai-glow-btn {{
    position: relative; overflow: hidden; background: {ColorTokens.PRIMARY}; color: white;
    border: none; border-radius: 10px; padding: 12px 28px; font-size: 14px; font-weight: 600;
    cursor: pointer; transition: all 0.3s;
}}
.ai-glow-btn::before {{
    content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.2) 45%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0.2) 55%, transparent 60%);
    animation: aiShimmer 2.5s infinite; 
}}
.ai-glow-btn:hover {{ box-shadow: 0 0 20px {ColorTokens.GLOW_BLUE}; transform: translateY(-2px); }}
.ai-glow-btn:disabled {{ background: {ColorTokens.LIGHT_GRAY}; animation: none; cursor: not-allowed; }}
.ai-glow-btn:disabled::before {{ display: none; }}

@keyframes aiShimmer {{
    0% {{ transform: translateX(-100%) translateY(-100%); }}
    100% {{ transform: translateX(100%) translateY(100%); }}
}}

/* === AI智能体微光脉冲 === */
@keyframes agentPulse {{
    0%, 100% {{ box-shadow: 0 0 0 0 {ColorTokens.GLOW_GREEN}; }}
    50% {{ box-shadow: 0 0 0 8px transparent; }}
}}
@keyframes agentPulseBlue {{
    0%, 100% {{ box-shadow: 0 0 0 0 {ColorTokens.GLOW_BLUE}; }}
    50% {{ box-shadow: 0 0 0 8px transparent; }}
}}

/* === 流式文字淡入 === */
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.stream-fade {{ animation: fadeInUp 0.4s ease-out; }}

/* === 进度条 === */
.ds-progress {{ height: 8px; background: {ColorTokens.BG_GRAY}; border-radius: 10px; overflow: hidden; }}
.ds-progress-fill {{ height: 100%; border-radius: 10px; background: linear-gradient(90deg, {ColorTokens.PRIMARY}, {ColorTokens.AGENT_GREEN}); 
    transition: width 0.5s ease; animation: progressFlow 2s ease-in-out infinite; }}
@keyframes progressFlow {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* === 卡片系统 === */
.ds-card {{
    background: {ColorTokens.BG_WHITE}; border: 1px solid {ColorTokens.CARD_BORDER};
    border-radius: 12px; padding: 20px; margin-bottom: 16px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
.ds-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.06); border-color: {ColorTokens.LIGHT_BLUE}; }}
.ds-card-blue {{ border-left: 4px solid {ColorTokens.PRIMARY}; background: {ColorTokens.LIGHT_BLUE}; }}
.ds-card-green {{ border-left: 4px solid {ColorTokens.AGENT_GREEN}; background: #ECFDF5; }}
.ds-card-red {{ border-left: 4px solid {ColorTokens.WARNING_RED}; background: {ColorTokens.WARNING_RED_LIGHT}; }}

/* === 6维画像卡片 === */
.profile-dim-card {{
    background: {ColorTokens.BG_WHITE}; border: 1px solid {ColorTokens.CARD_BORDER};
    border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 8px;
    transition: all 0.3s; height: 100%;
}}
.profile-dim-card:hover {{ border-color: {ColorTokens.PRIMARY}; box-shadow: 0 4px 12px {ColorTokens.GLOW_BLUE}; }}
.profile-dim-icon {{ font-size: 24px; margin-bottom: 4px; }}
.profile-dim-title {{ font-size: 13px; font-weight: 700; color: {ColorTokens.DARK_GRAY}; }}
.profile-dim-value {{ font-size: 12px; color: {ColorTokens.MID_GRAY}; line-height: 1.6; }}
.profile-dim-tag {{
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 500; margin: 2px;
}}
.tag-blue {{ background: {ColorTokens.LIGHT_BLUE}; color: {ColorTokens.PRIMARY}; }}
.tag-green {{ background: #ECFDF5; color: {ColorTokens.AGENT_GREEN}; }}
.tag-red {{ background: {ColorTokens.WARNING_RED_LIGHT}; color: {ColorTokens.WARNING_RED}; }}

/* === 五智能体协同流转面板 === */
.agent-flow-panel {{
    display: flex; align-items: center; gap: 12px; padding: 24px;
    background: linear-gradient(135deg, {ColorTokens.BG_GRAY} 0%, {ColorTokens.LIGHT_BLUE} 100%);
    border-radius: 16px; overflow-x: auto; margin: 16px 0;
}}
.agent-node {{
    min-width: 100px; text-align: center; padding: 14px 16px;
    background: {ColorTokens.BG_WHITE}; border-radius: 12px;
    border: 2px solid {ColorTokens.CARD_BORDER}; transition: all 0.3s;
}}
.agent-node:hover {{ border-color: {ColorTokens.PRIMARY}; transform: scale(1.05); }}
.agent-node.active {{ border-color: {ColorTokens.AGENT_GREEN}; animation: agentPulse 2s infinite; }}
.agent-node.processing {{ border-color: {ColorTokens.PRIMARY}; animation: agentPulseBlue 1.5s infinite; }}
.agent-node-icon {{ font-size: 28px; }}
.agent-node-name {{ font-size: 11px; font-weight: 600; color: {ColorTokens.DARK_GRAY}; margin-top: 6px; }}
.agent-node-status {{ font-size: 10px; margin-top: 4px; }}
.agent-arrow {{ font-size: 20px; color: {ColorTokens.PRIMARY}; min-width: 30px; text-align: center; }}

/* === 多模态资源卡片 === */
.resource-card {{
    display: flex; align-items: flex-start; gap: 14px; padding: 16px;
    background: {ColorTokens.BG_WHITE}; border: 1px solid {ColorTokens.CARD_BORDER};
    border-radius: 12px; margin-bottom: 10px; transition: all 0.3s;
}}
.resource-card:hover {{ border-color: {ColorTokens.PRIMARY}; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
.resource-icon {{ font-size: 28px; flex-shrink: 0; }}
.resource-info {{ flex: 1; }}
.resource-title {{ font-size: 14px; font-weight: 600; color: {ColorTokens.DARK_GRAY}; }}
.resource-meta {{ font-size: 12px; color: {ColorTokens.LIGHT_GRAY}; margin-top: 4px; }}
.resource-tag {{
    display: inline-block; padding: 2px 8px; border-radius: 6px;
    font-size: 10px; font-weight: 500; margin-right: 4px;
}}

/* === RAG引用来源标识 === */
.rag-citation {{
    display: flex; align-items: center; gap: 6px; padding: 6px 12px;
    background: {ColorTokens.BG_GRAY}; border-left: 3px solid {ColorTokens.PRIMARY};
    border-radius: 6px; font-size: 11px; color: {ColorTokens.MID_GRAY};
    margin-top: 8px; margin-bottom: 4px;
}}
.rag-citation-icon {{ color: {ColorTokens.PRIMARY}; font-size: 12px; }}
.rag-source-chip {{
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 8px; background: {ColorTokens.LIGHT_BLUE};
    border-radius: 4px; font-size: 10px; color: {ColorTokens.PRIMARY};
    font-weight: 500;
}}

/* === 知识图谱热力图 === */
.heatmap-container {{
    padding: 20px; background: {ColorTokens.BG_WHITE};
    border: 1px solid {ColorTokens.CARD_BORDER}; border-radius: 12px;
}}
.heatmap-cell {{
    display: inline-block; width: 40px; height: 40px; margin: 3px;
    border-radius: 6px; transition: all 0.3s; cursor: pointer;
    position: relative;
}}
.heatmap-cell:hover {{ transform: scale(1.1); z-index: 10; }}
.heatmap-mastery-90 {{ background: {ColorTokens.AGENT_GREEN}; opacity: 0.9; }}
.heatmap-mastery-70 {{ background: #34D399; opacity: 0.8; }}
.heatmap-mastery-50 {{ background: #FBBF24; opacity: 0.8; }}
.heatmap-mastery-30 {{ background: #F87171; opacity: 0.7; }}
.heatmap-mastery-10 {{ background: {ColorTokens.WARNING_RED}; opacity: 0.6; }}

/* === 问答面板 === */
.qa-panel {{ padding: 20px; background: {ColorTokens.BG_WHITE}; border-radius: 12px; }}
.qa-question {{
    padding: 12px 16px; background: {ColorTokens.LIGHT_BLUE};
    border-radius: 10px 10px 4px 10px; margin-bottom: 8px;
    font-size: 14px; color: {ColorTokens.DARK_GRAY};
}}
.qa-answer {{
    padding: 14px 16px; background: {ColorTokens.BG_GRAY};
    border-radius: 10px 10px 10px 4px; margin-bottom: 12px;
    font-size: 14px; line-height: 1.7;
}}

/* === 交互状态指示器 === */
.status-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
}}
.status-running {{ background: #FEF3C7; color: #D97706; }}
.status-success {{ background: #ECFDF5; color: {ColorTokens.AGENT_GREEN}; }}
.status-error {{ background: {ColorTokens.WARNING_RED_LIGHT}; color: {ColorTokens.WARNING_RED}; }}
.status-idle {{ background: {ColorTokens.BG_GRAY}; color: {ColorTokens.LIGHT_GRAY}; }}

.status-dot {{
    display: inline-block; width: 8px; height: 8px; border-radius: 50%;
    animation: statusPulse 1.5s infinite;
}}
@keyframes statusPulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.4; }}
}}

/* === 容错提示弹窗 === */
.toast-notify {{
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px; border-radius: 12px; margin: 10px 0;
    font-size: 13px; animation: fadeInUp 0.3s ease-out;
}}
.toast-warning {{ background: #FFFBEB; border: 1px solid #FCD34D; color: #92400E; }}
.toast-error {{ background: {ColorTokens.WARNING_RED_LIGHT}; border: 1px solid {ColorTokens.WARNING_RED}; color: #991B1B; }}
.toast-info {{ background: {ColorTokens.LIGHT_BLUE}; border: 1px solid {ColorTokens.PRIMARY}; color: {ColorTokens.PRIMARY}; }}
.toast-icon {{ font-size: 18px; flex-shrink: 0; }}

/* === 学情图表容器 === */
.chart-container {{
    padding: 20px; background: {ColorTokens.BG_WHITE};
    border: 1px solid {ColorTokens.CARD_BORDER}; border-radius: 12px;
    margin-bottom: 16px;
}}
.chart-title {{ font-size: 14px; font-weight: 700; color: {ColorTokens.DARK_GRAY}; margin-bottom: 12px; }}

/* === 技术标注 - 页面角落浅灰小字 === */
.tech-annotation {{
    position: fixed; bottom: 16px; right: 20px;
    display: flex; gap: 10px; z-index: 999;
}}
.tech-chip {{
    padding: 4px 10px; background: {ColorTokens.BG_GRAY};
    border: 1px solid {ColorTokens.CARD_BORDER}; border-radius: 20px;
    font-size: 10px; color: {ColorTokens.LIGHT_GRAY}; font-weight: 400;
    white-space: nowrap;
}}

/* === 教师后台专用 === */
.teacher-stat-card {{
    text-align: center; padding: 20px; background: {ColorTokens.BG_WHITE};
    border: 1px solid {ColorTokens.CARD_BORDER}; border-radius: 12px;
}}
.teacher-stat-value {{ font-size: 32px; font-weight: 800; color: {ColorTokens.PRIMARY}; }}
.teacher-stat-label {{ font-size: 12px; color: {ColorTokens.LIGHT_GRAY}; margin-top: 4px; }}
.teacher-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
.teacher-table th {{ background: {ColorTokens.LIGHT_BLUE}; color: {ColorTokens.PRIMARY}; padding: 10px 14px; text-align: left; font-weight: 700; }}
.teacher-table td {{ padding: 10px 14px; border-bottom: 1px solid {ColorTokens.CARD_BORDER}; }}
.teacher-table tr:hover td {{ background: {ColorTokens.BG_GRAY}; }}

/* === 知识库文件列表 === */
.kb-file-item {{
    display: flex; align-items: center; gap: 10px; padding: 10px 14px;
    background: {ColorTokens.BG_WHITE}; border: 1px solid {ColorTokens.CARD_BORDER};
    border-radius: 8px; margin-bottom: 6px; transition: all 0.2s;
}}
.kb-file-item:hover {{ border-color: {ColorTokens.PRIMARY}; }}
.kb-file-icon {{ color: {ColorTokens.PRIMARY}; font-size: 18px; }}
.kb-file-name {{ font-size: 13px; font-weight: 500; color: {ColorTokens.DARK_GRAY}; }}
.kb-file-meta {{ font-size: 11px; color: {ColorTokens.LIGHT_GRAY}; }}

/* === 侧边栏导航 === */
.sidebar-nav-item {{
    display: flex; align-items: center; gap: 10px; padding: 10px 16px;
    border-radius: 10px; cursor: pointer; font-size: 14px; font-weight: 500;
    color: rgba(255,255,255,0.7); transition: all 0.2s; margin-bottom: 4px;
}}
.sidebar-nav-item:hover, .sidebar-nav-item.active {{
    background: rgba(255,255,255,0.12); color: white;
}}
.sidebar-divider {{ height: 1px; background: rgba(255,255,255,0.1); margin: 12px 0; }}

/* === Responsive === */
@media (max-width: 768px) {{
    .agent-flow-panel {{ flex-wrap: wrap; justify-content: center; }}
    .agent-arrow {{ display: none; }}
    body {{ font-family: 'Source Han Sans SC', sans-serif; }}
}}
</style>
"""

# ============================================================================
# 第三部分: 可复用组件 (Reusable Components)
# ============================================================================

def inject_design_system():
    """注入全局CSS设计系统"""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_tech_annotations(labels: List[str] = None):
    """页面角落技术标注 - 赛题核心评分点"""
    if labels is None:
        labels = ["RAG本地知识库", "多智能体编排", "学生多维画像", "大模型防幻觉"]
    chips = "".join([f'<span class="tech-chip">🏷 {l}</span>' for l in labels])
    st.markdown(f'<div class="tech-annotation">{chips}</div>', unsafe_allow_html=True)


def render_agent_flow_panel(agents_status: List[Dict], current_active: int = -1):
    """
    五智能体协同流转面板
    agents_status: [{"name": "画像读取", "icon": "📖", "status": "idle"|"active"|"processing"|"done"}, ...]
    """
    nodes = []
    for i, agent in enumerate(agents_status):
        status_class = "active" if agent.get("active") else ("processing" if agent.get("processing") else "")
        nodes.append(f'''
            <div class="agent-node {status_class}">
                <div class="agent-node-icon">{agent.get("icon", "🤖")}</div>
                <div class="agent-node-name">{agent.get("name", "")}</div>
                <div class="agent-node-status" style="color:{ColorTokens.AGENT_GREEN if status_class=='active' else ColorTokens.MID_GRAY}">
                    {agent.get("status_text", "待命")}
                </div>
            </div>
        ''')
    
    arrows = '<div class="agent-arrow">→</div>'
    flow_html = arrows.join(nodes)
    
    st.markdown(f'''
        <div class="agent-flow-panel">{flow_html}</div>
    ''', unsafe_allow_html=True)


def render_profile_dimension_card(icon: str, title: str, items: List[str], tag_color: str = "blue"):
    """6维学生画像单维卡片"""
    tags_html = "".join([f'<span class="profile-dim-tag tag-{tag_color}">{item}</span>' for item in items])
    return f'''
        <div class="profile-dim-card">
            <div class="profile-dim-icon">{icon}</div>
            <div class="profile-dim-title">{title}</div>
            <div class="profile-dim-value">{tags_html if items else '<span style="color:{ColorTokens.LIGHT_GRAY}">暂无数据</span>'}</div>
        </div>
    '''


def render_profile_radar_card(profile) -> str:
    """6维画像可视化卡片 - 完整版"""
    profile_data = profile.__dict__ if hasattr(profile, '__dict__') else profile
    
    prerequisites = profile_data.get("prerequisites", [])
    learning_style = profile_data.get("learning_style", "")
    weak_points = profile_data.get("weak_points", [])
    error_types = profile_data.get("error_prone_types", [])
    goals = profile_data.get("learning_goals", [])
    rhythm = profile_data.get("daily_rhythm", {})
    
    dims = [
        ("📚 知识基础", prerequisites, "blue"),
        ("🎯 认知风格", [learning_style] if isinstance(learning_style, str) else learning_style, "green"),
        ("⚠️ 薄弱环节", weak_points, "red"),
        ("❌ 易错题型", error_types, "red"),
        ("🏆 学习目标", goals, "blue"),
        ("⏰ 学习节奏", [f"{k}: {v}" for k, v in rhythm.items()] if isinstance(rhythm, dict) else [str(rhythm)], "green"),
    ]
    
    cards = []
    for icon, items, color in dims:
        cards.append(render_profile_dimension_card(icon, icon[2:], items, color))
    
    row1 = f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:12px;">{"".join(cards[:3])}</div>'
    row2 = f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">{"".join(cards[3:])}</div>'
    
    return f'<div style="margin:16px 0;">{row1}{row2}</div>'


def render_resource_card(icon: str, title: str, meta: str, tags: List[str], tag_color: str = "blue"):
    """多模态资源展示卡片"""
    tags_html = "".join([f'<span class="resource-tag" style="background:{ColorTokens.LIGHT_BLUE};color:{ColorTokens.PRIMARY};">{t}</span>' for t in tags])
    return f'''
        <div class="resource-card">
            <div class="resource-icon">{icon}</div>
            <div class="resource-info">
                <div class="resource-title">{title}</div>
                <div class="resource-meta">{meta}</div>
                <div style="margin-top:6px;">{tags_html}</div>
            </div>
        </div>
    '''


def render_rag_citation(source_file: str, chunk_index: int, total_chunks: int, similarity: float = 0.0):
    """RAG引用来源标识"""
    return f'''
        <div class="rag-citation">
            <span class="rag-citation-icon">📎</span>
            <span>来源: <strong>{source_file}</strong> · 片段 {chunk_index + 1}/{total_chunks}</span>
            {f'<span style="margin-left:8px;color:{ColorTokens.AGENT_GREEN};">相似度 {similarity:.1%}</span>' if similarity > 0 else ''}
        </div>
    '''


def render_rag_source_chip(source: str):
    """RAG来源小标签"""
    return f'<span class="rag-source-chip">📌 {source}</span>'


def render_heatmap(knowledge_points: List[Dict]):
    """
    知识图谱热力图
    knowledge_points: [{"name": "TCP/IP", "mastery": 85}, ...]
    mastery: 0-100
    """
    cells = []
    for kp in knowledge_points:
        mastery = kp.get("mastery", 50)
        if mastery >= 85:
            cls = "heatmap-mastery-90"
        elif mastery >= 65:
            cls = "heatmap-mastery-70"
        elif mastery >= 40:
            cls = "heatmap-mastery-50"
        elif mastery >= 20:
            cls = "heatmap-mastery-30"
        else:
            cls = "heatmap-mastery-10"
        cells.append(f'<div class="heatmap-cell {cls}" title="{kp["name"]}: {mastery}%"></div>')
    
    st.markdown(f'''
        <div class="heatmap-container">
            <div style="font-size:14px;font-weight:700;margin-bottom:12px;">📊 知识点掌握热力图</div>
            <div style="display:flex;flex-wrap:wrap;">{"".join(cells)}</div>
            <div style="display:flex;gap:16px;margin-top:12px;font-size:11px;color:{ColorTokens.LIGHT_GRAY};">
                <span>🟢 熟练 (85-100)</span><span>🟡 一般 (40-84)</span><span>🔴 薄弱 (0-39)</span>
            </div>
        </div>
    ''', unsafe_allow_html=True)


def render_status_badge(status: str, text: str):
    """交互状态指示器"""
    status_map = {
        "running": "status-running",
        "success": "status-success",
        "error": "status-error",
        "idle": "status-idle"
    }
    dot_colors = {"running": "#D97706", "success": ColorTokens.AGENT_GREEN, "error": ColorTokens.WARNING_RED, "idle": ColorTokens.LIGHT_GRAY}
    cls = status_map.get(status, "status-idle")
    dot_color = dot_colors.get(status, ColorTokens.LIGHT_GRAY)
    return f'''
        <span class="status-badge {cls}">
            <span class="status-dot" style="background:{dot_color}"></span> {text}
        </span>
    '''


def render_toast(msg_type: str, title: str, message: str):
    """容错提示弹窗 (GPS弱信号同类风格)"""
    icon_map = {"warning": "⚠️", "error": "❌", "info": "ℹ️"}
    cls_map = {"warning": "toast-warning", "error": "toast-error", "info": "toast-info"}
    return f'''
        <div class="toast-notify {cls_map.get(msg_type, 'toast-info')}">
            <span class="toast-icon">{icon_map.get(msg_type, 'ℹ️')}</span>
            <div>
                <strong>{title}</strong>
                <div style="font-size:12px;margin-top:2px;">{message}</div>
            </div>
        </div>
    '''


def render_progress_with_label(percent: int, label: str = ""):
    """带标签的进度条"""
    st.markdown(f'''
        <div style="margin:8px 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="font-size:12px;color:{ColorTokens.MID_GRAY};">{label}</span>
                <span style="font-size:12px;font-weight:700;color:{ColorTokens.PRIMARY};">{percent}%</span>
            </div>
            <div class="ds-progress">
                <div class="ds-progress-fill" style="width:{percent}%"></div>
            </div>
        </div>
    ''', unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str = "", icon: str = ""):
    """统一区块标题"""
    icon_part = f'<span style="font-size:24px;">{icon}</span> ' if icon else ''
    sub_part = f'<p style="font-size:13px;color:{ColorTokens.LIGHT_GRAY};margin-top:4px;">{subtitle}</p>' if subtitle else ''
    st.markdown(f'''
        <div style="margin-bottom:20px;">
            <h2>{icon_part}{title}</h2>
            {sub_part}
        </div>
    ''', unsafe_allow_html=True)


def render_stat_grid(stats: List[Dict]):
    """统计指标网格"""
    cols = st.columns(len(stats))
    for i, stat in enumerate(stats):
        with cols[i]:
            st.markdown(f'''
                <div class="teacher-stat-card">
                    <div class="teacher-stat-value">{stat.get("value", "-")}</div>
                    <div class="teacher-stat-label">{stat.get("label", "")}</div>
                </div>
            ''', unsafe_allow_html=True)


def render_simple_sidebar():
    """统一样式侧边栏"""
    with st.sidebar:
        st.markdown(f'''
            <div style="padding:16px 0;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
                    <span style="font-size:24px;">🎓</span>
                    <div>
                        <div style="font-size:16px;font-weight:700;">智能学习助手</div>
                        <div style="font-size:11px;opacity:0.6;">AI Multi-Agent System</div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        return st  # 返回以便后续添加导航


def render_student_sidebar(current_page: str = "profile"):
    """学生端侧边栏"""
    with st.sidebar:
        st.markdown(f'''
            <div style="padding:16px 0;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
                    <span style="font-size:24px;">🎓</span>
                    <div>
                        <div style="font-size:16px;font-weight:700;">智能学习助手</div>
                        <div style="font-size:11px;opacity:0.6;">A3 · 科大讯飞</div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        pages = [
            ("dashboard", "🏠 个人首页", "学情概览与快捷入口"),
            ("profile", "📝 学生画像采集", "对话式构建6维画像"),
            ("learning", "⚡ 多智能体协同", "资源生成与路径规划"),
            ("resources", "📦 学习资源中心", "多模态资源展示"),
            ("qa", "💬 智能答疑", "知识库溯源防幻觉"),
        ]
        
        for page_id, name, desc in pages:
            active = current_page == page_id
            btn_color = f"background:{ColorTokens.PRIMARY};color:white;" if active else f"background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.9);border:1px solid rgba(255,255,255,0.1);"
            if st.sidebar.button(name, key=f"nav_{page_id}", use_container_width=True, help=desc):
                st.session_state.student_page = page_id
                st.rerun()
        
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        if "current_profile" in st.session_state and st.session_state.current_profile:
            p = st.session_state.current_profile
            st.markdown(f'''
                <div style="padding:8px 12px;background:rgba(16,185,129,0.15);border-radius:8px;font-size:12px;margin-top:8px;">
                    <div style="font-weight:600;color:{ColorTokens.AGENT_GREEN};">🟢 当前学生</div>
                    <div style="color:rgba(255,255,255,0.8);margin-top:4px;">{getattr(p, 'name', '未知')}</div>
                    <div style="color:rgba(255,255,255,0.5);font-size:10px;">{getattr(p, 'student_id', '')}</div>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        if st.sidebar.button("🚪 退出登录", use_container_width=True):
            for key in ["logged_in", "is_guest", "student_id", "student_name", "current_profile", "user_role"]:
                st.session_state[key] = False if key == "logged_in" or key == "is_guest" else None
            st.rerun()
        
        if st.sidebar.button("🔄 返回角色选择", use_container_width=True):
            st.session_state.user_role = None
            st.rerun()


def render_teacher_sidebar(current_page: str = "kb"):
    """教师端侧边栏"""
    with st.sidebar:
        st.markdown(f'''
            <div style="padding:16px 0;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
                    <span style="font-size:24px;">🏫</span>
                    <div>
                        <div style="font-size:16px;font-weight:700;">教师管理中台</div>
                        <div style="font-size:11px;opacity:0.6;">A3 · 后台管理</div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        pages = [
            ("kb", "📚 知识库管理", "批量管理课程文档"),
            ("agent_config", "⚙️ 智能体配置", "参数与协同编排"),
            ("stats", "📊 学情统计", "全班学习数据分析"),
            ("logs", "📋 资源生成日志", "追踪生成记录"),
            ("report", "📈 学习效果报表", "多维分析报告"),
        ]
        
        for page_id, name, desc in pages:
            active = "active" if current_page == page_id else ""
            st.markdown(f'''
                <div class="sidebar-nav-item {active}" style="cursor:pointer;">
                    <span>{name}</span>
                </div>
            ''', unsafe_allow_html=True)


# ============================================================================
# 第四部分: 工具函数
# ============================================================================
def generate_id() -> str:
    return str(uuid.uuid4())[:8]


def format_timestamp(iso_str: str) -> str:
    """ISO时间格式化为可读格式"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return iso_str


def render_voice_input(input_key: str, placeholder: str = "输入内容...") -> str:
    """语音转文字输入组件 - 使用浏览器Web Speech API"""
    if input_key not in st.session_state:
        st.session_state[input_key] = ""
    
    VOICE_INPUT_JS = f"""
    <script>
    (function() {{
        const recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!recognition) {{
            document.getElementById('voice-status-{input_key}').textContent = '浏览器不支持语音识别';
            return;
        }}
        
        const rec = new recognition();
        rec.continuous = false;
        rec.interimResults = true;
        rec.lang = 'zh-CN';
        
        const voiceBtn = document.getElementById('voice-btn-{input_key}');
        const status = document.getElementById('voice-status-{input_key}');
        let isRecording = false;
        
        voiceBtn.addEventListener('click', function() {{
            if (isRecording) {{
                rec.stop();
                isRecording = false;
                voiceBtn.style.background = '#F3F4F6';
                voiceBtn.style.color = '#6B7280';
                voiceBtn.textContent = '🎤';
                status.textContent = '点击麦克风开始说话';
                status.style.color = '#9CA3AF';
            }} else {{
                rec.start();
                isRecording = true;
                voiceBtn.style.background = '#EF4444';
                voiceBtn.style.color = 'white';
                voiceBtn.textContent = '⏹️';
                status.textContent = '正在聆听...请说话';
                status.style.color = '#EF4444';
            }}
        }});
        
        rec.onresult = function(event) {{
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {{
                transcript += event.results[i][0].transcript;
            }}
            const inputs = document.querySelectorAll('input[data-testid="stTextInput"]');
            for (const input of inputs) {{
                if (input.getAttribute('aria-label') === '') {{
                    input.value = transcript;
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    break;
                }}
            }}
        }};
        
        rec.onerror = function(event) {{
            isRecording = false;
            voiceBtn.style.background = '#F3F4F6';
            voiceBtn.style.color = '#6B7280';
            voiceBtn.textContent = '🎤';
            if (event.error === 'not-allowed') {{
                status.textContent = '请允许麦克风权限';
                status.style.color = '#EF4444';
            }} else {{
                status.textContent = '语音识别出错: ' + event.error;
                status.style.color = '#EF4444';
            }}
        }};
        
        rec.onend = function() {{
            if (isRecording) {{
                isRecording = false;
                voiceBtn.style.background = '#F3F4F6';
                voiceBtn.style.color = '#6B7280';
                voiceBtn.textContent = '🎤';
                status.textContent = '点击麦克风开始说话';
                status.style.color = '#9CA3AF';
            }}
        }};
    }})();
    </script>
    """
    
    col_mic, col_input = st.columns([1, 6])
    with col_mic:
        st.markdown(f"""
        <button id="voice-btn-{input_key}" 
            style="width:44px;height:44px;border-radius:12px;background:#F3F4F6;border:none;
                font-size:18px;cursor:pointer;transition:all .25s;width:100%;">
            🎤
        </button>
        """, unsafe_allow_html=True)
    with col_input:
        user_input = st.text_input("", key=input_key, placeholder=placeholder, label_visibility="collapsed")
    
    st.markdown(f"""
    <div id="voice-status-{input_key}" style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin-top:-8px;margin-bottom:8px;">
        点击麦克风开始说话
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(VOICE_INPUT_JS, unsafe_allow_html=True)
    return user_input
