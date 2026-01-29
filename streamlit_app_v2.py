#!/usr/bin/env python3
"""
健康國小社團選課系統 - 學生搜尋工具 V2 (含資料庫快取)
"""

import streamlit as st
import pandas as pd
from club_database import ClubDatabase
from club_crawler import ClubCrawler


def main():
    # 設定頁面
    st.set_page_config(
        page_title="健康國小社團選課系統 - 學生搜尋工具",
        page_icon="🔍",
        layout="wide"
    )

    # 初始化資料庫
    db = ClubDatabase()

    # 標題
    st.title("🔍 健康國小社團選課系統 - 學生搜尋工具 V2")
    st.markdown("---")

    # 側邊欄
    with st.sidebar:
        st.header("🔧 設定")

        # 顯示已有的學期資料
        semesters = db.get_all_semesters()

        if semesters:
            st.success(f"📚 資料庫中有 {len(semesters)} 個學期的資料")

            with st.expander("查看學期列表"):
                for sem in semesters:
                    st.write(f"• {sem['semester']} (更新: {sem['last_updated'][:10]})")

        # 搜尋模式選擇
        st.subheader("搜尋模式")
        search_mode = st.radio(
            "選擇搜尋方式",
            ["快速搜尋（使用快取資料）", "完整搜尋（登入並更新資料）"],
            help="快速搜尋使用資料庫快取，完整搜尋會登入系統並更新資料"
        )

        st.markdown("---")

        # 快速搜尋模式
        if search_mode == "快速搜尋（使用快取資料）":
            st.subheader("📝 搜尋條件")

            student_name = st.text_input("學生姓名", key="quick_name")

            # 學期選擇
            if semesters:
                semester_options = ["不限學期"] + [s['semester'] for s in semesters]
                selected_semester = st.selectbox("學期", semester_options)
            else:
                st.warning("⚠️ 資料庫中沒有資料，請使用完整搜尋先建立資料")
                selected_semester = None

            # 年級班級選擇
            use_grade_filter = st.checkbox("依年級班級篩選")

            if use_grade_filter:
                col1, col2 = st.columns(2)
                with col1:
                    grade = st.selectbox("年級", ["1", "2", "3", "4", "5", "6"])
                with col2:
                    class_num = st.selectbox("班級", ["1", "2", "3", "4", "5", "6"])
                grade_filter = f"{grade}年{class_num}班"
            else:
                grade_filter = None

            search_button = st.button("🔍 快速搜尋", type="primary", use_container_width=True)

        # 完整搜尋模式
        else:
            st.subheader("🔐 登入資訊")
            username = st.text_input("帳號", key="full_username")
            password = st.text_input("密碼", type="password", key="full_password")

            st.subheader("📝 搜尋條件")
            student_name = st.text_input("學生姓名", key="full_name")

            force_update = st.checkbox("強制更新資料（即使已有快取）", value=False)

            search_button = st.button("🔍 完整搜尋", type="primary", use_container_width=True)

    # 主要內容區
    if search_button:
        if not student_name:
            st.error("⚠️ 請輸入學生姓名！")
            return

        # 快速搜尋
        if search_mode == "快速搜尋（使用快取資料）":
            if not semesters:
                st.error("⚠️ 資料庫中沒有資料，請先使用完整搜尋建立資料！")
                return

            st.info(f"🔎 正在搜尋學生：**{student_name}**")

            # 決定 semester_id
            semester_id = None
            if selected_semester and selected_semester != "不限學期":
                for s in semesters:
                    if s['semester'] == selected_semester:
                        semester_id = s['id']
                        break

            # 搜尋
            results = db.search_student(student_name, semester_id, grade_filter)

            display_results(results, student_name)

        # 完整搜尋
        else:
            if not username or not password:
                st.error("⚠️ 請填寫帳號和密碼！")
                return

            st.info(f"🔎 正在搜尋學生：**{student_name}**")

            # 建立爬蟲
            with st.spinner("正在登入系統..."):
                crawler = ClubCrawler(username, password)

            # 爬取資料
            progress_bar = st.progress(0)
            status_text = st.empty()

            with st.spinner("正在爬取資料..."):
                status_text.text("正在取得學期資訊...")
                progress_bar.progress(0.1)

                semester_id, updated = crawler.crawl_all_data(force_update=force_update)

                progress_bar.progress(1.0)

            if updated:
                st.success("✅ 資料已更新！")
            else:
                st.info("ℹ️ 使用快取資料")

            # 搜尋
            results = db.search_student(student_name, semester_id)

            display_results(results, student_name)

    else:
        # 首頁說明
        st.markdown("""
        ### 📖 使用說明

        #### 🚀 快速搜尋（推薦）
        - 使用已儲存的資料進行搜尋
        - 速度快，不需要登入
        - 可以搜尋歷史學期資料
        - 可以依年級班級篩選

        #### 🔄 完整搜尋
        - 登入系統並爬取最新資料
        - 第一次使用或需要更新資料時使用
        - 資料會自動儲存供後續快速搜尋

        ### 💡 特色功能

        - ✅ 自動判斷學期（根據日期）
        - ✅ 資料快取（避免重複爬取）
        - ✅ 支援多學期查詢
        - ✅ 年級班級篩選
        - ✅ 歷史紀錄保存

        ### 📊 資料說明

        - 學期判斷：1-6月（前半年）為下學期（前一學年），7-12月（後半年）為上學期（當學年）
        - 例如：2026/3/1 → 114學年下學期
        - 例如：2026/9/1 → 115學年上學期

        ### 🔒 隱私保護

        - 帳號密碼僅用於登入，不會被儲存
        - 資料儲存在本地資料庫
        - 僅儲存學生姓名、學號、社團等基本資訊
        """)


def display_results(results, student_name):
    """顯示搜尋結果"""
    st.markdown("---")

    if results:
        st.success(f"✅ 找到 {len(results)} 筆記錄包含 **{student_name}**")

        # 轉換為 DataFrame
        df = pd.DataFrame(results)

        # 顯示表格
        st.markdown("### 📋 搜尋結果")

        display_df = df[['semester', 'club_number', 'club_name', 'grade', 'seat_number']].copy()
        display_df.columns = ['學期', '社團編號', '社團名稱', '班級', '座號']

        st.dataframe(display_df, use_container_width=True)

        # 詳細資訊
        st.markdown("### 📌 詳細資訊")

        # 依學期分組
        semesters = df['semester'].unique()

        for semester in sorted(semesters, reverse=True):
            semester_data = df[df['semester'] == semester]

            with st.expander(f"📅 {semester} ({len(semester_data)} 個社團)", expanded=True):
                for _, row in semester_data.iterrows():
                    col1, col2, col3 = st.columns([2, 3, 1])

                    with col1:
                        st.write(f"**社團編號:** {row['club_number']}")

                    with col2:
                        st.write(f"**社團名稱:** {row['club_name']}")

                    with col3:
                        st.write(f"**班級:** {row['grade']}")

                    st.divider()

        # 統計資訊
        st.markdown("### 📊 統計")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("總社團數", len(results))

        with col2:
            st.metric("涵蓋學期", len(semesters))

        with col3:
            most_common_semester = df['semester'].mode()[0] if len(df) > 0 else "N/A"
            st.metric("主要學期", most_common_semester)

    else:
        st.warning(f"⚠️ 未找到 **{student_name}** 的記錄")
        st.info("""
        **可能原因：**
        1. 姓名輸入錯誤
        2. 該學生未參加任何社團
        3. 資料庫中沒有該學期的資料（請使用完整搜尋）
        4. 年級班級篩選條件不符
        """)


if __name__ == "__main__":
    main()
