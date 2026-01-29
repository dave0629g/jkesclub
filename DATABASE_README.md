# 資料庫系統說明

## 📚 系統架構

### 1. 資料庫設計 (`club_database.py`)

使用 SQLite 資料庫，包含三個主要資料表：

#### semesters（學期表）
- `id`: 學期ID
- `semester`: 學期名稱（如 "114下", "115上"）
- `year`: 學年（如 114, 115）
- `term`: 學期（"上" 或 "下"）
- `last_updated`: 最後更新時間
- `source_date`: 原始日期字串

#### clubs（社團表）
- `id`: 社團ID
- `semester_id`: 所屬學期
- `class_id`: ClassID (1-50)
- `club_number`: 社團編號（如 "1-7"）
- `club_name`: 社團名稱

#### students（學生表）
- `id`: 學生記錄ID
- `club_id`: 所屬社團
- `student_id`: 學號
- `student_name`: 姓名
- `grade`: 年級班級（如 "1年5班"）
- `seat_number`: 座號

### 2. 爬蟲系統 (`club_crawler.py`)

負責從網站爬取資料並儲存到資料庫：

- 自動登入系統
- 取得學期資訊
- 爬取所有社團和學生名單
- 儲存到資料庫

### 3. 網頁介面 (`streamlit_app_v2.py`)

提供兩種搜尋模式：

#### 快速搜尋
- 使用資料庫快取
- 不需登入
- 可選擇學期
- 可依年級班級篩選

#### 完整搜尋
- 登入並爬取最新資料
- 自動儲存到資料庫
- 支援強制更新

## 🔄 學期判斷邏輯

根據日期自動判斷學期：

```
1-6月（前半年）→ 下學期（前一學年）
例如：2026/3/1 → 民國 115-1911=114 → 114學年下學期 → "114下"

7-12月（後半年）→ 上學期（當學年）
例如：2026/9/1 → 民國 115 → 115學年上學期 → "115上"
```

## 💾 資料儲存流程

1. **首次使用**
   - 使用者提供帳號密碼
   - 系統登入並爬取資料
   - 判斷學期並儲存

2. **後續查詢**
   - 檢查資料庫是否有該學期資料
   - 如有：直接使用快取（快速搜尋）
   - 如無或需更新：重新爬取

3. **資料更新**
   - 可選擇強制更新
   - 自動清除舊資料後重新爬取
   - 更新時間戳

## 🚀 使用方式

### 命令列測試爬蟲

```bash
python3 club_crawler.py
```

### 啟動網頁版

```bash
python3 -m streamlit run streamlit_app_v2.py
```

### 直接使用資料庫 API

```python
from club_database import ClubDatabase

db = ClubDatabase()

# 搜尋學生
results = db.search_student("陳胤侖")

# 搜尋特定學期
results = db.search_student("陳胤侖", semester_id=1)

# 搜尋特定年級
results = db.search_student("陳胤侖", grade="1年5班")

# 取得所有學期
semesters = db.get_all_semesters()
```

## 📊 資料庫檔案

- `club_data.db` - SQLite 資料庫檔案（自動建立）

## ⚡ 效能優化

- 建立索引加速查詢（學生姓名、學期、年級）
- 快取機制避免重複爬取
- 支援批次資料處理

## 🔒 隱私保護

- 帳號密碼不會儲存
- 資料僅存於本地
- 可隨時刪除資料庫檔案

## 🛠️ 維護操作

### 查看資料庫內容

```bash
sqlite3 club_data.db
.tables
SELECT * FROM semesters;
SELECT * FROM clubs LIMIT 10;
SELECT * FROM students LIMIT 10;
```

### 清除所有資料

```bash
rm club_data.db
```

### 重新爬取特定學期

使用網頁版的"強制更新"選項

## 📝 注意事項

1. 首次使用需要完整搜尋建立資料
2. 資料會永久保存，除非手動刪除
3. 可以保存多個學期的歷史資料
4. 搜尋速度：快速搜尋 < 1秒，完整搜尋 ~2分鐘
