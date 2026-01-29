# 健康國小社團選課系統 - 學生搜尋工具

這是一個幫助家長快速查詢學生參加哪些社團的工具。

## 功能特色

- 🔍 快速搜尋學生參加的所有社團
- 📋 顯示完整的社團名稱和編號
- 🌐 提供友善的網頁介面
- 🔒 不儲存任何帳號密碼資訊

## 安裝方式

### 本地端執行

1. 安裝 Python 3.8 或更新版本

2. 安裝所需套件：
```bash
pip install -r requirements.txt
```

3. 執行 Streamlit 應用程式：
```bash
streamlit run streamlit_app.py
```

4. 瀏覽器會自動打開，或手動訪問 http://localhost:8501

### 命令列版本

如果偏好使用命令列版本：
```bash
python search_classid.py
```

## 使用方式

1. 輸入您的帳號和密碼
2. 輸入要搜尋的學生姓名
3. 點擊「開始搜尋」
4. 等待搜尋完成，查看結果

## 部署到 Streamlit Cloud

1. 將程式碼上傳到 GitHub
2. 前往 [Streamlit Cloud](https://streamlit.io/cloud)
3. 使用 GitHub 帳號登入
4. 點擊 "New app"
5. 選擇您的 repository 和 `streamlit_app.py`
6. 點擊 "Deploy"

部署後會獲得一個公開網址，例如：`https://your-app.streamlit.app`

## 注意事項

- 搜尋範圍為 ClassID 1-50
- 每次搜尋約需 2-3 分鐘
- 帳號密碼僅用於登入，不會被儲存
- 請確保輸入的姓名完全正確

## 技術架構

- **Streamlit**: 網頁框架
- **Requests**: HTTP 請求
- **BeautifulSoup**: HTML 解析
- **Pandas**: 資料處理

## 授權

此工具僅供健康國小家長使用，請勿用於其他用途。
