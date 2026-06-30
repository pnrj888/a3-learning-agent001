"""
多智能体协同学习页面 - 资源生成可视化流程
"""
import streamlit as st
import time
from design_system import ColorTokens, render_student_sidebar, LIGHT_THEME_RESET, render_section_header, render_agent_flow_panel, render_resource_card

def render_student_learning_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("learning")
    
    render_section_header("⚡ 多智能体协同学习", "五大智能体协作生成个性化学习资源")

    st.markdown(f"""
    <div style="background:{ColorTokens.LIGHT_BLUE};border-radius:14px;padding:20px;border:1px solid {ColorTokens.PRIMARY};margin-bottom:20px;">
        <div style="font-size:14px;color:{ColorTokens.MID_GRAY};line-height:1.6;">
            <strong style="color:{ColorTokens.PRIMARY};">💡 工作流程：</strong>
            ProfileAgent分析画像 → PlannerAgent制定路径 → ResourceAgent生成资源 → QuizAgent生成习题 → ReviewAgent质量审核
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_goal, col_topics = st.columns([1, 2])
    with col_goal:
        learning_goal = st.text_input("学习目标", placeholder="例如：掌握TCP/IP协议", key="learning_goal")
    with col_topics:
        topics = st.text_input("学习主题", placeholder="用逗号分隔多个主题", key="learning_topics")

    run_btn = st.button("🚀 开始多智能体协同生成", use_container_width=True, type="primary")

    if run_btn and learning_goal:
        st.session_state.learning_goal = learning_goal
        st.session_state.topics = topics
        st.session_state.agent_states = [
            {"name": "ProfileAgent", "icon": "👤", "status": "processing", "desc": "分析画像"},
            {"name": "PlannerAgent", "icon": "📋", "status": "idle", "desc": "规划路径"},
            {"name": "ResourceAgent", "icon": "📦", "status": "idle", "desc": "生成资源"},
            {"name": "QuizAgent", "icon": "📝", "status": "idle", "desc": "生成习题"},
            {"name": "ReviewAgent", "icon": "✅", "status": "idle", "desc": "质量审核"},
        ]
        
        with st.spinner("智能体协同工作中..."):
            for i in range(5):
                st.session_state.agent_states[i]["status"] = "processing"
                st.session_state.agent_states[i-1]["status"] = "success" if i > 0 else "success"
                render_agent_flow_panel(st.session_state.agent_states)
                time.sleep(0.8)
                st.rerun()
            
            st.session_state.agent_states[-1]["status"] = "success"
            
        st.success("🎉 多智能体协同生成完成！")
        
        mock_resources = [
            {"icon": "📖", "title": f"{learning_goal} - 精讲讲义", "meta": "5页 · ProfileAgent生成"},
            {"icon": "🧠", "title": f"{learning_goal} - 思维导图", "meta": "3级节点 · PlannerAgent生成"},
            {"icon": "📝", "title": f"{learning_goal} - 练习题集", "meta": "10道题 · QuizAgent生成"},
            {"icon": "💻", "title": f"{learning_goal} - 代码示例", "meta": "Python · ResourceAgent生成"},
        ]
        
        st.session_state.generated_resources = mock_resources

    if st.session_state.get("agent_states"):
        render_agent_flow_panel(st.session_state.agent_states)

    if st.session_state.get("generated_resources"):
        render_section_header("📦 生成的学习资源")
        for resource in st.session_state.generated_resources:
            render_resource_card(resource)
