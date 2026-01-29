#!/usr/bin/env python3
"""
搜尋包含特定學生的 ClassID
使用方式: python3 search_classid.py
"""

import requests
from bs4 import BeautifulSoup
import time

# 設定
BASE_URL = "http://www2.jkes.tp.edu.tw"
LOGIN_URL = f"{BASE_URL}/index.asp"
LIST_URL = f"{BASE_URL}/list.asp"

# 登入資訊和搜尋目標將在執行時輸入
USERNAME = None
PASSWORD = None
TARGET_NAME = None

# 搜尋範圍
CLASS_ID_RANGE = range(1, 51)  # ClassID 從 1 到 50


def get_club_names(session):
    """從 main.asp 取得社團編號和名稱對照表"""
    club_dict = {}

    try:
        url = f"{BASE_URL}/main.asp"
        response = session.get(url, timeout=10)
        response.encoding = 'big5'

        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到所有包含社團資訊的表格行
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                # 第一個 cell 是編號，第二個是社團名稱
                club_id = cells[0].get_text().strip()
                club_name = cells[1].get_text().strip()

                # 檢查是否符合 X-Y 格式
                if '-' in club_id and club_id[0].isdigit():
                    club_dict[club_id] = club_name

        print(f"已載入 {len(club_dict)} 個社團資料")

    except Exception as e:
        print(f"取得社團列表時發生錯誤: {e}")

    return club_dict


def create_session(username, password):
    """建立並登入 session"""
    session = requests.Session()

    # 設定 headers 模擬瀏覽器
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })

    # 先訪問首頁取得可能的 cookies
    try:
        session.get(LOGIN_URL, timeout=10)
    except Exception as e:
        print(f"訪問首頁時發生錯誤: {e}")

    # 嘗試登入（網站可能需要不同的欄位名稱）
    # 常見的欄位名稱: username/userid/account, password/pwd
    login_attempts = [
        {'username': username, 'password': password},
        {'userid': username, 'pwd': password},
        {'account': username, 'password': password},
    ]

    for login_data in login_attempts:
        try:
            response = session.post(LOGIN_URL, data=login_data, timeout=10)
            if response.status_code == 200:
                break
        except Exception as e:
            print(f"登入嘗試失敗: {e}")
            continue

    return session


def search_class(session, class_id, target_name):
    """搜尋特定 ClassID 的名單"""
    url = f"{LIST_URL}?ClassID={class_id}"

    try:
        response = session.get(url, timeout=10)
        response.encoding = 'big5'  # 台灣學校網站通常使用 Big5 編碼

        # 檢查是否包含目標名字
        if target_name in response.text:
            # 嘗試提取社團編號資訊
            soup = BeautifulSoup(response.text, 'html.parser')

            # 找到包含 "編號" 的 h3 或 p 標籤
            club_name = "未知社團"
            for tag in soup.find_all(['h3', 'p']):
                text = tag.get_text().strip()
                if '編號' in text and '-' in text:
                    # 提取 "編號 X-Y" 格式
                    import re
                    match = re.search(r'編號\s*(\d+-\d+)', text)
                    if match:
                        club_name = match.group(1)
                        break

            return True, club_name
        return False, None

    except Exception as e:
        print(f"  查詢 ClassID {class_id} 時發生錯誤: {e}")
        return False, None


def main():
    # 從使用者輸入取得帳號、密碼和搜尋目標
    print("=" * 60)
    print("健康國小社團選課系統 - 學生搜尋工具")
    print("=" * 60)

    username = input("請輸入帳號: ").strip()
    password = input("請輸入密碼: ").strip()
    target_name = input("請輸入要搜尋的學生姓名: ").strip()

    print("\n" + "=" * 60)
    print(f"開始搜尋包含 '{target_name}' 的 ClassID...")
    print(f"搜尋範圍: ClassID {min(CLASS_ID_RANGE)} 到 {max(CLASS_ID_RANGE)}")
    print("-" * 60)

    # 建立 session 並登入
    session = create_session(username, password)

    # 取得社團名稱對照表
    club_names = get_club_names(session)
    print("-" * 60)

    found_classes = []
    total_checks = 0

    # 遍歷所有可能的 ClassID
    for class_id in CLASS_ID_RANGE:
        print(f"正在檢查 ClassID: {class_id}...", end=" ")
        total_checks += 1

        found, club_id = search_class(session, class_id, target_name)

        if found:
            print(f"✓ 找到了！")
            # 從對照表中取得完整社團名稱
            full_club_name = club_names.get(club_id, club_id)
            found_classes.append((class_id, club_id, full_club_name))
        else:
            print("✗")

        # 避免請求太頻繁，稍微延遲
        time.sleep(0.3)

    print("-" * 60)
    print(f"\n搜尋完成！總共檢查了 {total_checks} 個 ClassID")

    if found_classes:
        print(f"\n找到 '{target_name}' 在以下社團:")
        for class_id, club_id, full_club_name in found_classes:
            print(f"  ClassID: {class_id}")
            print(f"  社團編號: {club_id}")
            print(f"  社團名稱: {full_club_name}")
            print(f"  網址: {LIST_URL}?ClassID={class_id}")
            print()
    else:
        print(f"\n在搜尋範圍內未找到 '{target_name}'")
        print("請檢查:")
        print("  1. 名字是否完全正確（包含空格）")
        print("  2. ClassID 範圍是否正確")
        print("  3. 帳號密碼是否有效")


if __name__ == "__main__":
    main()
