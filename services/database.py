"""
统一数据库服务层 - 基于 SQLite 的 ORM 封装
支持学生画像、学习资源、问答记录、用户管理等核心业务
"""
import sqlite3
import os
from typing import Optional, Dict, List, Any
from datetime import datetime
import json

class DatabaseService:
    def __init__(self, db_path: str = "data/database/app.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_tables(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'student',
                name TEXT,
                email TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_profiles (
                id TEXT PRIMARY KEY,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT,
                student_id TEXT,
                major TEXT,
                grade TEXT,
                prerequisites TEXT DEFAULT '[]',
                learning_style TEXT,
                interest_preferences TEXT DEFAULT '[]',
                time_habits TEXT DEFAULT '{}',
                goals TEXT DEFAULT '[]',
                weak_points TEXT DEFAULT '[]',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_resources (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                metadata TEXT DEFAULT '{}',
                source TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT,
                sources TEXT DEFAULT '[]',
                accuracy REAL DEFAULT 0.0,
                is_hallucination INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_mastery (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                level INTEGER DEFAULT 0,
                last_practiced TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, topic)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generation_logs (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                task_type TEXT,
                topic TEXT,
                status TEXT DEFAULT 'pending',
                duration REAL DEFAULT 0.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return [dict(row) for row in results]

    def execute_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        results = self.execute(query, params)
        return results[0] if results else None

    def execute_non_query(self, query: str, params: tuple = ()) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rowcount = cursor.rowcount
        conn.commit()
        conn.close()
        return rowcount

    # === 用户管理 ===
    def create_user(self, user_id: str, username: str, password: str, role: str = "student", name: str = "") -> bool:
        try:
            self.execute_non_query('''
                INSERT INTO users (id, username, password, role, name)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, password, role, name))
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        return self.execute_one('SELECT * FROM users WHERE username = ?', (username,))

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        return self.execute_one('SELECT * FROM users WHERE id = ?', (user_id,))

    # === 学生画像 ===
    def create_or_update_profile(self, user_id: str, data: Dict) -> bool:
        profile = self.execute_one('SELECT id FROM student_profiles WHERE user_id = ?', (user_id,))
        if profile:
            self.execute_non_query('''
                UPDATE student_profiles SET 
                    name = ?, student_id = ?, major = ?, grade = ?,
                    prerequisites = ?, learning_style = ?, interest_preferences = ?,
                    time_habits = ?, goals = ?, weak_points = ?, updated_at = ?
                WHERE user_id = ?
            ''', (
                data.get('name', ''), data.get('student_id', ''), data.get('major', ''),
                data.get('grade', ''), json.dumps(data.get('prerequisites', [])),
                data.get('learning_style', ''), json.dumps(data.get('interest_preferences', [])),
                json.dumps(data.get('time_habits', {})), json.dumps(data.get('goals', [])),
                json.dumps(data.get('weak_points', [])), datetime.now().isoformat(), user_id
            ))
        else:
            from uuid import uuid4
            self.execute_non_query('''
                INSERT INTO student_profiles (id, user_id, name, student_id, major, grade,
                    prerequisites, learning_style, interest_preferences, time_habits, goals, weak_points)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid4())[:8], user_id, data.get('name', ''), data.get('student_id', ''),
                data.get('major', ''), data.get('grade', ''), json.dumps(data.get('prerequisites', [])),
                data.get('learning_style', ''), json.dumps(data.get('interest_preferences', [])),
                json.dumps(data.get('time_habits', {})), json.dumps(data.get('goals', [])),
                json.dumps(data.get('weak_points', []))
            ))
        return True

    def get_profile_by_user_id(self, user_id: str) -> Optional[Dict]:
        profile = self.execute_one('SELECT * FROM student_profiles WHERE user_id = ?', (user_id,))
        if profile:
            profile['prerequisites'] = json.loads(profile['prerequisites'])
            profile['interest_preferences'] = json.loads(profile['interest_preferences'])
            profile['time_habits'] = json.loads(profile['time_habits'])
            profile['goals'] = json.loads(profile['goals'])
            profile['weak_points'] = json.loads(profile['weak_points'])
        return profile

    # === 学习资源 ===
    def create_resource(self, user_id: str, resource_type: str, title: str, content: str, metadata: Dict = None) -> str:
        from uuid import uuid4
        rid = str(uuid4())[:8]
        self.execute_non_query('''
            INSERT INTO learning_resources (id, user_id, type, title, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (rid, user_id, resource_type, title, content, json.dumps(metadata or {})))
        return rid

    def get_resources_by_user(self, user_id: str, limit: int = 20) -> List[Dict]:
        resources = self.execute('''
            SELECT * FROM learning_resources WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
        ''', (user_id, limit))
        for r in resources:
            r['metadata'] = json.loads(r['metadata'])
        return resources

    # === 问答记录 ===
    def create_qa_record(self, user_id: str, question: str, answer: str, sources: List[str] = None, accuracy: float = 0.0) -> str:
        from uuid import uuid4
        qid = str(uuid4())[:8]
        self.execute_non_query('''
            INSERT INTO qa_records (id, user_id, question, answer, sources, accuracy)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (qid, user_id, question, answer, json.dumps(sources or []), accuracy))
        return qid

    def get_qa_records(self, user_id: str, limit: int = 20) -> List[Dict]:
        records = self.execute('''
            SELECT * FROM qa_records WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
        ''', (user_id, limit))
        for r in records:
            r['sources'] = json.loads(r['sources'])
        return records

    # === 知识掌握度 ===
    def update_mastery(self, user_id: str, topic: str, level: int) -> bool:
        existing = self.execute_one('''
            SELECT id FROM knowledge_mastery WHERE user_id = ? AND topic = ?
        ''', (user_id, topic))
        if existing:
            self.execute_non_query('''
                UPDATE knowledge_mastery SET level = ?, updated_at = ? WHERE user_id = ? AND topic = ?
            ''', (level, datetime.now().isoformat(), user_id, topic))
        else:
            from uuid import uuid4
            self.execute_non_query('''
                INSERT INTO knowledge_mastery (id, user_id, topic, level)
                VALUES (?, ?, ?, ?)
            ''', (str(uuid4())[:8], user_id, topic, level))
        return True

    def get_mastery_by_user(self, user_id: str) -> List[Dict]:
        return self.execute('SELECT * FROM knowledge_mastery WHERE user_id = ?', (user_id,))

    # === 生成日志 ===
    def create_generation_log(self, user_id: str, agent_name: str, task_type: str, topic: str) -> str:
        from uuid import uuid4
        lid = str(uuid4())[:8]
        self.execute_non_query('''
            INSERT INTO generation_logs (id, user_id, agent_name, task_type, topic)
            VALUES (?, ?, ?, ?, ?)
        ''', (lid, user_id, agent_name, task_type, topic))
        return lid

    def update_generation_log(self, log_id: str, status: str, duration: float = 0.0):
        self.execute_non_query('''
            UPDATE generation_logs SET status = ?, duration = ? WHERE id = ?
        ''', (status, duration, log_id))

    def get_generation_logs(self, user_id: str, limit: int = 20) -> List[Dict]:
        return self.execute('''
            SELECT * FROM generation_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
        ''', (user_id, limit))

    # === 统计查询 ===
    def get_user_stats(self, user_id: str) -> Dict:
        resources = self.execute('SELECT COUNT(*) as count FROM learning_resources WHERE user_id = ?', (user_id,))
        qa = self.execute('SELECT COUNT(*) as count FROM qa_records WHERE user_id = ?', (user_id,))
        mastery = self.execute('SELECT AVG(level) as avg FROM knowledge_mastery WHERE user_id = ?', (user_id,))
        logs = self.execute('SELECT agent_name, COUNT(*) as count FROM generation_logs WHERE user_id = ? GROUP BY agent_name', (user_id,))
        
        return {
            'resource_count': resources[0]['count'] if resources else 0,
            'qa_count': qa[0]['count'] if qa else 0,
            'avg_mastery': round(mastery[0]['avg'], 1) if mastery[0]['avg'] else 0,
            'agent_stats': {r['agent_name']: r['count'] for r in logs}
        }

    def get_all_students(self) -> List[Dict]:
        students = self.execute('SELECT * FROM users WHERE role = "student"')
        result = []
        for student in students:
            profile = self.get_profile_by_user_id(student['id'])
            stats = self.get_user_stats(student['id'])
            result.append({
                **student,
                'profile': profile,
                'stats': stats
            })
        return result

db = DatabaseService()
