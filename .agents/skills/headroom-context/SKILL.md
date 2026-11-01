---
name: headroom-context
description: >-
  Use this skill to optimize input tokens, perform context dehydration on large logs,
  CLI dumps, and massive JSON structures, and manage cross-session persistent memory.
---

# Headroom Context 脫水與輸入層優化技能

本技能指導 AI Agent 在面對海量數據、終端機輸出日誌或龐大資料結構時，如何進行高密度資訊脫水，避免「Lost in the Middle」與上下文浪費。

## 核心流程

1. **JSON 骨架化 (Skeletonization)**
   - 嚴禁直接將完整數百/數千筆的 JSON 陣列直接餵給推理模組。
   - 使用 [dehydrate.py](./scripts/dehydrate.py) 或就地提取：
     - 資料陣列長度 (Total count)
     - Schema / Key 結構
     - 前 1~2 筆標準樣本 (Sample items)
     - 統計邊界（Min, Max, Avg, Null 比例）

2. **日誌與 Traceback 脫水**
   - 遇到大量終端輸出或錯誤日誌時：
     - 剔除進度條（如 `tqdm`、`npm/pip` 下載進度條）。
     - 剔除重複的連線 Ping / Health check 日誌。
     - 保留 `Traceback`、`Exception`、`Error` 行以及發生點前後 3 行上下文。

3. **跨會話記憶引用 (Persistent Memory)**
   - 在新會話啟動或重構全域架構前，必須優先讀取根目錄下的 `MEMORY.md`。
   - 嚴禁在每一輪對話中要求使用者重新提供已記錄在 `MEMORY.md` 中的常數（如六大城製造加成、黑市手續費、Render 部署配置）。

## 輔助工具調用

當需要對外部巨型檔案做脫水時，可執行：
```bash
python .agents/skills/headroom-context/scripts/dehydrate.py <path_to_large_file>
```
