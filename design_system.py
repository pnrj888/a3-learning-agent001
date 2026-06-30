"""
A3 智能学习助手 - 设计系统
色彩体系 + 全局CSS + UI组件渲染函数
"""
import streamlit as st
from typing import List, Dict, Optional

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

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* {{ box-sizing: border-box; }}
body {{ font-family: 'Inter', sans-serif; background: {ColorTokens.BG_WHITE}; color: {ColorTokens.DARK_GRAY}; }}
h1, h2, h3, h4 {{ font-family: 'Inter', sans-serif; font-weight: 700; }}
h1 {{ font-size: 28px; color: {ColorTokens.DARK_GRAY}; }}
h2 {{ font-size: 22px; color: {ColorTokens.DARK_GRAY}; }}
h3 {{ font-size: 18px; color: {ColorTokens.DARK_GRAY}; }}
p  {{ font-size: 14px; line-height: 1.7; color: {ColorTokens.MID_GRAY}; }}

.stApp {{ background: {ColorTokens.BG_WHITE}; }}
section[data-testid="stSidebar"] {{ background: {ColorTokens.DARK_GRAY} !important; }}
section[data-testid="stSidebar"] * {{ color: rgba(255,255,255,0.95) !important; }}

.stButton > button {{ 
    font-family: 'Inter', sans-serif; font-weight: 600; font-size: 14px;
    border-radius: 10px !important; border: none; cursor: pointer;
    transition: all 0.25s; padding: 10px 24px;
}}

.ds-card {{
    background: {ColorTokens.BG_WHITE}; border: 1px solid {ColorTokens.CARD_BORDER};
    border-radius: 12px; padding: 20px; margin-bottom: 16px;
    transition: all 0.3s;
}}
.ds-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.06); }}
.ds-card-blue {{ border-left: 4px solid {ColorTokens.PRIMARY}; background: {ColorTokens.LIGHT_BLUE}; }}
.ds-card-green {{ border-left: 4px solid {ColorTokens.AGENT_GREEN}; background: #ECFDF5; }}
.ds-card-red {{ border-left: 4px solid {ColorTokens.WARNING_RED}; background: {ColorTokens.WARNING_RED_LIGHT}; }}

.status-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
}}
.status-running {{ background: #FEF3C7; color: #D97706; }}
.status-success {{ background: #ECFDF5; color: {ColorTokens.AGENT_GREEN}; }}
.status-error {{ background: {ColorTokens.WARNING_RED_LIGHT}; color: {ColorTokens.WARNING_RED}; }}
.status-idle {{ background: {ColorTokens.BG_GRAY}; color: {ColorTokens.LIGHT_GRAY}; }}

.toast-notify {{
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px; border-radius: 12px; margin: 10px 0;
    font-size: 13px;
}}
.toast-warning {{ background: #FFFBEB; border: 1px solid #FCD34D; color: #92400E; }}
.toast-error {{ background: {ColorTokens.WARNING_RED_LIGHT}; border: 1px solid {ColorTokens.WARNING_RED}; color: #991B1B; }}
.toast-info {{ background: {ColorTokens.LIGHT_BLUE}; border: 1px solid {ColorTokens.PRIMARY}; color: {ColorTokens.PRIMARY}; }}

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
.agent-node.active {{ border-color: {ColorTokens.AGENT_GREEN}; }}
.agent-node.processing {{ border-color: {ColorTokens.PRIMARY}; }}
.agent-arrow {{ font-size: 20px; color: {ColorTokens.PRIMARY}; min-width: 30px; text-align: center; }}

.resource-card {{
    display: flex; align-items: flex-start; gap: 14px; padding: 16px;
    background: {ColorTokens.BG_WHITE}; border: 1px solid {ColorTokens.CARD_BORDER};
    border-radius: 12px; margin-bottom: 10px; transition: all 0.3s;
}}
.resource-card:hover {{ border-color: {ColorTokens.PRIMARY}; }}

.rag-citation {{
    display: flex; align-items: center; gap: 6px; padding: 6px 12px;
    background: {ColorTokens.BG_GRAY}; border-left: 3px solid {ColorTokens.PRIMARY};
    border-radius: 6px; font-size: 11px; color: {ColorTokens.MID_GRAY};
    margin-top: 8px;
}}

.heatmap-cell {{
    display: inline-block; width: 40px; height: 40px; margin: 3px;
    border-radius: 6px; transition: all 0.3s; cursor: pointer;
}}

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

.teacher-stat-card {{
    text-align: center; padding: 20px; background: {ColorTokens.BG_WHITE};
    border: 1px solid {ColorTokens.CARD_BORDER}; border-radius: 12px;
}}
.teacher-stat-value {{ font-size: 32px; font-weight: 800; color: {ColorTokens.PRIMARY}; }}
.teacher-stat-label {{ font-size: 12px; color: {ColorTokens.LIGHT_GRAY}; margin-top: 4px; }}

.stMarkdown p, .stMarkdown li {{ color: {ColorTokens.MID_GRAY} !important; font-size: 14px; line-height: 1.7; }}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{ color: {ColorTokens.DARK_GRAY} !important; }}
.stMarkdown code {{ background: {ColorTokens.LIGHT_BLUE}; color: {ColorTokens.PRIMARY}; padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
</style>
"""

LIGHT_THEME_RESET = """
<style>
  .stApp { background: #FAFBFC !important; }
  .main { background: #FAFBFC !important; }
  section[data-testid="stSidebar"] { display: block !important; }
  section[data-testid="stSidebar"] > div { background: #111827 !important; }
</style>
"""

def inject_design_system():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def render_tech_annotations():
    st.markdown(f"""
    <div style="position:fixed;bottom:16px;right:20px;display:flex;gap:10px;z-index:999;">
        <span style="padding:4px 10px;background:{ColorTokens.BG_GRAY};border:1px solid {ColorTokens.CARD_BORDER};border-radius:20px;font-size:10px;color:{ColorTokens.LIGHT_GRAY};">🧠 讯飞星火大模型</span>
        <span style="padding:4px 10px;background:{ColorTokens.BG_GRAY};border:1px solid {ColorTokens.CARD_BORDER};border-radius:20px;font-size:10px;color:{ColorTokens.LIGHT_GRAY};">📚 RAG知识库</span>
        <span style="padding:4px 10px;background:{ColorTokens.BG_GRAY};border:1px solid {ColorTokens.CARD_BORDER};border-radius:20px;font-size:10px;color:{ColorTokens.LIGHT_GRAY};">🤖 多智能体协同</span>
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
        <span>{icon}</span>
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
        <div style="height: 8px; background: {ColorTokens.BG_GRAY}; border-radius: 10px; overflow: hidden;">
            <div style="height: 100%; width: {progress * 100}%; border-radius: 10px; background: linear-gradient(90deg, {ColorTokens.PRIMARY}, {ColorTokens.AGENT_GREEN});"></div>
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
    st.markdown('<div style="padding:20px;background:white;border:1px solid #E5E7EB;border-radius:12px;">', unsafe_allow_html=True)
    for item in data:
        level = item['level']
        if level >= 8: cls = '#10B981'
        elif level >= 6: cls = '#34D399'
        elif level >= 4: cls = '#FBBF24'
        elif level >= 2: cls = '#F87171'
        else: cls = '#EF4444'
        st.markdown(f'<div class="heatmap-cell" style="background:{cls};" title="{item["name"]}: {level}/10"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_rag_citation(source: str, chunk: int):
    st.markdown(f'<div class="rag-citation"><span>📌</span><span>来源: {source} · 片段 {chunk}</span></div>', unsafe_allow_html=True)

def render_agent_flow_panel(agents: List[Dict]):
    st.markdown('<div class="agent-flow-panel">', unsafe_allow_html=True)
    for i, agent in enumerate(agents):
        if i > 0:
            st.markdown('<div class="agent-arrow">→</div>', unsafe_allow_html=True)
        status = agent.get('status', 'idle')
        st.markdown(f"""
        <div class="agent-node {'active' if status == 'active' else ''} {'processing' if status == 'processing' else ''}">
            <div style="font-size:28px;">{agent['icon']}</div>
            <div style="font-size:11px;font-weight:600;color:{ColorTokens.DARK_GRAY};margin-top:6px;">{agent['name']}</div>
            <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin-top:4px;">{agent.get('desc', '')}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_resource_card(resource: Dict):
    st.markdown(f"""
    <div class="resource-card">
        <div style="font-size:28px;">{resource['icon']}</div>
        <div style="flex:1;">
            <div style="font-size:14px;font-weight:600;color:{ColorTokens.DARK_GRAY};">{resource['title']}</div>
            <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};margin-top:4px;">{resource['meta']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_student_sidebar(current_page: str = "dashboard"):
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0;margin-bottom:20px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:24px;">🎓</span>
                <div>
                    <div style="font-size:16px;font-weight:700;color:white;">智能学习助手</div>
                    <div style="font-size:11px;opacity:0.6;">A3 · 科大讯飞</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            ("dashboard", "🏠 个人首页"),
            ("profile", "📝 学生画像"),
            ("learning", "⚡ 多智能体协同"),
            ("resources", "📦 学习资源"),
            ("qa", "💬 智能答疑"),
        ]

        for page_id, name in pages:
            if st.button(name, key=f"sidebar_{page_id}", use_container_width=True):
                st.session_state.student_page = page_id
                st.rerun()

        st.markdown("---")
        if st.button("🚪 退出登录", key="sidebar_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def render_teacher_sidebar(current_page: str = "dashboard"):
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0;margin-bottom:20px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:24px;">🏫</span>
                <div>
                    <div style="font-size:16px;font-weight:700;color:white;">教师管理后台</div>
                    <div style="font-size:11px;opacity:0.6;">A3 · 科大讯飞</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pages = [
            ("dashboard", "📊 数据概览"),
            ("students", "🎓 学生管理"),
            ("knowledge", "📚 知识库"),
            ("settings", "⚙️ 系统设置"),
        ]

        for page_id, name in pages:
            if st.button(name, key=f"teacher_sidebar_{page_id}", use_container_width=True):
                st.session_state.teacher_page = page_id
                st.rerun()

        st.markdown("---")
        if st.button("🚪 退出登录", key="teacher_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
