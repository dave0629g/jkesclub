#!/usr/bin/env python3
"""
健康國小社團選課系統 - 手機優化版
專為 iPhone 和 Mac 優化的響應式設計
"""

import streamlit as st
import pandas as pd
try:
    from cloud_database import CloudDatabase as Database
except ImportError:
    from club_database import ClubDatabase as Database
from club_crawler import ClubCrawler


def apply_mobile_styles():
    """套用手機優化的 CSS 樣式"""
    st.markdown("""
    <style>
    /* 整體容器 */
    .main {
        padding: 1rem !important;
    }

    /* 手機優化：標題 */
    h1 {
        font-size: 1.5rem !important;
        line-height: 1.3 !important;
        margin-bottom: 1rem !important;
    }

    h2 {
        font-size: 1.3rem !important;
        margin-top: 1.5rem !important;
    }

    h3 {
        font-size: 1.1rem !important;
    }

    /* 按鈕優化 */
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }

    /* 輸入框優化 */
    .stTextInput > div > div > input {
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }

    .stSelectbox > div > div > select {
        font-size: 1.1rem;
        padding: 0.75rem;
    }

    /* 卡片樣式 */
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .info-card {
        background: #f7fafc;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #4299e1;
    }

    /* 表格優化 */
    .dataframe {
        font-size: 0.95rem !important;
    }

    /* Success/Warning/Error 樣式 */
    .stSuccess, .stWarning, .stError, .stInfo {
        padding: 1rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
    }

    /* 展開面板 */
    .streamlit-expanderHeader {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        background: #f7fafc;
        border-radius: 0.5rem;
    }

    /* 進度條 */
    .stProgress > div > div {
        height: 1rem;
        border-radius: 0.5rem;
    }

    /* 側邊欄優化 */
    [data-testid="stSidebar"] {
        padding: 2rem 1rem;
    }

    /* 隱藏 Streamlit 品牌 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 響應式：手機版 */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem !important;
        }

        h1 {
            font-size: 1.3rem !important;
        }

        .stButton > button {
            height: 3.5rem;
            font-size: 1.2rem;
        }

        .result-card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    # 設定頁面
    st.set_page_config(
        page_title="健康國小社團搜尋",
        page_icon="🎯",
        layout="centered",  # 手機優化：使用 centered
        initial_sidebar_state="collapsed"  # 手機優化：預設收起側邊欄
    )

    # 套用手機優化樣式
    apply_mobile_styles()

    # 初始化資料庫
    db = Database()

    # 標題
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h1 style='color: #667eea; margin: 0;'>🎯 健康國小</h1>
        <h2 style='color: #764ba2; margin: 0.5rem 0;'>社團搜尋系統</h2>
    </div>
    """, unsafe_allow_html=True)

    # 主要搜尋介面
    st.markdown("### 🔍 快速搜尋")

    # 搜尋模式選擇（用 tabs 取代 radio）
    tab1, tab2 = st.tabs(["⚡ 快速搜尋", "🔄 完整搜尋"])

    with tab1:
        quick_search_ui(db)

    with tab2:
        full_search_ui(db)


def quick_search_ui(db):
    """快速搜尋介面"""
    st.markdown("""
    <div class='info-card'>
        <p style='margin: 0; font-size: 0.95rem;'>
        ⚡ 使用已儲存的資料快速查詢<br>
        📱 不需要登入，立即獲得結果
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 取得學期資料
    semesters = db.get_all_semesters()

    if not semesters:
        st.warning("⚠️ 資料庫中沒有資料，請先使用「完整搜尋」建立資料")
        return

    # 學生姓名（大輸入框）
    student_name = st.text_input(
        "👤 學生姓名",
        placeholder="請輸入學生姓名",
        key="quick_name",
        label_visibility="collapsed"
    )

    # 學期選擇（簡化）
    semester_options = ["不限學期"] + [s['semester'] for s in semesters]
    selected_semester = st.selectbox(
        "📅 選擇學期",
        semester_options,
        key="quick_semester"
    )

    # 年級班級篩選（摺疊）
    with st.expander("🎓 進階篩選（選填）"):
        col1, col2 = st.columns(2)
        with col1:
            grade = st.selectbox("年級", ["不限", "1", "2", "3", "4", "5", "6"])
        with col2:
            class_num = st.selectbox("班級", ["不限", "1", "2", "3", "4", "5", "6"])

        if grade != "不限" and class_num != "不限":
            grade_filter = f"{grade}年{class_num}班"
        else:
            grade_filter = None

    # 搜尋按鈕
    if st.button("🔍 開始搜尋", type="primary", key="quick_search_btn"):
        if not student_name:
            st.error("⚠️ 請輸入學生姓名")
            return

        # 決定 semester_id
        semester_id = None
        if selected_semester != "不限學期":
            for s in semesters:
                if s['semester'] == selected_semester:
                    semester_id = s['id']
                    break

        # 搜尋
        with st.spinner("🔎 搜尋中..."):
            results = db.search_student(student_name, semester_id, grade_filter if 'grade_filter' in locals() else None)

        # 顯示結果
        display_results_mobile(results, student_name)


def full_search_ui(db):
    """完整搜尋介面"""
    st.markdown("""
    <div class='info-card'>
        <p style='margin: 0; font-size: 0.95rem;'>
        🔄 登入系統並爬取最新資料<br>
        💾 資料會自動儲存供後續查詢
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 登入資訊
    username = st.text_input("👤 帳號", key="full_username")
    password = st.text_input("🔒 密碼", type="password", key="full_password")

    # 學生姓名
    student_name = st.text_input("🎯 學生姓名", key="full_name")

    # 進階選項
    with st.expander("⚙️ 進階選項"):
        force_update = st.checkbox("強制更新資料（覆蓋已有資料）", value=False)

    # 搜尋按鈕
    if st.button("🚀 開始完整搜尋", type="primary", key="full_search_btn"):
        if not username or not password or not student_name:
            st.error("⚠️ 請填寫所有欄位")
            return

        # 進度顯示
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 建立爬蟲
        status_text.text("🔐 正在登入...")
        progress_bar.progress(0.1)
        crawler = ClubCrawler(username, password)

        # 爬取資料
        status_text.text("📡 正在爬取資料...")
        progress_bar.progress(0.3)

        semester_id, updated = crawler.crawl_all_data(force_update=force_update)
        progress_bar.progress(0.9)

        if updated:
            st.success("✅ 資料已更新！")
        else:
            st.info("ℹ️ 使用快取資料")

        progress_bar.progress(1.0)
        status_text.text("✨ 完成！")

        # 搜尋
        results = db.search_student(student_name, semester_id)
        display_results_mobile(results, student_name)


def display_results_mobile(results, student_name):
    """手機優化的結果顯示"""
    st.markdown("---")

    if results:
        # 統計資訊卡片
        st.markdown(f"""
        <div class='result-card'>
            <h2 style='margin: 0; color: white;'>✅ 找到 {len(results)} 個社團</h2>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>學生：{student_name}</p>
        </div>
        """, unsafe_allow_html=True)

        # 依學期分組顯示
        df = pd.DataFrame(results)
        semesters = df['semester'].unique()

        for semester in sorted(semesters, reverse=True):
            semester_data = df[df['semester'] == semester]

            st.markdown(f"### 📅 {semester} 學期")

            for idx, row in semester_data.iterrows():
                # 每個社團一張卡片
                with st.container():
                    st.markdown(f"""
                    <div style='background: white; padding: 1rem; border-radius: 0.75rem;
                                margin: 0.5rem 0; border-left: 4px solid #667eea;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <h4 style='margin: 0; color: #667eea;'>{row['club_name']}</h4>
                                <p style='margin: 0.25rem 0 0 0; color: #666; font-size: 0.9rem;'>
                                    編號: {row['club_number']} | 班級: {row['grade']}
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # 統計資訊
        st.markdown("### 📊 統計資訊")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("社團總數", len(results))
        with col2:
            st.metric("涵蓋學期", len(semesters))
        with col3:
            most_common = df['semester'].mode()[0] if len(df) > 0 else "N/A"
            st.metric("主要學期", most_common)

    else:
        st.markdown(f"""
        <div style='background: #fff5f5; padding: 2rem; border-radius: 1rem; text-align: center;'>
            <h3 style='color: #e53e3e; margin: 0;'>😕 未找到記錄</h3>
            <p style='color: #666; margin: 1rem 0 0 0;'>學生：{student_name}</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("💡 可能原因"):
            st.markdown("""
            - 姓名輸入錯誤
            - 該學生未參加任何社團
            - 資料庫中沒有該學期資料
            - 年級班級篩選條件不符
            """)


if __name__ == "__main__":
    main()
