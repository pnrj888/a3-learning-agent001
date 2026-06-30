"""
多智能体协同页面 - 资源生成与路径规划
"""
import streamlit as st
import time
from design_system import ColorTokens, render_student_sidebar, LIGHT_THEME_RESET, render_agent_flow_panel

def render_student_learning_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("learning")
    
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:4px;">⚡ 多智能体协同学习</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">五大智能体协同工作，为你生成个性化学习资源</div>
    </div>
    """, unsafe_allow_html=True)

    agents = [
        {"name": "ProfileAgent", "icon": "👤", "desc": "画像采集", "status": "idle"},
        {"name": "PlannerAgent", "icon": "📋", "desc": "路径规划", "status": "idle"},
        {"name": "ResourceAgent", "icon": "📦", "desc": "资源生成", "status": "idle"},
        {"name": "QuizAgent", "icon": "📝", "desc": "习题生成", "status": "idle"},
        {"name": "ReviewAgent", "icon": "✅", "desc": "质量审核", "status": "idle"},
    ]
    
    render_agent_flow_panel(agents)

    st.markdown("---")
    
    st.markdown(f"""
    <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:16px;">
        🎯 选择学习任务
    </div>
    """, unsafe_allow_html=True)

    task_type = st.selectbox(
        "",
        ["生成讲义", "生成习题", "生成思维导图", "生成PPT", "生成学习路径"],
        key="learning_task",
        label_visibility="collapsed"
    )

    topic = st.text_input("学习主题", placeholder="输入你想学习的知识点，例如：TCP/IP协议", key="learning_topic")

    if st.button("🚀 开始生成", use_container_width=True):
        if not topic:
            st.warning("请输入学习主题")
            st.stop()
        
        with st.spinner("智能体正在协同工作..."):
            agents[0]["status"] = "processing"
            render_agent_flow_panel(agents)
            time.sleep(0.5)
            
            agents[0]["status"] = "success"
            agents[1]["status"] = "processing"
            render_agent_flow_panel(agents)
            time.sleep(0.5)
            
            agents[1]["status"] = "success"
            agents[2]["status"] = "processing"
            render_agent_flow_panel(agents)
            time.sleep(0.5)
            
            agents[2]["status"] = "success"
            agents[3]["status"] = "processing"
            render_agent_flow_panel(agents)
            time.sleep(0.5)
            
            agents[3]["status"] = "success"
            agents[4]["status"] = "processing"
            render_agent_flow_panel(agents)
            time.sleep(0.5)
            
            agents[4]["status"] = "success"
            render_agent_flow_panel(agents)
        
        st.success("✅ 资源生成完成！")
        
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:20px;border:1px solid {ColorTokens.CARD_BORDER};margin-top:20px;">
            <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:16px;">
                📦 生成结果：{task_type}
            </div>
            <div style="font-size:14px;color:{ColorTokens.MID_GRAY};line-height:1.7;">
                这是为你生成的关于「{topic}」的学习资源。内容基于你的学生画像和知识库中的相关资料。
            </div>
        </div>
        """, unsafe_allow_html=True)
