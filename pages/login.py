"""
登录页面 - 学生登录 + 游客模式
简化版：使用纯 Streamlit 组件
"""
import streamlit as st
from design_system import ColorTokens, inject_design_system

def render_login_page():
    inject_design_system()

    st.title("🎓 智能学习助手")
    st.subheader("A3 · 科大讯飞")
    
    st.markdown("---")
    
    username = st.text_input("用户名", placeholder="请输入用户名", key="login_username")
    password = st.text_input("密码", placeholder="请输入密码", type="password", key="login_password")
    
    col_rm, col_fp = st.columns([2, 1])
    with col_rm:
        st.checkbox("记住登录", key="login_remember")
    with col_fp:
        st.markdown(f'<a href="#" style="font-size:12px;color:{ColorTokens.PRIMARY};">忘记密码？</a>', unsafe_allow_html=True)
    
    login_btn = st.button("登录", key="login_submit", use_container_width=True, type="primary")
    
    st.markdown(f"""
    <div style="text-align:center;margin-top:20px;">
        <a href="#" onclick="window.location.href='?guest=true'" style="font-size:13px;color:{ColorTokens.MID_GRAY};">🚪 游客免登体验</a>
    </div>
    """, unsafe_allow_html=True)

    if login_btn:
        if not username or not password:
            st.warning("请输入用户名和密码")
            return
        
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.user_role = "student"
        st.session_state.student_page = "dashboard"
        st.rerun()

    query_params = st.query_params
    if query_params.get("login") == "true":
        username = query_params.get("user", "user")
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.user_role = "student"
        st.session_state.student_page = "dashboard"
        st.rerun()
    elif query_params.get("guest") == "true":
        st.session_state.logged_in = True
        st.session_state.username = "游客"
        st.session_state.user_role = "student"
        st.session_state.is_guest = True
        st.session_state.student_page = "dashboard"
        st.rerun()
