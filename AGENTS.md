# 阿爾比恩量化帝國 - 2026 AI Agent 工程作業規範 (AGENTS.md)

本規範適用於在此專案工作的所有 AI Agent 與輔助開發工具，強制執行 2026 AI 工具組合與最佳工程實踐。

---

## 1. 基礎架構與環境層 (Infrastructure & Environment)
- **MCP 工具調用**：優先透過 `mcpServers.json` / `mcp_config.json` 連接的標準本機工具（SQLite、Git、檔案系統）執行操作，避免自編不可控的臨時抓取指令。
- **Tree-sitter / AST 感知**：定位代碼時，以語法結構（Function, Class, Method, Signature）為維度精確切片，避免暴力讀取整個萬行檔案。
- **本機增量同步**：數據與代碼狀態優先以本機 SQLite / 本地快取維護，拒絕反覆全庫掃描。

---

## 2. 輸入層優化 (Input Optimization / Headroom)
- **Context 脫水壓縮**：
  - 遇到大型資料輸出、CLI 日誌或 API 傳回值時，必須進行脫水過濾（去除空白、過濾重覆行、壓縮巨型 JSON 陣列為 Schema + Sample）。
  - 可使用 `.agents/skills/headroom-context/scripts/dehydrate.py` 進行預處理，砍掉 90% 冗餘 Token。
- **跨會話記憶錨定**：
  - 開發前必須先查閱根目錄 [`MEMORY.md`](file:///c:/Users/user/Desktop/阿爾比恩/MEMORY.md)。
  - 專案架構（FastAPI + Render 雲端部署 + 靜態 UI）、六大城製造返還率（24.8% / 47.9%）、黑市 7 天價格加權模型均已錨定在本地，嚴禁向使用者重複提問已記錄之既定事實。

---

## 3. 結構層導航 (Structural Navigation / CodeGraph & Graphify)
- **拓撲圖譜優先 (Graph-First)**：
  - 在進行跨模組改動前，必須先查閱 [`graphify-out/GRAPH_REPORT.md`](file:///c:/Users/user/Desktop/阿爾比恩/graphify-out/GRAPH_REPORT.md) 或執行 `.agents/skills/codegraph-graphify/scripts/sync_graph.py` 查詢相依性。
  - 牢記本專案 6 大社群樞紐：
    1. 前端 UI (`static/index.html`)
    2. API 入口 (`app.py`)
    3. 計算與掃描引擎 (`scanner.py`)
    4. 裝備配方資料庫 (`items_database.py`)
    5. 資料持久化 (`ledger_manager.py`, `data/specs.json`, `data/記帳.xlsx`)
    6. 雲端部署維運 (`render.yaml`, `Dockerfile`)
- **圖譜版本控制**：
  - `graphify-out/graph.json` 與 `graphify-out/GRAPH_REPORT.md` 必須納入 Git 版本控制，與程式碼同步演進。

---

## 4. 輸出層約束 (Output Constraints / Ponytail & YAGNI)
- **強制執行 YAGNI (You Aren't Gonna Need It)**：
  - 嚴格禁止未經指示的預防性過度工程（不擅自新增無用的 Factory、抽象層、非同步隊列）。
  - 嚴格禁止私自引入未經同意的外部第三方套件。
  - 每次代碼修改追求「最小有效 Diff」，嚴禁無故重構無關代碼或破壞既有註解。
- **極簡代碼審查**：
  - 交付代碼前必須自主執行安全審查（無憑證外洩、無 SQL 注入、無死代碼）。
  - 確保新增功能內聚且符合極簡原則。
