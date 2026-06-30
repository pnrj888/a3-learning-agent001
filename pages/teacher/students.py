"""
教师端学生管理页面 - 学生列表 + 画像查看 + 批量操作
"""
import streamlit as st
from design_system import ColorTokens, render_teacher_sidebar, LIGHT_THEME_RESET
from data.mock_data import MOCK_STUDENTS, MOCK_KNOWLEDGE_TOPICS

def render_teacher_students_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_teacher_sidebar("students")
    
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:4px;">🎓 学生管理</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">查看和管理所有学生信息</div>
    </div>
    """, unsafe_allow_html=True)

    col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
    with col_t1:
        search = st.text_input("", placeholder="🔍 搜索学生...", key="student_search", label_visibility="collapsed")
    with col_t2:
        st.selectbox("", ["全部班级", "计科2101", "计科2102"], key="student_class", label_visibility="collapsed")
    with col_t3:
        st.selectbox("", ["全部状态", "已绑定", "未绑定"], key="student_status", label_visibility="collapsed")

    st.markdown("---")

    for student in MOCK_STUDENTS:
        status_color = ColorTokens.AGENT_GREEN if student["profile_ready"] else ColorTokens.WARNING_RED
        status_text = "已绑定" if student["profile_ready"] else "未绑定"
        
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="display:flex;align-items:center;gap:14px;">
                    <div style="width:48px;height:48px;border-radius:50%;background:{ColorTokens.LIGHT_BLUE};
                        display:flex;align-items:center;justify-content:center;font-size:24px;">
                        {student['name'][0]}
                    </div>
                    <div>
                        <div style="font-size:14px;font-weight:700;color:{ColorTokens.DARK_GRAY};">
                            {student['name']}
                            <span style="font-size:11px;font-weight:400;color:{ColorTokens.LIGHT_GRAY};margin-left:8px;">
                                {student['id']}
                            </span>
                        </div>
                        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};margin-top:2px;">
                            {student['class']}
                        </div>
                    </div>
                </div>
                
                <div style="display:flex;gap:12px;align-items:center;">
                    <div style="text-align:right;">
                        <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};">平均掌握度</div>
                        <div style="font-size:16px;font-weight:700;color:{ColorTokens.PRIMARY};">{student['avg_score']}%</div>
                    </div>
                    
                    <span style="font-size:10px;color:{status_color};font-weight:600;
                        background:{status_color}15;padding:4px 10px;border-radius:8px;">
                        {status_text}
                    </span>
                    
                    <button style="padding:8px 16px;border:none;border-radius:8px;
                        background:{ColorTokens.LIGHT_BLUE};color:{ColorTokens.PRIMARY};font-size:12px;font-weight:600;
                        cursor:pointer;">
                        查看画像
                    </button>
                </div>
            </div>
            
            {f'''
            <div style="margin-top:12px;padding-top:12px;border-top:1px solid {ColorTokens.CARD_BORDER};">
                <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:8px;">生成资源 ({student['resources_count']})</div>
                <div style="display:flex;gap:6px;flex-wrap:wrap;">
                    {'📝' * (student['resources_count'] // 3)}{'📋' * ((student['resources_count'] % 3))}
                </div>
            </div>
            ''' if student['profile_ready'] else ''}
        </div>
        """, unsafe_allow_html=True)
