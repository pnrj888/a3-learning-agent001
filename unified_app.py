"""
A3 赛题 - 统一应用入口
基于大模型的个性化资源生成与学习多智能体系统开发
遵循 AtomCode 设计规范 | v4.0
整合学生端 + 教师管理后台
"""
import streamlit as st
import time
import os
import sys
import json
import random
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta

# === 统一页面配置 (只调用一次) ===
st.set_page_config(
    page_title="AI多智能体个性化学习系统 | A3",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === 注入设计系统 (只调用一次) ===
from design_system import (
    inject_design_system, ColorTokens,
    render_tech_annotations, render_agent_flow_panel,
    render_profile_radar_card, render_profile_dimension_card,
    render_resource_card, render_rag_citation, render_rag_source_chip,
    render_heatmap, render_status_badge, render_toast,
    render_progress_with_label, render_section_header,
    render_student_sidebar, render_teacher_sidebar, render_stat_grid,
    generate_id, format_timestamp
)

inject_design_system()

sys.path.insert(0, str(Path(__file__).resolve().parent))

# === 统一会话初始化 ===
def init_unified_session():
    """初始化学生端 + 教师端所有 session state"""
    # 角色选择（student / teacher / None）
    student_defaults = {
        "student_page": "splash",
        "splash_shown": False,
        "logged_in": False,
        "is_guest": False,
        "login_username": "",
        "profile_agent": None,
        "conversation_history": [],
        "current_profile": None,
        "student_id": "",
        "student_name": "",
        "generation_logs": [],
        "generation_progress": 0,
        "generated_resources": [],
        "learning_plan": "",
        "learning_goal": "",
        "topics": "",
        "agent_states": [],
        "qa_history": [],
    }
    teacher_defaults = {
        "teacher_page": "kb",
        "kb_files": [],
        "agent_configs": {},
        "selected_student": None,
        "log_filter": "all",
        "report_period": "weekly",
        "teacher_logged_in": False,
        "teacher_role": None,
        "teacher_name": "",
    }
    all_defaults = {}
    all_defaults.update(student_defaults)
    all_defaults.update(teacher_defaults)
    all_defaults["user_role"] = None
    all_defaults["student_page"] = "splash"
    all_defaults["teacher_page"] = "kb"
    for key, value in all_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_unified_session()

# === 导航函数 ===
def student_nav(page: str):
    st.session_state.user_role = "student"
    st.session_state.student_page = page

def teacher_nav(p: str):
    st.session_state.user_role = "teacher"
    st.session_state.teacher_page = p

# 兼容原 app.py 中的 nav_to 引用（已被 student_nav 替代，此处保留以防万一）
def nav_to(page: str):
    student_nav(page)

LIGHT_THEME_RESET = """
<style>
  /* 淡蓝渐变基底 + 极淡网格线 + 柔和径向装饰 */
  .stApp {
    background:
      radial-gradient(circle at 5% 15%, rgba(37,99,235,0.05) 0%, transparent 35%),
      radial-gradient(circle at 95% 85%, rgba(16,185,129,0.035) 0%, transparent 40%),
      radial-gradient(circle at 80% 10%, rgba(139,92,246,0.03) 0%, transparent 30%),
      linear-gradient(rgba(37,99,235,0.018) 1px, transparent 1px),
      linear-gradient(90deg, rgba(37,99,235,0.018) 1px, transparent 1px),
      linear-gradient(180deg, #F8FAFC 0%, #F0F5FF 45%, #F8FAFC 100%) !important;
    background-size: 100% 100%, 100% 100%, 100% 100%, 72px 72px, 72px 72px, 100% 100% !important;
  }
  .main { background: transparent !important; }
  section[data-testid="stSidebar"] { display: block !important; }
  section[data-testid="stSidebar"] > div { background: #F9FAFB !important; }
</style>
"""

# ========================================================================
# 角色选择首页
# ========================================================================
def render_role_landing():
    """统一入口 - 选择学生端或教师端"""
    st.markdown("""
    <style>
        .stApp {
            background:
                radial-gradient(circle at 8% 20%, rgba(37,99,235,0.06) 0%, transparent 38%),
                radial-gradient(circle at 92% 80%, rgba(16,185,129,0.04) 0%, transparent 42%),
                linear-gradient(rgba(37,99,235,0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(37,99,235,0.02) 1px, transparent 1px),
                linear-gradient(180deg, #EBF3FE 0%, #E8F0FE 40%, #EEF3FF 100%) !important;
            background-size: 100% 100%, 100% 100%, 64px 64px, 64px 64px, 100% 100% !important;
        }
        section[data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="max-width:500px;margin:0 auto;padding:60px 20px;text-align:center;">
        <div style="display:inline-block;width:80px;height:80px;
            background:linear-gradient(135deg,#2563EB,#1D4ED8);
            border-radius:22px;display:flex;align-items:center;justify-content:center;
            box-shadow:0 12px 40px rgba(37,99,235,0.3);margin-bottom:24px;
            animation:logoBeat 3s ease-in-out infinite;">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="40" height="40">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
            </svg>
        </div>
        <style>
            @keyframes logoBeat {{ 0%,100%{{transform:scale(1)}} 50%{{transform:scale(1.05)}} }}
        </style>
        <div style="font-size:28px;font-weight:800;color:{ColorTokens.DARK_GRAY};margin-bottom:8px;">
            AI多智能体个性化学习系统
        </div>
        <div style="font-size:14px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:40px;">
            基于讯飞星火大模型 · RAG知识库 · 多智能体协同
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:28px 20px;
            border:1px solid {ColorTokens.CARD_BORDER};text-align:center;
            transition:all 0.3s;cursor:pointer;"
            onmouseover="this.style.boxShadow='0 8px 30px rgba(37,99,235,0.12)'"
            onmouseout="this.style.boxShadow='none'">
            <div style="font-size:40px;margin-bottom:12px;">🎓</div>
            <div style="font-size:18px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:8px;">学生端</div>
            <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};line-height:1.6;">
                智能学习助手<br/>多智能体协同 · 6维画像 · RAG答疑
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎓 进入学生端", use_container_width=True, type="primary"):
            st.session_state.user_role = "student"
            st.session_state.student_page = "splash"
            st.rerun()
    with col2:
        st.markdown(f"""
        <div style="background:white;border-radius:16px;padding:28px 20px;
            border:1px solid {ColorTokens.CARD_BORDER};text-align:center;
            transition:all 0.3s;cursor:pointer;"
            onmouseover="this.style.boxShadow='0 8px 30px rgba(37,99,235,0.12)'"
            onmouseout="this.style.boxShadow='none'">
            <div style="font-size:40px;margin-bottom:12px;">🏫</div>
            <div style="font-size:18px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:8px;">教师管理后台</div>
            <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};line-height:1.6;">
                学情统计 · 知识库管理<br/>智能体配置 · 资源日志 · 数据大屏
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🏫 进入教师管理后台", use_container_width=True):
            st.session_state.user_role = "teacher"
            st.session_state.teacher_page = "kb"
            st.rerun()

    st.markdown(f"""
    <div style="text-align:center;margin-top:40px;font-size:10px;color:{ColorTokens.LIGHT_GRAY};">
        RAG本地知识库 · 多智能体编排 · 学生多维画像 · 大模型防幻觉<br/>
        AI多智能体个性化学习系统 v1.0 · 基于讯飞星火大模型
    </div>
    """, unsafe_allow_html=True)

# 椤甸潰0: 鍚姩杩囨浮椤?(Splash Screen)

# 页面0: 启动过渡页 (Splash Screen)
# ========================================================================
def render_splash_page():
    """手机竖屏启动页 - 自动跳转到画像采集"""
    import time as _time
    
    splash_html = """
    <style>
        .stApp { background: linear-gradient(180deg, #EBF3FE 0%, #E8F0FE 30%, #DCE8FC 60%, #EEF3FF 100%) !important; }
        section[data-testid="stSidebar"] { display: none; }
        .splash-container {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            height: 100vh; text-align: center; padding: 40px 20px;
            animation: splashFadeIn 0.6s ease-out;
        }
        @keyframes splashFadeIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }

        .splash-logo {
            width: 80px; height: 80px; background: linear-gradient(135deg, #2563EB, #1D4ED8);
            border-radius: 22px; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 12px 40px rgba(37,99,235,0.3); margin-bottom: 28px;
            animation: logoBeat 3s ease-in-out infinite; position: relative;
        }
        .splash-logo::after {
            content: ''; position: absolute; inset: -5px; border-radius: 26px;
            background: linear-gradient(135deg, rgba(37,99,235,0.35), rgba(16,185,129,0.3), rgba(37,99,235,0.35));
            filter: blur(10px); z-index: -1; animation: logoGlow 3s ease-in-out infinite;
        }
        @keyframes logoBeat { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
        @keyframes logoGlow { 0%,100%{opacity:.5} 50%{opacity:1} }

        .splash-main-title {
            font-size: 28px; font-weight: 800; letter-spacing: -0.02em;
            background: linear-gradient(135deg, #1F2937 0%, #2563EB 50%, #1F2937 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; margin-bottom: 10px; line-height: 1.3;
        }
        .splash-sub-title { font-size: 14px; color: #374151; margin-bottom: 36px; }

        .splash-divider { width: 56px; height: 3px; border-radius: 2px; background: linear-gradient(90deg, #2563EB, #10B981); margin: 0 auto 36px; opacity: 0.6; }

        .splash-agents { display: flex; gap: 22px; margin-bottom: 40px; justify-content: center; }
        .splash-agent-icon {
            width: 56px; height: 56px; border-radius: 16px;
            background: rgba(255,255,255,0.88); backdrop-filter: blur(10px);
            border: 1.5px solid rgba(37,99,235,0.12);
            box-shadow: 0 2px 16px rgba(0,0,0,0.04);
            display: flex; align-items: center; justify-content: center;
            font-size: 24px; animation: agentFloat 4s ease-in-out infinite;
        }
        .splash-agent-icon:nth-child(1){animation-delay:0s}
        .splash-agent-icon:nth-child(2){animation-delay:.3s}
        .splash-agent-icon:nth-child(3){animation-delay:.6s}
        .splash-agent-icon:nth-child(4){animation-delay:.9s}
        .splash-agent-icon:nth-child(5){animation-delay:1.2s}
        @keyframes agentFloat { 0%,100%{transform:translateY(0)} 30%{transform:translateY(-8px)} 60%{transform:translateY(0)} }

        .splash-loading-track { width: 220px; height: 4px; background: rgba(37,99,235,0.08); border-radius: 2px; overflow: hidden; margin: 0 auto 12px; }
        .splash-loading-fill {
            height: 100%; width: 70%; border-radius: 2px;
            background: linear-gradient(90deg, #2563EB 0%, #10B981 50%, #2563EB 100%);
            background-size: 200% 100%;
            animation: shimmerFlow 2.5s ease-in-out infinite; position: relative;
        }
        .splash-loading-fill::after {
            content: ''; position: absolute; top: 0; left: -30px; width: 30px; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent);
            animation: microGlow 1.8s ease-in-out infinite;
        }
        @keyframes shimmerFlow { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
        @keyframes microGlow { 0%{left:-30px} 100%{left:100%} }

        .splash-loading-text { font-size: 11px; color: #6B7280; letter-spacing: 0.04em; }

        .splash-tech-row { display: flex; gap: 10px; margin-top: 48px; }
        .splash-tech-chip { padding: 4px 10px; background: rgba(255,255,255,0.6); border-radius: 12px; border: 1px solid rgba(37,99,235,0.08); font-size: 10px; color: #6B7280; }
    </style>

    <div class="splash-container">
        <div class="splash-logo">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="36" height="36">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
            </svg>
        </div>
        <div class="splash-main-title">AI多智能体<br/>个性化学习系统</div>
        <div class="splash-sub-title">基于大模型的自适应学习资源生成平台</div>
        <div class="splash-divider"></div>
        <div class="splash-agents">
            <div class="splash-agent-icon">📖</div>
            <div class="splash-agent-icon">🎯</div>
            <div class="splash-agent-icon">📝</div>
            <div class="splash-agent-icon">📊</div>
            <div class="splash-agent-icon">🗺️</div>
        </div>
        <div class="splash-loading-track"><div class="splash-loading-fill"></div></div>
        <div class="splash-loading-text">多智能体初始化中 · 知识库加载</div>
        <div class="splash-tech-row">
            <span class="splash-tech-chip">RAG知识库</span>
            <span class="splash-tech-chip">多智能体</span>
            <span class="splash-tech-chip">讯飞星火</span>
            <span class="splash-tech-chip">防幻觉</span>
        </div>
    </div>
    """
    st.markdown(splash_html, unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        if st.button("🎓 进入学生端", key="splash_student", use_container_width=True):
            st.session_state.user_role = "student"
            nav_to("login")
            st.rerun()
    with col_s2:
        if st.button("🏫 进入教师管理后台", key="splash_teacher", use_container_width=True):
            st.session_state.user_role = "teacher"
            nav_to("teacher_login")
            st.rerun()
    
    if not st.session_state.splash_shown:
        _time.sleep(3)
        st.session_state.splash_shown = True
        nav_to("login")
        st.rerun()

# ========================================================================
# 页面1: 登录/注册二合一
# ========================================================================
def render_login_page():
    """移动端风格登录注册二合一页面"""

    # 隐藏侧边栏
    login_css = f"""
    <style>
        .stApp {{
            background:
                radial-gradient(circle at 8% 20%, rgba(37,99,235,0.06) 0%, transparent 38%),
                radial-gradient(circle at 92% 80%, rgba(16,185,129,0.04) 0%, transparent 42%),
                linear-gradient(rgba(37,99,235,0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(37,99,235,0.02) 1px, transparent 1px),
                linear-gradient(180deg, #EBF3FE 0%, #E8F0FE 40%, #EEF3FF 100%) !important;
            background-size: 100% 100%, 100% 100%, 64px 64px, 64px 64px, 100% 100% !important;
        }}
        section[data-testid="stSidebar"] {{ display: none; }}
        header[data-testid="stHeader"] {{ background: transparent !important; }}
        .stTextInput > div > div > input {{
            border-radius: 10px !important; border: 1.5px solid {ColorTokens.CARD_BORDER} !important;
            padding: 12px 16px !important; font-size: 15px !important;
            background: rgba(255,255,255,0.85) !important; backdrop-filter: blur(8px) !important;
            transition: all 0.25s !important;
        }}
        .stTextInput > div > div > input:focus {{
            border-color: {ColorTokens.PRIMARY} !important; box-shadow: 0 0 0 3px {ColorTokens.GLOW_BLUE} !important;
        }}
        .stButton > button {{
            width: 100% !important; border-radius: 10px !important; font-size: 15px !important;
            font-weight: 700 !important; padding: 14px !important;
            transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
        }}
    </style>
    """
    st.markdown(login_css, unsafe_allow_html=True)

    # 居中容器
    st.markdown("""
    <div style="max-width:400px;margin:0 auto;padding:40px 20px;">
    """, unsafe_allow_html=True)

    # Logo区
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:8px;">
        <div style="display:inline-block;width:72px;height:72px;
            background:linear-gradient(135deg,#2563EB,#1D4ED8);
            border-radius:20px;display:flex;align-items:center;justify-content:center;
            box-shadow:0 10px 36px rgba(37,99,235,0.28);margin-bottom:20px;
            animation:loginLogoBeat 3s ease-in-out infinite;position:relative;">
            <div style="position:absolute;inset:-4px;border-radius:24px;
                background:linear-gradient(135deg,rgba(37,99,235,0.35),rgba(16,185,129,0.3),rgba(37,99,235,0.35));
                filter:blur(8px);z-index:-1;animation:loginGlow 3s ease-in-out infinite;"></div>
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round" width="34" height="34">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
            </svg>
        </div>
    </div>
    <style>
        @keyframes loginLogoBeat {{ 0%,100%{{transform:scale(1)}} 50%{{transform:scale(1.04)}} }}
        @keyframes loginGlow {{ 0%,100%{{opacity:.5}} 50%{{opacity:1}} }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;margin-bottom:36px;">
        <div style="font-size:24px;font-weight:800;color:{ColorTokens.DARK_GRAY};letter-spacing:-0.02em;">AI多智能体</div>
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.PRIMARY};">个性化学习系统</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};margin-top:6px;">登录同步你的专属学习画像</div>
    </div>
    """, unsafe_allow_html=True)

    # 输入框区域 — 增加间距提升呼吸感
    st.markdown('<div style="margin-bottom:14px;">', unsafe_allow_html=True)
    username = st.text_input("📧 学号 / 账号", key="login_username_input",
        placeholder="请输入学号或已注册账号")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-bottom:10px;">', unsafe_allow_html=True)
    password = st.text_input("🔒 密码", type="password", key="login_password_input",
        placeholder="请输入密码")
    st.markdown('</div>', unsafe_allow_html=True)

    # 选项行 — 记住登录 + 忘记密码 同层级对齐，视觉更协调
    col_op1, col_op2 = st.columns([3, 2])
    with col_op1:
        st.markdown(f"""
        <style>
        div[data-testid="stCheckbox"] > label > div[data-testid="stMarkdownContainer"] p {{
            font-size:13px !important; color:{ColorTokens.MID_GRAY} !important;
        }}
        div[data-testid="stCheckbox"] {{
            min-height:28px; display:flex; align-items:center;
        }}
        </style>
        """, unsafe_allow_html=True)
        st.checkbox("记住登录", key="remember_me", value=True,
            help="14天内免密登录")
    with col_op2:
        st.markdown(f"""
        <div style="text-align:right;padding-top:2px;">
            <span style="font-size:13px;color:{ColorTokens.PRIMARY};cursor:pointer;
                font-weight:500; transition:opacity 0.2s;"
                onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'">
                忘记密码？
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # 登录按钮 — 全宽展示，提升主操作层级
    login_clicked = st.button("🚀 登录系统", use_container_width=True, type="primary",
        key="login_main_btn")

    # 交互反馈容器
    feedback_placeholder = st.empty()

    if login_clicked:
        if not username:
            feedback_placeholder.markdown(f"""
            <div style="background:{ColorTokens.WARNING_RED_LIGHT};padding:12px 16px;
                border-radius:10px;font-size:13px;color:{ColorTokens.WARNING_RED};
                border:1px solid {ColorTokens.WARNING_RED};margin-top:10px;
                animation:shakeX 0.4s ease-in-out;
                display:flex;align-items:center;gap:8px;">
                <span style="font-size:16px;">⚠️</span>
                <span>请输入学号/账号</span>
            </div>
            <style>
            @keyframes shakeX {{
                0%,100%{{transform:translateX(0)}}
                20%,60%{{transform:translateX(-4px)}}
                40%,80%{{transform:translateX(4px)}}
            }}
            </style>
            """, unsafe_allow_html=True)
        elif not password:
            feedback_placeholder.markdown(f"""
            <div style="background:{ColorTokens.WARNING_RED_LIGHT};padding:12px 16px;
                border-radius:10px;font-size:13px;color:{ColorTokens.WARNING_RED};
                border:1px solid {ColorTokens.WARNING_RED};margin-top:10px;
                animation:shakeX 0.4s ease-in-out;
                display:flex;align-items:center;gap:8px;">
                <span style="font-size:16px;">⚠️</span>
                <span>请输入密码</span>
            </div>
            <style>
            @keyframes shakeX {{
                0%,100%{{transform:translateX(0)}}
                20%,60%{{transform:translateX(-4px)}}
                40%,80%{{transform:translateX(4px)}}
            }}
            </style>
            """, unsafe_allow_html=True)
        else:
            feedback_placeholder.markdown(f"""
            <div style="background:#ECFDF5;padding:12px 16px;border-radius:10px;
                font-size:13px;color:{ColorTokens.AGENT_GREEN};
                border:1px solid {ColorTokens.AGENT_GREEN};margin-top:10px;
                display:flex;align-items:center;gap:8px;">
                <span style="font-size:16px;">✅</span>
                <span>登录成功！正在跳转...</span>
            </div>
            """, unsafe_allow_html=True)
            # 全屏 loading overlay，避免用户误以为卡死
            st.markdown(f"""
            <div id="login-loading-overlay" style="position:fixed;top:0;left:0;right:0;bottom:0;
                background:rgba(255,255,255,0.75);z-index:9999;display:flex;
                align-items:center;justify-content:center;backdrop-filter:blur(4px);">
                <div style="text-align:center;">
                    <div style="width:48px;height:48px;border:4px solid {ColorTokens.BG_GRAY};
                        border-top-color:{ColorTokens.PRIMARY};border-radius:50%;
                        animation:spin 0.8s linear infinite;margin:0 auto 16px;"></div>
                    <div style="font-size:15px;font-weight:600;color:{ColorTokens.DARK_GRAY};">
                        正在进入学习空间...</div>
                    <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};margin-top:6px;">
                        多智能体初始化中</div>
                </div>
            </div>
            <style>@keyframes spin{{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}</style>
            """, unsafe_allow_html=True)
            st.session_state.logged_in = True
            st.session_state.is_guest = False
            st.session_state.login_username = username
            st.session_state.student_id = username
            st.session_state.student_name = username
            time.sleep(1.2)
            nav_to("dashboard")
            st.rerun()

    # 分割线
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;margin:24px 0;">
        <div style="flex:1;height:1px;background:{ColorTokens.CARD_BORDER};"></div>
        <span style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};">或</span>
        <div style="flex:1;height:1px;background:{ColorTokens.CARD_BORDER};"></div>
    </div>
    """, unsafe_allow_html=True)

    # 游客免登
    if st.button("👤 游客免登 · 体验基础功能", use_container_width=True, key="guest_btn"):
        st.session_state.logged_in = False
        st.session_state.is_guest = True
        st.session_state.login_username = "游客用户"
        # 可视化跳转反馈
        st.markdown(f"""
        <div style="background:{ColorTokens.LIGHT_BLUE};padding:12px 16px;border-radius:10px;
            font-size:13px;color:{ColorTokens.PRIMARY};text-align:center;
            border:1px solid {ColorTokens.PRIMARY};margin-top:10px;
            display:flex;align-items:center;justify-content:center;gap:8px;">
            <div style="width:16px;height:16px;border:2px solid {ColorTokens.BG_GRAY};
                border-top-color:{ColorTokens.PRIMARY};border-radius:50%;
                animation:spin 0.8s linear infinite;"></div>
            <span>以游客身份进入，跳转至简易体验页...</span>
        </div>
        <style>@keyframes spin{{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}</style>
        """, unsafe_allow_html=True)
        time.sleep(1.2)
        nav_to("guest")
        st.rerun()

    # 游客说明
    st.markdown(f"""
    <div style="text-align:center;margin-top:20px;">
        <p style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};line-height:1.7;">
            💡 <strong>游客模式</strong>仅可体验基础问答功能<br/>
            完整功能（多智能体协同、学习画像、多模态资源生成）<br/>
            需<strong style="color:{ColorTokens.PRIMARY};">登录</strong>同步个人学习画像后使用
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 技术标注
    st.markdown(f"""
    <div style="display:flex;gap:8px;justify-content:center;margin-top:32px;flex-wrap:wrap;">
        <span style="padding:3px 10px;background:rgba(255,255,255,0.7);border-radius:14px;
            border:1px solid rgba(37,99,235,0.1);font-size:10px;color:{ColorTokens.LIGHT_GRAY};">RAG知识库</span>
        <span style="padding:3px 10px;background:rgba(255,255,255,0.7);border-radius:14px;
            border:1px solid rgba(37,99,235,0.1);font-size:10px;color:{ColorTokens.LIGHT_GRAY};">多智能体</span>
        <span style="padding:3px 10px;background:rgba(255,255,255,0.7);border-radius:14px;
            border:1px solid rgba(37,99,235,0.1);font-size:10px;color:{ColorTokens.LIGHT_GRAY};">讯飞星火</span>
        <span style="padding:3px 10px;background:rgba(255,255,255,0.7);border-radius:14px;
            border:1px solid rgba(37,99,235,0.1);font-size:10px;color:{ColorTokens.LIGHT_GRAY};">防幻觉</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ========================================================================
# 页面1.5: 游客简易体验页
# ========================================================================
def render_guest_page():
    """游客模式 - 仅可体验基础问答功能"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("qa")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{ColorTokens.LIGHT_BLUE},white);
        padding:16px 20px;border-radius:12px;margin-bottom:20px;
        border:1px solid {ColorTokens.CARD_BORDER};">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:24px;">👤</span>
            <div>
                <div style="font-weight:700;color:{ColorTokens.DARK_GRAY};">游客模式</div>
                <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">
                    仅体验基础智能答疑 | 
                    <span style="color:{ColorTokens.PRIMARY};cursor:pointer;font-weight:600;">立即登录获取完整功能 →</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 功能卡片对比
    col_feat1, col_feat2 = st.columns(2)
    with col_feat1:
        st.markdown(f"""
        <div class="ds-card ds-card-green" style="text-align:center;">
            <div style="font-size:28px;">✅</div>
            <div style="font-weight:700;color:{ColorTokens.DARK_GRAY};margin-top:8px;">游客可体验</div>
            <div style="font-size:12px;color:{ColorTokens.MID_GRAY};margin-top:8px;line-height:1.8;">
                💬 智能问答<br/>
                📚 知识库检索<br/>
                📖 基础课程讲解
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_feat2:
        st.markdown(f"""
        <div class="ds-card ds-card-blue" style="text-align:center;">
            <div style="font-size:28px;">🔓</div>
            <div style="font-weight:700;color:{ColorTokens.DARK_GRAY};margin-top:8px;">登录后解锁</div>
            <div style="font-size:12px;color:{ColorTokens.MID_GRAY};margin-top:8px;line-height:1.8;">
                🧠 6维学习画像<br/>
                ⚡ 多智能体协同<br/>
                📝 分层题库练习<br/>
                🧠 思维导图生成<br/>
                📊 学习路线规划
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 简易问答
    st.markdown("---")
    st.markdown(f"### 💬 基础智能问答")
    st.markdown(f"<p style='color:{ColorTokens.LIGHT_GRAY};font-size:13px;'>基于RAG知识库的有限次数问答（免登模式限5次/日）</p>", unsafe_allow_html=True)

    if "guest_qa_count" not in st.session_state:
        st.session_state.guest_qa_count = 0

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
        <span style="font-size:13px;color:{ColorTokens.MID_GRAY};">今日剩余:</span>
        <strong style="color:{ColorTokens.PRIMARY};">{5 - st.session_state.guest_qa_count}</strong>
        <span style="font-size:13px;color:{ColorTokens.MID_GRAY};">/ 5次</span>
    </div>
    """, unsafe_allow_html=True)

    with st.form("guest_qa_form"):
        guest_q = st.text_input("", placeholder="请输入你的学习疑问...", key="guest_q_input")
        submitted = st.form_submit_button("🔍 提问")

        if submitted and guest_q and st.session_state.guest_qa_count < 5:
            st.session_state.guest_qa_count += 1
            with st.spinner("🔍 RAG知识库检索中..."):
                time.sleep(1)
            st.success("检索完成")
            st.markdown(f"""
            <div style="background:{ColorTokens.BG_GRAY};padding:14px 16px;border-radius:10px;
                font-size:14px;line-height:1.7;margin-top:8px;">
                🤖 基于知识库检索结果：<br/><br/>
                关于 <strong>"{guest_q}"</strong> 的解答需要结合计算机网络基础知识。
                建议登录后使用完整版多智能体系统获取详细的个性化解答和配套学习资源。
            </div>
            """, unsafe_allow_html=True)
            st.markdown(render_rag_citation("computer_network_ch01.pdf", 2, 10, 0.85), unsafe_allow_html=True)
        elif submitted and st.session_state.guest_qa_count >= 5:
            st.warning("⚠️ 今日免登提问次数已用完，请登录获取无限制问答服务")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔐 登录获取完整功能", use_container_width=True, type="primary"):
        nav_to("login")
        st.rerun()

    render_tech_annotations(["RAG本地知识库", "游客体验模式", "完整功能需登录"])

# ========================================================================
# 页面2: 学生画像采集 (对话式构建6维画像)
# ========================================================================
# ========================================================================
# 页面0: 个人仪表盘首页 (数据驾驶舱 · 对标教师大屏)
# ========================================================================
def render_student_dashboard_page():
    """学生个人仪表盘 - 4-KPI + 双图表 + 热力图 + 智能体调度 + 薄弱点 + 打卡"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("dashboard")

    profile = st.session_state.get("current_profile")
    student_name = getattr(profile, 'name', '同学') if profile else '同学'

    # ── Top Welcome Bar ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;padding-bottom:12px;
        border-bottom:1px solid {ColorTokens.CARD_BORDER};">
        <div style="flex:1;">
            <div style="font-size:18px;font-weight:700;color:{ColorTokens.DARK_GRAY};">
                👋 欢迎回来，{student_name}
            </div>
            <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-top:4px;">
                {time.strftime('%Y年%m月%d日 %A')} · 这是你学习的第 <strong style="color:{ColorTokens.PRIMARY};">12</strong> 天
            </div>
        </div>
        <span style="font-size:10px;color:{ColorTokens.AGENT_GREEN};font-weight:600;
            background:#ECFDF5;padding:4px 10px;border-radius:8px;">
            🟢 画像已绑定
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Cards Row (4列对标教师大屏) ──
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    kpi_items = [
        ("在线学习时长", "48h", "▲ 12% 较上月", ColorTokens.PRIMARY),
        ("知识掌握率", "58%", "▲ 5% 较上月", ColorTokens.AGENT_GREEN),
        ("生成资源总数", "12", "▲ 3 本周新增", "#8B5CF6"),
        ("待补强薄弱点", "3", "▼ 2 较上月", ColorTokens.WARNING_RED),
    ]
    for col, (label, val, change, color) in zip([col_k1, col_k2, col_k3, col_k4], kpi_items):
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};
                position:relative;overflow:hidden;">
                <div style="position:absolute;top:-12px;right:-12px;width:56px;height:56px;
                    background:{color}0D;border-radius:50%;"></div>
                <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:6px;">{label}</div>
                <div style="font-size:28px;font-weight:800;color:{color};">{val}</div>
                <div style="font-size:10px;color:{ColorTokens.AGENT_GREEN};margin-top:4px;">{change}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Quick Actions Row ──
    st.markdown(f"""
    <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:10px;margin-top:16px;">
        ⚡ 快捷入口
    </div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:14px;">
    """, unsafe_allow_html=True)
    quick_actions = [
        ("📝", "采集画像", "profile", ColorTokens.PRIMARY),
        ("⚡", "生成资源", "learning", ColorTokens.AGENT_GREEN),
        ("💬", "智能答疑", "qa", "#8B5CF6"),
        ("🗺️", "学习路径", "learning_path", "#F59E0B"),
    ]
    for icon, label, page, color in quick_actions:
        if st.button(f"{icon} {label}", key=f"dash_qa_{page}", use_container_width=True):
            nav_to(page)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Chart Row 1: 掌握度趋势 + 资源类型分布 (对标教师大屏双图表) ──
    st.markdown(f"""
    <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:10px;">
        📊 个人学习分析
    </div>
    """, unsafe_allow_html=True)

    col_c1, col_c2 = st.columns([1.4, 1])

    with col_c1:
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:12px;">
            <div style="font-size:12px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:8px;">
                📈 知识掌握度变化趋势
            </div>
            <div style="display:flex;gap:12px;margin-bottom:6px;font-size:9px;color:{ColorTokens.LIGHT_GRAY};">
                <span><span style="color:#60A5FA;">●</span> 掌握率</span>
                <span><span style="color:#34D399;">●</span> 知识点数</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        trend_data = {
            "日期": ["06-23", "06-24", "06-25", "06-26", "06-27", "06-28", "06-29"],
            "掌握率(%)": [38, 42, 45, 49, 52, 55, 58],
            "已掌握知识点(个)": [3, 4, 5, 5, 6, 7, 8],
        }
        st.line_chart(trend_data, x="日期", y=["掌握率(%)", "已掌握知识点(个)"],
            color=["#60A5FA", "#34D399"])

    with col_c2:
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:12px;">
            <div style="font-size:12px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:8px;">
                📊 生成的资源类型分布
            </div>
        </div>
        """, unsafe_allow_html=True)
        res_data = {
            "类型": ["课程讲义", "习题题库", "思维导图", "拓展阅读", "学习路径"],
            "数量": [4, 3, 2, 2, 1],
        }
        st.bar_chart(res_data, x="类型", y="数量", color="#3B82F6")

    # ── Knowledge Heatmap + Weak Points (左右分栏) ──
    col_hm, col_wp = st.columns([1.2, 1])

    with col_hm:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                <div style="font-size:12px;font-weight:700;color:{ColorTokens.DARK_GRAY};">🧠 知识掌握热力图</div>
                <div style="display:flex;gap:8px;font-size:9px;color:{ColorTokens.LIGHT_GRAY};">
                    <span><span style="color:#10B981;">●</span> 掌握</span>
                    <span><span style="color:#F59E0B;">●</span> 一般</span>
                    <span><span style="color:#EF4444;">●</span> 薄弱</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        heatmap_data = [
            (8, "OSI参考模型", "#10B981"), (5, "TCP/IP协议", "#F59E0B"),
            (9, "UDP协议", "#10B981"), (2, "TCP拥塞控制", "#EF4444"),
            (7, "物理层基础", "#10B981"), (4, "IP路由算法", "#EF4444"),
            (6, "子网划分", "#F59E0B"), (3, "网络安全协议", "#EF4444"),
            (5, "HTTP/HTTPS", "#F59E0B"), (8, "应用层协议", "#10B981"),
            (4, "DNS解析", "#F59E0B"), (6, "DHCP协议", "#F59E0B"),
            (3, "IPv6基础", "#EF4444"), (7, "Socket编程", "#10B981"),
            (5, "VLAN", "#F59E0B"), (8, "数据链路层", "#10B981"),
        ]
        cols_hm = st.columns(4)
        for i, (level, name, color) in enumerate(heatmap_data):
            with cols_hm[i % 4]:
                st.markdown(f"""
                <div style="background:{color}15;border:1.5px solid {color};border-radius:6px;
                    padding:6px 2px;text-align:center;margin-bottom:5px;cursor:pointer;
                    transition:all .2s;"
                    title="{name}: 掌握等级 {level}/10"
                    onmouseover="this.style.transform='scale(1.08)'"
                    onmouseout="this.style.transform='scale(1)'">
                    <div style="font-size:7px;color:{ColorTokens.LIGHT_GRAY};overflow:hidden;
                        text-overflow:ellipsis;white-space:nowrap;">{name[:5]}</div>
                    <div style="font-size:11px;font-weight:800;color:{color};margin-top:1px;">{level}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_wp:
        # ── Weak Points Alert ──
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#FEF2F2,#F9FAFB);border-radius:14px;
            padding:14px 14px 8px;border:1px solid #FECACA;height:100%;">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:10px;">
                <span style="font-size:14px;">⚠️</span>
                <span style="font-size:12px;font-weight:700;color:{ColorTokens.DARK_GRAY};">薄弱点提醒</span>
                <span style="font-size:9px;color:{ColorTokens.WARNING_RED};margin-left:auto;">3 个待补强</span>
            </div>
            <div style="display:flex;flex-direction:column;gap:6px;">
                <div style="display:flex;align-items:center;gap:6px;font-size:10px;color:{ColorTokens.MID_GRAY};">
                    <span style="width:5px;height:5px;border-radius:50%;background:#EF4444;flex-shrink:0;"></span>
                    <span style="flex:1;">TCP拥塞控制 · 错误率67%</span>
                    <span style="padding:2px 6px;border-radius:4px;font-size:8px;background:{ColorTokens.PRIMARY};
                        color:white;cursor:pointer;">📄 讲义</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;font-size:10px;color:{ColorTokens.MID_GRAY};">
                    <span style="width:5px;height:5px;border-radius:50%;background:#EF4444;flex-shrink:0;"></span>
                    <span style="flex:1;">IP路由算法 · 错误率52%</span>
                    <span style="padding:2px 6px;border-radius:4px;font-size:8px;background:{ColorTokens.PRIMARY};
                        color:white;cursor:pointer;">🧠 导图</span>
                </div>
                <div style="display:flex;align-items:center;gap:6px;font-size:10px;color:{ColorTokens.MID_GRAY};">
                    <span style="width:5px;height:5px;border-radius:50%;background:#F59E0B;flex-shrink:0;"></span>
                    <span style="flex:1;">网络安全协议 · 错误率41%</span>
                    <span style="padding:2px 6px;border-radius:4px;font-size:8px;background:{ColorTokens.PRIMARY};
                        color:white;cursor:pointer;">📝 习题</span>
                </div>
            </div>
            <div style="margin-top:8px;"></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📦 一键补强", key="dash_weak_pack", use_container_width=True, type="primary"):
            st.success("✅ 已生成 3 个薄弱点的补强资源包")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Agent Schedule Panel + 学习打卡 (左右分栏，对标教师智能体调度) ──
    col_agent, col_checkin = st.columns([1.5, 1])

    with col_agent:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};margin-top:12px;">
            <div style="font-size:12px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:10px;">
                🔄 智能体为我做了什么
            </div>
            <div style="display:flex;align-items:center;gap:4px;font-size:9px;flex-wrap:wrap;">
        """, unsafe_allow_html=True)
        agent_schedule = [
            ("📖 ProfileAgent", "画像已更新", "#60A5FA"),
            ("🎯 PlannerAgent", "路径已规划", "#34D399"),
            ("📝 ResourceAgent", "12份资源", "#A78BFA"),
            ("📊 QuizAgent", "3套习题", "#FBBF24"),
            ("✅ ReviewAgent", "校验通过", "#EC4899"),
        ]
        agent_html = ""
        for i, (name, status, color) in enumerate(agent_schedule):
            agent_html += f"""
            <div style="text-align:center;padding:8px 6px;border-radius:8px;
                background:{color}12;border:1px solid {color}30;min-width:0;flex:1;">
                <div style="font-size:8px;font-weight:700;color:{color};">{name}</div>
                <div style="font-size:13px;margin:3px 0;">
                    {'✅' if '通过' in status or '更新' in status or '已' in status else '⏳'}
                </div>
                <div style="font-size:7px;color:{ColorTokens.LIGHT_GRAY};">{status}</div>
            </div>"""
            if i < len(agent_schedule) - 1:
                agent_html += f'<span style="color:{ColorTokens.CARD_BORDER};font-size:10px;flex-shrink:0;">→</span>'
        st.markdown(agent_html + "</div></div>", unsafe_allow_html=True)

    with col_checkin:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};margin-top:12px;">
            <div style="font-size:12px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:10px;">
                📅 本周学习打卡
            </div>
            <div style="display:flex;justify-content:space-between;gap:4px;">
        """, unsafe_allow_html=True)
        checkin_days = [
            ("一", True, "1.2h"), ("二", True, "0.8h"), ("三", True, "2.1h"),
            ("四", False, "—"), ("五", True, "1.5h"), ("六", False, "—"), ("日", False, "—")
        ]
        for day, done, duration in checkin_days:
            bg = "#ECFDF5" if done else ColorTokens.BG_GRAY
            border = "#10B981" if done else ColorTokens.CARD_BORDER
            icon = "✅" if done else "○"
            text_color = ColorTokens.AGENT_GREEN if done else ColorTokens.LIGHT_GRAY
            st.markdown(f"""
            <div style="flex:1;text-align:center;padding:6px 2px;border-radius:8px;
                background:{bg};border:1.5px solid {border};min-width:0;">
                <div style="font-size:8px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:2px;">{day}</div>
                <div style="font-size:12px;">{icon}</div>
                <div style="font-size:8px;font-weight:600;color:{text_color};">{duration}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Recent Activities ──
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};
        margin-top:12px;margin-bottom:12px;">
        <div style="font-size:12px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:10px;">
            🕐 最近动态
        </div>
        <div style="display:flex;flex-direction:column;gap:8px;">
            <div style="display:flex;align-items:center;gap:8px;padding:6px 10px;
                background:{ColorTokens.BG_GRAY};border-radius:8px;font-size:10px;">
                <span style="font-size:14px;">📄</span>
                <span style="flex:1;color:{ColorTokens.DARK_GRAY};font-weight:600;">
                    生成了《计算机网络核心原理精讲》讲义</span>
                <span style="color:{ColorTokens.LIGHT_GRAY};">2h前</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:6px 10px;
                background:{ColorTokens.BG_GRAY};border-radius:8px;font-size:10px;">
                <span style="font-size:14px;">📝</span>
                <span style="flex:1;color:{ColorTokens.DARK_GRAY};font-weight:600;">
                    完成「TCP拥塞控制」专项练习 · 正确率60%</span>
                <span style="color:{ColorTokens.LIGHT_GRAY};">昨天</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:6px 10px;
                background:{ColorTokens.BG_GRAY};border-radius:8px;font-size:10px;">
                <span style="font-size:14px;">🧠</span>
                <span style="flex:1;color:{ColorTokens.DARK_GRAY};font-weight:600;">
                    更新了6维学习画像 · 薄弱点减少1项</span>
                <span style="color:{ColorTokens.LIGHT_GRAY};">2天前</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_tech_annotations(["个人数据驾驶舱", "知识热力图", "智能体调度", "薄弱点追踪", "趋势图表"])


def render_profile_page():
    """移动端对话式画像采集页面 - 聊天风格"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("profile")

    # ── Top Title Bar ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;padding-bottom:12px;
        border-bottom:1px solid {ColorTokens.CARD_BORDER};">
        <div style="cursor:pointer;font-size:18px;padding:4px 8px;border-radius:8px;
            transition:all 0.2s;color:{ColorTokens.DARK_GRAY};"
            onclick="window.location.href='?page=learning'">←</div>
        <div style="flex:1;">
            <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};">AI学情画像采集</div>
            <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};">对话式构建6维动态画像</div>
        </div>
        <div style="font-size:11px;color:{ColorTokens.PRIMARY};font-weight:600;
            background:{ColorTokens.LIGHT_BLUE};padding:4px 10px;border-radius:12px;">
            {len(st.session_state.conversation_history)}轮对话
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chat Area ──
    st.markdown('<div class="ds-card" style="min-height:400px;max-height:500px;overflow-y:auto;margin-bottom:12px;">', unsafe_allow_html=True)

    if not st.session_state.conversation_history:
        st.session_state.conversation_history = [
            ("assistant", 
             "你好！我是你的AI学情画像助手 🤖\n\n"
             "接下来我会通过几个问题了解你的学习情况，为你构建专属的学习画像。准备好了吗？\n\n"
             "**第一个问题：你学过哪些计算机网络相关的先修课程？**\n"
             "（如：计算机基础、操作系统、数据结构等）")
        ]

    for role, content in st.session_state.conversation_history:
        if role == "assistant":
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:8px;margin:10px 0;">
                <div style="width:32px;height:32px;border-radius:10px;
                    background:linear-gradient(135deg,{ColorTokens.PRIMARY},{ColorTokens.PRIMARY_HOVER});
                    display:flex;align-items:center;justify-content:center;
                    color:white;font-size:14px;flex-shrink:0;box-shadow:0 2px 6px rgba(37,99,235,0.2);">🤖</div>
                <div style="max-width:75%;background:{ColorTokens.BG_GRAY};
                    padding:10px 14px;border-radius:4px 14px 14px 14px;
                    font-size:13px;line-height:1.7;color:{ColorTokens.DARK_GRAY};">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:8px;margin:10px 0;justify-content:flex-end;">
                <div style="max-width:75%;background:{ColorTokens.LIGHT_BLUE};
                    padding:10px 14px;border-radius:14px 4px 14px 14px;
                    font-size:13px;line-height:1.7;color:{ColorTokens.DARK_GRAY};">
                    {content}
                </div>
                <div style="width:32px;height:32px;border-radius:10px;
                    background:{ColorTokens.BG_GRAY};display:flex;align-items:center;
                    justify-content:center;font-size:14px;flex-shrink:0;">👤</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Generating Modal Overlay ──
    if "show_profile_modal" in st.session_state and st.session_state.show_profile_modal:
        step_idx = st.session_state.get("profile_gen_step", 0)
        steps = [
            ("🔍", "解析对话内容..."),
            ("🧠", "提取知识基础维度..."),
            ("🎯", "识别学习目标与认知风格..."),
            ("⚠️", "定位薄弱知识点..."),
            ("📊", "分析资源偏好与学习节奏..."),
            ("✅", "6维学习画像生成完毕！"),
        ]
        modal_steps = ""
        for i, (icon, text) in enumerate(steps):
            if i < step_idx:
                modal_steps += f"""
                <div style="display:flex;align-items:center;gap:10px;padding:8px 0;
                    color:{ColorTokens.AGENT_GREEN};font-size:13px;">
                    <span>{icon}</span><span>{text}</span><span>✅</span>
                </div>"""
            elif i == step_idx:
                modal_steps += f"""
                <div style="display:flex;align-items:center;gap:10px;padding:8px 0;
                    color:{ColorTokens.PRIMARY};font-size:13px;font-weight:600;">
                    <span>{icon}</span><span>{text}</span>
                    <div style="width:16px;height:16px;border:2px solid {ColorTokens.PRIMARY};
                        border-top-color:transparent;border-radius:50%;
                        animation:spin 0.8s linear infinite;"></div>
                </div>"""
            else:
                modal_steps += f"""
                <div style="display:flex;align-items:center;gap:10px;padding:8px 0;
                    color:{ColorTokens.LIGHT_GRAY};font-size:13px;opacity:0.5;">
                    <span>{icon}</span><span>{text}</span>
                </div>"""

        progress_pct = min(int((step_idx + 1) / len(steps) * 100), 100)
        st.markdown(f"""
        <style>@keyframes spin{{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}</style>
        <div style="position:fixed;top:0;left:0;right:0;bottom:0;
            background:rgba(0,0,0,0.45);z-index:999;display:flex;
            align-items:center;justify-content:center;">
            <div style="background:white;border-radius:16px;padding:28px 24px;
                width:320px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.2);">
                <div style="font-size:40px;margin-bottom:12px;">🧠</div>
                <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};
                    margin-bottom:6px;">正在生成6维学生画像</div>
                <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:20px;">
                    多智能体协同分析中...
                </div>
                <div style="text-align:left;padding:0 8px;">{modal_steps}</div>
                <div style="height:4px;background:{ColorTokens.BG_GRAY};border-radius:2px;
                    margin-top:16px;overflow:hidden;">
                    <div style="height:100%;width:{progress_pct}%;border-radius:2px;
                        background:linear-gradient(90deg,{ColorTokens.PRIMARY},{ColorTokens.AGENT_GREEN});
                        transition:width 0.5s ease;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Auto advance steps
        if step_idx < len(steps):
            time.sleep(0.6)
            st.session_state.profile_gen_step = step_idx + 1
            st.rerun()
        else:
            # Done - generate profile and navigate
            time.sleep(0.5)
            st.session_state.show_profile_modal = False
            st.session_state.profile_gen_step = 0
            from student_profile.profile_model import StudentProfile
            st.session_state.current_profile = StudentProfile(
                student_id=st.session_state.get("student_id", "0001"),
                name=st.session_state.get("student_name", "同学"),
                grade="大学本科",
                subject="计算机网络",
                prerequisites=["计算机基础", "操作系统", "数据结构"],
                learning_style="混合式学习（理论+实践）",
                weak_points=["TCP拥塞控制", "IP路由算法", "网络安全协议"],
                error_prone_types=["计算题", "协议分析题"],
                learning_goals=["系统掌握计算机网络原理", "具备网络编程能力"],
                daily_rhythm={"上午": "理论学习", "下午": "实践编码", "晚上": "错题复习"}
            )
            nav_to("profile_result")
            st.rerun()

    # ── Bottom Input Bar ──
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:6px;border:1.5px solid {ColorTokens.CARD_BORDER};
        display:flex;align-items:center;gap:8px;margin-bottom:16px;">
        <div style="width:40px;height:40px;border-radius:10px;background:{ColorTokens.BG_GRAY};
            display:flex;align-items:center;justify-content:center;font-size:16px;
            flex-shrink:0;cursor:pointer;transition:all 0.2s;"
            onclick="this.style.background='#FEE2E2';this.style.color='#EF4444';">
            🎤
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Send Logic ──
    conversation_questions = [
        ("assistant", "很好！接下来：\n\n**你在计算机网络学习中遇到过哪些困难或薄弱的知识点？**\n（比如：TCP拥塞控制、IP路由、子网划分等）"),
        ("assistant", "了解了！那：\n\n**你希望通过学习达到什么具体目标？**\n（如：通过期末考试、考证、求职面试、项目实战等）"),
        ("assistant", "最后两个问题：\n\n**你更喜欢哪种学习方式？**\n（视频讲解 / 阅读文档 / 动手编码 / 小组讨论）"),
        ("assistant", "好的！最后一个问题：\n\n**你每天可以投入多少时间学习？偏好什么时间段？**\n（如：晚上2小时、周末全天等）"),
    ]
    question_idx = len(st.session_state.conversation_history) // 2

    # 动态示例提示 — 根据当前问题轮换，降低用户回答门槛
    example_hints = [
        "如：计算机基础、操作系统、数据结构...",
        "如：TCP拥塞控制、IP路由、子网划分...",
        "如：通过期末考试、考证、项目实战...",
        "如：视频讲解、阅读文档、动手编码...",
        "如：晚上2小时、周末全天...",
    ]
    current_hint = example_hints[min(question_idx, len(example_hints) - 1)]

    # 输入与发送区域 — 调整比例提升输入舒适度，按钮增加主操作层级
    conv_feedback = st.empty()
    col_input, col_send = st.columns([6, 1])
    with col_input:
        user_input = st.text_input("", key="conv_input",
            placeholder=current_hint, label_visibility="collapsed")
    with col_send:
        st.markdown(f"""
        <style>
        div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] div:nth-child(2) .stButton > button {{
            background: {ColorTokens.PRIMARY} !important;
            color: white !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            height: 42px !important;
            padding: 0 16px !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] div:nth-child(2) .stButton > button:hover {{
            background: {ColorTokens.PRIMARY_HOVER} !important;
            box-shadow: 0 4px 12px rgba(37,99,235,0.25) !important;
            transform: translateY(-1px) !important;
        }}
        div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] div:nth-child(2) .stButton > button:active {{
            transform: translateY(0) !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        send_clicked = st.button("发送", key="send_msg", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 空输入校验 — 明确提示，避免无效操作
    if send_clicked:
        if not user_input or not user_input.strip():
            conv_feedback.markdown(f"""
            <div style="background:{ColorTokens.WARNING_RED_LIGHT};padding:8px 12px;
                border-radius:8px;font-size:12px;color:{ColorTokens.WARNING_RED};
                border:1px solid {ColorTokens.WARNING_RED};margin:4px 0 10px;
                animation:shakeX 0.35s ease-in-out;
                display:flex;align-items:center;gap:6px;">
                <span style="font-size:14px;">⚠️</span>
                <span>请输入内容后再发送</span>
            </div>
            <style>
            @keyframes shakeX {{
                0%,100%{{transform:translateX(0)}}
                20%,60%{{transform:translateX(-3px)}}
                40%,80%{{transform:translateX(3px)}}
            }}
            </style>
            """, unsafe_allow_html=True)
        else:
            st.session_state.conversation_history.append(("user", user_input.strip()))
            if question_idx < len(conversation_questions) + 1:
                next_q = conversation_questions[question_idx - 1] if question_idx > 0 else None
                if next_q:
                    st.session_state.conversation_history.append(next_q)
            st.rerun()

    # ── Generate Profile Button ──
    if len(st.session_state.conversation_history) >= 6:
        st.markdown(f"""
        <div style="text-align:center;margin:8px 0;
            padding:8px;background:{ColorTokens.LIGHT_BLUE};border-radius:10px;
            font-size:11px;color:{ColorTokens.PRIMARY};">
            📊 已采集足够信息，可以生成画像了
        </div>
        """, unsafe_allow_html=True)
        if st.button("🧠 生成我的6维学习画像", use_container_width=True, type="primary"):
            st.session_state.show_profile_modal = True
            st.session_state.profile_gen_step = 0
            st.rerun()

    # ── Bottom Annotation ──
    st.markdown(f"""
    <div style="text-align:center;margin-top:12px;">
        <p style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};line-height:1.8;">
            自动提取六大画像维度：
            知识基础 · 学习目标 · 认知风格 · 薄弱知识点 · 资源偏好 · 每日可学习时长
        </p>
    </div>
    """, unsafe_allow_html=True)

    render_tech_annotations(["对话式画像采集", "6维AI分析", "多轮引导", "特征自动抽取"])

# ========================================================================
# 页面2.5: 画像结果展示页
# ========================================================================
def render_profile_result_page():
    """画像结果展示页 - 6维卡片 + 环形进度 + 学情总结"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("profile")

    if not st.session_state.current_profile:
        st.warning("请先完成画像采集")
        if st.button("← 返回画像采集"):
            nav_to("profile")
            st.rerun()
        render_tech_annotations()
        return

    profile = st.session_state.current_profile
    profile_id = getattr(profile, 'student_id', '0001')
    profile_name = getattr(profile, 'name', '同学')
    profile_grade = getattr(profile, 'grade', '-')

    # ── Top Bar ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;padding-bottom:12px;
        border-bottom:1px solid {ColorTokens.CARD_BORDER};">
        <div style="cursor:pointer;font-size:18px;padding:4px 8px;border-radius:8px;
            color:{ColorTokens.DARK_GRAY};">←</div>
        <div style="flex:1;">
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};">学习画像</div>
                <span style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};background:{ColorTokens.BG_GRAY};
                    padding:2px 8px;border-radius:8px;">ID: {profile_id}</span>
            </div>
            <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};">{profile_name} · {profile_grade}</div>
        </div>
        <div style="font-size:11px;color:{ColorTokens.PRIMARY};cursor:pointer;font-weight:600;
            border:1px solid {ColorTokens.PRIMARY};padding:4px 10px;border-radius:8px;"
            onclick="document.dispatchEvent(new Event('recollect'))">🔄 重新采集</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 重新采集画像", key="recollect_btn") or "recollect" not in st.session_state:
        pass

    # ── Profile Summary Banner ──
    weak_count = len(getattr(profile, 'weak_points', []))
    prerequisites = getattr(profile, 'prerequisites', [])
    goals = getattr(profile, 'learning_goals', [])
    style = getattr(profile, 'learning_style', '')
    rhythm = getattr(profile, 'daily_rhythm', {})

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#F0FDF4,#F9FAFB);border-radius:14px;
        padding:14px;margin-bottom:16px;border:1px solid #A7F3D0;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span style="font-size:16px;">✅</span>
            <span style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};">画像已生成</span>
        </div>
        <div style="font-size:11px;color:{ColorTokens.MID_GRAY};line-height:1.8;">
            知识基础 <strong style="color:{ColorTokens.DARK_GRAY};">{' · '.join(prerequisites) if prerequisites else '待采集'}</strong>
            · 学习目标 <strong style="color:{ColorTokens.DARK_GRAY};">{' · '.join(goals) if goals else '待采集'}</strong>
            · 认知风格 <strong style="color:{ColorTokens.PRIMARY};">{style}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 6 Dimension Cards ──
    dimensions = [
        {
            "icon": "📚", "title": "知识基础", "value": 75,
            "items": prerequisites if prerequisites else ["待采集"],
            "color": ColorTokens.PRIMARY, "is_weak": False,
        },
        {
            "icon": "🎯", "title": "学习目标", "value": 70,
            "items": goals if goals else ["待采集"],
            "color": ColorTokens.AGENT_GREEN, "is_weak": False,
        },
        {
            "icon": "🧠", "title": "认知风格", "value": 60,
            "items": [style] if style else ["待采集"],
            "color": ColorTokens.AGENT_GREEN, "is_weak": False,
        },
        {
            "icon": "⚠️", "title": "薄弱知识点", "value": 25,
            "items": getattr(profile, 'weak_points', []) or ["待采集"],
            "color": ColorTokens.WARNING_RED, "is_weak": True,
        },
        {
            "icon": "📖", "title": "资源偏好", "value": 55,
            "items": [f"{k}: {v}" for k, v in rhythm.items()] if rhythm else ["待采集"],
            "color": ColorTokens.PRIMARY, "is_weak": False,
        },
        {
            "icon": "⏰", "title": "每日学习时长", "value": 50,
            "items": getattr(profile, 'error_prone_types', []) or ["待采集"],
            "color": ColorTokens.PRIMARY, "is_weak": False,
        },
    ]

    # Render 2 cards per row
    for row_start in range(0, 6, 2):
        cols = st.columns(2)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx >= 6:
                break
            dim = dimensions[idx]
            with col:
                # Ring progress using conic-gradient
                pct = dim["value"]
                ring_color = dim["color"]
                ring_bg = "#F3F4F6"
                if dim["is_weak"]:
                    ring_color = ColorTokens.WARNING_RED
                    card_border = f"border:1.5px solid {ColorTokens.WARNING_RED};border-left:4px solid {ColorTokens.WARNING_RED};box-shadow:0 0 12px rgba(239,68,68,0.08);"
                else:
                    card_border = f"border:1px solid {ColorTokens.CARD_BORDER};"

                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:14px;margin-bottom:14px;
                    {card_border}position:relative;">
                    {'<div style="position:absolute;top:8px;right:8px;background:#FEF2F2;color:#EF4444;font-size:9px;font-weight:700;padding:2px 7px;border-radius:6px;">⚠ 薄弱</div>' if dim['is_weak'] else ''}
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="position:relative;width:50px;height:50px;flex-shrink:0;">
                            <svg width="50" height="50" viewBox="0 0 50 50">
                                <circle cx="25" cy="25" r="22" fill="none" stroke="{ring_bg}" stroke-width="4"/>
                                <circle cx="25" cy="25" r="22" fill="none" stroke="{ring_color}"
                                    stroke-width="4" stroke-linecap="round" stroke-dasharray="{pct * 1.38} 138"
                                    transform="rotate(-90 25 25)" style="transition:all 0.8s ease;"/>
                            </svg>
                            <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
                                font-size:13px;font-weight:800;color:{ColorTokens.DARK_GRAY};">{pct}%</div>
                        </div>
                        <div>
                            <div style="display:flex;align-items:center;gap:6px;">
                                <span style="font-size:16px;">{dim['icon']}</span>
                                <span style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};">{dim['title']}</span>
                            </div>
                            <div style="font-size:10px;margin-top:3px;">{
                                ''.join([f'<span style="display:inline-block;margin:1px 2px;padding:1px 7px;background:{ColorTokens.BG_GRAY};border-radius:6px;color:{ColorTokens.MID_GRAY};">{item}</span>' for item in dim['items']])
                            }</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Summary ──
    weak_list = getattr(profile, 'weak_points', [])
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span style="font-size:18px;">📋</span>
            <span style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};">学情总结</span>
        </div>
        <div style="font-size:12px;color:{ColorTokens.MID_GRAY};line-height:1.8;">
            {profile_name}同学已具备{'、'.join(prerequisites) if prerequisites else '基础'}等先修知识，
            偏好<strong style="color:{ColorTokens.PRIMARY};">{style}</strong>学习方式。
            {'当前核心短板集中在<strong style="color:{ColorTokens.WARNING_RED};">' + '、'.join(weak_list) + '</strong>，' if weak_list else ''}
            建议优先针对薄弱环节生成专项练习和课程讲解，同时加强代码实操训练。
        </div>
        {'<div style="margin-top:8px;padding:8px 10px;background:#FEF2F2;border-radius:8px;font-size:11px;color:#EF4444;border:1px solid #FECACA;">⚠️ 薄弱项告警：' + '、'.join(weak_list) + ' 需重点关注</div>' if weak_list else ''}
    </div>
    """, unsafe_allow_html=True)

    # ── Heatmap ──
    render_heatmap([
        {"name": "OSI模型", "mastery": 85}, {"name": "TCP/IP", "mastery": 45},
        {"name": "HTTP", "mastery": 70}, {"name": "DNS", "mastery": 60},
        {"name": "路由算法", "mastery": 30}, {"name": "拥塞控制", "mastery": 25},
        {"name": "网络安全", "mastery": 35}, {"name": "Socket", "mastery": 55},
        {"name": "IPv6", "mastery": 40}, {"name": "WLAN", "mastery": 65},
    ])

    # ── Bottom Buttons ──
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🗺️ 生成个性化学习路径", use_container_width=True, type="primary"):
            nav_to("learning")
            st.rerun()
    with col_b:
        if st.button("💬 前往智能答疑", use_container_width=True):
            nav_to("qa")
            st.rerun()

    render_tech_annotations(["6维画像可视化", "环形进度卡片", "薄弱项红色标识", "学情智能总结"])


# ========================================================================
# 页面2: 多智能体协同资源生成
# ========================================================================
def render_learning_page():
    """学生主交互首页 - 五智能体可视化 + 知识图谱 + 快捷输入"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("learning")

    # ── Top Nav Bar ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:38px;height:38px;border-radius:12px;
                background:linear-gradient(135deg,{ColorTokens.PRIMARY},{ColorTokens.PRIMARY_HOVER});
                display:flex;align-items:center;justify-content:center;
                color:white;font-size:16px;font-weight:700;
                box-shadow:0 2px 8px rgba(37,99,235,0.2);">
                {st.session_state.student_name[:1] if st.session_state.student_name else '学'}
            </div>
            <div>
                <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};">
                    你好，{st.session_state.student_name or '同学'} 👋
                </div>
                <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};">智能体已就绪，输入学习需求开始</div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="background:{ColorTokens.LIGHT_BLUE};padding:6px 12px;border-radius:20px;
                display:flex;align-items:center;gap:6px;">
                <span>⏱</span>
                <span style="font-size:12px;font-weight:600;color:{ColorTokens.DARK_GRAY};">48</span>
                <span style="font-size:10px;color:{ColorTokens.MID_GRAY};">分钟</span>
            </div>
            <div style="width:38px;height:38px;border-radius:12px;background:white;
                border:1px solid {ColorTokens.CARD_BORDER};display:flex;align-items:center;
                justify-content:center;font-size:16px;position:relative;">
                🔔
                <span style="position:absolute;top:6px;right:6px;width:7px;height:7px;
                    border-radius:50%;background:{ColorTokens.WARNING_RED};border:1.5px solid white;"></span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 5-Agent Cards Row ──
    if not st.session_state.current_profile:
        st.warning("⚠️ 请先完成学生画像采集")
        if st.button("← 返回画像采集"):
            nav_to("profile")
            st.rerun()
        render_tech_annotations()
        return

    agents = [
        {"icon": "📖", "name": "画像智能体", "role": "提取6维学习特征", "status": "active"},
        {"icon": "🎯", "name": "规划智能体", "role": "拆解任务规划路径", "status": "idle"},
        {"icon": "📝", "name": "资源智能体", "role": "RAG生成课程讲义", "status": "idle"},
        {"icon": "📊", "name": "习题智能体", "role": "薄弱点分层出题", "status": "idle"},
        {"icon": "✅", "name": "审核智能体", "role": "防幻觉质量校验", "status": "idle"},
    ]

    agent_html = ""
    for i, ag in enumerate(agents):
        status_cls = "active" if ag["status"] == "active" else ("processing" if ag["status"] == "processing" else "")
        status_text = {"active": "就绪", "idle": "空闲", "processing": "运行中"}.get(ag["status"], "空闲")
        status_cls_name = {"active": "status-active", "idle": "status-idle", "processing": "status-processing"}.get(ag["status"], "status-idle")
        agent_html += f"""
        <div class="agent-node {status_cls}" style="min-width:68px;text-align:center;padding:10px 6px;border-radius:12px;background:white;border:1.5px solid {ColorTokens.CARD_BORDER};flex-shrink:0;transition:all 0.35s;">
            <div style="font-size:24px;line-height:1;">{ag['icon']}</div>
            <div style="font-size:10px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin:4px 0 2px;">{ag['name']}</div>
            <div style="font-size:8px;color:{ColorTokens.LIGHT_GRAY};line-height:1.4;margin-bottom:4px;">{ag['role']}</div>
            <span class="agent-node-status" style="font-size:8px;padding:2px 7px;border-radius:10px;font-weight:600;background:{
            '#ECFDF5' if ag['status']=='active' else '#F3F4F6'};color:{
            ColorTokens.AGENT_GREEN if ag['status']=='active' else ColorTokens.LIGHT_GRAY};">{status_text}</span>
        </div>
        """
        if i < len(agents) - 1:
            agent_html += """<div style="flex-shrink:0;width:16px;display:flex;align-items:center;justify-content:center;font-size:13px;color:#2563EB;">→</div>"""

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#F0F5FF,#F9FAFB);border-radius:16px;padding:14px 8px;
        margin-bottom:16px;border:1px solid {ColorTokens.CARD_BORDER};overflow-x:auto;white-space:nowrap;">
        <div style="display:flex;align-items:flex-start;">{agent_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Knowledge Graph Thumbnail ──
    kg_points = [
        ("OSI模型", 90), ("TCP/IP", 85), ("HTTP", 70), ("DNS", 65), ("Socket", 55),
        ("UDP", 50), ("IPv4", 80), ("IPv6", 40), ("路由算法", 30), ("子网划分", 60),
        ("拥塞控制", 25), ("VLAN", 45), ("ARP", 70), ("DHCP", 55), ("NAT", 50),
        ("ICMP", 35), ("FTP", 75), ("SMTP", 80), ("SSL/TLS", 45), ("防火墙", 30),
    ]
    kg_cells = ""
    for name, mastery in kg_points:
        if mastery >= 85: bg = "#10B981"
        elif mastery >= 65: bg = "#34D399"
        elif mastery >= 40: bg = "#FBBF24"
        elif mastery >= 20: bg = "#F87171"
        else: bg = "#EF4444"
        kg_cells += f"""<div style="aspect-ratio:1;border-radius:6px;background:{bg};cursor:pointer;transition:all 0.25s;position:relative;" title="{name} {mastery}%"
            onmouseover="this.style.transform='scale(1.15)';this.style.zIndex='5'" onmouseout="this.style.transform='scale(1)'">
        </div>"""

    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <span style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};">🧠 知识图谱 · 计算机网络</span>
            <span style="font-size:9px;color:{ColorTokens.LIGHT_GRAY};display:flex;gap:10px;">
                <span>🟢已掌握</span><span>🟡一般</span><span>🔴薄弱</span>
            </span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:5px;">{kg_cells}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Progress Flow (shown when generating) ──
    if st.session_state.generation_progress > 0 and st.session_state.generation_progress < 100:
        steps = [
            ("📖", "画像智能体 → 提取学生6维特征"),
            ("🔍", "RAG检索 → 知识库匹配相关文档"),
            ("📝", "资源智能体 → 生成课程讲义"),
            ("📊", "习题智能体 → 生成分层练习"),
            ("✅", "审核智能体 → 防幻觉校验"),
        ]
        step_html = ""
        current_step = min(int(st.session_state.generation_progress / 20), 4)
        for i, (icon, text) in enumerate(steps):
            if i < current_step:
                cls = "done"
            elif i == current_step:
                cls = "current"
            else:
                cls = ""
            step_html += f"""
            <div class="progress-step {cls}" style="display:flex;align-items:center;gap:8px;padding:8px 12px;
                background:white;border-radius:10px;border:1px solid {ColorTokens.CARD_BORDER};
                font-size:11px;margin-bottom:4px;opacity:{1 if cls else 0.4};
                {'border-color:#10B981;background:#ECFDF5;' if cls=='done' else ''}
                {'border-color:#2563EB;background:#E8F0FE;animation:stepPulse 1.2s infinite;' if cls=='current' else ''}">
                <span style="font-size:14px;">{icon}</span>
                <span style="flex:1;color:{ColorTokens.AGENT_GREEN if cls=='done' else ColorTokens.DARK_GRAY};">{text}</span>
                <span style="font-size:12px;{'visibility:visible;color:#10B981' if cls=='done' else 'visibility:hidden'}">✅</span>
            </div>
            """
        st.markdown(step_html, unsafe_allow_html=True)
        render_progress_with_label(st.session_state.generation_progress, "多智能体协同进度")

    # ── Input Row ──
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:6px;border:1.5px solid {ColorTokens.CARD_BORDER};
        margin-bottom:10px;display:flex;align-items:center;gap:8px;transition:all 0.25s;"
        onfocus="this.style.borderColor='{ColorTokens.PRIMARY}'">
        <div style="width:42px;height:42px;border-radius:12px;background:{ColorTokens.BG_GRAY};
            display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">🎤</div>
    """, unsafe_allow_html=True)

    col_inp, col_btn = st.columns([3, 1])
    with col_inp:
        learning_input = st.text_input("", placeholder="输入你想学习的内容...",
            key="main_learning_input", label_visibility="collapsed")
    with col_btn:
        gen_clicked = st.button("生成专属资源包", key="main_generate_btn", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Quick Category Tags ──
    st.markdown('<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;">', unsafe_allow_html=True)
    quick_tags = ["🤖 人工智能导论", "📐 高等数学", "💻 编程实战", "📝 期末冲刺"]
    for tag in quick_tags:
        st.markdown(f"""
        <span style="padding:7px 14px;border-radius:20px;border:1px solid {ColorTokens.CARD_BORDER};
            background:white;font-size:11px;color:{ColorTokens.MID_GRAY};cursor:pointer;transition:all 0.25s;"
            onmouseover="this.style.borderColor='{ColorTokens.PRIMARY}';this.style.color='{ColorTokens.PRIMARY}';this.style.background='{ColorTokens.LIGHT_BLUE}'"
            onmouseout="this.style.borderColor='{ColorTokens.CARD_BORDER}';this.style.color='{ColorTokens.MID_GRAY}';this.style.background='white'">
            {tag}
        </span>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Trigger Generation ──
    gen_feedback = st.empty()
    if gen_clicked:
        if not learning_input or not learning_input.strip():
            gen_feedback.markdown(f"""
            <div style="background:{ColorTokens.WARNING_RED_LIGHT};padding:10px 14px;
                border-radius:8px;font-size:12px;color:{ColorTokens.WARNING_RED};
                border:1px solid {ColorTokens.WARNING_RED};margin-bottom:10px;
                animation:shakeX 0.35s ease-in-out;
                display:flex;align-items:center;gap:6px;">
                <span style="font-size:14px;">⚠️</span>
                <span>请输入想学习的内容后再生成</span>
            </div>
            <style>
            @keyframes shakeX {{
                0%,100%{{transform:translateX(0)}}
                20%,60%{{transform:translateX(-3px)}}
                40%,80%{{transform:translateX(3px)}}
            }}
            </style>
            """, unsafe_allow_html=True)
        else:
            st.session_state.learning_goal = learning_input.strip()
            st.session_state.generation_logs = []
            st.session_state.generated_resources = []
            st.session_state.generation_progress = 0

            logs = [
                (10, "📖 画像智能体: 提取学生6维特征完成"),
                (20, "🔍 RAG检索: 知识库匹配相关文档"),
                (35, "📝 资源智能体: 生成课程讲义"),
                (45, "✅ 内容校验: 防幻觉校验通过"),
                (60, "📊 习题智能体: 针对薄弱点分层出题"),
                (75, "🎨 多模态: 生成思维导图结构"),
                (85, "📑 多模态: 生成PPT大纲"),
                (95, "🗺️ 规划智能体: 构建学习路线"),
                (100, "✅ 审核完成 · 全部资源包已就绪"),
            ]
            # 实时进度占位，避免用户误以为页面卡死
            progress_placeholder = st.empty()
            for percent, msg in logs:
                time.sleep(0.3)
                st.session_state.generation_progress = percent
                st.session_state.generation_logs.append(msg)
                progress_placeholder.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;padding:10px 14px;
                    background:{ColorTokens.LIGHT_BLUE};border-radius:10px;font-size:12px;margin-bottom:10px;">
                    <div style="width:16px;height:16px;border:2px solid {ColorTokens.PRIMARY};
                        border-top-color:transparent;border-radius:50%;
                        animation:spin 0.8s linear infinite;"></div>
                    <span>{msg}</span>
                    <span style="margin-left:auto;font-weight:700;color:{ColorTokens.PRIMARY};">{percent}%</span>
                </div>
                <style>@keyframes spin{{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}</style>
                """, unsafe_allow_html=True)

            progress_placeholder.empty()

            topic_list = [t.strip() for t in learning_input.split() if len(t.strip()) > 1]
            if not topic_list:
                topic_list = ["计算机网络基础"]

            st.session_state.generated_resources = [
                {"type": "lecture", "icon": "📄", "title": "课程讲义 · 计算机网络精讲",
                 "meta": f"基于RAG检索 · {len(topic_list)}个知识点 · 含代码示例",
                 "tags": ["讲义", "RAG溯源", "代码实操"], "content": generate_lecture_content(topic_list)},
                {"type": "exam", "icon": "📝", "title": "分层题库 · 薄弱点专项练习",
                 "meta": "单选题5道 · 简答题3道 · 实操2道",
                 "tags": ["题库", "薄弱点", "含解析"], "content": generate_exam_content(topic_list)},
                {"type": "mindmap", "icon": "🧠", "title": "知识点思维导图",
                 "meta": "结构化梳理 · 层级清晰",
                 "tags": ["思维导图", "可视化", "知识体系"], "content": ""},
                {"type": "extend", "icon": "📖", "title": "拓展阅读材料",
                 "meta": "学术推荐 · 深度文档",
                 "tags": ["拓展", "RAG溯源", "学术"], "content": "推荐阅读: RFC 793 (TCP), RFC 2616 (HTTP), RFC 791 (IP)"},
                {"type": "ppt", "icon": "📊", "title": "课程PPT大纲",
                 "meta": "共15页 · 含代码示例",
                 "tags": ["PPT", "教学辅助"], "content": ""},
                {"type": "plan", "icon": "🗺️", "title": "个性化学习路线图",
                 "meta": "3阶段 · 每日安排 · 资源匹配",
                 "tags": ["路线图", "规划", "动态调整"], "content": generate_plan_content(topic_list)},
            ]
            st.session_state.learning_plan = st.session_state.generated_resources[-1]["content"]
            st.rerun()

    # ── Generated Results ──
    if st.session_state.get("generated_resources") and st.session_state.generation_progress == 100:
        st.markdown("---")
        st.markdown("### 📦 生成的多模态学习资源")
        for idx, resource in enumerate(st.session_state.generated_resources):
            with st.expander(f"{resource['icon']} {resource['title']}", expanded=(idx == 0)):
                st.markdown(render_resource_card(
                    resource["icon"], resource["title"], resource["meta"], resource["tags"]
                ), unsafe_allow_html=True)
                if resource.get("content"):
                    st.markdown(resource["content"])
                    st.markdown(render_rag_citation(
                        "computer_network_ch01.pdf", idx, len(st.session_state.generated_resources),
                        0.92 - idx * 0.03
                    ), unsafe_allow_html=True)

    if st.session_state.get("generated_resources") and st.session_state.generation_progress == 100:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📦 查看全部学习资源", use_container_width=True):
                nav_to("resources")
                st.rerun()
        with col_b:
            if st.button("💬 进入智能答疑", use_container_width=True):
                nav_to("qa")
                st.rerun()

    render_tech_annotations(["6维画像自动提取", "RAG本地知识库", "多智能体协同", "防幻觉校验"])


# ========================================================================
# 页面3: 自适应学习路径
# ========================================================================
def render_learning_path_page():
    """自适应学习路径 - 时间线 + 知识图谱"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("learning")

    profile = st.session_state.get("current_profile")
    student_name = getattr(profile, 'name', '同学') if profile else '同学'

    # ── Top Filter Bar ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;padding-bottom:12px;
        border-bottom:1px solid {ColorTokens.CARD_BORDER};">
        <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};">🗺️ 学习路径</div>
        <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-left:auto;">绑定画像: {student_name}</div>
    </div>
    """, unsafe_allow_html=True)

    col_course, col_period, _ = st.columns([2, 1.5, 2])
    with col_course:
        course = st.selectbox("课程", ["计算机网络", "操作系统", "数据结构", "人工智能导论"], key="path_course",
            label_visibility="collapsed")
    with col_period:
        period = st.selectbox("周期", ["7天冲刺", "14天强化", "30天系统"], key="path_period",
            label_visibility="collapsed")

    period_days = {"7天冲刺": 7, "14天强化": 14, "30天系统": 30}[period]

    # ── Profile-linked Summary Banner ──
    weak_str = ""
    if profile:
        weaks = getattr(profile, 'weak_points', [])
        if weaks:
            weak_str = ' · '.join(weaks)
        style = getattr(profile, 'learning_style', '自主学习')
    else:
        weak_str = "待画像采集"
        style = "自主学习"

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{ColorTokens.LIGHT_BLUE},#F9FAFB);border-radius:14px;
        padding:12px 14px;margin-bottom:16px;border:1px solid #BFDBFE;">
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:14px;">🧬</span>
            <div style="font-size:12px;color:{ColorTokens.DARK_GRAY};line-height:1.7;">
                <strong>{course}</strong> · {period} · 
                基于<strong style="color:{ColorTokens.PRIMARY};">{style}</strong>偏好定制 · 
                薄弱项: <strong style="color:{ColorTokens.WARNING_RED};">{weak_str}</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Phase Timeline ──
    phase_days = period_days
    phase1_days = max(phase_days // 3, 2)
    phase2_days = max(phase_days // 3, 2)
    phase3_days = phase_days - phase1_days - phase2_days

    phases = [
        {
            "icon": "🌱", "title": "第一阶段 · 基础夯实",
            "days": phase1_days,
            "label": f"第1-{phase1_days}天",
            "points": ["OSI参考模型", "TCP/IP协议栈", "IP地址与子网划分", "ARP/DHCP基础"],
            "desc": "建立网络体系结构认知，掌握核心协议基础概念",
            "color": ColorTokens.PRIMARY,
        },
        {
            "icon": "🌿", "title": "第二阶段 · 能力进阶",
            "days": phase2_days,
            "label": f"第{phase1_days+1}-{phase1_days+phase2_days}天",
            "points": ["路由算法与协议", "TCP拥塞控制", "HTTP/HTTPS", "DNS/SMTP应用层"],
            "desc": "深入传输层与应用层机制，掌握核心算法原理",
            "color": ColorTokens.AGENT_GREEN,
        },
        {
            "icon": "🌳", "title": "第三阶段 · 实战冲刺",
            "days": phase3_days,
            "label": f"第{phase1_days+phase2_days+1}-{phase_days}天",
            "points": ["Socket编程实战", "网络安全与防火墙", "综合项目演练", "错题回顾与查漏"],
            "desc": "代码实操+项目实战，巩固全链路知识体系",
            "color": "#8B5CF6",
        },
    ]

    for ph in phases:
        st.markdown(f"""
        <div style="display:flex;gap:0;margin-bottom:2px;">
            <!-- Timeline left -->
            <div style="width:44px;display:flex;flex-direction:column;align-items:center;flex-shrink:0;">
                <div style="width:36px;height:36px;border-radius:12px;
                    background:{ph['color']}15;border:2px solid {ph['color']};
                    display:flex;align-items:center;justify-content:center;font-size:16px;z-index:2;">
                    {ph['icon']}
                </div>
                <div style="width:3px;flex:1;min-height:30px;
                    background:{ph['color']}30;"></div>
            </div>
            <!-- Card -->
            <div style="flex:1;margin-left:10px;margin-bottom:12px;
                background:white;border-radius:14px;padding:14px;
                border:1px solid {ColorTokens.CARD_BORDER};border-left:4px solid {ph['color']};">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                    <div>
                        <span style="font-size:14px;">{ph['icon']}</span>
                        <span style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-left:6px;">{ph['title']}</span>
                    </div>
                    <span style="font-size:10px;color:{ph['color']};font-weight:600;
                        background:{ph['color']}10;padding:3px 8px;border-radius:8px;">
                        🕐 {ph['days']}天 · {ph['label']}
                    </span>
                </div>
                <div style="font-size:11px;color:{ColorTokens.MID_GRAY};margin-bottom:8px;">{ph['desc']}</div>
                <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px;">
                    {''.join([f'<span style="padding:3px 8px;background:{ColorTokens.BG_GRAY};border-radius:6px;font-size:10px;color:{ColorTokens.DARK_GRAY};">{p}</span>' for p in ph['points']])}
                </div>
                <div style="display:flex;gap:6px;">
                    <span style="padding:5px 10px;border-radius:8px;font-size:10px;cursor:pointer;
                        border:1px solid {ColorTokens.PRIMARY};color:{ColorTokens.PRIMARY};font-weight:600;
                        background:white;transition:all .2s;"
                        onmouseover="this.style.background='{ColorTokens.LIGHT_BLUE}'"
                        onmouseout="this.style.background='white'">📄 生成讲义</span>
                    <span style="padding:5px 10px;border-radius:8px;font-size:10px;cursor:pointer;
                        border:1px solid {ColorTokens.AGENT_GREEN};color:{ColorTokens.AGENT_GREEN};font-weight:600;
                        background:white;transition:all .2s;"
                        onmouseover="this.style.background='#ECFDF5'"
                        onmouseout="this.style.background='white'">🧠 思维导图</span>
                    <span style="padding:5px 10px;border-radius:8px;font-size:10px;cursor:pointer;
                        border:1px solid #8B5CF6;color:#8B5CF6;font-weight:600;
                        background:white;transition:all .2s;"
                        onmouseover="this.style.background='#F5F3FF'"
                        onmouseout="this.style.background='white'">📝 专项习题</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Knowledge Graph Coverage ──
    all_kg = [
        ("OSI模型", 90), ("TCP/IP", 50), ("HTTP", 70), ("DNS", 65), ("Socket", 55),
        ("UDP", 50), ("IPv4", 80), ("IPv6", 40), ("路由算法", 30), ("子网划分", 60),
        ("拥塞控制", 25), ("VLAN", 45), ("ARP", 75), ("DHCP", 60), ("NAT", 50),
        ("ICMP", 35), ("FTP", 75), ("SMTP", 80), ("SSL/TLS", 45), ("防火墙", 30),
    ]
    covered = {"OSI模型", "TCP/IP", "HTTP", "DNS", "ARP", "DHCP", "IPv4", "IPv6",
               "路由算法", "TCP拥塞控制" if "拥塞控制" in all_kg else "拥塞控制", "Socket",
               "子网划分", "UDP", "NAT", "ICMP", "FTP", "SMTP", "SSL/TLS", "VLAN", "防火墙"}
    kg_cells = ""
    for name, mastery in all_kg:
        is_covered = name in covered or any(c in name for c in covered if c in name)
        if mastery >= 85: bg = "#10B981"
        elif mastery >= 65: bg = "#34D399"
        elif mastery >= 40: bg = "#FBBF24"
        elif mastery >= 20: bg = "#F87171"
        else: bg = "#EF4444"
        border = "2px solid #2563EB" if is_covered else "none"
        kg_cells += f"""<div style="aspect-ratio:1;border-radius:6px;background:{bg};
            cursor:pointer;transition:all .25s;position:relative;
            border:{border};box-sizing:border-box;"
            onmouseover="this.style.transform='scale(1.15)';this.style.zIndex='5'"
            onmouseout="this.style.transform='scale(1)'"
            title="{name} {mastery}% {'✅路线覆盖' if is_covered else ''}">
        </div>"""

    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <span style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};">🧠 知识图谱 · {course}</span>
            <span style="font-size:9px;color:{ColorTokens.LIGHT_GRAY};display:flex;gap:10px;">
                <span>🟢掌握</span><span>🟡一般</span><span>🔴薄弱</span><span style="color:{ColorTokens.PRIMARY};">▣路线覆盖</span>
            </span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:5px;">{kg_cells}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bottom Buttons ──
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("⭐ 收藏此路线", use_container_width=True, type="primary"):
            st.success("路线已收藏！可在「我的中心」查看")
    with col_b:
        if st.button("🔄 重新规划路线", use_container_width=True):
            st.info("正在基于最新画像重新规划...")
            time.sleep(0.8)
            st.rerun()

    render_tech_annotations(["6维画像绑定", "3阶段递进", "知识点覆盖热力", "自适应周期"])


# ========================================================================
# 页面3: 学习资源中心
# ========================================================================
def render_resources_page():
    """移动端资源展示 - 5类卡片 + 知识点溯源"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("resources")

    profile = st.session_state.get("current_profile")
    student_name = getattr(profile, 'name', '同学') if profile else '同学'

    # ── Top Info Bar ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;padding-bottom:10px;
        border-bottom:1px solid {ColorTokens.CARD_BORDER};">
        <div style="flex:1;">
            <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};">� 学习资源</div>
            <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin-top:2px;">
                课程: 计算机网络 · {time.strftime("%Y-%m-%d %H:%M")} · 画像: {student_name}
            </div>
        </div>
        <span style="font-size:10px;color:{ColorTokens.PRIMARY};font-weight:600;
            background:{ColorTokens.LIGHT_BLUE};padding:3px 8px;border-radius:8px;">
            混合式学习
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Resource Cards Grid (5 types) ──
    resources = [
        {
            "icon": "📄", "type": "lecture", "title": "课程讲解文档",
            "desc": "计算机网络核心原理精讲",
            "meta": "15页 · 5个知识模块 · 含代码示例",
            "preview": """### 计算机网络核心原理精讲\n\n#### 第一章：OSI参考模型\n...（课程讲解内容）\n\n**引用来源**: computer_network_ch01.pdf""",
            "citation": "computer_network_ch01.pdf",
            "sim": 0.94,
            "color": ColorTokens.PRIMARY,
        },
        {
            "icon": "🧠", "type": "mindmap", "title": "思维导图结构化文本",
            "desc": "知识体系层级可视化梳理",
            "meta": "5个一级节点 · 23个子节点 · 可展开",
            "preview": """### 计算机网络思维导图\n\n- OSI参考模型\n  - 物理层\n  - 数据链路层\n  - 网络层\n  - 传输层\n  - 会话层\n  - 表示层\n  - 应用层\n\n**引用来源**: computer_network_ch02.pdf""",
            "citation": "computer_network_ch02.pdf",
            "sim": 0.91,
            "color": ColorTokens.AGENT_GREEN,
        },
        {
            "icon": "📝", "type": "exam", "title": "专项练习题（含解析）",
            "desc": "针对薄弱点分层出题",
            "meta": "单选5道 · 简答3道 · 代码2道 · 解析齐全",
            "preview": """### 计算机网络专项练习\n\n**单选题**\n1. TCP三次握手中，第三次握手的ACK标志位携带的序列号是？\n   A. ISN  B. ISN+1  C. 确认号  D. 0\n   **答案**: B  **解析**: ...\n\n**引用来源**: computer_network_ch03.pdf""",
            "citation": "computer_network_ch03.pdf",
            "sim": 0.89,
            "color": "#8B5CF6",
        },
        {
            "icon": "📖", "type": "extend", "title": "拓展阅读资料",
            "desc": "学术论文+深度文档推荐",
            "meta": "RFC 793 · RFC 2616 · 3篇学术推荐",
            "preview": """### 拓展阅读推荐\n\n1. **RFC 793** - Transmission Control Protocol\n2. **RFC 2616** - Hypertext Transfer Protocol\n3. **《计算机网络：自顶向下方法》** 第3章\n\n**引用来源**: extended_reading_index.pdf""",
            "citation": "extended_reading_index.pdf",
            "sim": 0.87,
            "color": "#F59E0B",
        },
        {
            "icon": "💻", "type": "code", "title": "实操案例代码",
            "desc": "Socket编程+协议实现",
            "meta": "Python 3 · 5个示例 · 可运行",
            "preview": """### Socket编程实操案例\n\n```python\n# TCP简单服务器\nimport socket\ns = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\ns.bind(('0.0.0.0', 8080))\ns.listen(5)\nwhile True:\n    conn, addr = s.accept()\n    # ...\n```\n\n**引用来源**: code_examples_ch05.pdf""",
            "citation": "code_examples_ch05.pdf",
            "sim": 0.93,
            "color": ColorTokens.AGENT_GREEN,
        },
    ]

    for res in resources:
        c = res["color"]
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:14px;
            border:1px solid {ColorTokens.CARD_BORDER};border-left:4px solid {c};margin-bottom:12px;
            transition:all .3s;position:relative;">
            <div style="display:flex;align-items:flex-start;gap:10px;">
                <div style="width:42px;height:42px;border-radius:12px;
                    background:{c}15;display:flex;align-items:center;
                    justify-content:center;font-size:20px;flex-shrink:0;">{res['icon']}</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};">{res['title']}</div>
                    <div style="font-size:11px;color:{ColorTokens.MID_GRAY};margin:3px 0;">{res['desc']}</div>
                    <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};">{res['meta']}</div>
                </div>
            </div>
            <div style="display:flex;gap:8px;margin-top:10px;">
                <span style="padding:5px 10px;border-radius:8px;font-size:10px;cursor:pointer;
                    border:1px solid {c};color:{c};font-weight:600;background:white;
                    transition:all .2s;"
                    onmouseover="this.style.background='{c}15'"
                    onmouseout="this.style.background='white'">👁 在线预览</span>
                <span style="padding:5px 10px;border-radius:8px;font-size:10px;cursor:pointer;
                    border:1px solid {ColorTokens.CARD_BORDER};color:{ColorTokens.MID_GRAY};
                    background:white;transition:all .2s;"
                    onmouseover="this.style.background='{ColorTokens.BG_GRAY}'"
                    onmouseout="this.style.background='white'">⬇ 下载</span>
                <span style="padding:5px 10px;border-radius:8px;font-size:10px;cursor:pointer;
                    border:1px solid {ColorTokens.CARD_BORDER};color:{ColorTokens.MID_GRAY};
                    background:white;transition:all .2s;margin-left:auto;"
                    onmouseover="this.style.background='#FEF3C7';this.style.borderColor='#F59E0B';this.style.color='#F59E0B'"
                    onmouseout="this.style.background='white';this.style.borderColor='{ColorTokens.CARD_BORDER}';this.style.color='{ColorTokens.MID_GRAY}'">☆ 收藏</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Preview expander
        with st.expander(f"{res['icon']} 预览: {res['title']}"):
            st.markdown(res["preview"])
            st.markdown(render_rag_citation(res["citation"], resources.index(res), len(resources), res["sim"]), unsafe_allow_html=True)

    # ── Fixed Bottom: Knowledge Source Tracing ──
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};
        margin-top:8px;position:sticky;bottom:0;z-index:5;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
            <span style="font-size:16px;">🔗</span>
            <span style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};">知识点溯源 · 防幻觉验证</span>
            <span style="font-size:10px;color:{ColorTokens.AGENT_GREEN};margin-left:auto;font-weight:600;
                background:#ECFDF5;padding:2px 8px;border-radius:6px;">RAG溯源率 100%</span>
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;">
            <div style="display:flex;align-items:center;gap:8px;padding:6px 10px;
                background:{ColorTokens.BG_GRAY};border-radius:8px;font-size:11px;">
                <span style="color:{ColorTokens.PRIMARY};">📎</span>
                <span style="flex:1;color:{ColorTokens.DARK_GRAY};">computer_network_ch01.pdf</span>
                <span style="color:{ColorTokens.LIGHT_GRAY};">相似度 94%</span>
                <span style="color:{ColorTokens.AGENT_GREEN};">✅ 已验证</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:6px 10px;
                background:{ColorTokens.BG_GRAY};border-radius:8px;font-size:11px;">
                <span style="color:{ColorTokens.PRIMARY};">📎</span>
                <span style="flex:1;color:{ColorTokens.DARK_GRAY};">computer_network_ch02.pdf</span>
                <span style="color:{ColorTokens.LIGHT_GRAY};">相似度 91%</span>
                <span style="color:{ColorTokens.AGENT_GREEN};">✅ 已验证</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:6px 10px;
                background:{ColorTokens.BG_GRAY};border-radius:8px;font-size:11px;">
                <span style="color:{ColorTokens.PRIMARY};">📎</span>
                <span style="flex:1;color:{ColorTokens.DARK_GRAY};">computer_network_ch03.pdf</span>
                <span style="color:{ColorTokens.LIGHT_GRAY};">相似度 89%</span>
                <span style="color:{ColorTokens.AGENT_GREEN};">✅ 已验证</span>
            </div>
        </div>
        <div style="font-size:9px;color:{ColorTokens.LIGHT_GRAY};margin-top:8px;text-align:center;">
            ResourceAgent + QuizAgent 协同生成 · ReviewAgent 完成内容校验 · 杜绝AI幻觉
        </div>
    </div>
    """, unsafe_allow_html=True)

    render_tech_annotations(["RAG溯源防幻觉", "ResourceAgent&QuizAgent协同", "ReviewAgent校验", "5类资源生成"])



# ========================================================================
# 页面3.5: 多智能体协同执行 (纵向时间线)
# ========================================================================
def render_agent_execution_page():
    """多智能体协同执行进度 - 纵向时间线"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("learning")

    # Initialize execution state
    if "execution_step" not in st.session_state:
        st.session_state.execution_step = -1
    if "execution_done" not in st.session_state:
        st.session_state.execution_done = False

    # ── Top Bar ──
    current_agent = ""
    agents_list = ["ProfileAgent", "PlannerAgent", "ResourceAgent", "QuizAgent", "ReviewAgent"]
    if 0 <= st.session_state.execution_step < len(agents_list):
        current_agent = agents_list[st.session_state.execution_step]
    
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;padding-bottom:12px;
        border-bottom:1px solid {ColorTokens.CARD_BORDER};">
        <div style="cursor:pointer;font-size:18px;padding:4px 8px;border-radius:8px;color:{ColorTokens.DARK_GRAY};">←</div>
        <div style="flex:1;">
            <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};">多智能体任务调度</div>
            <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};">
                {'当前执行: <strong style="color:' + ColorTokens.PRIMARY + ';">' + current_agent + '</strong>' if current_agent else '等待启动'}
            </div>
        </div>
        <div style="font-size:11px;color:{ColorTokens.AGENT_GREEN};font-weight:600;
            background:#ECFDF5;padding:4px 10px;border-radius:12px;">
            {st.session_state.execution_step + 1 if st.session_state.execution_step >= 0 else 0}/5
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Agent Timeline ──
    agents = [
        {
            "id": "profile", "icon": "📖", "name": "ProfileAgent", "label": "画像读取智能体",
            "desc": "从数据库加载学生6维画像数据，解析知识薄弱点与学习偏好",
            "output": "已提取画像: 知识基础 75% · 认知风格 60% · 薄弱点 3项 · 日均学习 2h",
            "status_color": ColorTokens.PRIMARY,
        },
        {
            "id": "planner", "icon": "🎯", "name": "PlannerAgent", "label": "任务规划智能体",
            "desc": "根据画像拆解学习任务，制定分层目标和执行顺序",
            "output": "已规划: 3阶段学习路线 · 5个知识模块 · 预计2周完成",
            "status_color": ColorTokens.PRIMARY,
        },
        {
            "id": "resource", "icon": "📝", "name": "ResourceAgent", "label": "资源生成智能体",
            "desc": "基于RAG知识库检索，生成针对性课程讲义与拓展阅读",
            "output": "已生成: 课程讲义 1份 · 拓展阅读 3篇 · RAG引用 12处",
            "status_color": ColorTokens.PRIMARY,
        },
        {
            "id": "quiz", "icon": "📊", "name": "QuizAgent", "label": "习题生成智能体",
            "desc": "针对薄弱知识点生成分层练习题和代码实操案例",
            "output": "已生成: 单选题5道 · 简答题3道 · 代码实操2题 · 难度梯度 3级",
            "status_color": ColorTokens.PRIMARY,
        },
        {
            "id": "review", "icon": "✅", "name": "ReviewAgent", "label": "质量审核智能体",
            "desc": "校验生成内容的事实准确性，检测潜在幻觉风险",
            "output": "审核通过 · 事实准确率 96.7% · 无高危幻觉 · 建议复核 1处",
            "status_color": ColorTokens.AGENT_GREEN,
            "is_review": True,
        },
    ]

    step = st.session_state.execution_step

    for i, agent in enumerate(agents):
        if i < step:
            state = "done"
            state_color = ColorTokens.AGENT_GREEN
            icon_bg = "#ECFDF5"
            icon_text = "✅"
            border_color = ColorTokens.AGENT_GREEN
            bar_style = f"background:{ColorTokens.AGENT_GREEN};"
        elif i == step:
            state = "running"
            state_color = ColorTokens.PRIMARY
            icon_bg = ColorTokens.LIGHT_BLUE
            icon_text = agent["icon"]
            border_color = ColorTokens.PRIMARY
            bar_style = f"background:linear-gradient(180deg,{ColorTokens.AGENT_GREEN} 0%,{ColorTokens.PRIMARY} 60%,{ColorTokens.BG_GRAY} 100%);"
        else:
            state = "pending"
            state_color = ColorTokens.LIGHT_GRAY
            icon_bg = ColorTokens.BG_GRAY
            icon_text = agent["icon"]
            border_color = ColorTokens.CARD_BORDER
            bar_style = f"background:{ColorTokens.BG_GRAY};"

        is_review = agent.get("is_review", False)

        st.markdown(f"""
        <div style="display:flex;gap:0;margin-bottom:2px;">
            <!-- Timeline Left -->
            <div style="width:44px;display:flex;flex-direction:column;align-items:center;flex-shrink:0;">
                <div style="width:36px;height:36px;border-radius:12px;
                    background:{icon_bg};border:2px solid {border_color};
                    display:flex;align-items:center;justify-content:center;
                    font-size:16px;z-index:2;position:relative;
                    {'animation:agentPulse 2s infinite;' if state == 'running' else ''}">
                    {icon_text}
                </div>
                {f'<div style="width:3px;flex:1;min-height:40px;{bar_style}"></div>' if i < len(agents) - 1 else ''}
            </div>
            <!-- Card -->
            <div style="flex:1;margin-left:10px;margin-bottom:{'4px' if i == len(agents)-1 else '0'};">
                <div style="background:white;border-radius:14px;padding:14px;
                    border:1.5px solid {border_color};
                    {'border-color:' + ColorTokens.WARNING_RED + ';border-left:4px solid ' + ColorTokens.WARNING_RED + ';' if is_review and state == 'done' else ''}
                    {'box-shadow:0 0 16px rgba(37,99,235,0.10);' if state == 'running' else ''}
                    opacity:{'1' if state != 'pending' else '0.5'};">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                        <span style="font-size:14px;">{agent['icon']}</span>
                        <span style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};">{agent['name']}</span>
                        <span style="font-size:10px;color:{state_color};margin-left:auto;font-weight:600;
                            background:{icon_bg};padding:2px 8px;border-radius:8px;">
                            {'✅ 完成' if state == 'done' else ('🔄 执行中' if state == 'running' else '⏳ 待执行')}
                        </span>
                    </div>
                    <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:6px;">{agent['label']}</div>
                    <div style="font-size:11px;color:{ColorTokens.MID_GRAY};line-height:1.6;">{agent['desc']}</div>
                    {f'''
                    <div style="margin-top:8px;padding:8px 10px;background:{ColorTokens.BG_GRAY};
                        border-radius:8px;font-size:11px;color:{ColorTokens.DARK_GRAY};
                        border-left:3px solid {state_color};">
                        <strong>📤 输出摘要:</strong> {agent['output']}
                    </div>
                    ''' if state == 'done' else ''}
                    {f'''
                    <div style="margin-top:8px;padding:8px 10px;
                        {('background:#F0FDF4;border:1px solid #A7F3D0;' if state == 'done' else 'background:#FFFBEB;border:1px solid #FCD34D;')}
                        border-radius:8px;font-size:11px;">
                        <strong>{'✅ 质量审核结果' if state == 'done' else '🔍 质量审核中'}</strong>
                        <div style="margin-top:4px;color:{'#065F46' if state == 'done' else '#92400E'};line-height:1.6;">
                            事实准确率 96.7% · 引用来源 12处 · 低风险
                        </div>
                        <div style="margin-top:4px;padding:4px 8px;background:#FFFBEB;border-radius:4px;
                            font-size:10px;color:#92400E;">
                            ⚠️ 幻觉风险提示: 1处低置信度引用建议人工复核 (computer_network_ch02.pdf §3.2)
                        </div>
                    </div>
                    ''' if is_review else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Control / Progress ──
    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.execution_done:
        if st.session_state.execution_step < 0:
            if st.button("🚀 启动多智能体协同执行", use_container_width=True, type="primary"):
                st.session_state.execution_step = 0
                st.rerun()

        elif st.session_state.execution_step < len(agents_list):
            # Auto advance every 1.2s
            import time as _time
            _time.sleep(1.2)
            st.session_state.execution_step += 1
            if st.session_state.execution_step >= len(agents_list):
                st.session_state.execution_done = True
            st.rerun()

    # ── Done Popup ──
    if st.session_state.execution_done:
        st.markdown(f"""
        <div style="position:fixed;top:0;left:0;right:0;bottom:0;
            background:rgba(0,0,0,0.45);z-index:999;display:flex;
            align-items:center;justify-content:center;">
            <div style="background:white;border-radius:16px;padding:28px 24px;
                width:320px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,0.2);
                animation:modalIn .35s ease-out;">
                <div style="font-size:48px;margin-bottom:12px;">🎉</div>
                <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:6px;">
                    多智能体协同完成！
                </div>
                <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:20px;">
                    5个智能体全部执行成功 · 资源包已生成
                </div>
                <div style="display:flex;flex-direction:column;gap:8px;">
                    <div style="font-size:11px;color:{ColorTokens.AGENT_GREEN};">
                        📄 课程讲义 · 🧠 思维导图 · 📝 分层题库
                    </div>
                    <div style="font-size:11px;color:{ColorTokens.AGENT_GREEN};">
                        📖 拓展阅读 · 📊 PPT大纲 · 🗺️ 学习路线
                    </div>
                </div>
            </div>
        </div>
        <style>@keyframes modalIn{{from{{opacity:0;transform:translateY(20px) scale(.95)}}to{{opacity:1;transform:translateY(0) scale(1)}}}}</style>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📦 查看学习资源", use_container_width=True, type="primary"):
                st.session_state.execution_step = -1
                st.session_state.execution_done = False
                nav_to("resources")
                st.rerun()
        with col_b:
            if st.button("🔄 重新执行", use_container_width=True):
                st.session_state.execution_step = -1
                st.session_state.execution_done = False
                st.rerun()

    render_tech_annotations(["5Agent协同编排", "串行时间线", "审核防幻觉", "RAG溯源"])

# ========================================================================
# 页面4: 智能答疑 (知识库溯源防幻觉)
# ========================================================================
def render_qa_page():
    """移动端智能答疑 - 知识库溯源防幻觉"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("qa")

    # ── Top Course Selector ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;padding-bottom:10px;
        border-bottom:1px solid {ColorTokens.CARD_BORDER};">
        <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};">💬 智能答疑</div>
        <div style="margin-left:auto;font-size:10px;color:{ColorTokens.AGENT_GREEN};font-weight:600;
            background:#ECFDF5;padding:3px 8px;border-radius:8px;">
            🔒 知识库溯源
        </div>
    </div>
    """, unsafe_allow_html=True)

    course = st.selectbox("限定检索范围", ["计算机网络", "操作系统", "数据结构", "人工智能导论"],
        key="qa_course_selector", label_visibility="collapsed")

    # ── Knowledge Base Status Banner ──
    kb_stats = {course: {"docs": ["ch01.pdf", "ch02.pdf", "ch03.pdf", "ch04.pdf", "ch05.pdf"], "total": 5, "status": "就绪"}}

    c_stats = kb_stats.get(course, {"docs": [], "total": 0, "status": "待初始化"})

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{ColorTokens.LIGHT_BLUE},#F9FAFB);border-radius:14px;
        padding:10px 14px;margin-bottom:14px;border:1px solid #BFDBFE;">
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:14px;">{'🔒' if c_stats['total'] > 0 else '⚠️'}</span>
            <div style="font-size:11px;color:{ColorTokens.MID_GRAY};line-height:1.6;">
                当前课程: <strong style="color:{ColorTokens.DARK_GRAY};">{course}</strong> ·
                知识库文档 <strong style="color:{ColorTokens.PRIMARY};">{c_stats['total']}</strong> 篇 ·
                {'✅ 仅基于知识库回答，杜绝编造' if c_stats['total'] > 0 else '⚠️ 知识库待初始化'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chat Area ──
    if not st.session_state.qa_history:
        st.session_state.qa_history = [
            {"role": "assistant", "content": f"👋 你好！我是基于RAG知识库的智能答疑助手。\n\n当前检索范围：**【{course}】**\n\n你可以问我任何相关的问题，例如：\n- TCP三次握手的过程是怎样的？\n- OSI七层模型各层功能是什么？\n- HTTP和HTTPS的区别？\n\n💡 我的回答会标注知识库来源，确保准确可靠。\n⚠️ 若知识库无相关内容，我会如实告知，绝不编造。",
             "source": "system", "similarity": 1.0}
        ]

    st.markdown('<div style="min-height:380px;max-height:480px;overflow-y:auto;margin-bottom:12px;">', unsafe_allow_html=True)

    for msg in st.session_state.qa_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:8px;margin:10px 0;justify-content:flex-end;">
                <div style="max-width:78%;background:{ColorTokens.LIGHT_BLUE};
                    padding:10px 14px;border-radius:14px 4px 14px 14px;
                    font-size:13px;line-height:1.6;color:{ColorTokens.DARK_GRAY};">
                    {msg['content']}
                </div>
                <div style="width:30px;height:30px;border-radius:10px;background:{ColorTokens.BG_GRAY};
                    display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0;">🙋</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            is_no_answer = "当前课程知识库资料不足" in msg["content"] or "无法编造答案" in msg["content"]
            card_border = f"border:1px solid {ColorTokens.WARNING_RED};border-left:4px solid {ColorTokens.WARNING_RED};" if is_no_answer else f"border:1px solid {ColorTokens.CARD_BORDER};"
            card_bg = "#FEF2F2" if is_no_answer else "white"

            st.markdown(f"""
            <div style="display:flex;align-items:flex-start;gap:8px;margin:10px 0;">
                <div style="width:30px;height:30px;border-radius:10px;
                    background:linear-gradient(135deg,{ColorTokens.PRIMARY},{ColorTokens.PRIMARY_HOVER});
                    display:flex;align-items:center;justify-content:center;
                    color:white;font-size:13px;flex-shrink:0;">🤖</div>
                <div style="max-width:78%;background:{card_bg};
                    padding:10px 14px;border-radius:4px 14px 14px 14px;
                    font-size:13px;line-height:1.7;color:{ColorTokens.DARK_GRAY};{card_border}">
                    {msg['content']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Citation
            if msg.get("source") and msg["source"] != "system":
                st.markdown(render_rag_citation(
                    msg["source"],
                    st.session_state.qa_history.index(msg),
                    len(st.session_state.qa_history),
                    msg.get("similarity", 0.85),
                ), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Bottom Input Bar ──
    col_i, col_b = st.columns([4, 1])
    with col_i:
        question = st.text_input("", key="qa_input", placeholder="输入你的学习疑问...",
            label_visibility="collapsed")
    with col_b:
        ask_clicked = st.button("发送", key="qa_submit", use_container_width=True)

    # ── Quick Questions ──
    st.markdown('<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">', unsafe_allow_html=True)
    quick_qs = ["TCP三次握手的过程是怎样的？", "OSI七层模型各层功能", "HTTP和HTTPS的区别？", "什么是子网掩码？"]
    for i, qq in enumerate(quick_qs):
        st.markdown(f"""
        <span style="padding:6px 12px;border-radius:18px;border:1px solid {ColorTokens.CARD_BORDER};
            background:white;font-size:10px;color:{ColorTokens.MID_GRAY};cursor:pointer;
            transition:all .2s;white-space:nowrap;"
            onmouseover="this.style.borderColor='{ColorTokens.PRIMARY}';this.style.color='{ColorTokens.PRIMARY}';this.style.background='{ColorTokens.LIGHT_BLUE}'"
            onmouseout="this.style.borderColor='{ColorTokens.CARD_BORDER}';this.style.color='{ColorTokens.MID_GRAY}';this.style.background='white'">{qq[:18]}...</span>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Ask Logic ──
    if ask_clicked and question:
        st.session_state.qa_history.append({"role": "user", "content": question})

        # RAG retrieval simulation with loading
        placeholder = st.empty()
        placeholder.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;padding:10px 14px;
            background:{ColorTokens.LIGHT_BLUE};border-radius:10px;font-size:12px;margin-bottom:10px;">
            <div style="width:16px;height:16px;border:2px solid {ColorTokens.PRIMARY};
                border-top-color:transparent;border-radius:50%;
                animation:spin 0.8s linear infinite;"></div>
            🔍 搜索范围: {course}知识库 · 检索中...
        </div>
        <style>@keyframes spin{{0%{{transform:rotate(0deg)}}100%{{transform:rotate(360deg)}}}}</style>
        """, unsafe_allow_html=True)
        time.sleep(0.8)

        # Simulated RAG check: some questions have answers, some don't
        no_answer_triggers = ["区块链", "量子计算", "深度学习框架", "前端框架", "机器学习算法"]
        is_no_answer = any(trigger in question for trigger in no_answer_triggers)

        if is_no_answer:
            answer = f"## ⚠️ 无法回答\n\n**当前课程《{course}》**知识库中未检索到与该问题相关的内容。\n\n> 📢 当前课程知识库资料不足，无法编造答案\n\n**建议：**\n- 尝试更换为相关课程（如《人工智能导论》）\n- 向教师后台提交知识库补充申请\n- 换一种问法重新提问"
            source_info = {"file": None, "similarity": 0.0}
        else:
            answer, source_info = generate_qa_answer(question, course)

        placeholder.empty()
        time.sleep(0.3)

        msg_entry = {"role": "assistant", "content": answer}
        if source_info.get("file"):
            msg_entry["source"] = source_info["file"]
            msg_entry["similarity"] = source_info["similarity"]
            msg_entry["chunk_idx"] = source_info.get("chunk", 0)
            msg_entry["total_chunks"] = source_info.get("total", 5)
        st.session_state.qa_history.append(msg_entry)

        # Auto-save hint
        st.info("💾 对话记录已自动保存，教师后台可同步查看高频疑问")
        st.rerun()

    # ── Clear ──
    if st.session_state.qa_history:
        if st.button("🗑️ 清空对话记录", key="clear_qa"):
            st.session_state.qa_history = []
            st.rerun()

    render_tech_annotations(["RAG知识库溯源", "拒绝编造·防幻觉", "引用来源标注", "对话自动保存"])


# ========================================================================
# 页面5: 个人学情报告 (数据分析+AI建议)
# ========================================================================
def render_student_report_page():
    """移动端个人学情报告 - 图表+AI建议"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("report")

    profile = st.session_state.get("current_profile")
    student_name = getattr(profile, 'name', '同学') if profile else '同学'

    # ── Top Bar ──
    period = st.selectbox("数据周期", ["📅 日", "📅 周", "📅 月"], key="report_period",
        label_visibility="collapsed")

    period_label = period.split()[-1] if period else "周"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;padding-bottom:10px;
        border-bottom:1px solid {ColorTokens.CARD_BORDER};margin-top:10px;">
        <div style="flex:1;">
            <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};">📊 个人学情报告</div>
            <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};">{student_name} · {period_label}数据 · {time.strftime('%Y-%m-%d')}</div>
        </div>
        <span style="font-size:10px;color:{ColorTokens.AGENT_GREEN};font-weight:600;
            background:#ECFDF5;padding:3px 8px;border-radius:8px;">
            画像已绑定
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Stat Cards Row ──
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:16px;">
    """, unsafe_allow_html=True)
    stats = [
        ("📚", "16", "已学知识点", ColorTokens.PRIMARY),
        ("⏱", "8.5h", "累计学习", ColorTokens.AGENT_GREEN),
        ("📝", "47%", "掌握率", "#F59E0B"),
        ("⚠️", "3", "薄弱项", ColorTokens.WARNING_RED),
    ]
    for icon, val, label, color in stats:
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:12px;border:1px solid {ColorTokens.CARD_BORDER};text-align:center;">
            <span style="font-size:20px;">{icon}</span>
            <div style="font-size:18px;font-weight:800;color:{color};margin:4px 0;">{val}</div>
            <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};">{label}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Chart 1: Ring Chart - Knowledge Mastery ──
    ring_pct = 47
    ring_color = ColorTokens.AGENT_GREEN if ring_pct >= 60 else ("#F59E0B" if ring_pct >= 30 else ColorTokens.WARNING_RED)
    
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:14px;">
        <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">
            🧠 知识点掌握度环形图
        </div>
        <div style="display:flex;align-items:center;justify-content:center;gap:24px;">
            <div style="position:relative;width:100px;height:100px;">
                <svg width="100" height="100" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="44" fill="none" stroke="{ColorTokens.BG_GRAY}" stroke-width="8"/>
                    <circle cx="50" cy="50" r="44" fill="none" stroke="{ring_color}"
                        stroke-width="8" stroke-linecap="round" stroke-dasharray="{ring_pct * 2.76} 276"
                        transform="rotate(-90 50 50)" style="transition:all 1s ease;"/>
                </svg>
                <div style="position:absolute;inset:0;display:flex;flex-direction:column;
                    align-items:center;justify-content:center;">
                    <span style="font-size:22px;font-weight:800;color:{ring_color};">{ring_pct}%</span>
                    <span style="font-size:9px;color:{ColorTokens.LIGHT_GRAY};">掌握率</span>
                </div>
            </div>
            <div style="font-size:11px;color:{ColorTokens.MID_GRAY};line-height:2;">
                <div>✅ 已掌握: <strong style="color:{ColorTokens.AGENT_GREEN};">8 个</strong></div>
                <div>🟡 学习中: <strong style="color:#F59E0B;">5 个</strong></div>
                <div>🔴 薄弱: <strong style="color:{ColorTokens.WARNING_RED};">3 个</strong></div>
                <div>📊 总计: <strong>16 个</strong></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chart 2: Line Chart - Daily Study Time ──
    days = ["周一","周二","周三","周四","周五","周六","周日"]
    hours = [1.2, 0.8, 2.1, 1.5, 0.6, 2.8, 1.9]
    max_h = max(hours)
    points_html = ""
    for i, (d, h) in enumerate(zip(days, hours)):
        bar_h = int(h / max_h * 100)
        color = ColorTokens.AGENT_GREEN if h >= 1.5 else ("#F59E0B" if h >= 0.8 else ColorTokens.WARNING_RED)
        points_html += f"""
        <div style="flex:1;text-align:center;">
            <div style="margin-bottom:4px;font-size:10px;font-weight:700;color:{color};">{h}h</div>
            <div style="height:80px;display:flex;align-items:flex-end;justify-content:center;">
                <div style="width:18px;height:{bar_h}%;background:{color};border-radius:6px 6px 2px 2px;
                    transition:height 0.8s ease;min-height:4px;"></div>
            </div>
            <div style="font-size:9px;color:{ColorTokens.LIGHT_GRAY};margin-top:4px;">{d}</div>
        </div>
        """

    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:14px;">
        <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">
            ⏱ 每日学习时长 · 本周
        </div>
        <div style="display:flex;gap:4px;align-items:flex-end;padding:0 4px;">{points_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chart 3: Bar Chart - TOP5 Weak Points ──
    weak_top5 = [
        ("TCP拥塞控制", 8, ColorTokens.WARNING_RED),
        ("IP路由算法", 6, ColorTokens.WARNING_RED),
        ("网络安全协议", 5, "#F87171"),
        ("子网划分", 3, "#FBBF24"),
        ("IPv6基础", 2, "#FBBF24"),
    ]
    bars_html = ""
    for name, count, color in weak_top5:
        bar_pct = count / 8 * 100
        bars_html += f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span style="width:80px;font-size:10px;color:{ColorTokens.DARK_GRAY};text-align:right;flex-shrink:0;">{name}</span>
            <div style="flex:1;height:18px;background:{ColorTokens.BG_GRAY};border-radius:4px;overflow:hidden;">
                <div style="height:100%;width:{bar_pct}%;background:{color};border-radius:4px;
                    transition:width 0.8s ease;"></div>
            </div>
            <span style="width:28px;font-size:10px;font-weight:700;color:{color};">{count}次</span>
        </div>
        """

    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:14px;">
        <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">
            ⚠️ 高频薄弱知识点 TOP5
        </div>
        {bars_html}
    </div>
    """, unsafe_allow_html=True)

    # ── AI Advice Section ──
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#F0FDF4,#F9FAFB);border-radius:14px;
        padding:14px;margin-bottom:14px;border:1px solid #A7F3D0;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
            <span style="font-size:16px;">🤖</span>
            <span style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};">AI 智能优化建议</span>
            <span style="font-size:9px;color:{ColorTokens.AGENT_GREEN};margin-left:auto;
                background:#ECFDF5;padding:2px 7px;border-radius:6px;">基于画像生成</span>
        </div>
        <div style="font-size:11px;color:{ColorTokens.MID_GRAY};line-height:1.8;">
            1. <strong>TCP拥塞控制</strong>错误率偏高(8次)，建议优先学习
            <span style="color:{ColorTokens.PRIMARY};cursor:pointer;font-weight:600;">📄 TCP协议精讲</span>
            <br>
            2. 周末学习时长最高(2.8h)，建议在周六安排薄弱项专项练习
            <br>
            3. <strong>IP路由算法</strong>为高频错题点，建议观看思维导图梳理知识结构
            <br>
            4. 整体掌握率47%，预计再投入<span style="color:{ColorTokens.PRIMARY};font-weight:600;">12小时</span>可提升至70%
        </div>
        <div style="display:flex;gap:8px;margin-top:12px;">
            <span style="padding:6px 12px;border-radius:8px;font-size:10px;font-weight:600;
                background:{ColorTokens.PRIMARY};color:white;cursor:pointer;">
                📦 一键生成补强资源包
            </span>
            <span style="padding:6px 12px;border-radius:8px;font-size:10px;font-weight:600;
                border:1px solid {ColorTokens.PRIMARY};color:{ColorTokens.PRIMARY};cursor:pointer;">
                🗺️ 更新学习路径
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Agent Schedule Panel (对标教师大屏智能体调度) ──
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:14px;">
        <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:10px;">
            🔄 智能体为我做了什么 · 本月统计
        </div>
        <div style="display:flex;align-items:center;gap:4px;font-size:9px;flex-wrap:wrap;">
    """, unsafe_allow_html=True)
    agent_stats = [
        ("📖 ProfileAgent", "画像刷新", "3次", "#60A5FA"),
        ("🎯 PlannerAgent", "路径规划", "2次", "#34D399"),
        ("📝 ResourceAgent", "生成资源", "12份", "#A78BFA"),
        ("📊 QuizAgent", "出题组卷", "5套", "#FBBF24"),
        ("✅ ReviewAgent", "内容校验", "15次", "#EC4899"),
    ]
    agent_html = ""
    for i, (name, action, count, color) in enumerate(agent_stats):
        agent_html += f"""
        <div style="text-align:center;padding:10px 8px;border-radius:10px;
            background:{color}12;border:1px solid {color}30;min-width:0;flex:1;">
            <div style="font-size:8px;font-weight:700;color:{color};">{name}</div>
            <div style="font-size:16px;font-weight:800;color:{color};margin:4px 0;">{count}</div>
            <div style="font-size:7px;color:{ColorTokens.LIGHT_GRAY};">{action}</div>
        </div>"""
        if i < len(agent_stats) - 1:
            agent_html += f'<span style="color:{ColorTokens.CARD_BORDER};font-size:10px;flex-shrink:0;">→</span>'
    st.markdown(agent_html + "</div>", unsafe_allow_html=True)

    # ── Recent Generation Timeline ──
    st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:6px;margin-top:10px;">
            <div style="display:flex;align-items:center;gap:8px;font-size:10px;
                color:{ColorTokens.MID_GRAY};padding:4px 0;">
                <span style="width:8px;height:8px;border-radius:50%;background:#60A5FA;flex-shrink:0;"></span>
                <span style="flex:1;">06-29 15:30 · ResourceAgent 生成《TCP/IP协议精讲》讲义</span>
                <span style="color:{ColorTokens.AGENT_GREEN};">成功</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:10px;
                color:{ColorTokens.MID_GRAY};padding:4px 0;">
                <span style="width:8px;height:8px;border-radius:50%;background:#FBBF24;flex-shrink:0;"></span>
                <span style="flex:1;">06-29 14:20 · QuizAgent 生成「拥塞控制」专项习题5道</span>
                <span style="color:{ColorTokens.AGENT_GREEN};">成功</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:10px;
                color:{ColorTokens.MID_GRAY};padding:4px 0;">
                <span style="width:8px;height:8px;border-radius:50%;background:#A78BFA;flex-shrink:0;"></span>
                <span style="flex:1;">06-28 09:15 · PlannerAgent 更新学习路径为"3阶段冲刺"</span>
                <span style="color:{ColorTokens.AGENT_GREEN};">成功</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:10px;
                color:{ColorTokens.MID_GRAY};padding:4px 0;">
                <span style="width:8px;height:8px;border-radius:50%;background:#EC4899;flex-shrink:0;"></span>
                <span style="flex:1;">06-27 18:00 · ReviewAgent 校验通过率 98.5% · 无幻觉</span>
                <span style="color:{ColorTokens.AGENT_GREEN};">通过</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Bottom Buttons ──
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📤 导出学情报告", use_container_width=True, type="primary"):
            st.success("📄 学情报告已生成，同步上传至教师管理后台")
    with col_b:
        if st.button("🔄 刷新数据", use_container_width=True):
            st.rerun()

    render_tech_annotations(["多维度数据图表", "智能体调度追踪", "AI智能建议", "画像驱动分析"])


# ========================================================================
# 页面6: 课程库 (知识库加载)
# ========================================================================
def render_courses_page():
    """移动端课程库 - 搜索+筛选+卡片"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("courses")

    # ── Top Bar ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;padding-bottom:10px;
        border-bottom:1px solid {ColorTokens.CARD_BORDER};">
        <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};">📚 课程库</div>
        <span style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin-left:auto;">6门课程</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Search ──
    search = st.text_input("", placeholder="🔍 搜索课程...", key="course_search", label_visibility="collapsed")

    # ── Filter Tags ──
    st.markdown('<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px;">', unsafe_allow_html=True)
    filters = ["全部", "计算机科学", "数学", "人工智能", "编程实战"]
    for f in filters:
        st.markdown(f"""
        <span style="padding:6px 12px;border-radius:16px;border:1px solid {ColorTokens.CARD_BORDER};
            background:white;font-size:10px;color:{ColorTokens.MID_GRAY};cursor:pointer;
            transition:all .2s;"
            onmouseover="this.style.borderColor='{ColorTokens.PRIMARY}';this.style.color='{ColorTokens.PRIMARY}';this.style.background='{ColorTokens.LIGHT_BLUE}'"
            onmouseout="this.style.borderColor='{ColorTokens.CARD_BORDER}';this.style.color='{ColorTokens.MID_GRAY}';this.style.background='white'">{f}</span>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Course Cards ──
    courses = [
        {"icon": "🌐", "name": "计算机网络", "desc": "TCP/IP、OSI模型、路由与交换",
         "total": 24, "progress": 47, "docs": 5, "color": ColorTokens.PRIMARY, "tag": "计算机科学"},
        {"icon": "💻", "name": "操作系统", "desc": "进程管理、内存管理、文件系统",
         "total": 28, "progress": 62, "docs": 6, "color": ColorTokens.AGENT_GREEN, "tag": "计算机科学"},
        {"icon": "🗄️", "name": "数据结构", "desc": "线性表、树、图、排序算法",
         "total": 32, "progress": 35, "docs": 8, "color": "#8B5CF6", "tag": "计算机科学"},
        {"icon": "🧮", "name": "高等数学", "desc": "微积分、线性代数、概率论",
         "total": 40, "progress": 80, "docs": 10, "color": "#F59E0B", "tag": "数学"},
        {"icon": "🤖", "name": "人工智能导论", "desc": "机器学习、深度学习、NLP",
         "total": 20, "progress": 15, "docs": 4, "color": "#EC4899", "tag": "人工智能"},
        {"icon": "🐍", "name": "编程实战", "desc": "Python项目、算法题、系统设计",
         "total": 18, "progress": 55, "docs": 3, "color": ColorTokens.AGENT_GREEN, "tag": "编程实战"},
    ]

    for c in courses:
        progress_color = ColorTokens.AGENT_GREEN if c["progress"] >= 60 else ("#F59E0B" if c["progress"] >= 30 else ColorTokens.WARNING_RED)
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:14px;
            border:1px solid {ColorTokens.CARD_BORDER};border-left:4px solid {c['color']};
            margin-bottom:10px;position:relative;cursor:pointer;transition:all .3s;">
            <div style="position:absolute;top:8px;right:8px;font-size:8px;color:{ColorTokens.LIGHT_GRAY};
                background:{ColorTokens.BG_GRAY};padding:2px 6px;border-radius:4px;">
                RAG向量知识库
            </div>
            <div style="display:flex;align-items:flex-start;gap:10px;">
                <div style="width:44px;height:44px;border-radius:12px;
                    background:{c['color']}15;display:flex;align-items:center;
                    justify-content:center;font-size:22px;flex-shrink:0;">{c['icon']}</div>
                <div style="flex:1;min-width:0;">
                    <div style="font-size:14px;font-weight:700;color:{ColorTokens.DARK_GRAY};">{c['name']}</div>
                    <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin:3px 0;">{c['desc']}</div>
                    <div style="display:flex;align-items:center;gap:10px;margin-top:6px;flex-wrap:wrap;">
                        <span style="font-size:10px;color:{ColorTokens.MID_GRAY};">
                            📚 <strong>{c['total']}</strong> 知识点
                        </span>
                        <span style="font-size:10px;color:{ColorTokens.MID_GRAY};">
                            📄 <strong>{c['docs']}</strong> 篇文档
                        </span>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;margin-top:8px;">
                        <div style="flex:1;height:5px;background:{ColorTokens.BG_GRAY};border-radius:3px;overflow:hidden;">
                            <div style="height:100%;width:{c['progress']}%;background:{progress_color};border-radius:3px;
                                transition:width 0.6s ease;"></div>
                        </div>
                        <span style="font-size:9px;font-weight:700;color:{progress_color};white-space:nowrap;">{c['progress']}%</span>
                    </div>
                </div>
            </div>
            <div style="display:flex;gap:8px;margin-top:10px;">
                <span style="padding:5px 10px;border-radius:8px;font-size:10px;cursor:pointer;
                    background:{c['color']};color:white;font-weight:600;transition:all .2s;">
                    📖 加载知识库
                </span>
                <span style="padding:5px 10px;border-radius:8px;font-size:10px;cursor:pointer;
                    border:1px solid {ColorTokens.CARD_BORDER};color:{ColorTokens.MID_GRAY};
                    background:white;transition:all .2s;"
                    onmouseover="this.style.borderColor='#F59E0B';this.style.color='#F59E0B';this.style.background='#FEF3C7'"
                    onmouseout="this.style.borderColor='{ColorTokens.CARD_BORDER}';this.style.color='{ColorTokens.MID_GRAY}';this.style.background='white'">☆ 收藏</span>
                <span style="font-size:9px;color:{ColorTokens.MID_GRAY};margin-left:auto;display:flex;align-items:center;gap:4px;">
                    {c['tag']}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    render_tech_annotations(["RAG向量知识库", "课程进度追踪", "知识库加载", "多学科覆盖"])


# ========================================================================
# 页面7: 个人中心 (设置+功能闭环)
# ========================================================================
def render_settings_page():
    """移动端个人中心 - 信息/收藏/记录/通知/设置"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("settings")

    profile = st.session_state.get("current_profile")
    student_name = getattr(profile, 'name', '同学') if profile else '同学'
    student_id = getattr(profile, 'student_id', '2024001') if profile else '2024001'

    # ── Profile Header Card ──
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{ColorTokens.PRIMARY},{ColorTokens.PRIMARY_HOVER});
        border-radius:16px;padding:20px;margin-bottom:16px;color:white;">
        <div style="display:flex;align-items:center;gap:14px;">
            <div style="width:56px;height:56px;border-radius:16px;
                background:rgba(255,255,255,0.2);display:flex;align-items:center;
                justify-content:center;font-size:24px;flex-shrink:0;">
                👤
            </div>
            <div style="flex:1;">
                <div style="font-size:18px;font-weight:700;">{student_name}</div>
                <div style="font-size:11px;opacity:0.8;">学号: {student_id}</div>
                <div style="font-size:10px;opacity:0.7;margin-top:4px;">
                    {'画像已完成' if profile else '画像待采集'} · 学习 12 天
                </div>
            </div>
            <span style="font-size:20px;cursor:pointer;">✏️</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Menu Sections ──
    sections = [
        {
            "title": "个人资料",
            "items": [
                {"icon": "👤", "label": "个人信息修改", "desc": "姓名、学号、年级、联系方式", "action": "edit_profile"},
                {"icon": "🔑", "label": "账号安全", "desc": "修改密码、绑定手机", "action": "security"},
            ]
        },
        {
            "title": "学习数据",
            "items": [
                {"icon": "⭐", "label": "我的收藏资源", "desc": f"{6} 个收藏 · 课程讲义、习题等", "action": "favorites"},
                {"icon": "📋", "label": "生成记录", "desc": f"{12} 条 · 最近: 计算机网络讲义", "action": "history"},
                {"icon": "📊", "label": "学情报告存档", "desc": "历史周报/月报 · 3 份", "action": "reports_archive"},
            ]
        },
        {
            "title": "消息",
            "items": [
                {"icon": "🔔", "label": "消息通知", "desc": "3 条未读 · AI建议已更新", "action": "notifications",
                 "badge": True},
            ]
        },
        {
            "title": "系统设置",
            "items": [
                {"icon": "⚙️", "label": "系统参数设置", "desc": "模型切换、语音、缓存管理", "action": "settings_detail"},
            ]
        },
    ]

    for sec in sections:
        st.markdown(f"""
        <div style="font-size:11px;font-weight:700;color:{ColorTokens.LIGHT_GRAY};
            padding:8px 4px 6px;text-transform:uppercase;letter-spacing:0.05em;">
            {sec['title']}
        </div>
        """, unsafe_allow_html=True)
        for item in sec["items"]:
            badge_html = ""
            if item.get("badge"):
                badge_html = f"""<span style="background:{ColorTokens.WARNING_RED};color:white;font-size:9px;
                    padding:1px 6px;border-radius:8px;margin-left:8px;">3</span>"""
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:12px 14px;
                border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:6px;
                display:flex;align-items:center;gap:10px;cursor:pointer;
                transition:all .2s;" 
                onmouseover="this.style.background='{ColorTokens.BG_GRAY}'"
                onmouseout="this.style.background='white'">
                <span style="font-size:18px;">{item['icon']}</span>
                <div style="flex:1;">
                    <div style="font-size:13px;font-weight:600;color:{ColorTokens.DARK_GRAY};display:flex;align-items:center;">
                        {item['label']}{badge_html}
                    </div>
                    <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};">{item['desc']}</div>
                </div>
                <span style="color:{ColorTokens.LIGHT_GRAY};">›</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Settings Detail Panel (expandable) ──
    with st.expander("⚙️ 系统参数设置（展开配置）"):
        st.markdown("#### 🤖 大模型切换")
        model = st.selectbox("讯飞星火模型版本", ["Spark 4.0 Ultra", "Spark 3.0 Max", "Spark Lite"], 
            key="model_switch", label_visibility="collapsed")
        st.caption(f"当前: {model} · 支持多模态生成 · 上下文 128K")

        st.markdown("#### 🔊 语音播报设置")
        voice = st.selectbox("音色", ["温柔女声", "沉稳男声", "清晰童声"], key="voice_tone",
            label_visibility="collapsed")
        speed = st.slider("语速", 0.5, 2.0, 1.0, 0.1, key="voice_speed")
        st.caption(f"音色: {voice} · 语速: {speed}x")

        st.markdown("#### 🗑️ 缓存管理")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            if st.button("🧹 清除知识库缓存", key="clr_kb", use_container_width=True):
                st.success("知识库缓存已清除")
        with col_c2:
            if st.button("🔄 重置画像数据", key="clr_profile", use_container_width=True):
                st.warning("画像数据已重置")
        with col_c3:
            if st.button("📦 清理生成资源", key="clr_res", use_container_width=True):
                st.success("临时资源已清理")

        st.markdown("#### 🔐 其他")
        theme = st.selectbox("界面主题", ["浅色模式", "深色模式", "跟随系统"], key="theme_switch",
            label_visibility="collapsed")

    # ── Logout ──
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 退出登录", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown(f"""
    <div style="text-align:center;margin-top:8px;font-size:10px;color:{ColorTokens.LIGHT_GRAY};">
        AI多智能体个性化学习系统 v1.0 · 基于讯飞星火大模型
    </div>
    """, unsafe_allow_html=True)

    render_tech_annotations(["个人中心闭环", "模型切换", "语音配置", "缓存管理"])


# ========================================================================
# 辅助内容生成函数
# ========================================================================
def generate_lecture_content(topics: List[str]) -> str:
    first_topic = topics[0] if topics else "计算机网络基础"
    return f"""## 📖 {first_topic} 课程讲义

### 核心概念
{first_topic}是计算机网络领域的核心知识点，理解其原理对于掌握整个网络体系至关重要。

### 详细讲解

#### 1. 基础原理
网络通信的根本在于协议栈的分层设计。每一层负责特定的功能：
- **应用层**：提供用户接口和应用服务
- **传输层**：端到端的数据传输控制
- **网络层**：路由选择和数据包转发
- **数据链路层**：相邻节点间的可靠传输

#### 2. 关键协议
- TCP提供可靠的、面向连接的服务
- UDP提供无连接的快速传输
- IP负责寻址和路由

#### 3. 代码示例
```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('example.com', 80))
s.send(b'GET / HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n')
data = s.recv(4096)
print(data.decode())
```

### 📌 学习要点
1. 理解分层架构的设计思想
2. 掌握各层核心协议的功能
3. 能够使用Socket进行网络编程
"""


def generate_exam_content(topics: List[str]) -> str:
    return """## 📝 分层练习题库

### 一、单选题 (5题)

**1. TCP协议工作在OSI模型的哪一层？**
A. 网络层
B. 传输层 ✓
C. 应用层
D. 数据链路层

**2. HTTP默认端口是？**
A. 21  B. 22  C. 80 ✓  D. 443

**3. 以下哪个协议是面向无连接的？**
A. TCP  B. HTTP  C. UDP ✓  D. FTP

**4. IP地址192.168.1.1属于哪类地址？**
A. A类  B. B类  C. C类 ✓  D. D类

**5. DNS协议的主要功能是？**
A. 文件传输  B. 域名解析 ✓  C. 邮件发送  D. 远程登录

### 二、简答题 (3题)

**6. 简述TCP三次握手过程。**
> 第一次：客户端发送SYN=1, seq=x
> 第二次：服务器回复SYN+ACK, seq=y, ack=x+1
> 第三次：客户端发送ACK, seq=x+1, ack=y+1

**7. OSI七层模型从上到下分别是哪些层？**
> 应用层→表示层→会话层→传输层→网络层→数据链路层→物理层

**8. HTTP与HTTPS的主要区别？**
> HTTPS = HTTP + SSL/TLS加密，使用443端口，提供数据加密和身份认证

### 三、代码实操 (2题)

**9. Python TCP服务器示例：**
```python
import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 8888))
server.listen(5)
while True:
    conn, addr = server.accept()
    conn.send(b'Welcome!')
    conn.close()
```

**10. Python UDP客户端示例：**
```python
import socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b'Hello', ('server.com', 9999))
data, addr = client.recvfrom(1024)
```
"""


def generate_plan_content(topics: List[str]) -> str:
    return f"""## 🗺️ 个性化学习路线图

### 📍 第一阶段：基础夯实 (第1-2周)
| 时间 | 学习内容 | 推荐资源 |
|------|---------|---------|
| 周一 | OSI模型概览 | 📄 课程讲义 |
| 周二 | TCP/IP协议栈 | 📄 课程讲义 + 🧠 思维导图 |
| 周三 | 应用层协议 (HTTP/DNS) | 📄 课程讲义 |
| 周四 | 传输层详解 | 📖 拓展阅读 |
| 周五 | 练习题巩固 | 📝 分层题库 |
| 周末 | 周复习 + 代码实操 | 💻 Socket编程练习 |

### 📍 第二阶段：深入突破 (第3-4周)
- 重点突破薄弱点
- 完成代码实操案例
- 期中自我测评

### 📍 第三阶段：综合提升 (第5-6周)
- 项目实战：构建简易HTTP服务器
- 模拟考试
- 查漏补缺

### ⏰ 每日学习节奏
- 🌅 上午 (8:00-11:00)：理论学习
- ☀️ 下午 (14:00-17:00)：实践编码
- 🌙 晚上 (19:00-21:00)：错题复习 + 答疑
"""


def generate_qa_answer(question: str, course: str = "计算机网络"):
    """模拟RAG检索+大模型回答"""
    q_lower = question.lower()

    if "三次握手" in question or "tcp" in question:
        answer = """## TCP三次握手详解

**三次握手（Three-Way Handshake）** 是TCP协议建立连接的过程：

### 过程图解
```
客户端                    服务器
  |───SYN(seq=x)──────────→|
  |                         |
  |←──SYN+ACK(seq=y,ack=x+1)─|
  |                         |
  |───ACK(seq=x+1,ack=y+1)→|
  |                         |
  连接建立 ✅
```

### 详细说明
1. **第一次握手**：客户端发送SYN报文，序列号seq=x，进入SYN_SENT状态
2. **第二次握手**：服务器收到后，回复SYN+ACK报文，seq=y, ack=x+1，进入SYN_RCVD状态
3. **第三次握手**：客户端发送ACK报文，seq=x+1, ack=y+1，双方进入ESTABLISHED状态

### 为什么是三次？
- 防止已失效的连接请求突然传到服务器
- 确保双方收发能力均正常
- 同步双方的初始序列号

> 💡 记忆口诀：客户端"请求"→ 服务器"确认+请求"→ 客户端"确认\""""
        source = {"file": "tcp_ip_protocols.pdf", "chunk": 3, "total": 8, "similarity": 0.94}

    elif "osi" in question or "七层" in question:
        answer = """## OSI七层模型

| 层次 | 名称 | 主要功能 | 典型协议 |
|------|-----|---------|---------|
| 7 | 应用层 | 用户接口 | HTTP, FTP, SMTP |
| 6 | 表示层 | 数据格式转换 | JPEG, ASCII |
| 5 | 会话层 | 会话管理 | NetBIOS |
| 4 | 传输层 | 端到端传输 | TCP, UDP |
| 3 | 网络层 | 路由选择 | IP, ICMP |
| 2 | 数据链路层 | 帧传输 | Ethernet, PPP |
| 1 | 物理层 | 比特流传输 | RS-232 |

**记忆技巧**：All People Seem To Need Data Processing
(Application→Presentation→Session→Transport→Network→Data Link→Physical)"""
        source = {"file": "computer_network_ch01.pdf", "chunk": 1, "total": 10, "similarity": 0.96}

    elif "http" in question or "https" in question:
        answer = """## HTTP vs HTTPS

| 特性 | HTTP | HTTPS |
|------|------|-------|
| 端口 | 80 | 443 |
| 加密 | 无 | SSL/TLS |
| 证书 | 不需要 | 需要CA证书 |
| 安全性 | 低 | 高 |
| 速度 | 较快 | 略慢 |

**HTTPS工作流程**：
1. 客户端请求HTTPS连接
2. 服务器返回SSL证书
3. 客户端验证证书合法性
4. 协商加密算法，生成会话密钥
5. 使用对称加密进行数据传输"""
        source = {"file": "computer_network_ch02.pdf", "chunk": 5, "total": 10, "similarity": 0.91}

    elif "子网" in question:
        answer = """## 子网掩码

**子网掩码**用于划分IP地址的网络部分和主机部分。

### 常见子网掩码
| CIDR | 子网掩码 | 可用IP数 |
|------|---------|---------|
| /24 | 255.255.255.0 | 254 |
| /16 | 255.255.0.0 | 65,534 |
| /8  | 255.0.0.0 | 16,777,214 |

### 示例
IP: 192.168.1.100, 掩码: 255.255.255.0
- 网络地址: 192.168.1.0
- 广播地址: 192.168.1.255
- 可用范围: 192.168.1.1 ~ 192.168.1.254"""
        source = {"file": "computer_network_ch01.pdf", "chunk": 7, "total": 10, "similarity": 0.88}

    else:
        answer = f"""## 关于「{question}」的解答

我已在知识库中检索相关内容。根据RAG检索结果：

该知识点可能涉及的领域包括计算机网络基础理论。如需更详细的解答，建议：

1. 📖 查阅课程讲义中的相关章节
2. 🔍 尝试使用更具体的关键词提问
3. 📚 参考拓展阅读材料中的学术文献

> ⚠️ 知识库中暂未检索到该问题的精确匹配内容，以上回答基于通用知识，建议结合教材进一步验证。"""
        source = {"file": "computer_network_ch01.pdf", "chunk": 0, "total": 10, "similarity": 0.62}

    return answer, source



# 模拟数据
# ========================================================================
MOCK_STUDENTS = [
    {"id": "2024001", "name": "张三", "class": "计科2101", "profile_ready": True, "resources_count": 6, "avg_score": 78, "weak_count": 3, "last_active": "2026-06-29 14:30"},
    {"id": "2024002", "name": "李四", "class": "计科2101", "profile_ready": True, "resources_count": 5, "avg_score": 85, "weak_count": 1, "last_active": "2026-06-29 15:10"},
    {"id": "2024003", "name": "王五", "class": "计科2102", "profile_ready": True, "resources_count": 8, "avg_score": 62, "weak_count": 5, "last_active": "2026-06-29 11:45"},
    {"id": "2024004", "name": "赵六", "class": "计科2102", "profile_ready": False, "resources_count": 0, "avg_score": 0, "weak_count": 0, "last_active": "-"},
    {"id": "2024005", "name": "孙七", "class": "计科2101", "profile_ready": True, "resources_count": 4, "avg_score": 91, "weak_count": 0, "last_active": "2026-06-29 09:20"},
    {"id": "2024006", "name": "周八", "class": "计科2102", "profile_ready": True, "resources_count": 3, "avg_score": 55, "weak_count": 6, "last_active": "2026-06-28 16:50"},
]

MOCK_KB_FILES = [
    {"name": "computer_network_ch01.pdf", "size": "2.3 MB", "chunks": 12, "status": "indexed", "date": "2026-06-20"},
    {"name": "computer_network_ch02.pdf", "size": "1.8 MB", "chunks": 10, "status": "indexed", "date": "2026-06-20"},
    {"name": "tcp_ip_protocols.pdf", "size": "3.1 MB", "chunks": 8, "status": "indexed", "date": "2026-06-21"},
    {"name": "network_security_basics.pdf", "size": "2.7 MB", "chunks": 10, "status": "indexed", "date": "2026-06-22"},
    {"name": "socket_programming_guide.pdf", "size": "1.5 MB", "chunks": 6, "status": "pending", "date": "2026-06-28"},
    {"name": "http_protocol_deep_dive.pdf", "size": "4.2 MB", "chunks": 15, "status": "indexed", "date": "2026-06-23"},
]

MOCK_GENERATION_LOGS = [
    {"time": "2026-06-29 15:30:22", "student": "张三", "type": "lecture", "topic": "TCP/IP协议", "status": "success", "duration": "3.2s", "agent_count": 5},
    {"time": "2026-06-29 15:30:18", "student": "李四", "type": "exam", "topic": "路由算法", "status": "success", "duration": "2.8s", "agent_count": 5},
    {"time": "2026-06-29 15:15:45", "student": "王五", "type": "mindmap", "topic": "OSI模型", "status": "success", "duration": "2.1s", "agent_count": 4},
    {"time": "2026-06-29 15:12:10", "student": "赵六", "type": "lecture", "topic": "HTTP/HTTPS", "status": "failed", "duration": "-", "agent_count": 2},
    {"time": "2026-06-29 14:55:33", "student": "张三", "type": "plan", "topic": "综合学习路线", "status": "success", "duration": "4.5s", "agent_count": 5},
    {"time": "2026-06-29 14:40:01", "student": "孙七", "type": "extend", "topic": "网络安全", "status": "success", "duration": "1.9s", "agent_count": 3},
    {"time": "2026-06-29 14:30:15", "student": "李四", "type": "ppt", "topic": "传输层详解", "status": "success", "duration": "3.7s", "agent_count": 5},
    {"time": "2026-06-29 14:20:50", "student": "周八", "type": "exam", "topic": "IP寻址", "status": "warning", "duration": "5.1s", "agent_count": 5},
    {"time": "2026-06-29 13:45:12", "student": "王五", "type": "lecture", "topic": "子网划分", "status": "success", "duration": "2.4s", "agent_count": 5},
    {"time": "2026-06-29 13:30:00", "student": "张三", "type": "video", "topic": "TCP三次握手动画", "status": "success", "duration": "8.2s", "agent_count": 5},
]


# ========================================================================
# 页面1: 课程知识库批量管理 (重写)
# ========================================================================
def render_kb_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    st.markdown(f"""
    <style>
    .kb-table {{ width:100%;border-collapse:collapse;font-size:13px; }}
    .kb-table th {{ background:{ColorTokens.BG_GRAY};padding:12px 14px;text-align:left;
      font-weight:700;color:{ColorTokens.DARK_GRAY};border-bottom:2px solid {ColorTokens.CARD_BORDER}; }}
    .kb-table td {{ padding:10px 14px;border-bottom:1px solid {ColorTokens.CARD_BORDER};color:{ColorTokens.MID_GRAY}; }}
    .kb-table tr:hover td {{ background:{ColorTokens.LIGHT_BLUE}; }}
    .kb-toolbar {{ display:flex;gap:10px;align-items:center;margin-bottom:16px;flex-wrap:wrap; }}
    .kb-search {{ flex:1;min-width:200px;padding:10px 14px;border-radius:10px;
      border:1.5px solid {ColorTokens.CARD_BORDER};font-size:13px;outline:none; }}
    .kb-search:focus {{ border-color:{ColorTokens.PRIMARY};box-shadow:0 0 0 3px rgba(37,99,235,.08); }}
    .kb-btn {{ padding:9px 16px;border-radius:10px;border:none;font-size:12px;font-weight:600;
      cursor:pointer;font-family:inherit;transition:all .2s;white-space:nowrap; }}
    .kb-btn-pri {{ background:{ColorTokens.PRIMARY};color:white; }}
    .kb-btn-pri:hover {{ background:{ColorTokens.PRIMARY_HOVER};box-shadow:0 4px 12px rgba(37,99,235,.25); }}
    .kb-btn-out {{ border:1.5px solid {ColorTokens.CARD_BORDER};background:white;color:{ColorTokens.MID_GRAY}; }}
    .kb-btn-out:hover {{ border-color:{ColorTokens.PRIMARY};color:{ColorTokens.PRIMARY}; }}
    </style>
    """, unsafe_allow_html=True)

    # ── Top Toolbar ──
    col_t1, col_t2, col_t3, col_t4 = st.columns([1.5, 1, 1, 1.5])
    with col_t1:
        if st.button("📤 批量上传课程文档", use_container_width=True, key="kb_upload"):
            st.session_state.kb_show_upload = True
    with col_t2:
        if st.button("➕ 新增知识点", use_container_width=True, key="kb_add"):
            st.session_state.kb_show_modal = True
    with col_t3:
        if st.button("📦 批量导出知识库", use_container_width=True, key="kb_export"):
            st.success("知识库数据导出中...已生成 kb_export_20260629.json")
    with col_t4:
        search = st.text_input("", placeholder="🔍 关键词检索...", key="kb_search", label_visibility="collapsed")

    # ── Upload Panel ──
    if st.session_state.get("kb_show_upload"):
        with st.expander("📤 批量上传课程文档（展开）", expanded=True):
            uploaded = st.file_uploader("选择PDF文件（支持批量）", type=["pdf"], accept_multiple_files=True, key="kb_uploader")
            if uploaded:
                for f in uploaded:
                    st.markdown(f'📄 {f.name} · {f.size/1024:.1f} KB · 待索引', unsafe_allow_html=True)
            col_up1, col_up2 = st.columns(2)
            with col_up1:
                if st.button("🚀 批量索引到向量库", use_container_width=True):
                    with st.spinner("📚 文档分块 + 向量化写入Chroma..."):
                        time.sleep(1.5)
                    st.success(f"✅ {len(uploaded) if uploaded else 0} 个文档已索引")
            with col_up2:
                if st.button("关闭上传面板", use_container_width=True):
                    st.session_state.kb_show_upload = False
                    st.rerun()

    st.markdown("---")

    # ── Data Table ──
    st.markdown("### 📋 知识库文档列表")
    kb_data = [
        {"name": "计算机网络·核心原理", "subject": "计算机科学", "docs": 5, "chunks": 58, "date": "2026-06-20", "accuracy": "97.2%", "status": "indexed"},
        {"name": "TCP/IP协议详解", "subject": "计算机科学", "docs": 3, "chunks": 32, "date": "2026-06-21", "accuracy": "95.8%", "status": "indexed"},
        {"name": "操作系统原理与实践", "subject": "计算机科学", "docs": 6, "chunks": 67, "date": "2026-06-22", "accuracy": "93.4%", "status": "indexed"},
        {"name": "数据结构与算法", "subject": "计算机科学", "docs": 4, "chunks": 41, "date": "2026-06-23", "accuracy": "94.1%", "status": "indexed"},
        {"name": "人工智能导论", "subject": "人工智能", "docs": 4, "chunks": 28, "date": "2026-06-25", "accuracy": "91.7%", "status": "indexed"},
        {"name": "高等数学·微积分", "subject": "数学", "docs": 5, "chunks": 45, "date": "2026-06-26", "accuracy": "96.5%", "status": "indexed"},
        {"name": "编程实战·Python", "subject": "编程实战", "docs": 3, "chunks": 22, "date": "2026-06-28", "accuracy": "--", "status": "pending"},
    ]

    # Apply search filter
    if search:
        kb_data = [k for k in kb_data if search.lower() in k["name"].lower() or search.lower() in k["subject"].lower()]

    st.markdown(f"""
    <table class="kb-table">
      <tr>
        <th>知识库名称</th>
        <th>所属学科</th>
        <th>文档数</th>
        <th>向量片段</th>
        <th>入库时间</th>
        <th>准确率</th>
        <th>状态</th>
        <th>操作</th>
      </tr>
    """, unsafe_allow_html=True)

    for k in kb_data:
        status_color = ColorTokens.AGENT_GREEN if k["status"] == "indexed" else "#FBBF24"
        status_text = "✅ 已索引" if k["status"] == "indexed" else "⏳ 待索引"
        acc_color = ColorTokens.AGENT_GREEN if k["accuracy"] != "--" and float(k["accuracy"].replace("%", "")) >= 95 else ("#FBBF24" if k["accuracy"] != "--" else ColorTokens.LIGHT_GRAY)
        st.markdown(f"""
        <tr>
          <td><strong>{k["name"]}</strong></td>
          <td><span style="background:{ColorTokens.BG_GRAY};padding:2px 8px;border-radius:4px;font-size:11px;">{k["subject"]}</span></td>
          <td>{k["docs"]} 篇</td>
          <td>{k["chunks"]} 段</td>
          <td>{k["date"]}</td>
          <td><span style="color:{acc_color};font-weight:600;">{k["accuracy"]}</span></td>
          <td><span style="color:{status_color};font-weight:600;">{status_text}</span></td>
          <td>
            <span style="color:{ColorTokens.PRIMARY};cursor:pointer;margin-right:10px;">✏️ 编辑</span>
            <span style="color:{ColorTokens.WARNING_RED};cursor:pointer;">🗑️ 删除</span>
          </td>
        </tr>
        """, unsafe_allow_html=True)

    st.markdown("</table>", unsafe_allow_html=True)

    # ── Add KB Modal ──
    if st.session_state.get("kb_show_modal"):
        with st.expander("➕ 新增知识库（展开表单）", expanded=True):
            st.markdown("""
            <div style="background:#F0FDF4;padding:10px 14px;border-radius:8px;border:1px solid #A7F3D0;
              font-size:11px;color:#065F46;margin-bottom:14px;">
              💡 提示：知识库准确率需达到 <strong>90%</strong> 以上方可作为智能体底层数据源
            </div>
            """, unsafe_allow_html=True)

            kb_name = st.text_input("知识库名称", placeholder="例：计算机网络·核心原理", key="kb_new_name")
            kb_subject = st.selectbox("所属学科", ["计算机科学", "人工智能", "数学", "编程实战", "其他"], key="kb_new_subject")
            kb_desc = st.text_area("知识库描述", placeholder="富文本编辑区：描述本知识库覆盖的知识点范围...", key="kb_new_desc", height=100)

            col_upf1, col_upf2 = st.columns(2)
            with col_upf1:
                st.file_uploader("📷 上传封面图片", type=["png", "jpg"], key="kb_img")
            with col_upf2:
                st.file_uploader("💻 上传代码文件", type=["py", "c", "java", "ipynb"], key="kb_code")

            # Accuracy check
            acc_val = st.select_slider("知识库准确率预估", options=["85%", "90%", "92%", "95%", "97%", "98%", "99%+"], value="92%", key="kb_acc")
            if "90" in acc_val or "85" in acc_val:
                st.warning(f"⚠️ 当前准确率 {acc_val}，建议补充更多文档资料以达到 90% 以上标准，确保AI生成内容质量")
            else:
                st.success(f"✅ 准确率 {acc_val}，达到智能体数据源标准")

            col_sav, col_cancel = st.columns(2)
            with col_sav:
                if st.button("✅ 保存知识库", use_container_width=True):
                    st.success(f"知识库「{kb_name or '未命名'}」创建成功！正在向量化...")
                    time.sleep(1)
                    st.session_state.kb_show_modal = False
                    st.rerun()
            with col_cancel:
                if st.button("❌ 取消", use_container_width=True):
                    st.session_state.kb_show_modal = False
                    st.rerun()

    # ── Side annotations ──
    st.markdown(f"""
    <div style="margin-top:24px;padding:16px;background:{ColorTokens.LIGHT_BLUE};border-radius:12px;
      border-left:4px solid {ColorTokens.PRIMARY};">
      <div style="font-size:12px;color:{ColorTokens.DARK_GRAY};line-height:1.8;">
        <strong>📌 知识库说明</strong><br>
        本知识库为五大智能体（ProfileAgent、PlannerAgent、ResourceAgent、QuizAgent、ReviewAgent）的底层数据支撑，
        所有AI生成内容均基于库内经过向量化索引的资料，实现 <strong style="color:{ColorTokens.PRIMARY};">防幻觉管控</strong><br>
        支持批量导入《人工智能导论》《计算机网络》《数据结构》等测试课程素材 |
        <span style="color:{ColorTokens.LIGHT_GRAY};">已索引文档: {sum(k['docs'] for k in kb_data)} 篇 · 向量片段: {sum(k['chunks'] for k in kb_data)} 段</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    render_tech_annotations(["Chroma向量库", "RAG检索增强", "五大智能体数据支撑", "防幻觉管控", "批量导入导出"])


# ========================================================================
# 页面2: 智能体参数配置 (重写 - 左右分栏)
# ========================================================================
def render_agent_config_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    # ── Page title ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">
      <div>
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};">⚙️ 多智能体全局配置</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">五智能体参数调优 · 协同编排 · 实时同步 · 服务器负载监控</div>
      </div>
      <span style="font-size:11px;color:{ColorTokens.AGENT_GREEN};display:flex;align-items:center;gap:4px;">
        <span style="width:8px;height:8px;border-radius:50%;background:{ColorTokens.AGENT_GREEN};animation:pulse 2s infinite;display:inline-block;"></span>
        系统运行中
      </span>
    </div>
    <style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
    .ag-panel{{background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:12px;}}
    .ag-label{{font-size:12px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:10px;}}
    .ag-slider-label{{font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin-top:4px;}}
    </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.markdown(f"""
        <div class="ag-panel">
          <div class="ag-label">🔄 五智能体实时运行面板</div>
        </div>
        """, unsafe_allow_html=True)

        # Agent visualization cards
        agents_viz = [
            {"id": "profile", "icon": "📖", "name": "ProfileAgent", "role": "画像智能体",
             "queue": 12, "load": 34, "status": True, "desc": "6维画像提取·对话采集"},
            {"id": "planner", "icon": "🎯", "name": "PlannerAgent", "role": "路径规划智能体",
             "queue": 8, "load": 28, "status": True, "desc": "学习路径·阶段拆分"},
            {"id": "resource", "icon": "📝", "name": "ResourceAgent", "role": "资源生成智能体",
             "queue": 23, "load": 67, "status": True, "desc": "讲义生成·多模态"},
            {"id": "quiz", "icon": "📊", "name": "QuizAgent", "role": "习题生成智能体",
             "queue": 15, "load": 45, "status": True, "desc": "分层出题·代码案例"},
            {"id": "review", "icon": "✅", "name": "ReviewAgent", "role": "质量审核智能体",
             "queue": 6, "load": 22, "status": True, "desc": "幻觉检测·内容校验"},
        ]

        for ag in agents_viz:
            load_color = ColorTokens.AGENT_GREEN if ag["load"] < 40 else ("#F59E0B" if ag["load"] < 65 else ColorTokens.WARNING_RED)
            status_dot = "🟢" if ag["status"] else "🔴"
            st.markdown(f"""
            <div class="ag-panel" style="display:flex;align-items:center;gap:12px;padding:12px 14px;">
              <div style="width:40px;height:40px;border-radius:10px;
                background:{ColorTokens.LIGHT_BLUE};display:flex;align-items:center;
                justify-content:center;font-size:18px;flex-shrink:0;">{ag['icon']}</div>
              <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:center;gap:6px;">
                  <span style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};">{ag['name']}</span>
                  <span style="font-size:9px;color:{ColorTokens.LIGHT_GRAY};">{ag['role']}</span>
                  <span style="font-size:9px;margin-left:auto;">{status_dot}</span>
                </div>
                <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};">{ag['desc']}</div>
                <div style="display:flex;align-items:center;gap:10px;margin-top:6px;">
                  <span style="font-size:10px;color:{ColorTokens.MID_GRAY};">📥 队列: <strong>{ag['queue']}</strong></span>
                  <span style="font-size:10px;color:{ColorTokens.MID_GRAY};">⚡ 负载: </span>
                  <div style="flex:1;height:4px;background:{ColorTokens.BG_GRAY};border-radius:2px;overflow:hidden;max-width:80px;">
                    <div style="height:100%;width:{ag['load']}%;background:{load_color};border-radius:2px;"></div>
                  </div>
                  <span style="font-size:9px;font-weight:600;color:{load_color};">{ag['load']}%</span>
                </div>
                <div style="display:flex;gap:6px;margin-top:8px;">
                  <span style="padding:3px 8px;border-radius:6px;background:{ColorTokens.BG_GRAY};
                    font-size:9px;color:{ColorTokens.MID_GRAY};cursor:pointer;">▶ 启动</span>
                  <span style="padding:3px 8px;border-radius:6px;background:#FEF2F2;
                    font-size:9px;color:{ColorTokens.WARNING_RED};cursor:pointer;">⏹ 停止</span>
                  <span style="padding:3px 8px;border-radius:6px;background:{ColorTokens.LIGHT_BLUE};
                    font-size:9px;color:{ColorTokens.PRIMARY};cursor:pointer;">🔄 重置</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Flow chain visualization
        st.markdown(f"""
        <div class="ag-panel">
          <div class="ag-label">🔗 协同流转链路</div>
          <div style="display:flex;align-items:center;justify-content:center;gap:4px;font-size:11px;flex-wrap:wrap;">
            <span style="color:#60A5FA;font-weight:600;">ProfileAgent</span>
            <span style="color:{ColorTokens.LIGHT_GRAY};">→</span>
            <span style="color:#34D399;font-weight:600;">PlannerAgent</span>
            <span style="color:{ColorTokens.LIGHT_GRAY};">→</span>
            <span style="color:#A78BFA;font-weight:600;">ResourceAgent</span>
            <span style="color:{ColorTokens.LIGHT_GRAY};">→</span>
            <span style="color:#FBBF24;font-weight:600;">QuizAgent</span>
            <span style="color:{ColorTokens.LIGHT_GRAY};">→</span>
            <span style="color:#EC4899;font-weight:600;">ReviewAgent</span>
          </div>
          <div style="font-size:9px;color:{ColorTokens.LIGHT_GRAY};text-align:center;margin-top:6px;">
            串行协同 · 最大并发 5 · 全局超时 300s
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Right: Config Forms ──
    with col_right:
        st.markdown(f"""
        <div class="ag-panel">
          <div class="ag-label">🎛️ 参数配置表单</div>
        </div>
        """, unsafe_allow_html=True)

        config_tabs = ["📖 ProfileAgent", "🎯 PlannerAgent", "📝 ResourceAgent", "📊 QuizAgent", "✅ ReviewAgent"]
        tab_labels = [t for t in config_tabs]
        tabs = st.tabs(tab_labels)

        config_data = {
            "profile": {"precision": 0.75, "max_rounds": 6, "style_mode": "混合式学习"},
            "planner": {"path_length": 3, "difficulty": 0.5, "phase_mode": "递进式"},
            "resource": {"length": "中等", "format": "Markdown+PDF", "include_code": True},
            "quiz": {"difficulty": 0.5, "count": 10, "types": "单选+简答+代码"},
            "review": {"hall_check": True, "min_accuracy": 0.90, "auto_reject": True},
        }

        # Tab 1: ProfileAgent
        with tabs[0]:
            st.markdown("**画像读取智能体 · 学生6维画像提取**")
            st.slider("画像提取精度阈值", 0.50, 1.00, config_data["profile"]["precision"], 0.05, key="prof_precision")
            st.slider("最大对话采集轮次", 3, 12, config_data["profile"]["max_rounds"], 1, key="prof_rounds")
            st.selectbox("学习风格识别模式", ["混合式学习", "视觉型", "听觉型", "读写型", "动手实践型"], index=0, key="prof_style")
            st.caption(f"当前: 精度 {config_data['profile']['precision']} · 最大 {config_data['profile']['max_rounds']} 轮")

        # Tab 2: PlannerAgent
        with tabs[1]:
            st.markdown("**路径规划智能体 · 学习路径与阶段拆分**")
            st.slider("学习路径长度(阶段数)", 2, 6, config_data["planner"]["path_length"], 1, key="plan_len")
            st.slider("整体难度调节", 0.1, 1.0, config_data["planner"]["difficulty"], 0.1, key="plan_diff")
            st.selectbox("学习阶段递进模式", ["递进式", "螺旋式", "模块化"], index=0, key="plan_mode")
            val = config_data['planner']['path_length']
            st.caption(f"当前: {val} 阶段 · 难度 {config_data['planner']['difficulty']:.1f}")

        # Tab 3: ResourceAgent
        with tabs[2]:
            st.markdown("**资源生成智能体 · 篇幅与输出控制**")
            st.select_slider("生成资源篇幅", options=["简短(1-2页)", "中等(3-5页)", "详细(6-10页)", "完整(10+页)"], value="中等(3-5页)", key="res_len")
            st.selectbox("输出格式", ["Markdown", "Markdown+PDF", "HTML", "纯文本"], index=1, key="res_format")
            st.checkbox("附带代码实操案例", value=True, key="res_code")
            st.checkbox("附带知识点思维导图", value=True, key="res_mindmap")
            st.caption("生成: 中等篇幅 · Markdown+PDF · 含代码+导图")

        # Tab 4: QuizAgent
        with tabs[3]:
            st.markdown("**习题生成智能体 · 难度与题量控制**")
            st.slider("习题难度级别", 0.1, 1.0, config_data["quiz"]["difficulty"], 0.1, key="quiz_diff")
            st.slider("单次生成题目数量", 5, 50, config_data["quiz"]["count"], 5, key="quiz_count")
            st.multiselect("题目类型", ["选择题", "填空题", "简答题", "代码题", "判断题", "案例分析"], default=["选择题", "简答题", "代码题"], key="quiz_types")
            st.checkbox("附带详细解析与知识点溯源", value=True, key="quiz_explain")
            st.caption(f"难度 {config_data['quiz']['difficulty']:.1f} · {config_data['quiz']['count']} 题 · 含解析")

        # Tab 5: ReviewAgent
        with tabs[4]:
            st.markdown("**质量审核智能体 · 防幻觉严格度**")
            st.toggle("启用幻觉检测", value=True, key="rev_hall")
            st.select_slider("检测严格度", options=["宽松", "标准", "严格", "极严"], value="严格", key="rev_strict")
            st.slider("最低准确率阈值", 0.80, 1.00, config_data["review"]["min_accuracy"], 0.01, key="rev_acc")
            st.checkbox("自动拒绝低质内容(准确率<90%)", value=True, key="rev_auto")
            st.checkbox("生成内容溯源引用(防幻觉)", value=True, key="rev_cite")
            st.caption("严格模式 · 阈值 90% · 自动拒绝 + 溯源引用")

        # ── Save button ──
        st.markdown("---")
        col_save, col_reset = st.columns(2)
        with col_save:
            if st.button("💾 保存全局配置", use_container_width=True, type="primary"):
                with st.spinner("配置同步中..."):
                    time.sleep(1)
                st.success("✅ 全局配置已保存并同步至全体学生移动端智能体！")
                st.info("📱 5 个智能体参数已更新 · 在线学生 2,847 人 · 预计同步完成 < 3s")
        with col_reset:
            if st.button("🔄 恢复默认配置", use_container_width=True):
                st.warning("已恢复默认配置")

    render_tech_annotations(["CrewAI多智能体", "5Agent协同", "参数热同步", "防幻觉配置", "负载监控"])


# ========================================================================
# 页面3: 全班学情统计
# ========================================================================
def render_stats_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    # ── Filters ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
      <div>
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};">📊 班级学情分析</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">多维度学习数据 · 知识图谱 · 薄弱追踪 · 批量管理</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1, 1.5])
    with col_f1:
        st.selectbox("班级", ["计科2101 (35人)", "计科2102 (32人)", "全部班级 (67人)"], key="stats_class")
    with col_f2:
        st.selectbox("学科", ["全部学科", "计算机网络", "操作系统", "数据结构", "高等数学"], key="stats_subject")
    with col_f3:
        st.selectbox("统计周期", ["📅 日", "📅 周", "📅 月"], key="stats_period")
    with col_f4:
        search_student = st.text_input("", placeholder="🔍 搜索学生姓名或学号...", key="stats_search", label_visibility="collapsed")

    # ── KPI Cards ──
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    for col, (label, val, color) in zip([kpi1, kpi2, kpi3, kpi4], [
        ("全班人数", "67", ColorTokens.PRIMARY),
        ("画像覆盖率", "89.5%", ColorTokens.AGENT_GREEN),
        ("平均掌握度", "72.6%", "#F59E0B"),
        ("薄弱知识点(人)", "3.2", ColorTokens.WARNING_RED),
    ]):
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};text-align:center;">
              <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:6px;">{label}</div>
              <div style="font-size:26px;font-weight:800;color:{color};">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Charts Row 1: Heatmap + Trend ──
    col_ht, col_tr = st.columns([1, 1])

    with col_ht:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};">
          <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">🧠 班级整体知识图谱热力图</div>
        """, unsafe_allow_html=True)
        
        # Heatmap grid
        heatmap_data = [
            (8, "OSI参考模型", "#10B981"), (7, "TCP/IP协议", "#10B981"),
            (5, "HTTP/HTTPS", "#F59E0B"), (3, "DNS解析", "#F59E0B"),
            (2, "TCP拥塞控制", "#EF4444"), (4, "IP路由算法", "#EF4444"),
            (6, "子网划分", "#F59E0B"), (9, "UDP协议", "#10B981"),
            (3, "网络安全协议", "#EF4444"), (5, "Socket编程", "#F59E0B"),
            (7, "物理层基础", "#10B981"), (4, "数据链路层", "#F59E0B"),
            (1, "IPv6基础", "#EF4444"), (6, "DHCP协议", "#F59E0B"),
            (8, "应用层协议", "#10B981"), (5, "TCP流量控制", "#F59E0B"),
        ]
        
        # 4x4 grid
        cols = st.columns(4)
        for i, (level, name, color) in enumerate(heatmap_data):
            # level 1-3 red, 4-6 yellow, 7-9 green
            with cols[i % 4]:
                cell_color = "#EF4444" if level <= 3 else ("#F59E0B" if level <= 6 else "#10B981")
                bg_color = cell_color + "20"
                st.markdown(f"""
                <div style="background:{bg_color};border:2px solid {cell_color};border-radius:8px;
                  padding:8px 4px;text-align:center;margin-bottom:6px;cursor:pointer;transition:all .2s;"
                  title="{name}: 掌握等级 {level}/10">
                  <div style="font-size:8px;color:{ColorTokens.LIGHT_GRAY};overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{name[:6]}</div>
                  <div style="font-size:12px;font-weight:800;color:{cell_color};">{level}/10</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<div style='display:flex;gap:12px;margin-top:8px;font-size:10px;color:#6B7280;'><span>🟢 掌握(7-10)</span><span>🟡 一般(4-6)</span><span>🔴 薄弱(1-3)</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_tr:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};">
          <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">📈 学生平均分趋势</div>
        </div>
        """, unsafe_allow_html=True)
        trend_data = {
            "周次": ["W1", "W2", "W3", "W4", "W5", "W6"],
            "平均分": [65, 68, 71, 74, 72, 76],
            "最高分": [92, 90, 94, 95, 93, 97],
            "最低分": [35, 38, 42, 40, 38, 45],
        }
        st.line_chart(trend_data, x="周次", y=["平均分", "最高分", "最低分"],
            color=["#2563EB", "#10B981", "#EF4444"])

    # ── Charts Row 2: Bar Chart + Student List ──
    col_bar, col_list = st.columns([1, 1])

    with col_bar:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};">
          <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">⚠️ 各知识点薄弱人数统计</div>
        </div>
        """, unsafe_allow_html=True)
        bar_data = {
            "知识点": ["TCP拥塞控制", "IP路由算法", "网络安全协议", "子网划分", "IPv6基础", "DNS解析", "HTTP状态码"],
            "薄弱人数": [42, 35, 30, 22, 18, 15, 12],
        }
        st.bar_chart(bar_data, x="知识点", y="薄弱人数", color="#EF4444")

    # ── Student Table + Individual View ──
    with col_list:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};">
          <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">👥 学生列表 · 点击查看画像</div>
        </div>
        """, unsafe_allow_html=True)

        # Apply search
        students = MOCK_STUDENTS[:]
        if search_student:
            students = [s for s in students if search_student.lower() in s["name"].lower() or search_student.lower() in s["id"].lower()]

        if not students:
            st.info("未找到匹配学生")

        for s in students:
            score_color = "#10B981" if s["avg_score"] >= 80 else ("#EF4444" if s["avg_score"] < 60 and s["avg_score"] > 0 else "#F59E0B")
            with st.expander(f"{s['name']} ({s['id']}) · {s['class']} · 平均分 {s['avg_score'] if s['avg_score']>0 else '-'}", expanded=False):
                # 6-dimension profile visualization
                dims = [
                    ("📚 知识基础", 75 if s["profile_ready"] else 0, "#2563EB"),
                    ("🎯 学习目标", 70 if s["profile_ready"] else 0, "#10B981"),
                    ("🧠 认知风格", 60 if s["profile_ready"] else 0, "#8B5CF6"),
                    ("⚠️ 薄弱知识", 25 if s["profile_ready"] else 100, "#EF4444"),
                    ("📖 资源偏好", 55 if s["profile_ready"] else 0, "#F59E0B"),
                    ("⏰ 学习时长", 50 if s["profile_ready"] else 0, "#EC4899"),
                ]
                for dim_name, dim_val, dim_color in dims:
                    bg = dim_color + "18"
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                      <span style="width:80px;font-size:10px;color:{ColorTokens.MID_GRAY};">{dim_name}</span>
                      <div style="flex:1;height:8px;background:{ColorTokens.BG_GRAY};border-radius:4px;overflow:hidden;">
                        <div style="height:100%;width:{dim_val}%;background:{dim_color};border-radius:4px;"></div>
                      </div>
                      <span style="width:30px;font-size:10px;font-weight:600;color:{dim_color};">{dim_val}%</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"**薄弱知识点**: TCP拥塞控制、IP路由算法" if s["weak_count"] > 0 else "**暂无薄弱项**")
                st.markdown(f"**已生成资源**: {s['resources_count']} 个 | **最近活跃**: {s['last_active']}")
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    st.button(f"📄 查看完整报告", key=f"rpt_{s['id']}", use_container_width=True)
                with col_a2:
                    st.button(f"📦 生成个人资源包", key=f"pkg_{s['id']}", use_container_width=True)

    # ── Batch Operations ──
    st.markdown("---")
    st.markdown(f"#### 🛠️ 批量操作")
    col_bt1, col_bt2, col_bt3, col_bt4 = st.columns(4)
    with col_bt1:
        if st.button("📦 一键生成班级补强资源包", use_container_width=True):
            with st.spinner("智能体协同生成中..."):
                time.sleep(1.5)
            st.success("✅ 已生成全班补强资源包！包含TCP拥塞控制专项讲义、IP路由习题集、网络安全思维导图")
    with col_bt2:
        if st.button("📤 批量下发学习任务", use_container_width=True):
            st.success("✅ 已向 67 名学生下发薄弱知识点补强任务")
    with col_bt3:
        if st.button("📥 导出全班学情Excel", use_container_width=True):
            st.success("📥 全班学情报表已导出: class_report_20260629.xlsx")
    with col_bt4:
        if st.button("📋 生成教学建议报告", use_container_width=True):
            st.info("📋 AI教学建议: 班级整体薄弱点为TCP拥塞控制(42人)，建议安排2课时专题讲解")

    render_tech_annotations(["知识图谱热力图", "6维学生画像", "薄弱点追踪", "批量补强", "Excel报表导出"])


# ========================================================================
# 页面4: 资源生成日志
# ========================================================================
def render_logs_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    # ── Title ──
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
      <div>
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};">📋 资源生成记录</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">多智能体执行追踪 · ReviewAgent审核结果 · 知识库溯源 · 批量导出</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ──
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        filter_student = st.text_input("学生账号", placeholder="学号或姓名...", key="log_student")
    with col_f2:
        filter_course = st.selectbox("课程", ["全部课程", "计算机网络", "操作系统", "数据结构", "人工智能导论", "高等数学", "编程实战"], key="log_course")
    with col_f3:
        filter_date = st.date_input("生成时间", value=None, key="log_date")
    with col_f4:
        filter_type = st.selectbox("资源类型", ["全部类型", "课程讲义", "习题题库", "思维导图", "拓展阅读", "PPT大纲", "学习路线", "教学视频"], key="log_type")

    # ── Stats Row ──
    success_count = sum(1 for l in MOCK_GENERATION_LOGS if l["status"] == "success")
    failed_count = sum(1 for l in MOCK_GENERATION_LOGS if l["status"] == "failed")
    warning_count = sum(1 for l in MOCK_GENERATION_LOGS if l["status"] == "warning")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    for col, (label, val, color) in zip([kpi1, kpi2, kpi3, kpi4], [
        ("总生成记录", len(MOCK_GENERATION_LOGS), ColorTokens.PRIMARY),
        ("成功", success_count, ColorTokens.AGENT_GREEN),
        ("异常/失败", failed_count + warning_count, ColorTokens.WARNING_RED),
        ("平均耗时", "3.1s", "#F59E0B"),
    ]):
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};text-align:center;">
              <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:4px;">{label}</div>
              <div style="font-size:24px;font-weight:800;color:{color};">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Data Table ──
    st.markdown(f"""
    <style>
    .logs-table {{ width:100%;border-collapse:collapse;font-size:12px; }}
    .logs-table th {{ background:{ColorTokens.BG_GRAY};padding:11px 12px;text-align:left;
      font-weight:700;color:{ColorTokens.DARK_GRAY};border-bottom:2px solid {ColorTokens.CARD_BORDER}; }}
    .logs-table td {{ padding:9px 12px;border-bottom:1px solid {ColorTokens.CARD_BORDER};color:{ColorTokens.MID_GRAY}; }}
    .logs-table tr:hover td {{ background:{ColorTokens.LIGHT_BLUE}; }}
    .logs-badge {{ padding:2px 7px;border-radius:4px;font-size:10px;font-weight:600; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 📝 生成记录列表")

    # Mock log data with review results
    log_data = [
        {"id": "GEN-0629-001", "student": "张三(2024001)", "agents": "5/5", "type": "课程讲义", "topic": "TCP/IP协议族详解",
         "course": "计算机网络", "duration": "3.2s", "review": "pass", "review_score": "97.2%", "review_note": "引用12处, 无幻觉风险",
         "date": "2026-06-29 15:30"},
        {"id": "GEN-0629-002", "student": "李四(2024002)", "agents": "5/5", "type": "习题题库", "topic": "OSI七层模型习题集",
         "course": "计算机网络", "duration": "2.8s", "review": "pass", "review_score": "95.1%", "review_note": "15题, 分层合理",
         "date": "2026-06-29 15:18"},
        {"id": "GEN-0629-003", "student": "王五(2024003)", "agents": "4/5", "type": "思维导图", "topic": "计算机网络知识体系",
         "course": "计算机网络", "duration": "2.1s", "review": "pass", "review_score": "93.8%", "review_note": "5节点23子节点",
         "date": "2026-06-29 14:55"},
        {"id": "GEN-0629-004", "student": "赵六(2024004)", "agents": "2/5", "type": "课程讲义", "topic": "HTTP/HTTPS协议",
         "course": "计算机网络", "duration": "--", "review": "fail", "review_score": "--", "review_note": "知识库匹配不足, 已终止生成",
         "date": "2026-06-29 14:30"},
        {"id": "GEN-0629-005", "student": "张三(2024001)", "agents": "5/5", "type": "学习路线", "topic": "计算机网络综合学习路线",
         "course": "计算机网络", "duration": "4.5s", "review": "pass", "review_score": "98.1%", "review_note": "3阶段, RAG溯源完整",
         "date": "2026-06-29 13:45"},
        {"id": "GEN-0629-006", "student": "孙七(2024005)", "agents": "3/5", "type": "拓展阅读", "topic": "网络安全前沿技术",
         "course": "计算机网络", "duration": "1.9s", "review": "pass", "review_score": "91.7%", "review_note": "3篇推荐, 部分中风险",
         "date": "2026-06-29 12:10"},
        {"id": "GEN-0629-007", "student": "李四(2024002)", "agents": "5/5", "type": "PPT大纲", "topic": "传输层协议详解",
         "course": "计算机网络", "duration": "3.7s", "review": "pass", "review_score": "96.4%", "review_note": "12页, 图表完整",
         "date": "2026-06-29 11:22"},
        {"id": "GEN-0629-008", "student": "周八(2024006)", "agents": "5/5", "type": "习题题库", "topic": "IP地址与子网划分",
         "course": "计算机网络", "duration": "5.1s", "review": "warn", "review_score": "84.2%", "review_note": "2处引用存疑, 建议复核",
         "date": "2026-06-29 10:05"},
        {"id": "GEN-0629-009", "student": "王五(2024003)", "agents": "5/5", "type": "课程讲义", "topic": "路由算法详解",
         "course": "计算机网络", "duration": "2.4s", "review": "pass", "review_score": "95.9%", "review_note": "8处RAG引用, 全部验证",
         "date": "2026-06-29 08:50"},
        {"id": "GEN-0629-010", "student": "张三(2024001)", "agents": "5/5", "type": "教学视频", "topic": "TCP三次握手动画",
         "course": "计算机网络", "duration": "8.2s", "review": "pass", "review_score": "99.0%", "review_note": "15秒动画, 多模态生成",
         "date": "2026-06-29 08:15"},
    ]

    # Apply filters
    filtered = log_data[:]
    if filter_student:
        filtered = [l for l in filtered if filter_student.lower() in l["student"].lower()]
    if filter_course != "全部课程":
        filtered = [l for l in filtered if l["course"] == filter_course]
    if filter_type != "全部类型":
        filtered = [l for l in filtered if l["type"] == filter_type]

    st.markdown(f"""
    <table class="logs-table">
      <tr>
        <th>生成ID</th><th>学生</th><th>智能体组</th><th>资源类型</th>
        <th>知识点</th><th>耗时</th><th>ReviewAgent审核</th><th>操作</th>
      </tr>
    """, unsafe_allow_html=True)

    for log in filtered:
        if log["review"] == "pass":
            review_color = ColorTokens.AGENT_GREEN
            review_badge = "✅ 通过"
        elif log["review"] == "warn":
            review_color = "#F59E0B"
            review_badge = "⚠️ 警告"
        else:
            review_color = ColorTokens.WARNING_RED
            review_badge = "❌ 未通过"

        st.markdown(f"""
        <tr>
          <td style="font-size:10px;font-family:monospace;">{log['id']}</td>
          <td>{log['student']}</td>
          <td><span style="font-weight:600;">{log['agents']}</span> Agent</td>
          <td><span class="logs-badge" style="background:{ColorTokens.LIGHT_BLUE};color:{ColorTokens.PRIMARY};">{log['type']}</span></td>
          <td>{log['topic']}</td>
          <td>{log['duration']}</td>
          <td>
            <span style="color:{review_color};font-weight:600;">{review_badge}</span>
            <div style="font-size:9px;color:{ColorTokens.LIGHT_GRAY};">{log['review_score']}</div>
          </td>
          <td><span style="color:{ColorTokens.PRIMARY};cursor:pointer;font-weight:600;">📋 详情</span></td>
        </tr>
        """, unsafe_allow_html=True)

    st.markdown("</table>", unsafe_allow_html=True)

    # ── Detail Modal (expandable) ──
    with st.expander("📋 查看最近一条生成记录详情", expanded=False):
        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            st.markdown("**📦 生成资源包内容**")
            st.markdown("""
            - 📄 课程讲解文档: TCP/IP协议族详解 (15页)
            - 🧠 思维导图: 计算机网络知识体系 (5节点)
            - 📝 专项练习题: 10题 (单选5 + 简答3 + 代码2)
            - 📖 拓展阅读: RFC 793 (TCP规范) + 3篇论文推荐
            - 💻 代码案例: Python Socket编程示例
            - 🗺️ 学习路径: 3阶段14天递进计划
            """)
        with col_d2:
            st.markdown("**🔗 知识库引用溯源记录**")
            st.markdown(f"""
            <div style="font-size:11px;line-height:1.8;">
              📎 computer_network_ch01.pdf · 94.3% ✅<br>
              📎 computer_network_ch02.pdf · 91.7% ✅<br>
              📎 tcp_ip_protocols.pdf · 89.2% ✅<br>
              📎 network_security_basics.pdf · 87.5% ✅
            </div>
            <div style="margin-top:8px;font-size:9px;color:{ColorTokens.AGENT_GREEN};">
              ✅ ReviewAgent审核通过 · 准确率 97.2% · 引用12处 · 0处幻觉
            </div>
            """, unsafe_allow_html=True)

    # ── Batch Export ──
    st.markdown("---")
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        if st.button("📥 批量导出全部生成日志 (JSON)", use_container_width=True):
            st.success("📥 日志已导出: generation_logs_20260629.json · 含审核结果+溯源引用")
    with col_exp2:
        if st.button("📊 导出为Excel报表", use_container_width=True):
            st.success("📊 Excel报表已导出: generation_report_20260629.xlsx · 含图表统计")

    render_tech_annotations(["多智能体执行追踪", "ReviewAgent审核", "RAG溯源", "批量导出", "答辩数据"])


# ========================================================================
# 页面6: 系统参数设置
# ========================================================================
def render_system_settings_page():
    """系统设置 - API配置、定时任务、权限、日志、缓存"""
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
      <div>
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};">🔧 系统参数设置</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">大模型API配置 · 知识库维护 · 权限管理 · 缓存清理</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Section 1: Model Switch ──
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:14px;">
      <div style="font-size:14px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">
        🤖 大模型运行模式
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_sw1, col_sw2 = st.columns(2)
    with col_sw1:
        use_mock = st.toggle("使用 Mock 模型 (演示模式)", value=True, key="sys_use_mock",
            help="开启后使用模拟数据，无需真实API Key；关闭后接入讯飞星火真实大模型")
        if use_mock:
            st.success("🎭 当前: Mock 演示模式 · 适用开发调试、答辩演示")
        else:
            st.warning("⚠️ 当前: 真实模型模式 · 需确保API Key有效且余额充足")
    with col_sw2:
        st.info("💡 Mock模式下不消耗API调用额度，所有智能体输出为预置示例数据，适合项目初期演示与测试。完成验证后可切换至真实大模型模式。")

    st.markdown("---")

    # ── Section 2: API Config ──
    st.markdown(f"#### 🗝️ 大模型API接口配置")
    if use_mock:
        st.info("🎭 Mock 模式下API配置项已隐藏，切换至真实模型模式后显示")
    else:
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            st.text_input("讯飞星火 API Key", value="●●●●●●●●●●●●●●●●", type="password", key="sys_api_key")
            st.text_input("API Secret", value="●●●●●●●●●●●●●●●●", type="password", key="sys_api_secret")
        with col_api2:
            st.selectbox("模型版本", ["Spark 4.0 Ultra", "Spark 3.0 Max", "Spark Lite"], key="sys_model_ver")
            st.text_input("API 接口地址", value="https://spark-api-open.xf-yun.com/v1", key="sys_api_url")
        st.button("🔗 测试API连接", key="sys_test_api")

    # ── Section 3: KB Update Schedule ──
    st.markdown(f"#### 📚 知识库更新定时任务")
    col_kb1, col_kb2, col_kb3 = st.columns(3)
    with col_kb1:
        st.selectbox("更新频率", ["每天 02:00", "每天 06:00", "每周一 03:00", "手动触发"], index=0, key="sys_kb_freq")
    with col_kb2:
        st.selectbox("更新范围", ["全部知识库", "仅新增文档", "仅变更文档"], index=0, key="sys_kb_scope")
    with col_kb3:
        if st.button("🔄 立即执行更新", use_container_width=True):
            with st.spinner("正在重建向量索引..."):
                time.sleep(1.5)
            st.success("✅ 知识库索引已更新 · 7个知识库 · 293个向量片段")

    st.caption("上次更新: 2026-06-29 02:00 · 耗时 12.3s · 293片段 · 状态: 成功")

    # ── Section 4: Response Latency ──
    st.markdown(f"#### ⚡ 问答响应延迟阈值")
    col_lat1, col_lat2 = st.columns(2)
    with col_lat1:
        st.slider("智能答疑超时时间 (秒)", 5, 60, 15, 5, key="sys_latency_qa")
        st.caption("超过阈值自动降级为简化回答")
    with col_lat2:
        st.slider("资源生成超时时间 (秒)", 30, 300, 120, 10, key="sys_latency_gen")
        st.caption("超过阈值返回部分完成结果并通知")

    # ── Section 5: Admin Users ──
    st.markdown(f"#### 👥 账号权限管理")
    st.markdown(f"""
    <style>
    .perm-table {{ width:100%;border-collapse:collapse;font-size:12px; }}
    .perm-table th {{ background:{ColorTokens.BG_GRAY};padding:10px 12px;text-align:left;
      font-weight:700;color:{ColorTokens.DARK_GRAY};border-bottom:2px solid {ColorTokens.CARD_BORDER}; }}
    .perm-table td {{ padding:8px 12px;border-bottom:1px solid {ColorTokens.CARD_BORDER};color:{ColorTokens.MID_GRAY}; }}
    </style>
    """, unsafe_allow_html=True)

    perm_data = [
        {"account": "zhang_prof", "name": "张教授", "role": "授课教师", "status": "正常", "last_login": "2026-06-29 14:30"},
        {"account": "admin", "name": "系统管理员", "role": "系统管理员", "status": "正常", "last_login": "2026-06-29 15:10"},
        {"account": "li_teacher", "name": "李老师", "role": "授课教师", "status": "正常", "last_login": "2026-06-28 09:45"},
        {"account": "wang_assist", "name": "王助教", "role": "助教", "status": "已禁用", "last_login": "2026-06-20 11:00"},
    ]

    st.markdown("""
    <table class="perm-table">
      <tr><th>账号</th><th>姓名</th><th>角色</th><th>状态</th><th>最后登录</th><th>操作</th></tr>
    """, unsafe_allow_html=True)
    for p in perm_data:
        status_color = ColorTokens.AGENT_GREEN if p["status"] == "正常" else ColorTokens.WARNING_RED
        st.markdown(f"""
        <tr>
          <td style="font-family:monospace;">{p['account']}</td>
          <td>{p['name']}</td>
          <td><span style="background:{ColorTokens.BG_GRAY};padding:2px 8px;border-radius:4px;font-size:10px;">{p['role']}</span></td>
          <td><span style="color:{status_color};font-weight:600;">● {p['status']}</span></td>
          <td style="font-size:10px;">{p['last_login']}</td>
          <td>
            <span style="color:{ColorTokens.PRIMARY};cursor:pointer;margin-right:8px;">✏️</span>
            <span style="color:{ColorTokens.WARNING_RED};cursor:pointer;">🗑️</span>
          </td>
        </tr>
        """, unsafe_allow_html=True)
    st.markdown("</table>", unsafe_allow_html=True)

    col_perm1, col_perm2 = st.columns(2)
    with col_perm1:
        if st.button("➕ 新增管理员账号", use_container_width=True):
            st.success("账号创建成功！")
    with col_perm2:
        if st.button("📋 查看操作日志", use_container_width=True):
            st.info("显示最近100条操作日志...")

    # ── Section 6: Cache ──
    st.markdown(f"#### 🗑️ 缓存与数据清理")
    col_cache1, col_cache2, col_cache3, col_cache4 = st.columns(4)
    with col_cache1:
        if st.button("🧹 清除知识库缓存", use_container_width=True):
            st.success("Chroma向量缓存已清除")
    with col_cache2:
        if st.button("🔄 重置智能体状态", use_container_width=True):
            st.success("5个智能体已恢复初始状态")
    with col_cache3:
        if st.button("📦 清理临时资源文件", use_container_width=True):
            st.success("临时文件已清理，释放 128MB")
    with col_cache4:
        if st.button("🗄️ 优化数据库", use_container_width=True):
            st.success("SQLite数据库已VACUUM优化")

    # ── Save All ──
    st.markdown("---")
    if st.button("💾 保存全部系统配置", type="primary", use_container_width=True):
        with st.spinner("配置同步中..."):
            time.sleep(1)
        st.success("✅ 系统配置已保存 · 知识库更新任务已设定 · 权限已同步")

    render_tech_annotations(["Mock/真实双模式", "API配置", "定时任务", "权限管理", "缓存优化"])


# ========================================================================
# 页面5: 学习效果分析报表
# ========================================================================
def render_teacher_report_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_teacher_sidebar("report")
    render_section_header("📈 学习效果分析报表", "多维度评估 · 趋势分析 · AI建议", "📈")

    # 报表周期选择
    col_r1, col_r2 = st.columns([2, 3])
    with col_r1:
        period = st.selectbox("分析周期", ["本周", "本月", "本学期", "自定义"], key="report_period_sel")

    st.markdown("---")

    # 核心指标
    st.markdown("### 🎯 核心教学指标")
    render_stat_grid([
        {"value": "76.2", "label": "📊 班级均分"},
        {"value": "+8.3%", "label": "📈 环比提升"},
        {"value": "3.2", "label": "⚠️ 人均薄弱点"},
        {"value": "89%", "label": "🎯 目标达成率"},
    ])

    st.markdown("---")

    col_rep1, col_rep2 = st.columns(2)

    with col_rep1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 每周学习趋势</div>', unsafe_allow_html=True)
        weeks = ["W1", "W2", "W3", "W4"]
        scores = [68, 72, 75, 78]
        for i, (w, s) in enumerate(zip(weeks, scores)):
            st.markdown(f'''
                <div style="display:flex;align-items:center;gap:10px;margin:8px 0;">
                    <span style="font-size:12px;width:30px;">{w}</span>
                    <div style="flex:1;height:24px;background:{ColorTokens.BG_GRAY};border-radius:4px;overflow:hidden;position:relative;">
                        <div style="height:100%;width:{s}%;background:linear-gradient(90deg,{ColorTokens.PRIMARY},{ColorTokens.AGENT_GREEN});border-radius:4px;"></div>
                        <span style="position:absolute;right:8px;top:4px;font-size:11px;color:white;font-weight:600;">{s}分</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:11px;color:{ColorTokens.AGENT_GREEN};text-align:right;">📈 趋势上升 +10分</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_rep2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🧠 认知维度雷达数据</div>', unsafe_allow_html=True)
        dims = [
            ("知识理解", 78, ColorTokens.PRIMARY),
            ("实践能力", 65, ColorTokens.AGENT_GREEN),
            ("分析能力", 72, "#FBBF24"),
            ("创新能力", 55, ColorTokens.WARNING_RED),
            ("协作能力", 80, "#8B5CF6"),
        ]
        for name, val, color in dims:
            st.markdown(f'''
                <div style="display:flex;align-items:center;gap:10px;margin:8px 0;">
                    <span style="font-size:12px;width:70px;">{name}</span>
                    <div style="flex:1;height:6px;background:{ColorTokens.BG_GRAY};border-radius:3px;">
                        <div style="height:100%;width:{val}%;background:{color};border-radius:3px;"></div>
                    </div>
                    <span style="font-size:11px;">{val}</span>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # AI教学建议
    st.markdown("### 🤖 AI教学建议")
    col_ai1, col_ai2, col_ai3 = st.columns(3)
    with col_ai1:
        st.markdown(f'''
            <div class="ds-card ds-card-red">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:20px;">⚠️</span>
                    <strong style="color:{ColorTokens.WARNING_RED};">重点关注的薄弱点</strong>
                </div>
                <ul style="font-size:13px;margin-top:8px;padding-left:20px;color:{ColorTokens.MID_GRAY};">
                    <li>TCP拥塞控制 (4人薄弱)</li>
                    <li>IP路由算法 (3人薄弱)</li>
                    <li>建议增加专题讲解</li>
                </ul>
            </div>
        ''', unsafe_allow_html=True)
    with col_ai2:
        st.markdown(f'''
            <div class="ds-card ds-card-green">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:20px;">✅</span>
                    <strong style="color:{ColorTokens.AGENT_GREEN};">教学优势区</strong>
                </div>
                <ul style="font-size:13px;margin-top:8px;padding-left:20px;color:{ColorTokens.MID_GRAY};">
                    <li>OSI模型掌握良好</li>
                    <li>Socket编程能力提升</li>
                    <li>实践环节效果显著</li>
                </ul>
            </div>
        ''', unsafe_allow_html=True)
    with col_ai3:
        st.markdown(f'''
            <div class="ds-card ds-card-blue">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="font-size:20px;">💡</span>
                    <strong style="color:{ColorTokens.PRIMARY};">行动建议</strong>
                </div>
                <ul style="font-size:13px;margin-top:8px;padding-left:20px;color:{ColorTokens.MID_GRAY};">
                    <li>增加小组讨论环节</li>
                    <li>引入更多工程案例</li>
                    <li>每周一次模拟测试</li>
                </ul>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("---")

    # 学生个体报表
    st.markdown("### 👤 学生个体报表")
    selected = st.selectbox("选择学生", [s["name"] for s in MOCK_STUDENTS])

    student = next((s for s in MOCK_STUDENTS if s["name"] == selected), None)
    if student:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown(f'''
                <div class="ds-card">
                    <h4>📊 {student["name"]} 学习概览</h4>
                    <table style="width:100%;font-size:13px;">
                        <tr><td style="padding:6px 0;color:{ColorTokens.MID_GRAY};">学号</td><td>{student["id"]}</td></tr>
                        <tr><td style="padding:6px 0;color:{ColorTokens.MID_GRAY};">班级</td><td>{student["class"]}</td></tr>
                        <tr><td style="padding:6px 0;color:{ColorTokens.MID_GRAY};">画像状态</td><td>{"✅ 已生成" if student["profile_ready"] else "⏳ 未生成"}</td></tr>
                        <tr><td style="padding:6px 0;color:{ColorTokens.MID_GRAY};">生成资源</td><td>{student["resources_count"]} 个</td></tr>
                        <tr><td style="padding:6px 0;color:{ColorTokens.MID_GRAY};">平均成绩</td><td style="font-weight:700;color:{ColorTokens.AGENT_GREEN if student['avg_score'] >= 80 else ColorTokens.WARNING_RED};">{student["avg_score"] if student["avg_score"] > 0 else "未测评"}</td></tr>
                        <tr><td style="padding:6px 0;color:{ColorTokens.MID_GRAY};">薄弱点数</td><td style="color:{ColorTokens.WARNING_RED};">{student["weak_count"]}</td></tr>
                    </table>
                </div>
            ''', unsafe_allow_html=True)
        with col_s2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">📈 学习进度</div>', unsafe_allow_html=True)
            render_progress_with_label(85 if student["resources_count"] > 0 else 0, "课程完成度")
            render_progress_with_label(student["avg_score"], "知识掌握度")
            render_progress_with_label(max(0, 100 - student["weak_count"] * 15), "学习健康度")
            st.markdown('</div>', unsafe_allow_html=True)

    render_tech_annotations(["多维度评估", "AI建议", "趋势分析", "个性化报告"])


# ========================================================================
# 管理后台数据大屏
# ========================================================================
def render_dashboard_page():
    """暗色数据大屏 - KPI+图表+实时面板"""
    # Dark theme override - scoped for this page only
    st.markdown("""
    <style>
    /* Dashboard dark styles - scoped */
    .dash-dark .main { background:#0B1120 !important; }
    .dash-dark .stApp { background:#0B1120; }
    .kpi-dark-card {
      background:linear-gradient(135deg,#111C2E,#162240) !important;
      border:1px solid #1E293B !important;border-radius:14px !important;
      padding:20px !important;position:relative;overflow:hidden;
    }
    /* Restore sidebar when on dashboard */
    section[data-testid="stSidebar"] { display: block !important; }
    section[data-testid="stSidebar"] > div { background:#0F172A; }
    </style>
    <div class="dash-dark">
    """, unsafe_allow_html=True)

    # ── KPI Row ──
    col1, col2, col3, col4 = st.columns(4)
    kpis = [
        ("在线学生总数", "2,847", "▲ 12.5% 较上月", "#60A5FA", "#34D399"),
        ("今日资源生成总量", "1,294", "▲ 8.3% 较昨日", "#34D399", "#34D399"),
        ("智能体调度总次数", "6,472", "▲ 15.2% 较上周", "#A78BFA", "#34D399"),
        ("全班平均掌握度", "72.6%", "▲ 3.1% 较上月", "#FBBF24", "#34D399"),
    ]
    for i, (col, (label, val, change, val_color, chg_color)) in enumerate(zip([col1, col2, col3, col4], kpis)):
        with col:
            st.markdown(f"""
            <div class="kpi-dark-card">
              <div style="font-size:11px;color:#64748B;margin-bottom:8px;">{label}</div>
              <div style="font-size:32px;font-weight:800;color:{val_color};">{val}</div>
              <div style="font-size:11px;color:{chg_color};margin-top:6px;">{change}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Charts Row ──
    col_chart1, col_chart2 = st.columns([1.4, 1])
    with col_chart1:
        st.markdown(f"""
        <div class="kpi-dark-card">
          <div style="font-size:13px;font-weight:700;color:#E2E8F0;margin-bottom:14px;">📈 班级整体学情趋势</div>
          <div style="display:flex;gap:14px;margin-bottom:12px;">
            <span style="font-size:10px;color:#94A3B8;"><span style="color:#60A5FA;">●</span> 掌握率</span>
            <span style="font-size:10px;color:#94A3B8;"><span style="color:#34D399;">●</span> 活跃学生</span>
            <span style="font-size:10px;color:#94A3B8;"><span style="color:#A78BFA;">●</span> 资源生成</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        chart_data = {
            "日期": ["06-23", "06-24", "06-25", "06-26", "06-27", "06-28", "06-29"],
            "掌握率(%)": [58, 63, 68, 72, 74, 78, 82],
            "活跃学生(百人)": [18, 20, 23, 25, 27, 29, 31],
            "资源生成(百个)": [8, 9, 11, 13, 14, 15, 17],
        }
        st.line_chart(chart_data, x="日期", y=["掌握率(%)", "活跃学生(百人)", "资源生成(百个)"],
            color=["#60A5FA", "#34D399", "#A78BFA"])

    with col_chart2:
        st.markdown(f"""
        <div class="kpi-dark-card">
          <div style="font-size:13px;font-weight:700;color:#E2E8F0;margin-bottom:14px;">📊 多模态资源生成类型占比</div>
        </div>
        """, unsafe_allow_html=True)
        pie_data = {
            "类型": ["课程讲义", "习题题库", "思维导图", "拓展阅读", "教学视频"],
            "数量": [452, 258, 220, 168, 196],
        }
        st.bar_chart(pie_data, x="类型", y="数量",
            color=["#60A5FA", "#34D399", "#A78BFA", "#FBBF24", "#EC4899"])

    # ── Bottom Row: Agent Flow + Right Panel ──
    col_flow, col_right = st.columns([1.6, 1])

    with col_flow:
        st.markdown(f"""
        <div class="kpi-dark-card" style="margin-bottom:0;">
          <div style="font-size:13px;font-weight:700;color:#E2E8F0;margin-bottom:14px;">🔄 多智能体协同调度实时流水</div>
          <div style="display:flex;align-items:center;gap:6px;font-size:11px;flex-wrap:wrap;">
        """, unsafe_allow_html=True)
        agents_flow = [
            ("📖 ProfileAgent", "15,230次", "#60A5FA"),
            ("🎯 PlannerAgent", "12,450次", "#34D399"),
            ("📝 ResourceAgent", "18,920次", "#A78BFA"),
            ("📊 QuizAgent", "9,870次", "#FBBF24"),
            ("✅ ReviewAgent", "8,760次", "#EC4899"),
        ]
        flow_html = ""
        for i, (name, count, color) in enumerate(agents_flow):
            flow_html += f"""
            <span style="padding:8px 14px;border-radius:8px;background:{color}18;color:{color};font-weight:600;white-space:nowrap;">
              {name}<br><span style="font-size:9px;font-weight:400;opacity:.7;">{count}调度</span>
            </span>"""
            if i < len(agents_flow) - 1:
                flow_html += '<span style="color:#334155;font-size:14px;">→</span>'
        st.markdown(flow_html + "</div></div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(f"""
        <div class="kpi-dark-card" style="margin-bottom:0;">
          <div style="font-size:13px;font-weight:700;color:#E2E8F0;margin-bottom:14px;">⚠️ 高频薄弱知识点 TOP5</div>
        </div>
        """, unsafe_allow_html=True)
        weak_items = [
            ("1", "TCP拥塞控制算法", 100, "#EF4444"),
            ("2", "IP路由与子网划分", 86, "#F87171"),
            ("3", "网络安全协议", 70, "#FB923C"),
            ("4", "操作系统进程调度", 55, "#FBBF24"),
            ("5", "数据结构图遍历", 42, "#FBBF24"),
        ]
        for rank, name, pct, color in weak_items:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;font-size:11px;color:#E2E8F0;">
              <span style="width:18px;height:18px;border-radius:5px;background:{color}18;color:{color};
                display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;">{rank}</span>
              <span style="flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{name}</span>
              <div style="flex:1;height:6px;background:#1E293B;border-radius:3px;overflow:hidden;max-width:80px;">
                <div style="height:100%;width:{pct}%;background:{color};border-radius:3px;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Hallucination Risk ──
    st.markdown(f"""
    <div class="kpi-dark-card" style="margin-top:14px;">
      <div style="font-size:13px;font-weight:700;color:#E2E8F0;margin-bottom:12px;">🔍 近期高幻觉风险问答记录 · <span style="font-size:9px;color:#475569;">今日拦截: 24次 · 准确率 98.7%</span></div>
    </div>
    """, unsafe_allow_html=True)

    hal_items = [
        ("量子计算对网络安全的影响？", "⚠️ 高风险 · 知识库无匹配 · 已拒绝回答", "#F87171"),
        ("请比较TCP和QUIC协议在5G场景下的性能", "⚡ 中风险 · 部分匹配(67%) · 人工复核", "#FBBF24"),
        ("解释元宇宙中的网络架构设计", "⚠️ 高风险 · 超出知识库范围 · 已拒绝", "#F87171"),
    ]
    for q, risk, color in hal_items:
        st.markdown(f"""
        <div style="padding:6px 0;border-bottom:1px solid #1E293B;font-size:10px;">
          <div style="color:#94A3B8;">Q: {q}</div>
          <div style="color:{color};font-weight:600;font-size:9px;">{risk}</div>
        </div>
        """, unsafe_allow_html=True)

    render_tech_annotations(["多智能体编排", "RAG知识库", "防幻觉", "数据大屏"])
    st.markdown("</div>", unsafe_allow_html=True)


# ========================================================================
# 管理后台登录页
# ========================================================================
def render_admin_login():
    """PC 宽屏左右分栏管理后台登录页"""
    st.markdown("""
    <style>
    .admin-login-wrapper { display:flex; min-height:100vh; margin:-4rem -4rem; }
    .admin-left { flex:0 0 46%; background:linear-gradient(160deg,#1E3A5F 0%,#2563EB 40%,#3B82F6 100%);
      display:flex; flex-direction:column; justify-content:center; align-items:center;
      padding:80px 60px; position:relative; overflow:hidden; color:white; }
    .admin-left::before { content:''; position:absolute; top:-120px; right:-80px;
      width:380px;height:380px;border-radius:50%;background:rgba(255,255,255,.04);border:2px solid rgba(255,255,255,.08); }
    .admin-left::after { content:''; position:absolute; bottom:-100px; left:-60px;
      width:260px;height:260px;border-radius:50%;background:rgba(255,255,255,.03);border:2px solid rgba(255,255,255,.06); }
    .admin-logo { width:72px;height:72px;border-radius:18px;background:rgba(255,255,255,.15);
      display:flex;align-items:center;justify-content:center;font-size:34px;margin-bottom:24px;
      box-shadow:0 8px 32px rgba(0,0,0,.15);position:relative;z-index:1; }
    .admin-title { font-size:32px;font-weight:800;letter-spacing:-.02em;margin-bottom:10px;position:relative;z-index:1;text-align:center; }
    .admin-subtitle { font-size:15px;opacity:.85;margin-bottom:32px;font-weight:300;position:relative;z-index:1;text-align:center; }
    .admin-divider { width:60px;height:3px;background:rgba(255,255,255,.3);border-radius:2px;margin:0 auto 32px;position:relative;z-index:1; }
    .admin-feature { display:flex;align-items:flex-start;gap:14px;margin-bottom:20px;
      font-size:13px;opacity:.9;line-height:1.6;position:relative;z-index:1;max-width:420px; }
    .admin-feature-icon { width:36px;height:36px;border-radius:10px;background:rgba(255,255,255,.12);
      display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0; }
    .admin-feature-text strong { display:block;font-size:14px;margin-bottom:3px;font-weight:700; }
    .admin-feature-text span { opacity:.8; }
    .admin-right { flex:1;display:flex;align-items:center;justify-content:center;
      background:#FAFBFC;padding:60px; }
    .admin-login-card { width:100%;max-width:440px;background:white;border-radius:16px;
      padding:48px 44px;box-shadow:0 1px 3px rgba(0,0,0,.04),0 8px 32px rgba(0,0,0,.06);
      border:1px solid #E5E7EB; }
    @media (max-width:900px) {
      .admin-login-wrapper { flex-direction:column; }
      .admin-left { flex:0 0 auto;padding:40px 28px; }
      .admin-title { font-size:22px; }
      .admin-feature { display:none; }
      .admin-right { padding:20px; }
      .admin-login-card { box-shadow:none;padding:24px 20px; }
    }
    </style>
    
    <div class="admin-login-wrapper">
    <div class="admin-left">
      <div class="admin-logo">🧠</div>
      <div class="admin-title">AI多智能体<br>个性化学习系统</div>
      <div class="admin-subtitle">基于讯飞星火大模型的自适应学习资源生成平台</div>
      <div class="admin-divider"></div>
      <div class="admin-feature">
        <div class="admin-feature-icon">👥</div>
        <div class="admin-feature-text"><strong>多智能体协同架构</strong><span>五智能体串行编排，个性化学习资源自动生成</span></div>
      </div>
      <div class="admin-feature">
        <div class="admin-feature-icon">📚</div>
        <div class="admin-feature-text"><strong>RAG本地知识库</strong><span>知识库向量化索引，内容溯源防幻觉</span></div>
      </div>
      <div class="admin-feature">
        <div class="admin-feature-icon">📊</div>
        <div class="admin-feature-text"><strong>6维学生画像</strong><span>知识基础·学习目标·认知风格·薄弱知识点·资源偏好·学习时长</span></div>
      </div>
      <div style="margin-top:40px;text-align:center;font-size:10px;opacity:.5;position:relative;z-index:1;">
        RAG本地知识库 · 多智能体编排 · 学生多维画像 · 大模型防幻觉
      </div>
    </div>
    <div class="admin-right">
      <div class="admin-login-card">
        <div style="text-align:center;margin-bottom:28px;">
          <div style="font-size:24px;font-weight:800;color:#1F2937;margin-bottom:6px;">管理后台</div>
          <div style="font-size:13px;color:#6B7280;">欢迎回来，请登录你的账号</div>
        </div>
    """, unsafe_allow_html=True)

    # Login form
    account = st.text_input("账号", placeholder="请输入教师工号或管理员账号", key="admin_account")
    password = st.text_input("密码", type="password", placeholder="请输入登录密码", key="admin_password")
    role = st.selectbox("角色", ["授课教师", "系统管理员"], key="admin_role")

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        st.checkbox("记住登录", key="admin_remember")
    with col_opt2:
        st.markdown(f'<p style="text-align:right;font-size:12px;"><a href="#" style="color:{ColorTokens.PRIMARY};text-decoration:none;font-weight:600;">忘记密码？</a></p>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("登 录 系 统", use_container_width=True, type="primary"):
        if account and password and role:
            st.session_state.teacher_logged_in = True
            st.session_state.teacher_role = role
            st.session_state.teacher_name = account
            st.success(f"登录成功！角色: {role}，正在跳转...")
            time.sleep(0.8)
            st.rerun()
        elif not account:
            st.error("请输入账号")
        elif not password:
            st.error("请输入密码")
        elif not role:
            st.error("请选择角色")

    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin:24px 0;color:#9CA3AF;font-size:11px;">
      <span style="flex:1;height:1px;background:#E5E7EB;"></span>其他登录方式<span style="flex:1;height:1px;background:#E5E7EB;"></span>
    </div>
    """, unsafe_allow_html=True)

    col_sso1, col_sso2 = st.columns(2)
    with col_sso1:
        st.button("🏫 校园统一认证", key="admin_sso1", use_container_width=True)
    with col_sso2:
        st.button("📱 扫码登录", key="admin_sso2", use_container_width=True)

    st.markdown(f"""
    <div style="text-align:center;margin-top:20px;font-size:11px;color:{ColorTokens.LIGHT_GRAY};">
      AI多智能体个性化学习系统 · 管理后台 v1.0 · 基于讯飞星火大模型
    </div>
    </div></div></div>
    """, unsafe_allow_html=True)


# ========================================================================
# 统一主路由
# ========================================================================

if st.session_state.user_role is None:
    render_role_landing()

elif st.session_state.user_role == "student":
    # ---- 学生端路由 ----
    page = st.session_state.student_page
    if page == "splash":
        render_splash_page()
    elif page == "login":
        render_login_page()
    elif page == "guest":
        render_guest_page()
    elif page == "dashboard":
        render_student_dashboard_page()
    elif page == "profile":
        render_profile_page()
    elif page == "profile_result":
        render_profile_result_page()
    elif page == "learning":
        render_learning_page()
    elif page == "resources":
        render_resources_page()
    elif page == "learning_path":
        render_learning_path_page()
    elif page == "agent_exec":
        render_agent_execution_page()
    elif page == "qa":
        render_qa_page()
    elif page == "report":
        render_student_report_page()
    elif page == "courses":
        render_courses_page()
    elif page == "settings":
        render_settings_page()
    else:
        render_splash_page()

else:
    # ---- 教师端路由 ----
    page = st.session_state.teacher_page

    if not st.session_state.get("teacher_logged_in", False):
        render_admin_login()
    else:
        # Sidebar for logged-in users
        st.sidebar.markdown(f"""
    <div style="padding:16px;text-align:center;border-bottom:1px solid {ColorTokens.CARD_BORDER};">
        <div style="font-size:24px;font-weight:700;color:{ColorTokens.PRIMARY};">🏫 管理后台</div>
        <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};margin-top:4px;">
            {st.session_state.get('teacher_role','')} · {st.session_state.get('teacher_name','')}
        </div>
    </div>
    """, unsafe_allow_html=True)

        st.sidebar.button("📊 数据大屏", on_click=teacher_nav, args=("dashboard",), use_container_width=True)
        st.sidebar.button("📋 知识库管理", on_click=teacher_nav, args=("kb",), use_container_width=True)
        st.sidebar.button("⚙️ 智能体配置", on_click=teacher_nav, args=("agent_config",), use_container_width=True)
        st.sidebar.button("📊 学情统计", on_click=teacher_nav, args=("stats",), use_container_width=True)
        st.sidebar.button("📜 资源日志", on_click=teacher_nav, args=("logs",), use_container_width=True)
        st.sidebar.button("📝 效果分析", on_click=teacher_nav, args=("report",), use_container_width=True)
        st.sidebar.button("🔧 系统设置", on_click=teacher_nav, args=("system_settings",), use_container_width=True)

        if st.sidebar.button("🚪 退出登录", use_container_width=True):
            for key in ["teacher_logged_in", "teacher_role", "teacher_name"]:
                st.session_state[key] = False if key == "teacher_logged_in" else None
            st.rerun()

        if st.sidebar.button("🔄 返回角色选择", use_container_width=True):
            st.session_state.user_role = None
            st.rerun()

        if page == "dashboard":
            render_dashboard_page()
        elif page == "kb":
            render_kb_page()
        elif page == "agent_config":
            render_agent_config_page()
        elif page == "stats":
            render_stats_page()
        elif page == "logs":
            render_logs_page()
        elif page == "report":
            render_teacher_report_page()
        elif page == "system_settings":
            render_system_settings_page()
        else:
            render_kb_page()
