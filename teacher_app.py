"""
A3 赛题 - 教师后台管理端
基于大模型的个性化资源生成与学习多智能体系统开发
遵循 AtomCode 设计规范 | v3.0
"""
import streamlit as st
import time
import os
import sys
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
import random

if __name__ == "__main__":
    st.set_page_config(
        page_title="教师管理中台 | A3 多智能体系统",
        page_icon="🏫",
        layout="wide",
        initial_sidebar_state="expanded"
    )

from design_system import (
    inject_design_system, ColorTokens,
    render_tech_annotations, render_agent_flow_panel,
    render_rag_citation, render_rag_source_chip,
    render_status_badge, render_toast, render_toast as render_toast_msg,
    render_progress_with_label, render_section_header,
    render_teacher_sidebar, render_stat_grid,
    generate_id, format_timestamp
)

if __name__ == "__main__":
    inject_design_system()

sys.path.insert(0, str(Path(__file__).resolve().parent))

def init_session():
    defaults = {
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
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

if __name__ == "__main__":
    init_session()

def nav_to(p: str):
    st.session_state.teacher_page = p

LIGHT_THEME_RESET = """
<style>
  .stApp { background: #FAFBFC !important; }
  .main { background: #FAFBFC !important; }
  section[data-testid="stSidebar"] { display: block !important; }
  section[data-testid="stSidebar"] > div { background: #F9FAFB !important; }
</style>
"""

# ========================================================================
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
def render_report_page():
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
# 主路由
# ========================================================================
if __name__ == "__main__":
    page = st.session_state.teacher_page

    # ── Login gate ──
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

        st.sidebar.button("📊 数据大屏", on_click=nav_to, args=("dashboard",), use_container_width=True)
        st.sidebar.button("📋 知识库管理", on_click=nav_to, args=("kb",), use_container_width=True)
        st.sidebar.button("⚙️ 智能体配置", on_click=nav_to, args=("agent_config",), use_container_width=True)
        st.sidebar.button("📊 学情统计", on_click=nav_to, args=("stats",), use_container_width=True)
        st.sidebar.button("📜 资源日志", on_click=nav_to, args=("logs",), use_container_width=True)
        st.sidebar.button("📝 效果分析", on_click=nav_to, args=("report",), use_container_width=True)
        st.sidebar.button("🔧 系统设置", on_click=nav_to, args=("system_settings",), use_container_width=True)

        if st.sidebar.button("🚪 退出登录", use_container_width=True):
            for key in ["teacher_logged_in", "teacher_role", "teacher_name"]:
                st.session_state[key] = False if key == "teacher_logged_in" else None
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
            render_report_page()
        elif page == "system_settings":
            render_system_settings_page()
        else:
            render_kb_page()
