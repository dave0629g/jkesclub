#!/usr/bin/env python3
"""
雲端資料庫管理系統 - 支援 Streamlit Cloud
使用 Google Sheets 作為後端資料庫（最簡單！）
"""

import os
from typing import Optional, List, Dict, Tuple


class CloudDatabase:
    """
    雲端資料庫接口
    支援本地 SQLite 和雲端 Google Sheets
    """

    def __init__(self, use_cloud=None):
        """
        初始化資料庫
        :param use_cloud: True=強制使用雲端, False=強制使用本地, None=自動判斷
        """
        # 自動判斷：如果在 Streamlit Cloud 環境就使用雲端
        if use_cloud is None:
            use_cloud = self._is_streamlit_cloud()

        self.use_cloud = use_cloud

        if use_cloud:
            self._init_sheets()
        else:
            self._init_sqlite()

    def _is_streamlit_cloud(self):
        """檢查是否在 Streamlit Cloud 環境"""
        return os.getenv('STREAMLIT_SHARING_MODE') is not None

    def _init_sqlite(self):
        """初始化 SQLite（本地開發）"""
        from club_database import ClubDatabase
        self.db = ClubDatabase()
        print("✓ 使用本地 SQLite 資料庫")

    def _init_sheets(self):
        """初始化 Google Sheets（雲端部署）"""
        try:
            from sheets_database import SheetsDatabase
            self.db = SheetsDatabase()
            print("✓ 使用 Google Sheets 雲端資料庫")

        except Exception as e:
            print(f"⚠️ 無法連接 Google Sheets: {e}")
            print("改用本地資料庫")
            self._init_sqlite()
            self.use_cloud = False

    def parse_semester_from_date(self, date_str: str) -> Tuple[int, str]:
        """從日期字串解析學期"""
        match = re.search(r'(\d{4})/(\d{1,2})', date_str)
        if not match:
            raise ValueError(f"無法解析日期: {date_str}")

        year = int(match.group(1))
        month = int(match.group(2))
        roc_year = year - 1911

        if 1 <= month <= 6:
            semester_year = roc_year - 1
            term = "下"
        else:
            semester_year = roc_year
            term = "上"

        return semester_year, term

    # 以下方法會根據 use_cloud 自動路由到正確的實作

    def get_or_create_semester(self, date_str: str) -> int:
        """取得或建立學期"""
        if not self.use_cloud:
            return self.db.get_or_create_semester(date_str)

        # Supabase 實作
        year, term = self.parse_semester_from_date(date_str)
        semester_name = f"{year}{term}"

        result = self.supabase.table('semesters').select('*').eq('semester', semester_name).execute()

        if result.data:
            return result.data[0]['id']
        else:
            new_semester = self.supabase.table('semesters').insert({
                'semester': semester_name,
                'year': year,
                'term': term,
                'source_date': date_str
            }).execute()
            return new_semester.data[0]['id']

    def is_semester_cached(self, semester_id: int) -> bool:
        """檢查學期是否有快取"""
        if not self.use_cloud:
            return self.db.is_semester_cached(semester_id)

        result = self.supabase.table('clubs').select('id').eq('semester_id', semester_id).limit(1).execute()
        return len(result.data) > 0

    def save_club(self, semester_id: int, class_id: int, club_number: str, club_name: str) -> int:
        """儲存社團"""
        if not self.use_cloud:
            return self.db.save_club(semester_id, class_id, club_number, club_name)

        result = self.supabase.table('clubs').upsert({
            'semester_id': semester_id,
            'class_id': class_id,
            'club_number': club_number,
            'club_name': club_name
        }).execute()
        return result.data[0]['id']

    def save_student(self, club_id: int, student_name: str, student_id: str = None,
                     grade: str = None, seat_number: str = None):
        """儲存學生"""
        if not self.use_cloud:
            return self.db.save_student(club_id, student_name, student_id, grade, seat_number)

        self.supabase.table('students').insert({
            'club_id': club_id,
            'student_id': student_id,
            'student_name': student_name,
            'grade': grade,
            'seat_number': seat_number
        }).execute()

    def search_student(self, student_name: str, semester_id: Optional[int] = None,
                      grade: Optional[str] = None) -> List[Dict]:
        """搜尋學生"""
        if not self.use_cloud:
            return self.db.search_student(student_name, semester_id, grade)

        # Supabase 實作
        query = self.supabase.table('students').select(
            'student_id, student_name, grade, seat_number, '
            'clubs(class_id, club_number, club_name, semesters(semester))'
        ).eq('student_name', student_name)

        if semester_id:
            query = query.eq('clubs.semester_id', semester_id)
        if grade:
            query = query.eq('grade', grade)

        result = query.execute()

        # 轉換格式
        results = []
        for row in result.data:
            club = row['clubs']
            semester = club['semesters']['semester']
            results.append({
                'semester': semester,
                'class_id': club['class_id'],
                'club_number': club['club_number'],
                'club_name': club['club_name'],
                'student_id': row['student_id'],
                'student_name': row['student_name'],
                'grade': row['grade'],
                'seat_number': row['seat_number']
            })

        return results

    def get_all_semesters(self) -> List[Dict]:
        """取得所有學期"""
        if not self.use_cloud:
            return self.db.get_all_semesters()

        result = self.supabase.table('semesters').select('*').order('year', desc=True).execute()
        return result.data

    def clear_semester_data(self, semester_id: int):
        """清除學期資料"""
        if not self.use_cloud:
            return self.db.clear_semester_data(semester_id)

        # 先刪除學生
        self.supabase.table('students').delete().in_(
            'club_id',
            self.supabase.table('clubs').select('id').eq('semester_id', semester_id)
        ).execute()

        # 再刪除社團
        self.supabase.table('clubs').delete().eq('semester_id', semester_id).execute()

    def update_semester_timestamp(self, semester_id: int):
        """更新學期時間戳"""
        if not self.use_cloud:
            return self.db.update_semester_timestamp(semester_id)

        self.supabase.table('semesters').update({
            'last_updated': datetime.now().isoformat()
        }).eq('id', semester_id).execute()
