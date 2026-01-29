#!/usr/bin/env python3
"""
社團資料庫管理系統
"""

import sqlite3
import json
import re
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import requests
from bs4 import BeautifulSoup


class ClubDatabase:
    def __init__(self, db_path='club_data.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化資料庫"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 學期資料表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semesters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                semester TEXT UNIQUE NOT NULL,  -- 例如: "114下", "115上"
                year INTEGER NOT NULL,           -- 例如: 114, 115
                term TEXT NOT NULL,              -- "上" 或 "下"
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_date TEXT                 -- 原始日期字串，如 "2026/3/1"
            )
        ''')

        # 社團資料表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clubs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                semester_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,       -- ClassID (1-50)
                club_number TEXT NOT NULL,       -- 社團編號 (如 "1-7")
                club_name TEXT NOT NULL,         -- 社團名稱
                FOREIGN KEY (semester_id) REFERENCES semesters(id),
                UNIQUE(semester_id, class_id)
            )
        ''')

        # 學生資料表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                club_id INTEGER NOT NULL,
                student_id TEXT,                 -- 學號
                student_name TEXT NOT NULL,      -- 姓名
                grade TEXT,                      -- 年級班級 (如 "1年5班")
                seat_number TEXT,                -- 座號
                FOREIGN KEY (club_id) REFERENCES clubs(id)
            )
        ''')

        # 建立索引加速查詢
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_student_name ON students(student_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_semester ON clubs(semester_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_grade ON students(grade)')

        conn.commit()
        conn.close()

    def parse_semester_from_date(self, date_str: str) -> Tuple[int, str]:
        """
        從日期字串解析學期
        例如: "2026/3/1" -> (114, "下")   # 2026前半年 -> 114下
              "2026/9/1" -> (115, "上")   # 2026後半年 -> 115上
        """
        match = re.search(r'(\d{4})/(\d{1,2})', date_str)
        if not match:
            raise ValueError(f"無法解析日期: {date_str}")

        year = int(match.group(1))
        month = int(match.group(2))

        # 轉換為民國年
        roc_year = year - 1911

        # 判斷學期：1-6月為下學期(前一學年)，7-12月為上學期(當學年)
        if 1 <= month <= 6:
            # 前半年：下學期屬於前一學年
            semester_year = roc_year - 1
            term = "下"
        else:
            # 後半年：上學期屬於當學年
            semester_year = roc_year
            term = "上"

        return semester_year, term

    def get_or_create_semester(self, date_str: str) -> int:
        """取得或建立學期記錄，返回 semester_id"""
        year, term = self.parse_semester_from_date(date_str)
        semester_name = f"{year}{term}"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id FROM semesters WHERE semester = ?
        ''', (semester_name,))

        result = cursor.fetchone()

        if result:
            semester_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO semesters (semester, year, term, source_date)
                VALUES (?, ?, ?, ?)
            ''', (semester_name, year, term, date_str))
            semester_id = cursor.lastrowid
            conn.commit()

        conn.close()
        return semester_id

    def is_semester_cached(self, semester_id: int) -> bool:
        """檢查該學期資料是否已經快取"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM clubs WHERE semester_id = ?
        ''', (semester_id,))

        count = cursor.fetchone()[0]
        conn.close()

        return count > 0

    def save_club(self, semester_id: int, class_id: int, club_number: str, club_name: str) -> int:
        """儲存社團資料，返回 club_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO clubs (semester_id, class_id, club_number, club_name)
            VALUES (?, ?, ?, ?)
        ''', (semester_id, class_id, club_number, club_name))

        club_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return club_id

    def save_student(self, club_id: int, student_name: str, student_id: str = None,
                     grade: str = None, seat_number: str = None):
        """儲存學生資料"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO students (club_id, student_id, student_name, grade, seat_number)
            VALUES (?, ?, ?, ?, ?)
        ''', (club_id, student_id, student_name, grade, seat_number))

        conn.commit()
        conn.close()

    def search_student(self, student_name: str, semester_id: Optional[int] = None,
                      grade: Optional[str] = None) -> List[Dict]:
        """
        搜尋學生
        :param student_name: 學生姓名
        :param semester_id: 學期ID（可選）
        :param grade: 年級班級（可選，如 "1年5班"）
        :return: 學生參加的社團列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''
            SELECT
                s.semester,
                c.class_id,
                c.club_number,
                c.club_name,
                st.student_id,
                st.student_name,
                st.grade,
                st.seat_number
            FROM students st
            JOIN clubs c ON st.club_id = c.id
            JOIN semesters s ON c.semester_id = s.id
            WHERE st.student_name = ?
        '''

        params = [student_name]

        if semester_id:
            query += ' AND c.semester_id = ?'
            params.append(semester_id)

        if grade:
            query += ' AND st.grade = ?'
            params.append(grade)

        query += ' ORDER BY s.semester DESC, c.class_id'

        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                'semester': row[0],
                'class_id': row[1],
                'club_number': row[2],
                'club_name': row[3],
                'student_id': row[4],
                'student_name': row[5],
                'grade': row[6],
                'seat_number': row[7]
            })

        conn.close()
        return results

    def get_latest_semester(self) -> Optional[Tuple[int, str]]:
        """取得最新的學期資料"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, semester FROM semesters
            ORDER BY year DESC,
                     CASE term WHEN '下' THEN 1 ELSE 0 END DESC
            LIMIT 1
        ''')

        result = cursor.fetchone()
        conn.close()

        return result if result else None

    def get_all_semesters(self) -> List[Dict]:
        """取得所有學期列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, semester, year, term, last_updated, source_date
            FROM semesters
            ORDER BY year DESC,
                     CASE term WHEN '下' THEN 1 ELSE 0 END DESC
        ''')

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'semester': row[1],
                'year': row[2],
                'term': row[3],
                'last_updated': row[4],
                'source_date': row[5]
            })

        conn.close()
        return results

    def update_semester_timestamp(self, semester_id: int):
        """更新學期的最後更新時間"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE semesters
            SET last_updated = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (semester_id,))

        conn.commit()
        conn.close()

    def clear_semester_data(self, semester_id: int):
        """清除某學期的所有資料（重新爬取時使用）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 先刪除學生資料
        cursor.execute('''
            DELETE FROM students
            WHERE club_id IN (
                SELECT id FROM clubs WHERE semester_id = ?
            )
        ''', (semester_id,))

        # 再刪除社團資料
        cursor.execute('''
            DELETE FROM clubs WHERE semester_id = ?
        ''', (semester_id,))

        conn.commit()
        conn.close()
