---
name: mcp-treesitter-env
description: >-
  Use this skill to configure and verify MCP servers (mcpServers.json), inspect Tree-sitter AST
  syntax nodes, and maintain SQLite local incremental indexing for sub-second change synchronization.
---

# MCP、Tree-sitter 與本機增量索引環境技能

本技能指導 AI Agent 配置現代本機基礎環境，串接本機工具至 AI 協議，並利用語法樹與本機索引進行高效程式碼感知。

## 1. MCP 伺服器配置與維運 (Model Context Protocol)

- **配置檔案標準**：在工作區根目錄或全域使用 `mcpServers.json`（或 `mcp_config.json`）。
- **常用伺服器規格**：
  - `sqlite`：提供唯讀或讀寫本機 SQLite 資料庫能力（例如 `data/market.db` 或市場紀錄）。
  - `git`：提供標準化 Git Diff、Commit 與 Status 查詢。
  - `filesystem`：受限目錄的檔案讀寫與搜尋。
- **健康檢查**：
  - 確保執行環境具備 Python / Node 執行檔。
  - 啟動前驗證參數 `--db-path`、目錄絕對路徑與唯讀權限設定。

## 2. Tree-sitter 靜態分析與 AST 理解

- **原理**：Tree-sitter 提供毫秒級增量語法解析，在不執行代碼的前提下，將程式碼轉成具型別標記的 AST。
- **應用場景**：
  - **符號定位**：擷取檔案內所有 Class、Function、Decorators 與 Type Annotations。
  - **精確代碼切片**：當 Context 預算吃緊時，只抽取特定目標函數的 AST 子樹，而不是傳遞整個 1,000 行檔案。
  - **依賴反查**：從語法樹提取 `import`、`from ... import` 與動態呼叫關係。

## 3. 本機增量索引管理 (SQLite + Local Embedding)

- **增量監聽機制**：
  - 透過 Git Commit Hash 或檔案 `mtime` 比對，僅挑選「變更檔案」進行重新切塊（Chunking）。
  - 將代碼塊 AST 特徵與 Local Embedding（如輕量向量模型）存入本機 SQLite。
- **成果指標**：
  - 程式碼變更秒級完成同步索引。
  - Agent 本機語意檢索回應延遲 < 100ms。
