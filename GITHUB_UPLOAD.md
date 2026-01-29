# 上傳到 GitHub 快速指南

## 📋 準備上傳的檔案清單

### ✅ 必要檔案（一定要上傳）

```
✓ streamlit_app_v2.py       # 主應用程式
✓ club_database.py           # 本地資料庫
✓ cloud_database.py          # 雲端資料庫
✓ club_crawler.py            # 爬蟲
✓ requirements.txt           # 套件清單
✓ README.md                  # 說明文件
✓ .gitignore                 # Git 忽略檔案
✓ .streamlit/config.toml     # Streamlit 設定
```

### 📖 選用檔案（建議上傳）

```
✓ DEPLOYMENT.md              # 部署指南
✓ DATABASE_README.md         # 資料庫說明
✓ GITHUB_UPLOAD.md          # 本文件
```

### ❌ 不要上傳的檔案

```
✗ club_data.db              # 本地資料庫（自動忽略）
✗ search_classid.py         # 舊版命令列工具
✗ streamlit_app.py          # 舊版應用程式
✗ check_*.py                # 測試檔案
✗ test_*.py                 # 測試檔案
✗ __pycache__/              # Python 快取
```

## 🚀 上傳步驟

### 方法 1: 使用 GitHub 網頁介面（最簡單）

1. **建立 Repository**
   - 前往 https://github.com/new
   - Repository name: `jkes-club-search`
   - Description: `健康國小社團選課系統 - 學生搜尋工具`
   - 選擇 Public 或 Private
   - **不要**勾選 "Add a README file"
   - 點擊 "Create repository"

2. **上傳檔案**
   - 在新建立的 repository 頁面
   - 點擊 "uploading an existing file"
   - 拖曳上方列出的必要檔案
   - 記得也上傳 `.streamlit` 資料夾
   - Commit message: `Initial commit`
   - 點擊 "Commit changes"

3. **完成！**
   - Repository 網址會是: `https://github.com/你的帳號/jkes-club-search`

### 方法 2: 使用 Git 命令列（進階）

```bash
# 1. 初始化 Git（在 /Users/dave.chen/test 目錄下）
cd /Users/dave.chen/test
git init

# 2. 加入檔案
git add streamlit_app_v2.py
git add club_database.py
git add cloud_database.py
git add club_crawler.py
git add requirements.txt
git add README.md
git add .gitignore
git add DEPLOYMENT.md
git add DATABASE_README.md
git add .streamlit/config.toml

# 3. 建立第一個 commit
git commit -m "Initial commit: 健康國小社團搜尋系統"

# 4. 連接到 GitHub（替換成你的 repository 網址）
git remote add origin https://github.com/你的帳號/jkes-club-search.git

# 5. 推送到 GitHub
git branch -M main
git push -u origin main
```

## ✅ 驗證上傳

上傳完成後，在 GitHub 上應該看到：

```
你的Repository/
├── .gitignore
├── .streamlit/
│   └── config.toml
├── README.md
├── DEPLOYMENT.md
├── DATABASE_README.md
├── streamlit_app_v2.py
├── club_database.py
├── cloud_database.py
├── club_crawler.py
└── requirements.txt
```

## 🔄 後續更新

當你修改程式碼後：

### 使用 GitHub 網頁

1. 前往你的 repository
2. 點擊要更新的檔案
3. 點擊右上角的 ✏️ (Edit)
4. 修改內容
5. 點擊 "Commit changes"

### 使用 Git 命令列

```bash
# 1. 修改檔案後
git add .
git commit -m "更新功能說明"
git push

# Streamlit Cloud 會自動偵測並重新部署！
```

## 📝 Commit Message 建議

```bash
git commit -m "Initial commit"              # 首次上傳
git commit -m "修正學期判斷邏輯"             # 修正 bug
git commit -m "新增年級篩選功能"             # 新功能
git commit -m "更新 README 文件"            # 文件更新
git commit -m "優化搜尋速度"                 # 效能優化
```

## ⚠️ 注意事項

1. **絕對不要**上傳包含真實帳號密碼的檔案
2. **絕對不要**上傳資料庫檔案（.db）
3. **記得**檢查 `.gitignore` 是否正確
4. **建議**先用 Private repository 測試

## 下一步

上傳到 GitHub 後：
1. ✅ 檢查檔案是否都正確上傳
2. ✅ 閱讀 [DEPLOYMENT.md](DEPLOYMENT.md) 進行部署
3. ✅ 設定 Supabase 資料庫
4. ✅ 在 Streamlit Cloud 部署應用程式
