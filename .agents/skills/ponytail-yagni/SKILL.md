---
name: ponytail-yagni
description: >-
  Use this skill to enforce YAGNI principles, prevent AI over-engineering, eliminate unnecessary
  abstractions and bloated dependencies, and conduct minimalist code reviews.
---

# Ponytail & YAGNI 輸出約束技能

本技能是用於約束 AI Agent 代碼輸出的「防劣化」規範，嚴格禁止過度設計、過度抽象化與膨脹式代碼生成。

## 核心防線 (The Ponytail Guardrails)

### 1. YAGNI 原則強制令 (Strict YAGNI)
- **禁止預防性過度設計**：嚴禁「為了以後可能支援」而擅自加入工廠模式（Factory）、抽象基礎類別（ABC）、中介軟體（Middleware）或非同步消息隊列。
- **禁止未經授權引進依賴**：非經使用者明確許可，嚴禁在 `requirements.txt` 或 `package.json` 隨意加入新外部套件。能用 Python 內建標準庫（`urllib`, `sqlite3`, `json`, `dataclasses`, `pathlib`）解決的，絕不新增依賴。
- **維持最小 Diff**：修復 Bug 或新增功能時，只修改絕對必要的程式碼區塊。不得擅自重排/重構非相關代碼，保護既有註解與 Docstrings。

### 2. 極簡代碼審查清單 (Minimalist Code Review)

在提交任何代碼變更前，必須對照下列核對點進行自主審查：

| 審查維度 | 合格標準 | 違規樣態 (需立刻修剪) |
| :--- | :--- | :--- |
| **程式碼體積** | 程式碼行數少、高內聚、可一目了然 | 出現只被調用一次的空泛包裝函數或過度解耦 |
| **依賴管理** | 零多餘依賴、優先標準庫 | 為了單一字串操作引進龐大第三方套件 |
| **錯誤處理** | 具體捕獲、清楚記錄、不吞掉例外 | 滿篇 `except Exception: pass` 或過度嵌套的 try-catch |
| **效能與安全** | 無 N+1 查詢、無記憶體洩漏、參數化防 SQL 注入 | 隨意開啟未保護的執行緒或在全域變數無鎖競爭 |
| **死代碼清理** | 廢棄變數、修復過渡檔立即刪除 | 保留無用暫存檔（如 `.bak`, `.reconstructed`） |

## 觸發時機

- 當使用者要求「優化代碼」、「新增功能」或「重構模組」時，主動以本規範作為自我約束輸出準則。
- 在產生變更後，列出修改行數與極簡審查結論，向使用者宣告已剔除所有非必要擴充。
