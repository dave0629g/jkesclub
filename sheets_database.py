#!/usr/bin/env python3
"""
使用 Google Sheets 作為雲端資料庫
不需要註冊任何服務，只需要一個 Google 帳號
"""

import os
import json
import re
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import streamlit as st


class SheetsDatabase:
    """
    使用 Google Sheets 作為後端資料庫
    透過 Streamlit 的 connection 功能自動處理認證
    """

    def __init__(self):
        """初始化 Google Sheets 連接"""
        self.use_sheets = self._try_init_sheets()

        if not self.use_sheets:
            # 如果無法使用 Google Sheets，回退到本地 SQLite
            from club_database import ClubDatabase
            self.db = ClubDatabase()
            print("✓ 使用本地 SQLite 資料庫")

    def _try_init_sheets(self):
        """嘗試初始化 Google Sheets"""
        try:
            # 檢查是否在 Streamlit 環境
            if 'gsheets' not in st.secrets:
                return False

            # 使用 st.connection 自動處理認證
            self.conn = st.connection("gsheets", type="gsheets")
            print("✓ 使用 Google Sheets 雲端資料庫")
            return True

        except Exception as e:
            print(f"⚠️ 無法連接 Google Sheets: {e}")
            return False

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

    def _get_or_create_sheet(self, sheet_name: str):
        """取得或建立工作表"""
        if not self.use_sheets:
            return None

        try:
            df = self.conn.read(worksheet=sheet_name)
            return df
        except:
            # 工作表不存在，建立空的
            import pandas as pd
            return pd.DataFrame()

    def get_or_create_semester(self, date_str: str) -> int:
        """取得或建立學期"""
        if not self.use_sheets:
            return self.db.get_or_create_semester(date_str)

        year, term = self.parse_semester_from_date(date_str)
        semester_name = f"{year}{term}"

        # 讀取 semesters 工作表
        import pandas as pd
        df = self._get_or_create_sheet("semesters")

        if not df.empty and 'semester' in df.columns:
            existing = df[df['semester'] == semester_name]
            if not existing.empty:
                return int(existing.iloc[0]['id'])

        # 建立新學期
        new_id = 1 if df.empty else int(df['id'].max()) + 1
        new_row = pd.DataFrame([{
            'id': new_id,
            'semester': semester_name,
            'year': year,
            'term': term,
            'last_updated': datetime.now().isoformat(),
            'source_date': date_str
        }])

        updated_df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
        self.conn.update(worksheet="semesters", data=updated_df)

        return new_id

    def is_semester_cached(self, semester_id: int) -> bool:
        """檢查學期是否有快取"""
        if not self.use_sheets:
            return self.db.is_semester_cached(semester_id)

        df = self._get_or_create_sheet("clubs")
        if df.empty or 'semester_id' not in df.columns:
            return False

        return len(df[df['semester_id'] == semester_id]) > 0

    def save_club(self, semester_id: int, class_id: int, club_number: str, club_name: str) -> int:
        """儲存社團"""
        if not self.use_sheets:
            return self.db.save_club(semester_id, class_id, club_number, club_name)

        import pandas as pd
        df = self._get_or_create_sheet("clubs")

        # 檢查是否已存在
        if not df.empty and 'semester_id' in df.columns and 'class_id' in df.columns:
            existing = df[(df['semester_id'] == semester_id) & (df['class_id'] == class_id)]
            if not existing.empty:
                club_id = int(existing.iloc[0]['id'])
                # 更新
                df.loc[(df['semester_id'] == semester_id) & (df['class_id'] == class_id),
                       ['club_number', 'club_name']] = [club_number, club_name]
                self.conn.update(worksheet="clubs", data=df)
                return club_id

        # 建立新社團
        new_id = 1 if df.empty else int(df['id'].max()) + 1
        new_row = pd.DataFrame([{
            'id': new_id,
            'semester_id': semester_id,
            'class_id': class_id,
            'club_number': club_number,
            'club_name': club_name
        }])

        updated_df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
        self.conn.update(worksheet="clubs", data=updated_df)

        return new_id

    def save_student(self, club_id: int, student_name: str, student_id: str = None,
                     grade: str = None, seat_number: str = None):
        """儲存學生"""
        if not self.use_sheets:
            return self.db.save_student(club_id, student_name, student_id, grade, seat_number)

        import pandas as pd
        df = self._get_or_create_sheet("students")

        new_id = 1 if df.empty else int(df['id'].max()) + 1
        new_row = pd.DataFrame([{
            'id': new_id,
            'club_id': club_id,
            'student_id': student_id if student_id else '',
            'student_name': student_name,
            'grade': grade if grade else '',
            'seat_number': seat_number if seat_number else ''
        }])

        updated_df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
        self.conn.update(worksheet="students", data=updated_df)

    def search_student(self, student_name: str, semester_id: Optional[int] = None,
                      grade: Optional[str] = None) -> List[Dict]:
        """搜尋學生"""
        if not self.use_sheets:
            return self.db.search_student(student_name, semester_id, grade)

        import pandas as pd

        # 讀取所有相關資料
        students_df = self._get_or_create_sheet("students")
        clubs_df = self._get_or_create_sheet("clubs")
        semesters_df = self._get_or_create_sheet("semesters")

        if students_df.empty:
            return []

        # 篩選學生
        filtered = students_df[students_df['student_name'] == student_name]

        if grade:
            filtered = filtered[filtered['grade'] == grade]

        if filtered.empty:
            return []

        results = []
        for _, student in filtered.iterrows():
            club_id = student['club_id']

            # 找到對應的社團
            club = clubs_df[clubs_df['id'] == club_id]
            if club.empty:
                continue

            club_row = club.iloc[0]

            # 篩選學期
            if semester_id and club_row['semester_id'] != semester_id:
                continue

            # 找到學期資訊
            semester = semesters_df[semesters_df['id'] == club_row['semester_id']]
            if semester.empty:
                continue

            results.append({
                'semester': semester.iloc[0]['semester'],
                'class_id': int(club_row['class_id']),
                'club_number': club_row['club_number'],
                'club_name': club_row['club_name'],
                'student_id': student['student_id'],
                'student_name': student['student_name'],
                'grade': student['grade'],
                'seat_number': student['seat_number']
            })

        return results

    def get_all_semesters(self) -> List[Dict]:
        """取得所有學期"""
        if not self.use_sheets:
            return self.db.get_all_semesters()

        df = self._get_or_create_sheet("semesters")
        if df.empty:
            return []

        df = df.sort_values(['year', 'term'], ascending=[False, False])

        return df.to_dict('records')

    def clear_semester_data(self, semester_id: int):
        """清除學期資料"""
        if not self.use_sheets:
            return self.db.clear_semester_data(semester_id)

        import pandas as pd

        # 刪除學生資料
        students_df = self._get_or_create_sheet("students")
        clubs_df = self._get_or_create_sheet("clubs")

        # 找出要刪除的 club_ids
        clubs_to_delete = clubs_df[clubs_df['semester_id'] == semester_id]['id'].tolist()

        # 刪除學生
        if not students_df.empty and clubs_to_delete:
            students_df = students_df[~students_df['club_id'].isin(clubs_to_delete)]
            self.conn.update(worksheet="students", data=students_df)

        # 刪除社團
        if not clubs_df.empty:
            clubs_df = clubs_df[clubs_df['semester_id'] != semester_id]
            self.conn.update(worksheet="clubs", data=clubs_df)

    def update_semester_timestamp(self, semester_id: int):
        """更新學期時間戳"""
        if not self.use_sheets:
            return self.db.update_semester_timestamp(semester_id)

        df = self._get_or_create_sheet("semesters")
        if not df.empty:
            df.loc[df['id'] == semester_id, 'last_updated'] = datetime.now().isoformat()
            self.conn.update(worksheet="semesters", data=df)
