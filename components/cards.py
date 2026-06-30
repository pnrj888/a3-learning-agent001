"""
可复用UI组件 - 智能体卡片、资源卡片、统计卡片等
"""
import streamlit as st
from design_system import ColorTokens

def render_kpi_card(title: str, value: str, icon: str = "", color: str = ColorTokens.PRIMARY):
    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:14px;border:1px solid {ColorTokens.CARD_BORDER};text-align:center;">
        <div style="font-size:24px;margin-bottom:4px;">{icon}</div>
        <div style="font-size:22px;font-weight:800;color:{color};margin-bottom:4px;">{value}</div>
        <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};">{title}</div>
    </div>
    """, unsafe_allow_html=True)

def render_agent_card(agent: dict):
    status_colors = {
        "idle": ColorTokens.LIGHT_GRAY,
        "processing": "#F59E0B",
        "success": ColorTokens.AGENT_GREEN,
        "failed": ColorTokens.WARNING_RED
    }
    
    status_color = status_colors.get(agent.get("status", "idle"), ColorTokens.LIGHT_GRAY)
    
    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};
        border-left:4px solid {agent.get('color', ColorTokens.PRIMARY)};text-align:center;">
        <div style="font-size:32px;margin-bottom:8px;">{agent['icon']}</div>
        <div style="font-size:13px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:4px;">
            {agent['name']}
        </div>
        <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};margin-bottom:8px;">
            {agent['desc']}
        </div>
        <span style="font-size:10px;color:{status_color};font-weight:600;
            background:{status_color}15;padding:3px 8px;border-radius:6px;">
            {agent.get('status', 'idle')}
        </span>
    </div>
    """, unsafe_allow_html=True)

def render_resource_card(resource: dict):
    type_colors = {
        "lecture": "#2563EB",
        "exam": "#F59E0B",
        "mindmap": "#8B5CF6",
        "ppt": "#EF4444",
        "video": "#10B981"
    }
    
    card_color = type_colors.get(resource.get("type", "lecture"), ColorTokens.PRIMARY)
    
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};
        margin-bottom:12px;transition:all 0.3s;cursor:pointer;">
        <div style="display:flex;gap:14px;">
            <div style="width:56px;height:56px;border-radius:12px;background:{card_color}15;
                display:flex;align-items:center;justify-content:center;font-size:28px;">
                {resource.get('icon', '📄')}
            </div>
            <div style="flex:1;">
                <div style="font-size:14px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:4px;">
                    {resource['title']}
                </div>
                <div style="font-size:11px;color:{ColorTokens.LIGHT_GRAY};">
                    {resource.get('meta', '')}
                </div>
            </div>
            <div style="display:flex;flex-direction:column;justify-content:center;gap:6px;">
                <button style="padding:6px 12px;border:none;border-radius:6px;
                    background:{ColorTokens.LIGHT_BLUE};color:{ColorTokens.PRIMARY};font-size:11px;font-weight:600;
                    cursor:pointer;">
                    查看
                </button>
                <button style="padding:6px 12px;border:none;border-radius:6px;
                    background:{ColorTokens.BG_GRAY};color:{ColorTokens.MID_GRAY};font-size:11px;font-weight:600;
                    cursor:pointer;">
                    下载
                </button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_student_card(student: dict):
    status_color = ColorTokens.AGENT_GREEN if student.get("profile_ready") else ColorTokens.WARNING_RED
    status_text = "已绑定" if student.get("profile_ready") else "未绑定"
    
    st.markdown(f"""
    <div style="background:white;border-radius:14px;padding:16px;border:1px solid {ColorTokens.CARD_BORDER};
        margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div style="display:flex;align-items:center;gap:14px;">
                <div style="width:48px;height:48px;border-radius:50%;background:{ColorTokens.LIGHT_BLUE};
                    display:flex;align-items:center;justify-content:center;font-size:24px;">
                    {student['name'][0]}
                </div>
                <div>
                    <div style="font-size:14px;font-weight:700;color:{ColorTokens.DARK_GRAY};">
                        {student['name']}
                    </div>
                    <div style="font-size:12px;color:{ColorTokens.LIGHT_GRAY};margin-top:2px;">
                        {student['id']} · {student['class']}
                    </div>
                </div>
            </div>
            <span style="font-size:10px;color:{status_color};font-weight:600;
                background:{status_color}15;padding:4px 10px;border-radius:8px;">
                {status_text}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_alert(message: str, type: str = "info"):
    type_config = {
        "info": {"bg": "#FEF3C7", "border": "#FCD34D", "text": "#92400E", "icon": "💡"},
        "success": {"bg": "#ECFDF5", "border": "#10B981", "text": "#065F46", "icon": "✅"},
        "warning": {"bg": "#FEF2F2", "border": "#EF4444", "text": "#991B1B", "icon": "⚠️"},
        "error": {"bg": "#FEF2F2", "border": "#EF4444", "text": "#991B1B", "icon": "❌"}
    }
    
    config = type_config.get(type, type_config["info"])
    
    st.markdown(f"""
    <div style="background:{config['bg']};border-radius:10px;padding:12px 16px;margin-bottom:16px;
        border:1px solid {config['border']};">
        <div style="display:flex;align-items:center;gap:8px;font-size:12px;color:{config['text']};">
            <span>{config['icon']}</span>
            <span>{message}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_empty_state(title: str, description: str, icon: str = "📭"):
    st.markdown(f"""
    <div style="text-align:center;padding:40px;">
        <div style="font-size:48px;margin-bottom:16px;">{icon}</div>
        <div style="font-size:16px;font-weight:700;color:{ColorTokens.DARK_GRAY};margin-bottom:8px;">
            {title}
        </div>
        <div style="font-size:13px;color:{ColorTokens.LIGHT_GRAY};">
            {description}
        </div>
    </div>
    """, unsafe_allow_html=True)
