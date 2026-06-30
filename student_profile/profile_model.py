import json
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DatabaseConfig


@dataclass
class StudentProfile:
    student_id: str
    name: str
    grade: str = ""
    subject: str = ""
    prerequisites: List[str] = field(default_factory=list)
    learning_style: str = ""
    weak_points: List[str] = field(default_factory=list)
    error_prone_types: List[str] = field(default_factory=list)
    learning_goals: List[str] = field(default_factory=list)
    daily_rhythm: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "StudentProfile":
        data = json.loads(json_str)
        return cls(**data)

    def update_timestamp(self):
        self.updated_at = datetime.now().isoformat()

    def add_weak_point(self, point: str):
        if point not in self.weak_points:
            self.weak_points.append(point)
            self.update_timestamp()

    def add_error_prone_type(self, question_type: str):
        if question_type not in self.error_prone_types:
            self.error_prone_types.append(question_type)
            self.update_timestamp()

    def remove_weak_point(self, point: str):
        if point in self.weak_points:
            self.weak_points.remove(point)
            self.update_timestamp()


class ProfileStorage:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DatabaseConfig.SQLITE_PATH
        self._ensure_table()

    def _ensure_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_profiles (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                grade TEXT,
                subject TEXT,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def save(self, profile: StudentProfile):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        data_json = profile.to_json()
        cursor.execute("""
            INSERT OR REPLACE INTO student_profiles 
            (student_id, name, grade, subject, data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.student_id,
            profile.name,
            profile.grade,
            profile.subject,
            data_json,
            profile.created_at,
            profile.updated_at
        ))
        conn.commit()
        conn.close()

    def get(self, student_id: str) -> Optional[StudentProfile]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM student_profiles WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return StudentProfile.from_json(row[0])
        return None

    def delete(self, student_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student_profiles WHERE student_id = ?", (student_id,))
        conn.commit()
        conn.close()

    def list_all(self) -> List[StudentProfile]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM student_profiles")
        profiles = []
        for row in cursor.fetchall():
            profiles.append(StudentProfile.from_json(row[0]))
        conn.close()
        return profiles
