# 部署到 Streamlit Cloud 指南

## 📋 準備工作

### 1. 建立 GitHub Repository

1. 前往 https://github.com
2. 點擊 "New repository"
3. 命名為 `jkes-club-search` （或你喜歡的名字）
4. 選擇 Public 或 Private
5. 點擊 "Create repository"

### 2. 上傳檔案到 GitHub

需要上傳以下檔案：

```
必要檔案：
├── streamlit_app_v2.py     # 主應用程式
├── club_database.py         # 資料庫（本地）
├── cloud_database.py        # 雲端資料庫支援
├── club_crawler.py          # 爬蟲
├── requirements.txt         # 套件清單
├── .streamlit/
│   └── config.toml         # Streamlit 設定
└── README.md               # 專案說明

選用檔案：
├── DATABASE_README.md       # 資料庫說明
└── DEPLOYMENT.md           # 部署指南（本文件）
```

## 🗄️ 設定雲端資料庫（Supabase）

### 為什麼需要雲端資料庫？

Streamlit Cloud 每次重啟會清除所有資料，所以需要外部資料庫來永久儲存。

### Step 1: 建立 Supabase 帳號

1. 前往 https://supabase.com
2. 點擊 "Start your project"
3. 使用 GitHub 帳號登入
4. 完全免費！

### Step 2: 建立新專案

1. 點擊 "New project"
2. 專案名稱：`jkes-club-db`
3. 設定資料庫密碼（請記住！）
4. 選擇區域：選擇最近的（如 Southeast Asia）
5. 點擊 "Create new project"
6. 等待 1-2 分鐘建立完成

### Step 3: 建立資料表

在 Supabase 專案中：

1. 點擊左側選單 "SQL Editor"
2. 點擊 "New query"
3. 複製貼上以下 SQL：

```sql
-- 建立 semesters 表
CREATE TABLE semesters (
    id BIGSERIAL PRIMARY KEY,
    semester TEXT UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    term TEXT NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW(),
    source_date TEXT
);

-- 建立 clubs 表
CREATE TABLE clubs (
    id BIGSERIAL PRIMARY KEY,
    semester_id BIGINT REFERENCES semesters(id),
    class_id INTEGER NOT NULL,
    club_number TEXT NOT NULL,
    club_name TEXT NOT NULL,
    UNIQUE(semester_id, class_id)
);

-- 建立 students 表
CREATE TABLE students (
    id BIGSERIAL PRIMARY KEY,
    club_id BIGINT REFERENCES clubs(id),
    student_id TEXT,
    student_name TEXT NOT NULL,
    grade TEXT,
    seat_number TEXT
);

-- 建立索引
CREATE INDEX idx_student_name ON students(student_name);
CREATE INDEX idx_semester ON clubs(semester_id);
CREATE INDEX idx_grade ON students(grade);
```

4. 點擊 "Run" 執行

### Step 4: 取得 API 金鑰

1. 點擊左側選單 "Settings" > "API"
2. 找到以下兩個值：
   - **Project URL** （如：https://xxxxx.supabase.co）
   - **anon public** key（一串很長的字串）
3. 複製這兩個值，稍後會用到

## 🚀 部署到 Streamlit Cloud

### Step 1: 前往 Streamlit Cloud

1. 前往 https://share.streamlit.io
2. 使用 GitHub 帳號登入

### Step 2: 建立新 App

1. 點擊 "New app"
2. 選擇你的 GitHub repository
3. Branch: `main` 或 `master`
4. Main file path: `streamlit_app_v2.py`
5. **不要馬上點 Deploy！先設定環境變數**

### Step 3: 設定環境變數（Secrets）

點擊 "Advanced settings"，在 Secrets 欄位中貼上：

```toml
SUPABASE_URL = "你的 Supabase Project URL"
SUPABASE_KEY = "你的 Supabase anon key"
```

例如：
```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Step 4: 部署

1. 點擊 "Deploy!"
2. 等待 2-3 分鐘
3. 完成！你會獲得一個公開網址

## 🔄 更新應用程式

### 自動更新

只要 push 到 GitHub，Streamlit Cloud 會自動重新部署：

```bash
git add .
git commit -m "更新功能"
git push
```

### 手動重新部署

1. 前往 https://share.streamlit.io
2. 找到你的 app
3. 點擊右邊 "⋮" > "Reboot app"

## ✅ 驗證部署

部署成功後：

1. 打開你的 app 網址
2. 使用「完整搜尋」建立第一筆資料
3. 重新啟動 app（Reboot app）
4. 再次訪問，資料應該還在！
5. 使用「快速搜尋」測試

## 💾 資料持久化確認

資料會永久儲存在 Supabase，不會因為 app 重啟而消失：

- ✅ 本地開發：使用 SQLite（`club_data.db`）
- ✅ Streamlit Cloud：自動使用 Supabase
- ✅ 資料在雲端永久保存
- ✅ 可隨時更新資料

## 🔒 安全注意事項

1. **不要**把 Supabase 金鑰寫在程式碼裡
2. **一定要**使用 Streamlit Secrets
3. Supabase 的 Row Level Security (RLS) 預設是關閉的
4. 如需更高安全性，可在 Supabase 啟用 RLS

## 📊 監控使用量

### Supabase 免費額度

- 500 MB 資料庫空間
- 每月 500 MB 傳輸
- 每月 200萬次 API 請求

對於學校使用綽綽有餘！

### Streamlit Cloud 免費額度

- 1 個私有 app
- 無限個公開 app
- 每個 app 1 GB RAM
- 社群支援

## ❓ 常見問題

### Q: 如何查看資料庫內容？

A: 在 Supabase 點擊 "Table Editor" 可以直接查看和編輯資料

### Q: 如何備份資料？

A: 在 Supabase 的 "Database" > "Backups" 可以手動建立備份

### Q: 如何刪除所有資料？

A: 在 Supabase SQL Editor 執行：
```sql
TRUNCATE students, clubs, semesters CASCADE;
```

### Q: 可以同時支援本地和雲端嗎？

A: 可以！程式會自動判斷環境：
- 本地開發 → SQLite
- Streamlit Cloud → Supabase

## 🎯 下一步

部署完成後，你可以：

1. 分享網址給其他家長使用
2. 定期更新資料（每學期一次）
3. 根據需求新增功能
4. 查看 Supabase 的資料使用情況

## 📞 需要協助？

- Streamlit 文件: https://docs.streamlit.io
- Supabase 文件: https://supabase.com/docs
- GitHub 問題回報
