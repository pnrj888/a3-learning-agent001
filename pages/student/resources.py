"""
学习资源中心页面 - 多模态资源展示
"""
import streamlit as st
from design_system import ColorTokens, render_student_sidebar, LIGHT_THEME_RESET, render_resource_card
from data.mock_data import MOCK_RESOURCES

def render_student_resources_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("resources")
    
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:4px;">📦 学习资源中心</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">查看和管理所有生成的学习资源</div>
    </div>
    """, unsafe_allow_html=True)

    col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
    with col_t1:
        search = st.text_input("", placeholder="🔍 搜索资源...", key="resource_search", label_visibility="collapsed")
    with col_t2:
        st.selectbox("", ["全部类型", "讲义", "习题", "思维导图", "PPT", "视频"], key="resource_filter", label_visibility="collapsed")
    with col_t3:
        st.selectbox("", ["最新", "最旧"], key="resource_sort", label_visibility="collapsed")

    st.markdown("---")

    for resource in MOCK_RESOURCES:
        render_resource_card(resource)
