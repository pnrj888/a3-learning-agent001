"""
A3 智能学习助手 - 统一应用入口
基于大模型的个性化资源生成与学习多智能体系统
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from design_system import inject_design_system, LIGHT_THEME_RESET

st.set_page_config(
    page_title="A3 智能学习助手",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    defaults = {
        "logged_in": False,
        "user_role": None,
        "username": None,
        "student_page": "dashboard",
        "teacher_page": "dashboard",
        "current_profile": None,
        "is_guest": False,
        "generation_logs": [],
        "generated_resources": [],
        "qa_history": [],
        "conversation_history": [],
        "learning_plan": None,
        "learning_goal": "",
        "topics": "",
        "agent_states": [],
        "student_id": "",
        "student_name": "",
        "guest_qa_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_page_module(page_name: str, role: str = ""):
    import importlib
    try:
        if role == "student":
            module = importlib.import_module(f"pages.student.{page_name}")
        elif role == "teacher":
            module = importlib.import_module(f"pages.teacher.{page_name}")
        else:
            module = importlib.import_module(f"pages.{page_name}")
        return module
    except ImportError as e:
        st.error(f"页面模块加载失败: {e}")
        return None

def render_page(page_name: str, role: str = ""):
    module = get_page_module(page_name, role)
    if module:
        func_name = f"render_{role}_{page_name}_page" if role else f"render_{page_name}_page"
        render_func = getattr(module, func_name, None)
        if render_func:
            render_func()
            return
    st.error(f"页面渲染函数 {func_name} 未找到")

def main():
    inject_design_system()
    init_session_state()
    
    query_params = st.query_params
    role = query_params.get("role")
    
    if role and not st.session_state.logged_in:
        st.session_state.user_role = role
        st.session_state.logged_in = True
        if role == "student":
            st.session_state.student_page = "dashboard"
        else:
            st.session_state.teacher_page = "dashboard"
    
    if not st.session_state.logged_in:
        render_page("splash")
        return
    
    if st.session_state.user_role == "student":
        st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
        render_page(st.session_state.student_page, "student")
    elif st.session_state.user_role == "teacher":
        st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
        render_page(st.session_state.teacher_page, "teacher")
    else:
        render_page("splash")

if __name__ == "__main__":
    main()
