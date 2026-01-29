#!/bin/bash
# 啟動 Streamlit 應用程式

echo "正在啟動健康國小社團選課系統 - 學生搜尋工具..."
echo "瀏覽器將自動開啟，或手動訪問 http://localhost:8501"
echo ""

python3 -m streamlit run streamlit_app.py
