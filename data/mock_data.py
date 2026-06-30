"""
模拟数据模块 - 提供测试用的静态数据
"""
MOCK_STUDENTS = [
    {"id": "2024001", "name": "张三", "class": "计科2101", "profile_ready": True, "resources_count": 6, "avg_score": 78, "weak_count": 3, "last_active": "2026-06-29 14:30"},
    {"id": "2024002", "name": "李四", "class": "计科2101", "profile_ready": True, "resources_count": 5, "avg_score": 85, "weak_count": 1, "last_active": "2026-06-29 15:10"},
    {"id": "2024003", "name": "王五", "class": "计科2102", "profile_ready": True, "resources_count": 8, "avg_score": 62, "weak_count": 5, "last_active": "2026-06-29 11:45"},
    {"id": "2024004", "name": "赵六", "class": "计科2102", "profile_ready": False, "resources_count": 0, "avg_score": 0, "weak_count": 0, "last_active": "-"},
    {"id": "2024005", "name": "孙七", "class": "计科2101", "profile_ready": True, "resources_count": 4, "avg_score": 91, "weak_count": 0, "last_active": "2026-06-29 09:20"},
    {"id": "2024006", "name": "周八", "class": "计科2102", "profile_ready": True, "resources_count": 3, "avg_score": 55, "weak_count": 6, "last_active": "2026-06-28 16:50"},
]

MOCK_KB_FILES = [
    {"name": "computer_network_ch01.pdf", "size": "2.3 MB", "chunks": 12, "status": "indexed", "date": "2026-06-20"},
    {"name": "computer_network_ch02.pdf", "size": "1.8 MB", "chunks": 10, "status": "indexed", "date": "2026-06-20"},
    {"name": "tcp_ip_protocols.pdf", "size": "3.1 MB", "chunks": 8, "status": "indexed", "date": "2026-06-21"},
    {"name": "network_security_basics.pdf", "size": "2.7 MB", "chunks": 10, "status": "indexed", "date": "2026-06-22"},
    {"name": "socket_programming_guide.pdf", "size": "1.5 MB", "chunks": 6, "status": "pending", "date": "2026-06-28"},
    {"name": "http_protocol_deep_dive.pdf", "size": "4.2 MB", "chunks": 15, "status": "indexed", "date": "2026-06-23"},
]

MOCK_GENERATION_LOGS = [
    {"time": "2026-06-29 15:30:22", "student": "张三", "type": "lecture", "topic": "TCP/IP协议", "status": "success", "duration": "3.2s", "agent_count": 5},
    {"time": "2026-06-29 15:30:18", "student": "李四", "type": "exam", "topic": "路由算法", "status": "success", "duration": "2.8s", "agent_count": 5},
    {"time": "2026-06-29 15:15:45", "student": "王五", "type": "mindmap", "topic": "OSI模型", "status": "success", "duration": "2.1s", "agent_count": 4},
    {"time": "2026-06-29 15:12:10", "student": "赵六", "type": "lecture", "topic": "HTTP/HTTPS", "status": "failed", "duration": "-", "agent_count": 2},
    {"time": "2026-06-29 14:55:33", "student": "张三", "type": "plan", "topic": "综合学习路线", "status": "success", "duration": "4.5s", "agent_count": 5},
    {"time": "2026-06-29 14:40:01", "student": "孙七", "type": "extend", "topic": "网络安全", "status": "success", "duration": "1.9s", "agent_count": 3},
    {"time": "2026-06-29 14:30:15", "student": "李四", "type": "ppt", "topic": "传输层详解", "status": "success", "duration": "3.7s", "agent_count": 5},
    {"time": "2026-06-29 14:20:50", "student": "周八", "type": "exam", "topic": "IP寻址", "status": "warning", "duration": "5.1s", "agent_count": 5},
    {"time": "2026-06-29 13:45:12", "student": "王五", "type": "lecture", "topic": "子网划分", "status": "success", "duration": "2.4s", "agent_count": 5},
    {"time": "2026-06-29 13:30:00", "student": "张三", "type": "video", "topic": "TCP三次握手动画", "status": "success", "duration": "8.2s", "agent_count": 5},
]

MOCK_KNOWLEDGE_TOPICS = [
    {"topic": "OSI参考模型", "level": 8, "color": "#10B981"},
    {"topic": "TCP/IP协议", "level": 5, "color": "#F59E0B"},
    {"topic": "UDP协议", "level": 9, "color": "#10B981"},
    {"topic": "TCP拥塞控制", "level": 2, "color": "#EF4444"},
    {"topic": "物理层基础", "level": 7, "color": "#10B981"},
    {"topic": "IP路由算法", "level": 4, "color": "#EF4444"},
    {"topic": "子网划分", "level": 6, "color": "#F59E0B"},
    {"topic": "网络安全协议", "level": 3, "color": "#EF4444"},
    {"topic": "HTTP/HTTPS", "level": 5, "color": "#F59E0B"},
    {"topic": "应用层协议", "level": 8, "color": "#10B981"},
    {"topic": "DNS解析", "level": 4, "color": "#F59E0B"},
    {"topic": "DHCP协议", "level": 6, "color": "#F59E0B"},
    {"topic": "IPv6基础", "level": 3, "color": "#EF4444"},
    {"topic": "Socket编程", "level": 7, "color": "#10B981"},
    {"topic": "VLAN", "level": 5, "color": "#F59E0B"},
    {"topic": "数据链路层", "level": 8, "color": "#10B981"},
]

MOCK_RESOURCES = [
    {"id": "res001", "type": "lecture", "title": "TCP/IP协议详解", "icon": "📝", "meta": "2026-06-29 · 1200字"},
    {"id": "res002", "type": "exam", "title": "网络基础测试题", "icon": "📋", "meta": "2026-06-29 · 10道题"},
    {"id": "res003", "type": "mindmap", "title": "OSI七层模型思维导图", "icon": "🧠", "meta": "2026-06-28 · 32节点"},
    {"id": "res004", "type": "ppt", "title": "传输层协议PPT", "icon": "📊", "meta": "2026-06-28 · 24页"},
    {"id": "res005", "type": "video", "title": "TCP三次握手动画", "icon": "🎬", "meta": "2026-06-27 · 3分钟"},
]

MOCK_AGENTS = [
    {"name": "ProfileAgent", "icon": "👤", "desc": "画像采集", "color": "#2563EB"},
    {"name": "PlannerAgent", "icon": "📋", "desc": "路径规划", "color": "#10B981"},
    {"name": "ResourceAgent", "icon": "📦", "desc": "资源生成", "color": "#8B5CF6"},
    {"name": "QuizAgent", "icon": "📝", "desc": "习题生成", "color": "#F59E0B"},
    {"name": "ReviewAgent", "icon": "✅", "desc": "质量审核", "color": "#EF4444"},
]

MOCK_QA_EXAMPLES = [
    {"question": "TCP三次握手的过程是怎样的？", "answer": "TCP三次握手包括：1. SYN（客户端请求连接）；2. SYN+ACK（服务器确认并请求连接）；3. ACK（客户端确认）。"},
    {"question": "OSI七层模型各层功能是什么？", "answer": "应用层：应用程序接口；表示层：数据格式转换；会话层：建立会话；传输层：端到端传输；网络层：路由选择；数据链路层：帧传输；物理层：比特传输。"},
    {"question": "HTTP和HTTPS有什么区别？", "answer": "HTTP明文传输，端口80；HTTPS加密传输，端口443。HTTPS使用SSL/TLS协议。"},
]
