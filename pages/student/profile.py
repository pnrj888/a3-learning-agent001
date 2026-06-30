"""
学生画像采集页面 - 对话式构建6维画像
"""
import streamlit as st
import time
from design_system import ColorTokens, render_student_sidebar, LIGHT_THEME_RESET

def render_student_profile_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("profile")
    
    st.markdown(f"""
    <div style="background:{ColorTokens.LIGHT_BLUE};border-radius:14px;padding:20px;border:1px solid {ColorTokens.PRIMARY};margin-bottom:20px;">
        <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:8px;">
            🤖 智能画像采集助手
        </div>
        <div style="font-size:12px;color:{ColorTokens.MID_GRAY};line-height:1.6;">
            我将通过对话方式收集你的学习信息，自动生成6维学生画像。请用自然语言回答即可，无需格式化。
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "profile_messages" not in st.session_state:
        st.session_state.profile_messages = [
            {"role": "assistant", "content": "你好！我是你的智能画像采集助手。为了更好地了解你，我想先问几个简单的问题。你目前是什么专业的学生？"}
        ]

    for msg in st.session_state.profile_messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="background:{ColorTokens.LIGHT_BLUE};border-radius:10px 10px 4px 10px;padding:12px 16px;margin-bottom:8px;">
                <div style="font-size:14px;color:{ColorTokens.DARK_GRAY};">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:{ColorTokens.BG_GRAY};border-radius:10px 10px 10px 4px;padding:12px 16px;margin-bottom:8px;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                    <span style="font-size:18px;">🤖</span>
                    <span style="font-size:12px;font-weight:600;color:{ColorTokens.PRIMARY};">智能助手</span>
                </div>
                <div style="font-size:14px;color:{ColorTokens.DARK_GRAY};line-height:1.6;">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)

    col_i, col_b = st.columns([4, 1])
    with col_i:
        user_input = st.text_input("", key="profile_input", placeholder="输入你的回答...", label_visibility="collapsed")
    with col_b:
        submit_btn = st.button("发送", key="profile_submit", use_container_width=True)

    if submit_btn and user_input:
        st.session_state.profile_messages.append({"role": "user", "content": user_input})
        
        with st.spinner("正在分析你的回答..."):
            time.sleep(1)
            
        mock_responses = [
            "好的！那你之前学过哪些计算机相关的课程呢？",
            "明白了。你更喜欢哪种学习方式？比如看视频、阅读文档还是动手实践？",
            "了解！你每天大概有多少时间可以用来学习？",
            "很好！你学习计算机网络的主要目标是什么？",
            "好的，收集完成！我来为你生成6维学生画像...",
        ]
        
        next_response = mock_responses[min(len(st.session_state.profile_messages) // 2, len(mock_responses) - 1)]
        st.session_state.profile_messages.append({"role": "assistant", "content": next_response})
        st.rerun()

    if len(st.session_state.profile_messages) >= 10:
        st.markdown(f"""
        <div style="background:#ECFDF5;border-radius:14px;padding:20px;border:1px solid {ColorTokens.AGENT_GREEN};margin-top:20px;">
            <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:16px;">
                🎉 画像采集完成！
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
                <div style="background:white;border-radius:10px;padding:12px;text-align:center;border:1px solid {ColorTokens.CARD_BORDER};">
                    <div style="font-size:24px;margin-bottom:4px;">👨‍🎓</div>
                    <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:2px;">专业背景</div>
                    <div style="font-size:12px;font-weight:600;color:{ColorTokens.DARK_GRAY};">计算机科学</div>
                </div>
                <div style="background:white;border-radius:10px;padding:12px;text-align:center;border:1px solid {ColorTokens.CARD_BORDER};">
                    <div style="font-size:24px;margin-bottom:4px;">🎯</div>
                    <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:2px;">学习风格</div>
                    <div style="font-size:12px;font-weight:600;color:{ColorTokens.DARK_GRAY};">视觉型</div>
                </div>
                <div style="background:white;border-radius:10px;padding:12px;text-align:center;border:1px solid {ColorTokens.CARD_BORDER};">
                    <div style="font-size:24px;margin-bottom:4px;">⏱</div>
                    <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:2px;">时间习惯</div>
                    <div style="font-size:12px;font-weight:600;color:{ColorTokens.DARK_GRAY};">每晚2小时</div>
                </div>
                <div style="background:white;border-radius:10px;padding:12px;text-align:center;border:1px solid {ColorTokens.CARD_BORDER};">
                    <div style="font-size:24px;margin-bottom:4px;">🎯</div>
                    <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:2px;">学习目标</div>
                    <div style="font-size:12px;font-weight:600;color:{ColorTokens.DARK_GRAY};">掌握网络基础</div>
                </div>
                <div style="background:white;border-radius:10px;padding:12px;text-align:center;border:1px solid {ColorTokens.CARD_BORDER};">
                    <div style="font-size:24px;margin-bottom:4px;">❤️</div>
                    <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:2px;">兴趣偏好</div>
                    <div style="font-size:12px;font-weight:600;color:{ColorTokens.DARK_GRAY};">网络安全</div>
                </div>
                <div style="background:white;border-radius:10px;padding:12px;text-align:center;border:1px solid {ColorTokens.CARD_BORDER};">
                    <div style="font-size:24px;margin-bottom:4px;">⚠️</div>
                    <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:2px;">薄弱环节</div>
                    <div style="font-size:12px;font-weight:600;color:{ColorTokens.WARNING_RED};">TCP拥塞控制</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
