# 最簡單的部署方式 - 使用 Google Sheets

**不需要註冊任何新服務！只要有 Google 帳號就可以！**

## 🎯 為什麼用 Google Sheets？

- ✅ 完全免費
- ✅ 不需要註冊新服務
- ✅ 只需要授權一次
- ✅ 資料永久保存
- ✅ 可以在 Google Sheets 中直接查看資料

## 📋 準備工作（5分鐘）

### Step 1: 建立 Google Sheet

1. 前往 https://sheets.google.com
2. 點擊「空白」建立新試算表
3. 命名為：`健康國小社團資料`
4. 記下網址，格式像這樣：
   ```
   https://docs.google.com/spreadsheets/d/你的SHEET_ID/edit
   ```
5. 複製 `SHEET_ID` 部分（一長串英數字）

### Step 2: 建立工作表

在剛建立的 Google Sheet 中，建立以下三個工作表（sheet）：

1. **semesters** （預設的 Sheet1 改名為這個）
   - 欄位：id, semester, year, term, last_updated, source_date

2. **clubs** （新增第二個工作表）
   - 欄位：id, semester_id, class_id, club_number, club_name

3. **students** （新增第三個工作表）
   - 欄位：id, club_id, student_id, student_name, grade, seat_number

**提示**：先在第一列填入欄位名稱即可，資料會自動寫入

### Step 3: 設定分享權限

1. 點擊右上角「共用」按鈕
2. 點擊「變更為知道連結的使用者」
3. 選擇「編輯者」（重要！）
4. 點擊「完成」

## 🚀 部署到 Streamlit Cloud（10分鐘）

### Step 1: 上傳到 GitHub

參考 `GITHUB_UPLOAD.md`，上傳以下檔案：

```
必要檔案（一定要上傳）：
✓ streamlit_app_v2.py
✓ club_database.py
✓ sheets_database.py          ← 新的！
✓ club_crawler.py
✓ requirements.txt
✓ .gitignore
✓ .streamlit/config.toml
✓ README.md
```

### Step 2: 修改 requirements.txt

確認 `requirements.txt` 包含：

```txt
streamlit>=1.28.0
requests>=2.31.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
streamlit-gsheets>=0.0.2
```

### Step 3: 部署到 Streamlit Cloud

1. 前往 https://share.streamlit.io
2. 用 GitHub 帳號登入
3. 點擊 "New app"
4. 選擇你的 repository
5. Main file: `streamlit_app_v2.py`
6. **點擊 "Advanced settings"**

### Step 4: 設定 Secrets（重要！）

在 Secrets 欄位貼上：

```toml
# Google Sheets 連接設定
[connections.gsheets]
spreadsheet = "你的SHEET_ID"  # 替換成你的 SHEET_ID
type = "service_account"
project_id = "streamlit-apps"
private_key_id = ""
private_key = ""
client_email = ""
client_id = ""
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
```

**等等！private_key 怎麼辦？**

### Step 5: 取得 Service Account（一次性設定）

這個步驟 Streamlit 會自動幫你完成！

1. 點擊 "Deploy!"
2. App 第一次啟動時會出現錯誤
3. 點擊錯誤訊息中的連結
4. 會自動引導你建立 Service Account
5. **允許授權** 即可

或者手動設定：

1. 前往 https://console.cloud.google.com
2. 建立新專案（隨便命名）
3. 啟用 Google Sheets API
4. 建立服務帳戶
5. 下載 JSON 金鑰
6. 把 JSON 內容貼到 Streamlit Secrets

**但其實 Streamlit 會自動幫你做這些！**

## ✅ 更簡單的方法（推薦）

使用 **Streamlit 的自動認證**：

修改 Secrets 為：

```toml
[connections.gsheets]
type = "service_account"
```

然後在 App 第一次執行時：
1. 會要求你授權 Google 帳號
2. 點擊「允許」
3. 完成！以後都不用再授權

## 🎉 完成！

現在你可以：
- ✅ 使用完整搜尋建立資料
- ✅ 資料永久保存在 Google Sheets
- ✅ 直接在 Google Sheets 查看資料
- ✅ App 重啟資料不會遺失
- ✅ 可以隨時更新資料

## 📊 查看資料

想看資料庫內容？

1. 打開你的 Google Sheet
2. 切換到不同工作表查看：
   - `semesters`: 所有學期
   - `clubs`: 所有社團
   - `students`: 所有學生

## 🔄 更新程式碼

只要 push 到 GitHub，Streamlit 就會自動更新：

```bash
git add .
git commit -m "更新功能"
git push
```

## ❓ 常見問題

**Q: 一定要用 Service Account 嗎？**
A: 不一定，Streamlit 支援 OAuth 自動認證，首次使用時授權即可

**Q: Google Sheet 有容量限制嗎？**
A: 有，單一檔案最多 500 萬個儲存格，對學校使用綽綽有餘

**Q: 資料會不會被別人看到？**
A: 不會，只有你的 Google 帳號和 App 可以存取

**Q: 可以改回用 Supabase 嗎？**
A: 可以，只要修改 `cloud_database.py` 的匯入即可

## 🆚 比較

| 方案 | 優點 | 缺點 |
|------|------|------|
| **Google Sheets** | 超簡單、免註冊、可視化 | 速度稍慢、容量有限 |
| **Supabase** | 專業、快速、容量大 | 需要註冊、設定較複雜 |
| **本地 SQLite** | 最快、最簡單 | 只能本地用、無法雲端 |

**建議**：先用 Google Sheets 試試，有需要再升級到 Supabase
