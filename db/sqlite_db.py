import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DatabaseConfig


class SQLiteDB:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DatabaseConfig.SQLITE_PATH
        self._ensure_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_tables(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_profile (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                grade TEXT DEFAULT '',
                subject TEXT DEFAULT '',
                prerequisites TEXT DEFAULT '[]',
                learning_style TEXT DEFAULT '',
                weak_points TEXT DEFAULT '[]',
                error_prone_types TEXT DEFAULT '[]',
                learning_goals TEXT DEFAULT '[]',
                daily_rhythm TEXT DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resource_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_title TEXT NOT NULL,
                resource_path TEXT DEFAULT '',
                resource_data TEXT DEFAULT '',
                generate_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                duration REAL DEFAULT 0.0,
                status TEXT DEFAULT 'success',
                FOREIGN KEY (student_id) REFERENCES student_profile(student_id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_resource_student_id ON resource_record(student_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_resource_type ON resource_record(resource_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_resource_time ON resource_record(generate_time)
        """)

        conn.commit()
        conn.close()

    def insert_profile(self, data: Dict[str, Any]) -> bool:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO student_profile 
                (student_id, name, grade, subject, prerequisites, learning_style, 
                 weak_points, error_prone_types, learning_goals, daily_rhythm, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("student_id"),
                data.get("name"),
                data.get("grade", ""),
                data.get("subject", ""),
                json.dumps(data.get("prerequisites", []), ensure_ascii=False),
                data.get("learning_style", ""),
                json.dumps(data.get("weak_points", []), ensure_ascii=False),
                json.dumps(data.get("error_prone_types", []), ensure_ascii=False),
                json.dumps(data.get("learning_goals", []), ensure_ascii=False),
                json.dumps(data.get("daily_rhythm", {}), ensure_ascii=False),
                data.get("created_at", datetime.now().isoformat()),
                data.get("updated_at", datetime.now().isoformat())
            ))
            conn.commit()
            return True
        except sqlite3.Error as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    def update_profile(self, student_id: str, data: Dict[str, Any]) -> bool:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            set_clauses = []
            params = []

            if "name" in data:
                set_clauses.append("name = ?")
                params.append(data["name"])
            if "grade" in data:
                set_clauses.append("grade = ?")
                params.append(data["grade"])
            if "subject" in data:
                set_clauses.append("subject = ?")
                params.append(data["subject"])
            if "prerequisites" in data:
                set_clauses.append("prerequisites = ?")
                params.append(json.dumps(data["prerequisites"], ensure_ascii=False))
            if "learning_style" in data:
                set_clauses.append("learning_style = ?")
                params.append(data["learning_style"])
            if "weak_points" in data:
                set_clauses.append("weak_points = ?")
                params.append(json.dumps(data["weak_points"], ensure_ascii=False))
            if "error_prone_types" in data:
                set_clauses.append("error_prone_types = ?")
                params.append(json.dumps(data["error_prone_types"], ensure_ascii=False))
            if "learning_goals" in data:
                set_clauses.append("learning_goals = ?")
                params.append(json.dumps(data["learning_goals"], ensure_ascii=False))
            if "daily_rhythm" in data:
                set_clauses.append("daily_rhythm = ?")
                params.append(json.dumps(data["daily_rhythm"], ensure_ascii=False))

            set_clauses.append("updated_at = ?")
            params.append(datetime.now().isoformat())

            params.append(student_id)

            if set_clauses:
                cursor.execute(f"""
                    UPDATE student_profile SET {', '.join(set_clauses)} WHERE student_id = ?
                """, params)
                conn.commit()

            return True
        except sqlite3.Error as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_profile(self, student_id: str) -> Optional[Dict[str, Any]]:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM student_profile WHERE student_id = ?
            """, (student_id,))

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                result = dict(zip(columns, row))

                result["prerequisites"] = json.loads(result["prerequisites"])
                result["weak_points"] = json.loads(result["weak_points"])
                result["error_prone_types"] = json.loads(result["error_prone_types"])
                result["learning_goals"] = json.loads(result["learning_goals"])
                result["daily_rhythm"] = json.loads(result["daily_rhythm"])

                return result
            return None
        except sqlite3.Error as e:
            return None
        finally:
            conn.close()

    def list_profiles(self, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            offset = (page - 1) * page_size
            cursor.execute("""
                SELECT * FROM student_profile ORDER BY created_at DESC LIMIT ? OFFSET ?
            """, (page_size, offset))

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in rows:
                result = dict(zip(columns, row))
                result["prerequisites"] = json.loads(result["prerequisites"])
                result["weak_points"] = json.loads(result["weak_points"])
                result["error_prone_types"] = json.loads(result["error_prone_types"])
                result["learning_goals"] = json.loads(result["learning_goals"])
                result["daily_rhythm"] = json.loads(result["daily_rhythm"])
                results.append(result)

            return results
        except sqlite3.Error as e:
            return []
        finally:
            conn.close()

    def delete_profile(self, student_id: str) -> bool:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM resource_record WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM student_profile WHERE student_id = ?", (student_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    def save_resource(self, data: Dict[str, Any]) -> int:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO resource_record 
                (student_id, resource_type, resource_title, resource_path, 
                 resource_data, generate_time, duration, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("student_id"),
                data.get("resource_type"),
                data.get("resource_title"),
                data.get("resource_path", ""),
                data.get("resource_data", ""),
                data.get("generate_time", datetime.now().isoformat()),
                data.get("duration", 0.0),
                data.get("status", "success")
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            conn.rollback()
            return -1
        finally:
            conn.close()

    def get_resource(self, resource_id: int) -> Optional[Dict[str, Any]]:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM resource_record WHERE id = ?
            """, (resource_id,))

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        except sqlite3.Error as e:
            return None
        finally:
            conn.close()

    def get_student_resources(self, student_id: str, resource_type: Optional[str] = None,
                            page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            offset = (page - 1) * page_size

            if resource_type:
                cursor.execute("""
                    SELECT * FROM resource_record 
                    WHERE student_id = ? AND resource_type = ?
                    ORDER BY generate_time DESC LIMIT ? OFFSET ?
                """, (student_id, resource_type, page_size, offset))
            else:
                cursor.execute("""
                    SELECT * FROM resource_record 
                    WHERE student_id = ?
                    ORDER BY generate_time DESC LIMIT ? OFFSET ?
                """, (student_id, page_size, offset))

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            return []
        finally:
            conn.close()

    def get_resource_stats(self, student_id: Optional[str] = None) -> Dict[str, Any]:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            if student_id:
                cursor.execute("""
                    SELECT resource_type, COUNT(*) as count, AVG(duration) as avg_duration
                    FROM resource_record WHERE student_id = ? GROUP BY resource_type
                """, (student_id,))
            else:
                cursor.execute("""
                    SELECT resource_type, COUNT(*) as count, AVG(duration) as avg_duration
                    FROM resource_record GROUP BY resource_type
                """)

            rows = cursor.fetchall()
            stats = {"by_type": {}}
            for row in rows:
                stats["by_type"][row[0]] = {
                    "count": row[1],
                    "avg_duration": round(row[2], 2) if row[2] else 0.0
                }

            if student_id:
                cursor.execute("SELECT COUNT(*) FROM resource_record WHERE student_id = ?", (student_id,))
                stats["total"] = cursor.fetchone()[0]
            else:
                cursor.execute("SELECT COUNT(*) FROM resource_record")
                stats["total"] = cursor.fetchone()[0]

            return stats
        except sqlite3.Error as e:
            return {"by_type": {}, "total": 0}
        finally:
            conn.close()

    def delete_resource(self, resource_id: int) -> bool:
        conn = self._connect()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM resource_record WHERE id = ?", (resource_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            conn.rollback()
            return False
        finally:
            conn.close()
