"""
学生仪表盘页面 - KPI卡片 + 知识掌握热力图 + 快捷入口 + 最近活动
"""
import streamlit as st
import pandas as pd
import time
from design_system import ColorTokens, render_student_sidebar, LIGHT_THEME_RESET, render_section_header

def render_student_dashboard_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("dashboard")
    
    profile = st.session_state.get("current_profile")
    student_name = getattr(profile, 'name', '同学') if profile else '同学'
    
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

    stats = [
        {"value": "48h", "label": "累计学习时长"},
        {"value": "58%", "label": "平均掌握度"},
        {"value": "12", "label": "已生成资源"},
        {"value": "3", "label": "薄弱知识点"},
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
            <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">📈 掌握度趋势</div>
        """, unsafe_allow_html=True)
        trend_data = pd.DataFrame({
            "日期": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
            "掌握度": [45, 48, 52, 49, 55, 58, 62]
        })
        st.line_chart(trend_data, x="日期", y="掌握度", color="#2563EB")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_chart2:
        st.markdown(f"""<div style="background:white;border-radius:12px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
            <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">📦 资源类型分布</div>
        """, unsafe_allow_html=True)
        res_data = pd.DataFrame({
            "类型": ["讲义", "习题", "思维导图", "PPT", "视频"],
            "数量": [5, 4, 3, 2, 1]
        })
        st.bar_chart(res_data, x="类型", y="数量", color="#2563EB")
        st.markdown("</div>", unsafe_allow_html=True)

    col_heatmap, col_weak = st.columns(2)
    with col_heatmap:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
            <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">🧠 知识掌握热力图</div>
        """, unsafe_allow_html=True)
        
        heatmap_data = [
            (8, "OSI模型", "#10B981"), (5, "TCP/IP", "#F59E0B"),
            (9, "UDP", "#10B981"), (2, "拥塞控制", "#EF4444"),
            (7, "物理层", "#10B981"), (4, "路由算法", "#EF4444"),
            (6, "子网划分", "#F59E0B"), (3, "网络安全", "#EF4444"),
        ]
        
        for i, (level, name, color) in enumerate(heatmap_data):
            st.markdown(f"""
            <div style="background:{color}18;border:2px solid {color};border-radius:8px;
                padding:6px 4px;text-align:center;margin-bottom:4px;">
                <div style="font-size:8px;color:{ColorTokens.LIGHT_GRAY};">{name[:4]}</div>
                <div style="font-size:12px;font-weight:800;color:{color};">{level}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_weak:
        st.markdown(f"""
        <div style="background:{ColorTokens.WARNING_RED_LIGHT};border-radius:14px;padding:16px;border:1px solid {ColorTokens.WARNING_RED};margin-bottom:16px;">
            <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">⚠️ 薄弱点提醒</div>
        """, unsafe_allow_html=True)
        
        weak_points = [
            {"name": "TCP拥塞控制", "error_rate": "68%", "level": 2},
            {"name": "IP路由算法", "error_rate": "52%", "level": 4},
            {"name": "网络安全协议", "error_rate": "45%", "level": 3},
        ]
        
        for wp in weak_points:
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:10px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:12px;font-weight:600;color:{ColorTokens.DARK_GRAY};">{wp['name']}</div>
                        <div style="font-size:10px;color:{ColorTokens.WARNING_RED};">错误率 {wp['error_rate']}</div>
                    </div>
                    <span style="font-size:10px;background:#FEF2F2;color:{ColorTokens.WARNING_RED};padding:3px 8px;border-radius:6px;">
                        掌握度 {wp['level']}/10
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🎯 一键生成薄弱点资源包", use_container_width=True):
            with st.spinner("正在生成个性化学习资源..."):
                time.sleep(1.5)
            st.success("✅ 薄弱点资源包已生成！")
        
        st.markdown("</div>", unsafe_allow_html=True)

    col_calendar, col_agents = st.columns(2)
    with col_calendar:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
            <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">📅 本周打卡</div>
        """, unsafe_allow_html=True)
        
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        hours = [1.5, 2.0, 0.5, 1.0, 2.5, 3.0, 1.5]
        
        for i, (day, hrs) in enumerate(zip(days, hours)):
            status = "✅" if hrs > 0 else "○"
            color = ColorTokens.AGENT_GREEN if hrs > 0 else ColorTokens.LIGHT_GRAY
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid {ColorTokens.CARD_BORDER};">
                <span style="font-size:11px;color:{ColorTokens.MID_GRAY};">{day}</span>
                <span style="font-size:11px;color:{color};">{status} {hrs}h</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col_agents:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
            <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">🤖 智能体为我做了什么</div>
        """, unsafe_allow_html=True)
        
        agents = [
            {"name": "ProfileAgent", "count": 3, "color": "#2563EB"},
            {"name": "PlannerAgent", "count": 2, "color": "#10B981"},
            {"name": "ResourceAgent", "count": 12, "color": "#8B5CF6"},
            {"name": "QuizAgent", "count": 5, "color": "#F59E0B"},
            {"name": "ReviewAgent", "count": 15, "color": "#EF4444"},
        ]
        
        for agent in agents:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="width:10px;height:10px;border-radius:50%;background:{agent['color']};"></span>
                    <span style="font-size:11px;color:{ColorTokens.MID_GRAY};">{agent['name']}</span>
                </div>
                <span style="font-size:12px;font-weight:700;color:{agent['color']};">{agent['count']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
        <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">📄 最近动态</div>
    """, unsafe_allow_html=True)
    
    activities = [
        ("📝", "生成了讲义《TCP/IP协议详解》", "10分钟前"),
        ("✅", "完成了习题《网络基础测试》", "30分钟前"),
        ("👤", "更新了学生画像", "1小时前"),
        ("📊", "生成了学习路径规划", "2小时前"),
    ]
    
    for icon, text, time_str in activities:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid {ColorTokens.CARD_BORDER};">
            <span style="font-size:16px;">{icon}</span>
            <div style="flex:1;">
                <div style="font-size:12px;color:{ColorTokens.DARK_GRAY};">{text}</div>
                <div style="font-size:10px;color:{ColorTokens.LIGHT_GRAY};">{time_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
