#!/usr/bin/env python3
"""
健康國小社團選課系統 - 學生搜尋工具 (Streamlit 網頁版)
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

# 設定
BASE_URL = "http://www2.jkes.tp.edu.tw"
LOGIN_URL = f"{BASE_URL}/index.asp"
LIST_URL = f"{BASE_URL}/list.asp"

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

    except Exception as e:
        st.error(f"取得社團列表時發生錯誤: {e}")

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
        st.warning(f"訪問首頁時發生錯誤: {e}")

    # 嘗試登入（網站可能需要不同的欄位名稱）
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
            continue

    return session


def search_class(session, class_id, target_name):
    """搜尋特定 ClassID 的名單"""
    url = f"{LIST_URL}?ClassID={class_id}"

    try:
        response = session.get(url, timeout=10)
        response.encoding = 'big5'

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
        return False, None


def main():
    # 設定頁面
    st.set_page_config(
        page_title="健康國小社團選課系統 - 學生搜尋工具",
        page_icon="🔍",
        layout="wide"
    )

    # 標題
    st.title("🔍 健康國小社團選課系統 - 學生搜尋工具")
    st.markdown("---")

    # 側邊欄輸入
    with st.sidebar:
        st.header("登入資訊")
        username = st.text_input("帳號", type="default")
        password = st.text_input("密碼", type="password")

        st.header("搜尋條件")
        target_name = st.text_input("學生姓名")

        search_button = st.button("🔍 開始搜尋", type="primary", use_container_width=True)

    # 主要內容區
    if search_button:
        if not username or not password or not target_name:
            st.error("⚠️ 請填寫所有欄位！")
            return

        # 顯示搜尋資訊
        st.info(f"🔎 正在搜尋學生：**{target_name}**")
        st.info(f"📊 搜尋範圍：ClassID {min(CLASS_ID_RANGE)} 到 {max(CLASS_ID_RANGE)}")

        # 進度條
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 建立 session 並登入
        with st.spinner("正在登入系統..."):
            session = create_session(username, password)

        # 取得社團名稱對照表
        with st.spinner("正在載入社團列表..."):
            club_names = get_club_names(session)
            if club_names:
                st.success(f"✅ 已載入 {len(club_names)} 個社團資料")
            else:
                st.warning("⚠️ 無法載入社團列表，將只顯示社團編號")

        st.markdown("---")
        status_text.text("搜尋中...")

        found_classes = []
        total_checks = len(CLASS_ID_RANGE)

        # 遍歷所有可能的 ClassID
        for idx, class_id in enumerate(CLASS_ID_RANGE):
            # 更新進度
            progress = (idx + 1) / total_checks
            progress_bar.progress(progress)
            status_text.text(f"正在檢查 ClassID: {class_id} ({idx + 1}/{total_checks})")

            found, club_id = search_class(session, class_id, target_name)

            if found:
                # 從對照表中取得完整社團名稱
                full_club_name = club_names.get(club_id, club_id)
                found_classes.append({
                    'ClassID': class_id,
                    '社團編號': club_id,
                    '社團名稱': full_club_name,
                    '網址': f"{LIST_URL}?ClassID={class_id}"
                })

            # 避免請求太頻繁
            time.sleep(0.3)

        # 完成搜尋
        progress_bar.progress(1.0)
        status_text.text("搜尋完成！")

        st.markdown("---")

        # 顯示結果
        if found_classes:
            st.success(f"✅ 找到 {len(found_classes)} 個社團包含 **{target_name}**")

            # 使用表格顯示
            df = pd.DataFrame(found_classes)

            # 將網址轉換為可點擊的連結
            df['網址'] = df['網址'].apply(lambda x: f'<a href="{x}" target="_blank">查看名單</a>')

            # 顯示表格
            st.markdown("### 📋 搜尋結果")
            st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

            # 也顯示卡片式結果
            st.markdown("### 📌 詳細資訊")
            for club in found_classes:
                with st.expander(f"🎯 {club['社團名稱']} (編號: {club['社團編號']})"):
                    st.write(f"**ClassID:** {club['ClassID']}")
                    st.write(f"**社團編號:** {club['社團編號']}")
                    st.write(f"**社團名稱:** {club['社團名稱']}")
                    st.markdown(f"**網址:** [{club['網址']}]({club['網址']})")

        else:
            st.warning(f"⚠️ 在搜尋範圍內未找到 **{target_name}**")
            st.info("""
            **請檢查：**
            1. 名字是否完全正確（包含空格）
            2. ClassID 範圍是否正確
            3. 帳號密碼是否有效
            """)

    else:
        # 首頁說明
        st.markdown("""
        ### 📖 使用說明

        1. 在左側輸入您的**帳號**和**密碼**
        2. 輸入要搜尋的**學生姓名**
        3. 點擊「🔍 開始搜尋」按鈕
        4. 等待搜尋完成，查看結果

        ### ℹ️ 注意事項

        - 請確保輸入的姓名完全正確
        - 搜尋可能需要數分鐘時間
        - 搜尋範圍為 ClassID 1-50

        ### 🔒 隱私保護

        - 您的帳號密碼僅用於登入系統，不會被儲存
        - 所有資料僅在搜尋期間暫存於記憶體中
        """)


if __name__ == "__main__":
    main()
