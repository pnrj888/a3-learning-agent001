"""
启动页面 - 角色选择入口
"""
import streamlit as st
from design_system import ColorTokens, inject_design_system

def render_splash_page():
    inject_design_system()
    
    st.markdown(f"""
    <div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;
        background:linear-gradient(135deg, {ColorTokens.PRIMARY} 0%, {ColorTokens.AGENT_GREEN} 100%);padding:40px;">
        
        <div style="text-align:center;margin-bottom:40px;">
            <div style="font-size:64px;margin-bottom:20px;">🎓</div>
            <div style="font-size:32px;font-weight:800;color:white;margin-bottom:8px;">
                A3 智能学习助手
            </div>
            <div style="font-size:14px;color:rgba(255,255,255,0.8);">
                基于大模型的个性化资源生成与学习多智能体系统
            </div>
        </div>

        <div style="width:100%;max-width:400px;display:flex;flex-direction:column;gap:16px;">
            <div style="background:white;border-radius:16px;padding:24px;box-shadow:0 10px 40px rgba(0,0,0,0.15);">
                <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:20px;text-align:center;">
                    请选择角色
                </div>
                
                <button onclick="window.location.href='?role=student'" 
                    style="width:100%;padding:14px;border:none;border-radius:12px;
                        background:linear-gradient(135deg, {ColorTokens.PRIMARY} 0%, #1D4ED8 100%);
                        color:white;font-size:16px;font-weight:600;cursor:pointer;
                        transition:all 0.3s;display:flex;align-items:center;justify-content:center;gap:10px;
                        box-shadow:0 4px 15px rgba(37,99,235,0.3);margin-bottom:12px;">
                    <span>🎓</span>
                    <span>进入学生端</span>
                </button>
                
                <button onclick="window.location.href='?role=teacher'" 
                    style="width:100%;padding:14px;border:none;border-radius:12px;
                        background:white;color:{ColorTokens.DARK_GRAY};font-size:16px;font-weight:600;
                        cursor:pointer;transition:all 0.3s;display:flex;align-items:center;justify-content:center;gap:10px;
                        border:2px solid {ColorTokens.CARD_BORDER};">
                    <span>🏫</span>
                    <span>进入教师管理后台</span>
                </button>
            </div>

            <div style="text-align:center;">
                <div style="font-size:12px;color:rgba(255,255,255,0.6);">
                    Powered by 科大讯飞星火大模型
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
