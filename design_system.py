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
    PRIMARY = "#2563EB"
    PRIMARY_HOVER = "#1D4ED8"
    LIGHT_BLUE = "#E8F0FE"
    AGENT_GREEN = "#10B981"
    WARNING_RED = "#EF4444"
    WARNING_RED_LIGHT = "#FEF2F2"
    DARK_GRAY = "#111827"
    MID_GRAY = "#374151"
    LIGHT_GRAY = "#6B7280"
    BG_WHITE = "#FFFFFF"
    BG_GRAY = "#F9FAFB"
    CARD_BORDER = "#E5E7EB"
    GLOW_BLUE = "rgba(37,99,235,0.15)"
    GLOW_GREEN = "rgba(16,185,129,0.15)"

# ============================================================================
# 第二部分: 全局CSS (Global Stylesheet)
# ============================================================================
GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* {{ box-sizing: border-box; }}
body {{ font-family: 'Inter', 'Source Han Sans SC', -apple-system, sans-serif; background: {ColorTokens.BG_WHITE}; color: {ColorTokens.DARK_GRAY}; }}
h1, h2, h3, h4 {{ font-family: 'Inter', sans-serif; font-weight: 700; letter-spacing: -0.025em; }}
h1 {{ font-size: 28px; color: {ColorTokens.DARK_GRAY}; }}
h2 {{ font-size: 22px; color: {ColorTokens.DARK_GRAY}; }}
h3 {{ font-size: 18px; color: {ColorTokens.DARK_GRAY}; }}
p  {{ font-size: 14px; line-height: 1.7; color: {ColorTokens.MID_GRAY}; }}

.stApp {{ background: {ColorTokens.BG_WHITE}; }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {ColorTokens.DARK_GRAY} 0%, #111827 100%) !important; }}
section[data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.95) !important; }}
section[data-testid="stSidebar"] svg {{ fill: rgba(255,255,255,0.95) !important; }}

.stButton > button, .stDownloadButton > button {{ 
    font-family: 'Inter', sans-serif; font-weight: 600; font-size: 14px;
    border-radius: 10px !important; border: none; cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); padding: 10px 24px;
}}

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

@keyframes agentPulse {{
    0%, 100% {{ box-shadow: 0 0 0 0 {ColorTokens.GLOW_GREEN}; }}
    50% {{ box-shadow: 0 0 0 8px transparent; }}
}}
@keyframes agentPulseBlue {{
    0%, 100% {{ box-shadow: 0 0 0 0 {ColorTokens.GLOW_BLUE}; }}
    50% {{ box-shadow: 0 0 0 8px transparent; }}
}}

@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.stream-fade {{ animation: fadeInUp 0.4s ease-out; }}

.ds-progress {{ height: 8px; background: {ColorTokens.BG_GRAY}; border-radius: 10px; overflow: hidden; }}
.ds-progress-fill {{ height: 100%; border-radius: 10px; background: linear-gradient(90deg, {ColorTokens.PRIMARY}, {ColorTokens.AGENT_GREEN}); 
    transition: width 0.5s ease; animation: progressFlow 2s ease-in-out infinite; }}
@keyframes progressFlow {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

.ds-card {{
    background: {ColorTokens.BG_WHITE}; border: 1px solid {ColorTokens.CARD_BORDER};
    border-radius: 12px; padding: 20px; margin-bottom: 16px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
.ds-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.06); border-color: {ColorTokens.LIGHT_BLUE}; }}
.ds-card-blue {{ border-left: 4px solid {ColorTokens.PRIMARY}; background: {ColorTokens.LIGHT_BLUE}; }}
.ds-card-green {{ border-left: 4px solid {ColorTokens.AGENT_GREEN}; background: #ECFDF5; }}
.ds-card-red {{ border-left: 4px solid {ColorTokens.WARNING_RED}; background: {ColorTokens.WARNING_RED_LIGHT}; }}

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

.toast-notify {{
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px; border-radius: 12px; margin: 10px 0;
    font-size: 13px; animation: fadeInUp 0.3s ease-out;
}}
.toast-warning {{ background: #FFFBEB; border: 1px solid #FCD34D; color: #92400E; }}
.toast-error {{ background: {ColorTokens.WARNING_RED_LIGHT}; border: 1px solid {ColorTokens.WARNING_RED}; color: #991B1B; }}
.toast-info {{ background: {ColorTokens.LIGHT_BLUE}; border: 1px solid {ColorTokens.PRIMARY}; color: {ColorTokens.PRIMARY}; }}
.toast-icon {{ font-size: 18px; flex-shrink: 0; }}

.chart-container {{
    padding: 20px; background: {ColorTokens.BG_WHITE};
    border: 1px solid {ColorTokens.CARD_BORDER}; border-radius: 12px;
    margin-bottom: 16px;
}}
.chart-title {{ font-size: 14px; font-weight: 700; color: {ColorTokens.DARK_GRAY}; margin-bottom: 12px; }}

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

.kb-file-item {{
    display: flex; align-items: center; gap: 12px; padding: 12px;
    background: {ColorTokens.BG_WHITE}; border-radius: 10px;
    border: 1px solid {ColorTokens.CARD_BORDER}; margin-bottom: 8px;
}}

.stMarkdown p, .stMarkdown li, .stMarkdown ul, .stMarkdown ol {{
    color: {ColorTokens.MID_GRAY} !important; font-size: 14px; line-height: 1.7;
}}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
    color: {ColorTokens.DARK_GRAY} !important;
}}
.stMarkdown strong, .stMarkdown b {{
    color: {ColorTokens.DARK_GRAY} !important;
}}
.stMarkdown code {{
    background: {ColorTokens.LIGHT_BLUE}; color: {ColorTokens.PRIMARY};
    padding: 2px 6px; border-radius: 4px; font-size: 13px;
}}

.sidebar-nav-btn {{
    width: 100%; text-align: left; padding: 10px 12px;
    border: none; background: rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.95); font-size: 14px;
    font-weight: 500; border-radius: 8px; cursor: pointer;
    transition: all 0.2s; margin-bottom: 4px;
    display: flex; align-items: center; gap: 8px;
}}
.sidebar-nav-btn:hover {{ background: rgba(255,255,255,0.15); }}
.sidebar-nav-btn.active {{ background: {ColorTokens.PRIMARY}; color: white; }}
</style>
"""

LIGHT_THEME_RESET = """
<style>
  .stApp { background: #FAFBFC !important; }
  .main { background: #FAFBFC !important; }
  section[data-testid="stSidebar"] { display: block !important; }
  section[data-testid="stSidebar"] > div { background: #F9FAFB !important; }
</style>
"""

# ============================================================================
# 第三部分: 通用工具函数
# ============================================================================
def generate_id() -> str:
    return str(uuid.uuid4())[:8]

def format_timestamp(iso_str: str) -> str:
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return iso_str

# ============================================================================
# 第四部分: UI组件渲染函数
# ============================================================================
def inject_design_system():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def render_tech_annotations():
    st.markdown(f"""
    <div class="tech-annotation">
        <span class="tech-chip">🧠 讯飞星火大模型</span>
        <span class="tech-chip">📚 RAG知识库</span>
        <span class="tech-chip">🤖 多智能体协同</span>
    </div>
    """, unsafe_allow_html=True)

def render_status_badge(status: str):
    status_map = {
        "running": ("status-running", "⏳ 运行中"),
        "success": ("status-success", "✅ 成功"),
        "error": ("status-error", "❌ 失败"),
        "idle": ("status-idle", "💤 空闲"),
    }
    cls, text = status_map.get(status, ("status-idle", "未知"))
    st.markdown(f'<span class="status-badge {cls}">{text}</span>', unsafe_allow_html=True)

def render_toast(message: str, type: str = "info"):
    type_map = {
        "warning": ("toast-warning", "⚠️"),
        "error": ("toast-error", "❌"),
        "info": ("toast-info", "ℹ️"),
    }
    cls, icon = type_map.get(type, ("toast-info", "ℹ️"))
    st.markdown(f"""
    <div class="toast-notify {cls}">
        <span class="toast-icon">{icon}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)

def render_progress_with_label(label: str, progress: float):
    st.markdown(f"""
    <div style="margin-bottom: 8px;">
        <div style="display: flex; justify-content: space-between; font-size: 12px; color: {ColorTokens.MID_GRAY}; margin-bottom: 4px;">
            <span>{label}</span>
            <span>{int(progress * 100)}%</span>
        </div>
        <div class="ds-progress">
            <div class="ds-progress-fill" style="width: {progress * 100}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_section_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(f"""
    <div style="margin-bottom: 16px;">
        <div style="font-size: 20px; font-weight: 700; color: {ColorTokens.DARK_GRAY}; display: flex; align-items: center; gap: 8px;">
            {icon} {title}
        </div>
        {f'<div style="font-size: 12px; color: {ColorTokens.LIGHT_GRAY}; margin-top: 4px;">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_stat_grid(stats: List[Dict]):
    cols = st.columns(len(stats))
    for i, stat in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div class="teacher-stat-card">
                <div class="teacher-stat-value">{stat['value']}</div>
                <div class="teacher-stat-label">{stat['label']}</div>
            </div>
            """, unsafe_allow_html=True)

def render_heatmap(data: List[Dict]):
    st.markdown('<div class="heatmap-container">', unsafe_allow_html=True)
    for item in data:
        level = item['level']
        if level >= 8: cls = 'heatmap-mastery-90'
        elif level >= 6: cls = 'heatmap-mastery-70'
        elif level >= 4: cls = 'heatmap-mastery-50'
        elif level >= 2: cls = 'heatmap-mastery-30'
        else: cls = 'heatmap-mastery-10'
        st.markdown(f'''
        <div class="heatmap-cell {cls}" title="{item['name']}: {level}/10"></div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_rag_citation(source: str, chunk: int):
    st.markdown(f'''
    <div class="rag-citation">
        <span class="rag-citation-icon">📌</span>
        <span>来源: {source} · 片段 {chunk}</span>
    </div>
    ''', unsafe_allow_html=True)

def render_rag_source_chip(source: str):
    st.markdown(f'''
    <span class="rag-source-chip">📚 {source}</span>
    ''', unsafe_allow_html=True)

def render_agent_flow_panel(agents: List[Dict]):
    st.markdown('<div class="agent-flow-panel">', unsafe_allow_html=True)
    for i, agent in enumerate(agents):
        if i > 0:
            st.markdown('<div class="agent-arrow">→</div>', unsafe_allow_html=True)
        status = agent.get('status', 'idle')
        st.markdown(f'''
        <div class="agent-node {'active' if status == 'active' else ''} {'processing' if status == 'processing' else ''}">
            <div class="agent-node-icon">{agent['icon']}</div>
            <div class="agent-node-name">{agent['name']}</div>
            <div class="agent-node-status">{agent.get('desc', '')}</div>
        </div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_resource_card(resource: Dict):
    st.markdown(f'''
    <div class="resource-card">
        <div class="resource-icon">{resource['icon']}</div>
        <div class="resource-info">
            <div class="resource-title">{resource['title']}</div>
            <div class="resource-meta">{resource['meta']}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

def render_profile_dimension_card(dimension: Dict):
    st.markdown(f'''
    <div class="profile-dim-card">
        <div class="profile-dim-icon">{dimension['icon']}</div>
        <div class="profile-dim-title">{dimension['title']}</div>
        <div class="profile-dim-value">{dimension['value']}</div>
        {''.join(f'<span class="profile-dim-tag tag-blue">{tag}</span>' for tag in dimension.get('tags', []))}
    </div>
    ''', unsafe_allow_html=True)

def render_profile_radar_card(profile: Dict):
    st.markdown(f'''
    <div class="ds-card ds-card-blue">
        <div style="font-size: 14px; font-weight: 700; color: {ColorTokens.DARK_GRAY}; margin-bottom: 12px;">
            📊 6维画像概览
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
            {''.join(f'''
            <div style="text-align: center; padding: 10px; background: white; border-radius: 8px;">
                <div style="font-size: 20px; font-weight: 800; color: {ColorTokens.PRIMARY};">{dim['value']}</div>
                <div style="font-size: 10px; color: {ColorTokens.LIGHT_GRAY}; margin-top: 4px;">{dim['name']}</div>
            </div>
            ''' for dim in profile.get('dimensions', []))}
        </div>
    </div>
    ''', unsafe_allow_html=True)

# ============================================================================
# 第五部分: 侧边栏组件
# ============================================================================
def render_student_sidebar(current_page: str = "dashboard"):
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
            active = "active" if current_page == page_id else ""
            if st.button(name, key=f"sidebar_{page_id}", use_container_width=True):
                st.session_state.student_page = page_id
                st.rerun()

        st.markdown("---")
        if st.button("🚪 退出登录", key="sidebar_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        if st.button("🔄 返回角色选择", key="sidebar_back", use_container_width=True):
            st.session_state.user_role = None
            st.rerun()

def render_teacher_sidebar(current_page: str = "dashboard"):
    with st.sidebar:
        st.markdown(f'''
            <div style="padding:16px 0;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
                    <span style="font-size:24px;">🏫</span>
                    <div>
                        <div style="font-size:16px;font-weight:700;">教师管理中台</div>
                        <div style="font-size:11px;opacity:0.6;">A3 · 科大讯飞</div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        pages = [
            ("dashboard", "📊 数据概览", "实时统计与监控"),
            ("students", "🎓 学生管理", "学生列表与画像"),
            ("knowledge", "📚 知识库管理", "课程文档与索引"),
            ("settings", "⚙️ 系统设置", "API配置与管理"),
        ]

        for page_id, name, desc in pages:
            active = "active" if current_page == page_id else ""
            if st.button(name, key=f"teacher_sidebar_{page_id}", use_container_width=True):
                st.session_state.teacher_page = page_id
                st.rerun()

        st.markdown("---")
        if st.button("🚪 退出登录", key="teacher_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        if st.button("🔄 返回角色选择", key="teacher_back", use_container_width=True):
            st.session_state.user_role = None
            st.rerun()
