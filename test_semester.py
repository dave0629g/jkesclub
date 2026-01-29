#!/usr/bin/env python3
"""
測試學期判斷邏輯
"""

from club_database import ClubDatabase

db = ClubDatabase()

# 測試案例
test_cases = [
    ("2026/1/15", 114, "下"),   # 1月 -> 前半年 -> 114下
    ("2026/3/1", 114, "下"),     # 3月 -> 前半年 -> 114下
    ("2026/6/30", 114, "下"),    # 6月 -> 前半年 -> 114下
    ("2026/7/1", 115, "上"),     # 7月 -> 後半年 -> 115上
    ("2026/9/1", 115, "上"),     # 9月 -> 後半年 -> 115上
    ("2026/12/31", 115, "上"),   # 12月 -> 後半年 -> 115上
    ("2027/1/1", 115, "下"),     # 2027年1月 -> 115下
    ("2027/7/1", 116, "上"),     # 2027年7月 -> 116上
]

print("學期判斷邏輯測試")
print("=" * 60)

all_passed = True

for date_str, expected_year, expected_term in test_cases:
    year, term = db.parse_semester_from_date(date_str)
    semester = f"{year}{term}"
    expected = f"{expected_year}{expected_term}"

    status = "✓" if (year == expected_year and term == expected_term) else "✗"

    if status == "✗":
        all_passed = False

    print(f"{status} {date_str:12s} -> {semester:6s} (預期: {expected:6s})")

print("=" * 60)

if all_passed:
    print("✅ 所有測試通過！")
else:
    print("❌ 有測試失敗")
