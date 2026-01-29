# 健康國小社團選課系統 - 學生搜尋工具

快速查詢學生參加的所有社團，支援歷史資料查詢和多學期管理。

## ✨ 功能特色

### 🚀 兩種搜尋模式

- **快速搜尋**：使用資料庫快取，瞬間查詢（< 1秒）
  - 不需要帳號密碼
  - 可選擇學期
  - 支援年級班級篩選
  - 查詢歷史資料

- **完整搜尋**：登入並爬取最新資料
  - 自動儲存到資料庫
  - 智慧判斷學期
  - 首次使用必選
  - 支援強制更新

### 💾 資料持久化

- 自動判斷環境（本地/雲端）
- 本地開發使用 SQLite
- Streamlit Cloud 使用 Supabase
- 資料永久保存，不會遺失

### 📊 學期管理

- 自動判斷學期（前半年=下學期，後半年=上學期）
- 保存多個學期的歷史資料
- 支援跨學期查詢

## 🚀 快速開始

### 本地端執行

```bash
# 安裝套件
pip install -r requirements.txt

# 啟動應用程式
streamlit run streamlit_app_v2.py
```

### 部署到 Streamlit Cloud

詳細步驟請見 [DEPLOYMENT.md](DEPLOYMENT.md)

簡要步驟：
1. 上傳到 GitHub
2. 建立 Supabase 資料庫
3. 在 Streamlit Cloud 部署
4. 設定環境變數

## 📖 使用說明

### 首次使用

1. 使用「完整搜尋」模式
2. 輸入帳號、密碼和學生姓名
3. 等待資料爬取完成（約 2-3 分鐘）
4. 資料會自動儲存

### 日常查詢

1. 使用「快速搜尋」模式
2. 輸入學生姓名
3. 選擇學期（可選）
4. 選擇年級班級（可選）
5. 瞬間獲得結果

### 更新資料

- 新學期開始時使用「完整搜尋」更新
- 可勾選「強制更新」覆蓋舊資料

## 📁 檔案結構

```
├── streamlit_app_v2.py      # 主應用程式（推薦）
├── club_database.py          # 本地資料庫
├── cloud_database.py         # 雲端資料庫支援
├── club_crawler.py           # 資料爬蟲
├── requirements.txt          # 套件清單
├── .streamlit/
│   └── config.toml          # Streamlit 設定
├── DEPLOYMENT.md            # 部署指南
├── DATABASE_README.md       # 資料庫說明
└── README.md               # 本文件
```

## 🔧 技術架構

- **前端**: Streamlit
- **爬蟲**: Requests + BeautifulSoup
- **本地資料庫**: SQLite
- **雲端資料庫**: Supabase (PostgreSQL)
- **資料處理**: Pandas

## 📊 學期判斷邏輯

```
1-6月（前半年） → 下學期（前一學年）
  例如：2026/3/1 → 114下

7-12月（後半年） → 上學期（當學年）
  例如：2026/9/1 → 115上
```

## 🔒 隱私與安全

- ✅ 帳號密碼僅用於登入，不會儲存
- ✅ 資料儲存在個人資料庫
- ✅ 支援本地部署完全私有化
- ✅ 雲端部署使用 Supabase 加密

## 📝 授權

此工具僅供教育用途，請勿用於商業目的。

## 📞 相關連結

- [部署指南](DEPLOYMENT.md) - 如何部署到 Streamlit Cloud
- [資料庫說明](DATABASE_README.md) - 資料庫架構詳解
- [Streamlit 文件](https://docs.streamlit.io)
- [Supabase 文件](https://supabase.com/docs)
