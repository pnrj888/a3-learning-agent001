"""
教师管理后台首页 - 统计概览 + 快速操作
"""
import streamlit as st
import pandas as pd
from design_system import ColorTokens, render_teacher_sidebar, LIGHT_THEME_RESET
from data.mock_data import MOCK_GENERATION_LOGS

def render_teacher_dashboard_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_teacher_sidebar("dashboard")
    
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;padding-bottom:12px;
        border-bottom:1px solid {ColorTokens.CARD_BORDER};">
        <div style="flex:1;">
            <div style="font-size:18px;font-weight:700;color:{ColorTokens.DARK_GRAY};">
                👋 教师管理后台
            </div>
            <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-top:4px;">
                实时监控学生学习状态与智能体运行情况
            </div>
        </div>
        <span style="font-size:10px;color:{ColorTokens.AGENT_GREEN};font-weight:600;
            background:#ECFDF5;padding:4px 10px;border-radius:8px;">
            🟢 系统运行正常
        </span>
    </div>
    """, unsafe_allow_html=True)

    stats = [
        {"value": "6", "label": "总学生数"},
        {"value": "12", "label": "已绑定画像"},
        {"value": "89", "label": "生成资源数"},
        {"value": "98%", "label": "生成成功率"},
    ]
    cols = st.columns(4)
    for i, stat in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};text-align:center;">
                <div style="font-size:22px;font-weight:800;color:{ColorTokens.PRIMARY};margin-bottom:4px;">{stat['value']}</div>
                <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};">{stat['label']}</div>
            </div>
            """, unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown(f"""<div style="background:white;border-radius:12px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
            <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">📊 生成任务趋势</div>
        """, unsafe_allow_html=True)
        trend_data = pd.DataFrame({
            "日期": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "任务数": [12, 15, 8, 18, 22, 25, 14]
        })
        st.line_chart(trend_data, x="日期", y="任务数", color="#2563EB")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart2:
        st.markdown(f"""<div style="background:white;border-radius:12px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
            <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">📈 智能体调用分布</div>
        """, unsafe_allow_html=True)
        agent_data = pd.DataFrame({
            "智能体": ["ProfileAgent", "PlannerAgent", "ResourceAgent", "QuizAgent", "ReviewAgent"],
            "调用次数": [15, 12, 30, 18, 35]
        })
        st.bar_chart(agent_data, x="智能体", y="调用次数", color="#2563EB")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
        <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">📋 生成日志</div>
    """, unsafe_allow_html=True)
    
    log_data = []
    for log in MOCK_GENERATION_LOGS[:8]:
        status_color = {
            "success": "#10B981",
            "failed": "#EF4444",
            "warning": "#F59E0B"
        }.get(log["status"], "#6B7280")
        
        status_icon = {
            "success": "✅",
            "failed": "❌",
            "warning": "⚠️"
        }.get(log["status"], "🔄")
        
        log_data.append(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid {ColorTokens.CARD_BORDER};">
            <div style="display:flex;align-items:center;gap:10px;">
                <span style="font-size:14px;">{status_icon}</span>
                <div>
                    <div style="font-size:12px;color:{ColorTokens.DARK_GRAY};font-weight:500;">
                        {log['student']} · {log['type']} · {log['topic']}
                    </div>
                    <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};">{log['time']}</div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:11px;color:{status_color};font-weight:600;">{log['status']}</div>
                <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};">{log['duration']}</div>
            </div>
        </div>
        """)
    
    st.markdown("".join(log_data), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
