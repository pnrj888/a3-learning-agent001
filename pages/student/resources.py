"""
学习资源中心页面 - 讲义、思维导图、习题、代码案例
"""
import streamlit as st
from design_system import ColorTokens, render_student_sidebar, LIGHT_THEME_RESET, render_section_header, render_resource_card

def render_student_resources_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("resources")
    
    render_section_header("📦 学习资源中心", "浏览和管理你的学习资源")

    tabs = st.tabs(["📖 讲义", "🧠 思维导图", "📝 习题", "💻 代码案例"])

    with tabs[0]:
        render_section_header("我的讲义", "", "")
        resources = [
            {"icon": "📖", "title": "TCP/IP协议详解", "meta": "第1章 · 网络基础"},
            {"icon": "📖", "title": "计算机网络自顶向下方法", "meta": "第5章 · 运输层"},
            {"icon": "📖", "title": "网络安全基础", "meta": "第3章 · 加密技术"},
        ]
        for r in resources:
            render_resource_card(r)

    with tabs[1]:
        render_section_header("我的思维导图", "", "")
        resources = [
            {"icon": "🧠", "title": "OSI七层模型", "meta": "7个主节点"},
            {"icon": "🧠", "title": "TCP协议状态机", "meta": "11个状态"},
            {"icon": "🧠", "title": "网络攻击分类", "meta": "5大类"},
        ]
        for r in resources:
            render_resource_card(r)

    with tabs[2]:
        render_section_header("我的习题", "", "")
        resources = [
            {"icon": "📝", "title": "网络基础测试", "meta": "10题 · 正确率80%"},
            {"icon": "📝", "title": "TCP/IP进阶练习", "meta": "15题 · 正确率67%"},
            {"icon": "📝", "title": "路由算法专项", "meta": "8题 · 正确率75%"},
        ]
        for r in resources:
            render_resource_card(r)

    with tabs[3]:
        render_section_header("我的代码案例", "", "")
        resources = [
            {"icon": "💻", "title": "TCP客户端实现", "meta": "Python · 50行"},
            {"icon": "💻", "title": "HTTP请求模拟", "meta": "Python · 30行"},
            {"icon": "💻", "title": "端口扫描工具", "meta": "Python · 80行"},
        ]
        for r in resources:
            render_resource_card(r)
