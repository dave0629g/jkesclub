#!/usr/bin/env python3
"""
社團資料爬蟲
"""

import requests
from bs4 import BeautifulSoup
import time
import re
try:
    from cloud_database import CloudDatabase as Database
except ImportError:
    from club_database import ClubDatabase as Database


class ClubCrawler:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = "http://www2.jkes.tp.edu.tw"
        self.session = None
        self.db = Database()

    def create_session(self):
        """建立並登入 session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        try:
            self.session.get(f"{self.base_url}/index.asp", timeout=10)
        except Exception as e:
            print(f"訪問首頁錯誤: {e}")

        login_attempts = [
            {'username': self.username, 'password': self.password},
            {'userid': self.username, 'pwd': self.password},
        ]

        for login_data in login_attempts:
            try:
                self.session.post(f"{self.base_url}/index.asp", data=login_data, timeout=10)
            except:
                pass

    def get_semester_date(self) -> str:
        """從 reindex.asp 取得學期日期"""
        try:
            response = self.session.get(f"{self.base_url}/main.asp", timeout=10)
            response.encoding = 'big5'

            # 尋找類似 "預計2026/3/1" 的文字
            match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})', response.text)
            if match:
                return match.group(1)

        except Exception as e:
            print(f"取得學期日期錯誤: {e}")

        return None

    def get_club_list(self) -> dict:
        """取得所有社團編號和名稱對照表"""
        club_dict = {}

        try:
            url = f"{self.base_url}/main.asp"
            response = self.session.get(url, timeout=10)
            response.encoding = 'big5'

            soup = BeautifulSoup(response.text, 'html.parser')

            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    club_id = cells[0].get_text().strip()
                    club_name = cells[1].get_text().strip()

                    if '-' in club_id and club_id[0].isdigit():
                        club_dict[club_id] = club_name

        except Exception as e:
            print(f"取得社團列表錯誤: {e}")

        return club_dict

    def get_class_students(self, class_id: int) -> list:
        """取得某個 ClassID 的所有學生名單"""
        students = []

        try:
            url = f"{self.base_url}/list.asp?ClassID={class_id}"
            response = self.session.get(url, timeout=10)
            response.encoding = 'big5'

            soup = BeautifulSoup(response.text, 'html.parser')

            # 找到社團編號
            club_number = None
            for tag in soup.find_all(['h3', 'p']):
                text = tag.get_text().strip()
                if '編號' in text and '-' in text:
                    match = re.search(r'編號\s*(\d+-\d+)', text)
                    if match:
                        club_number = match.group(1)
                        break

            # 解析學生名單表格
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 5:
                    # 跳過表頭
                    if cells[0].get_text().strip() == '序號':
                        continue

                    try:
                        student_id = cells[1].get_text().strip()
                        grade = cells[2].get_text().strip()
                        seat = cells[3].get_text().strip()
                        name = cells[4].get_text().strip()

                        if name and student_id:  # 確保有資料
                            students.append({
                                'student_id': student_id,
                                'name': name,
                                'grade': grade,
                                'seat': seat,
                                'club_number': club_number
                            })
                    except:
                        continue

        except Exception as e:
            print(f"取得 ClassID {class_id} 學生名單錯誤: {e}")

        return students

    def crawl_all_data(self, class_id_range=range(1, 51), force_update=False):
        """
        爬取所有資料並儲存到資料庫
        :param class_id_range: ClassID 範圍
        :param force_update: 是否強制更新（即使已有快取）
        :return: (semester_id, 是否更新)
        """
        print("正在建立連線...")
        self.create_session()

        print("正在取得學期資訊...")
        date_str = self.get_semester_date()
        if not date_str:
            print("⚠️ 無法取得學期日期，使用當前日期")
            from datetime import datetime
            date_str = datetime.now().strftime("%Y/%m/%d")

        print(f"學期日期: {date_str}")

        semester_id = self.db.get_or_create_semester(date_str)
        year, term = self.db.parse_semester_from_date(date_str)
        semester_name = f"{year}{term}"

        print(f"學期: {semester_name} (ID: {semester_id})")

        # 檢查是否已經有快取
        if not force_update and self.db.is_semester_cached(semester_id):
            print(f"✅ 學期 {semester_name} 的資料已存在，跳過更新")
            return semester_id, False

        print(f"🔄 開始更新學期 {semester_name} 的資料...")

        # 清除舊資料（如果是強制更新）
        if force_update:
            print("清除舊資料...")
            self.db.clear_semester_data(semester_id)

        # 取得社團列表
        print("正在取得社團列表...")
        club_list = self.get_club_list()
        print(f"找到 {len(club_list)} 個社團")

        # 爬取每個 ClassID
        total_students = 0
        total_clubs = 0

        for class_id in class_id_range:
            print(f"正在爬取 ClassID {class_id}...", end=" ")

            students = self.get_class_students(class_id)

            if students:
                club_number = students[0]['club_number']
                club_name = club_list.get(club_number, f"未知社團 ({club_number})")

                # 儲存社團
                db_club_id = self.db.save_club(semester_id, class_id, club_number, club_name)

                # 儲存學生
                for student in students:
                    self.db.save_student(
                        db_club_id,
                        student['name'],
                        student['student_id'],
                        student['grade'],
                        student['seat']
                    )

                print(f"✓ {len(students)} 位學生")
                total_students += len(students)
                total_clubs += 1
            else:
                print("✗")

            time.sleep(0.3)  # 避免請求過快

        # 更新時間戳
        self.db.update_semester_timestamp(semester_id)

        print(f"\n✅ 完成！共爬取 {total_clubs} 個社團，{total_students} 位學生")

        return semester_id, True


if __name__ == "__main__":
    # 測試用
    username = input("請輸入帳號: ").strip()
    password = input("請輸入密碼: ").strip()

    crawler = ClubCrawler(username, password)
    semester_id, updated = crawler.crawl_all_data()

    if updated:
        print(f"\n資料已儲存到資料庫 (semester_id: {semester_id})")
    else:
        print(f"\n使用快取資料 (semester_id: {semester_id})")
