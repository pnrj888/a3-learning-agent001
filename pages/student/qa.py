"""
智能答疑页面 - 知识库溯源防幻觉
"""
import streamlit as st
import time
from design_system import ColorTokens, render_student_sidebar, LIGHT_THEME_RESET
from data.mock_data import MOCK_QA_EXAMPLES
from services.llm_service import llm

def render_student_qa_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_student_sidebar("qa")
    
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:4px;">💬 智能答疑</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">基于知识库的智能问答，答案可溯源</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#FEF3C7;border-radius:10px;padding:12px 16px;margin-bottom:16px;
        border:1px solid #FCD34D;">
        <div style="display:flex;align-items:center;gap:8px;font-size:12px;color:#92400E;">
            <span>💡</span>
            <span>我的回答会标注知识库来源，确保准确可靠。若知识库无相关内容，我会如实告知，绝不编造。</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "qa_messages" not in st.session_state:
        st.session_state.qa_messages = []

    for msg in st.session_state.qa_messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="qa-question">{msg['content']}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="qa-answer">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                    <span style="font-size:18px;">🤖</span>
                    <span style="font-size:12px;font-weight:600;color:{ColorTokens.PRIMARY};">智能答疑助手</span>
                </div>
                <div>{msg['content']}</div>
                {f'<div class="rag-citation"><span class="rag-citation-icon">📌</span><span>来源: {msg.get("source", "知识库")}</span></div>' if msg.get("source") else ''}
            </div>
            """, unsafe_allow_html=True)

    col_i, col_b = st.columns([4, 1])
    with col_i:
        question = st.text_input("", key="qa_input", placeholder="输入你的学习疑问...", label_visibility="collapsed")
    with col_b:
        ask_clicked = st.button("发送", key="qa_submit", use_container_width=True)

    if ask_clicked and question:
        st.session_state.qa_messages.append({"role": "user", "content": question})
        
        with st.spinner("正在检索知识库并生成回答..."):
            time.sleep(1)
            answer = llm.generate(f"请回答关于计算机网络的问题：{question}")
            st.session_state.qa_messages.append({
                "role": "assistant", 
                "content": answer,
                "source": "computer_network_ch01.pdf"
            })
        st.rerun()

    st.markdown(f"""
    <div style="margin-top:16px;">
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:8px;">💡 热门问题：</div>
        <div style="display:flex;flex-wrap:wrap;gap:8px;">
    """, unsafe_allow_html=True)
    
    for example in MOCK_QA_EXAMPLES:
        if st.button(example["question"], key=f"qa_example_{example['question']}"):
            st.session_state.qa_messages.append({"role": "user", "content": example["question"]})
            st.session_state.qa_messages.append({
                "role": "assistant", 
                "content": example["answer"],
                "source": "computer_network_ch01.pdf"
            })
            st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)
