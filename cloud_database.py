#!/usr/bin/env python3
"""
雲端資料庫 - 簡化版
自動選擇使用 Google Sheets 或本地 SQLite
"""

import os


class CloudDatabase:
    """自動選擇資料庫後端"""

    def __init__(self):
        # 檢查是否在 Streamlit Cloud
        is_cloud = os.getenv('STREAMLIT_SHARING_MODE') is not None

        if is_cloud:
            try:
                from sheets_database import SheetsDatabase
                self.db = SheetsDatabase()
            except:
                from club_database import ClubDatabase
                self.db = ClubDatabase()
        else:
            from club_database import ClubDatabase
            self.db = ClubDatabase()

    # 代理所有方法到實際的資料庫
    def __getattr__(self, name):
        return getattr(self.db, name)
