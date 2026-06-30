"""
导航组件 - 侧边栏、面包屑、标签页等
"""
import streamlit as st
from design_system import ColorTokens

def render_nav_bar(items: list, current_page: str, on_click_callback=None):
    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:8px;border:1px solid {ColorTokens.CARD_BORDER};
        display:flex;gap:4px;">
    """, unsafe_allow_html=True)
    
    for item in items:
        is_active = item["id"] == current_page
        bg_color = ColorTokens.PRIMARY if is_active else ColorTokens.BG_GRAY
        text_color = "white" if is_active else ColorTokens.MID_GRAY
        
        st.markdown(f"""
        <button onclick="navigateTo('{item['id']}')"
            style="padding:10px 16px;border:none;border-radius:8px;
                background:{bg_color};color:{text_color};font-size:13px;font-weight:600;
                cursor:pointer;transition:all 0.2s;">
            {item['icon']} {item['label']}
        </button>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_breadcrumb(items: list):
    breadcrumb_html = ""
    for i, item in enumerate(items):
        if i == len(items) - 1:
            breadcrumb_html += f'<span style="color:{ColorTokens.DARK_GRAY};font-weight:600;">{item}</span>'
        else:
            breadcrumb_html += f'<a href="#" style="color:{ColorTokens.PRIMARY};text-decoration:none;">{item}</a> <span style="color:{ColorTokens.LIGHT_GRAY};">/</span> '
    
    st.markdown(f"""
    <div style="font-size:12px;margin-bottom:16px;">
        {breadcrumb_html}
    </div>
    """, unsafe_allow_html=True)

def render_tabs(tabs: list, active_tab: str = None):
    if active_tab is None:
        active_tab = tabs[0]["id"]
    
    tabs_html = ""
    for tab in tabs:
        is_active = tab["id"] == active_tab
        border_color = ColorTokens.PRIMARY if is_active else "transparent"
        text_color = ColorTokens.PRIMARY if is_active else ColorTokens.LIGHT_GRAY
        weight = "700" if is_active else "400"
        
        tabs_html += f"""
        <button onclick="switchTab('{tab['id']}')"
            style="padding:12px 20px;border:none;border-bottom:2px solid {border_color};
                background:none;color:{text_color};font-size:14px;font-weight:{weight};
                cursor:pointer;transition:all 0.2s;">
            {tab['icon']} {tab['label']}
        </button>
        """
    
    st.markdown(f"""
    <div style="display:flex;border-bottom:1px solid {ColorTokens.CARD_BORDER};margin-bottom:20px;">
        {tabs_html}
    </div>
    """, unsafe_allow_html=True)

def render_page_header(title: str, subtitle: str = "", icon: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:4px;">
            {icon} {title}
        </div>
        {f'<div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.markdown(f"""
    <div style="text-align:center;padding:20px;border-top:1px solid {ColorTokens.CARD_BORDER};
        margin-top:40px;">
        <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};">
            🎓 A3 智能学习助手 · 基于科大讯飞星火大模型
        </div>
    </div>
    """, unsafe_allow_html=True)
