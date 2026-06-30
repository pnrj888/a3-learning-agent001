"""
教师端系统设置页面 - LLM配置 + 系统参数 + 日志管理
"""
import streamlit as st
from design_system import ColorTokens, render_teacher_sidebar, LIGHT_THEME_RESET

def render_teacher_settings_page():
    st.markdown(LIGHT_THEME_RESET, unsafe_allow_html=True)
    render_teacher_sidebar("settings")
    
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="font-size:20px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:4px;">⚙️ 系统设置</div>
        <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">管理系统配置和参数</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["LLM配置", "系统参数", "日志管理"])

    with tab1:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:20px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
            <div style="font-size:14px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:16px;">
                🤖 大模型配置
            </div>
            
            <div style="margin-bottom:16px;">
                <div style="font-size:12px;font-weight:600;color:{ColorTokens.MID_GRAY};margin-bottom:8px;">
                    模型模式
                </div>
                <select style="width:100%;padding:12px;border-radius:10px;border:1.5px solid {ColorTokens.CARD_BORDER};
                    font-size:14px;">
                    <option>Mock模式（默认）</option>
                    <option>讯飞星火大模型</option>
                </select>
            </div>
            
            <div style="margin-bottom:16px;">
                <div style="font-size:12px;font-weight:600;color:{ColorTokens.MID_GRAY};margin-bottom:8px;">
                    API Key
                </div>
                <input type="password" placeholder="请输入讯飞API Key"
                    style="width:100%;padding:12px;border-radius:10px;border:1.5px solid {ColorTokens.CARD_BORDER};
                        font-size:14px;">
            </div>
            
            <div style="margin-bottom:16px;">
                <div style="font-size:12px;font-weight:600;color:{ColorTokens.MID_GRAY};margin-bottom:8px;">
                    App ID
                </div>
                <input type="text" placeholder="请输入App ID"
                    style="width:100%;padding:12px;border-radius:10px;border:1.5px solid {ColorTokens.CARD_BORDER};
                        font-size:14px;">
            </div>
            
            <div style="margin-bottom:16px;">
                <div style="font-size:12px;font-weight:600;color:{ColorTokens.MID_GRAY};margin-bottom:8px;">
                    API Secret
                </div>
                <input type="password" placeholder="请输入API Secret"
                    style="width:100%;padding:12px;border-radius:10px;border:1.5px solid {ColorTokens.CARD_BORDER};
                        font-size:14px;">
            </div>
            
            <div style="display:flex;gap:12px;">
                <button style="flex:1;padding:12px;border:none;border-radius:10px;
                    background:{ColorTokens.PRIMARY};color:white;font-size:14px;font-weight:600;
                    cursor:pointer;">
                    保存配置
                </button>
                <button style="padding:12px 24px;border:none;border-radius:10px;
                    background:{ColorTokens.BG_GRAY};color:{ColorTokens.MID_GRAY};font-size:14px;font-weight:600;
                    cursor:pointer;">
                    测试连接
                </button>
            </div>
        </div>
        
        <div style="background:#FEF3C7;border-radius:10px;padding:12px 16px;border:1px solid #FCD34D;">
            <div style="display:flex;align-items:center;gap:8px;font-size:12px;color:#92400E;">
                <span>💡</span>
                <span>配置完成后，系统会自动切换到真实API模式。建议先在Mock模式下测试功能。</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:20px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
            <div style="font-size:14px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:16px;">
                📊 智能体参数
            </div>
            
            <div style="margin-bottom:16px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                    <span style="font-size:12px;font-weight:600;color:{ColorTokens.MID_GRAY};">温度系数</span>
                    <span style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">0.7</span>
                </div>
                <input type="range" min="0" max="1" step="0.1" value="0.7"
                    style="width:100%;">
            </div>
            
            <div style="margin-bottom:16px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                    <span style="font-size:12px;font-weight:600;color:{ColorTokens.MID_GRAY};">最大输出长度</span>
                    <span style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};">2000</span>
                </div>
                <input type="range" min="500" max="5000" step="100" value="2000"
                    style="width:100%;">
            </div>
            
            <button style="width:100%;padding:12px;border:none;border-radius:10px;
                background:{ColorTokens.PRIMARY};color:white;font-size:14px;font-weight:600;
                cursor:pointer;">
                保存参数
            </button>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown(f"""
        <div style="background:white;border-radius:14px;padding:20px;border:1px solid {ColorTokens.CARD_BORDER};margin-bottom:16px;">
            <div style="font-size:14px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:16px;">
                📋 日志管理
            </div>
            
            <div style="display:flex;gap:12px;margin-bottom:16px;">
                <button style="flex:1;padding:12px;border:none;border-radius:10px;
                    background:{ColorTokens.BG_GRAY};color:{ColorTokens.MID_GRAY};font-size:14px;font-weight:600;
                    cursor:pointer;">
                    导出日志
                </button>
                <button style="flex:1;padding:12px;border:none;border-radius:10px;
                    background:{ColorTokens.WARNING_RED};color:white;font-size:14px;font-weight:600;
                    cursor:pointer;">
                    清空日志
                </button>
            </div>
            
            <div style="background:{ColorTokens.BG_GRAY};border-radius:10px;padding:16px;max-height:300px;overflow-y:auto;">
                <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};line-height:1.6;">
                    [2026-06-29 15:30:22] INFO - ProfileAgent 完成学生画像采集<br>
                    [2026-06-29 15:30:18] INFO - PlannerAgent 生成学习路径<br>
                    [2026-06-29 15:15:45] INFO - ResourceAgent 生成讲义成功<br>
                    [2026-06-29 15:12:10] ERROR - QuizAgent 生成习题失败<br>
                    [2026-06-29 14:55:33] INFO - ReviewAgent 审核通过<br>
                    [2026-06-29 14:40:01] INFO - ResourceAgent 生成思维导图成功<br>
                    [2026-06-29 14:30:15] INFO - ProfileAgent 更新学生画像<br>
                    [2026-06-29 14:20:50] WARN - 学生掌握度低于阈值<br>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
