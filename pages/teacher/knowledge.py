"""
教师端知识库管理页面 - 文件上传 + 索引管理 + 搜索
"""
import streamlit as st
from design_system import ColorTokens, render_teacher_sidebar, LIGHT_THEME_RESET
from data.mock_data import MOCK_KB_FILES

def render_teacher_kb_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_teacher_sidebar("knowledge")
    
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:4px;">📚 知识库管理</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">上传和管理课程资料，构建智能问答知识库</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{ColorTokens.LIGHT_BLUE};border-radius:14px;padding:20px;border:2px dashed {ColorTokens.PRIMARY};
        margin-bottom:20px;text-align:center;">
        <div style="font-size:32px;margin-bottom:8px;">📁</div>
        <div style="font-size:14px;font-weight:600;color:{ColorTokens.DARK_GRAY};margin-bottom:4px;">
            上传课程资料
        </div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:12px;">
            支持 PDF、Word、TXT 等格式，文件大小不超过 50MB
        </div>
        <button style="padding:10px 24px;border:none;border-radius:10px;
            background:{ColorTokens.PRIMARY};color:white;font-size:13px;font-weight:600;
            cursor:pointer;">
            选择文件
        </button>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:14px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:12px;">
        📋 已上传文件 ({len(MOCK_KB_FILES)})
    </div>
    """, unsafe_allow_html=True)

    for file in MOCK_KB_FILES:
        status_color = {
            "indexed": ColorTokens.AGENT_GREEN,
            "pending": "#F59E0B",
            "failed": ColorTokens.WARNING_RED
        }.get(file["status"], "#6B7280")
        
        status_text = {
            "indexed": "已索引",
            "pending": "待处理",
            "failed": "失败"
        }.get(file["status"], "未知")
        
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};
            margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:24px;">📄</span>
                <div>
                    <div style="font-size:13px;font-weight:600;color:{ColorTokens.DARK_GRAY};">
                        {file['name']}
                    </div>
                    <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-top:2px;">
                        {file['size']} · {file['chunks']} chunks · {file['date']}
                    </div>
                </div>
            </div>
            
            <div style="display:flex;gap:12px;align-items:center;">
                <span style="font-size:10px;color:{status_color};font-weight:600;
                    background:{status_color}15;padding:4px 10px;border-radius:8px;">
                    {status_text}
                </span>
                
                <div style="display:flex;gap:4px;">
                    <button style="padding:6px 12px;border:none;border-radius:6px;
                        background:{ColorTokens.BG_GRAY};color:{ColorTokens.MID_GRAY};font-size:11px;
                        cursor:pointer;">
                        预览
                    </button>
                    <button style="padding:6px 12px;border:none;border-radius:6px;
                        background:{ColorTokens.BG_GRAY};color:{ColorTokens.MID_GRAY};font-size:11px;
                        cursor:pointer;">
                        删除
                    </button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
