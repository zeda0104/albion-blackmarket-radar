---
name: codegraph-graphify
description: >-
  Use this skill to navigate the project's architectural dependency graph, locate code
  impacts using Graphify (graph.json), reduce blind tool calls, and maintain graph version control.
---

# CodeGraph & Graphify 架構拓撲導航技能

本技能指導 AI Agent 在進行跨模組重構、API 變更或功能增刪前，利用預先建構的架構拓撲圖（`graphify-out/graph.json`）進行精準導航，避免盲目 `read_file` 與全文 Grep。

## 核心流程

1. **圖譜優先導航 (Graph-First Navigation)**
   - 在修改任何核心模組（如 `app.py`, `scanner.py`, `items_database.py`, `ledger_manager.py`）之前，先確認該模組的被依賴關係（Callers）與依賴關係（Callees）。
   - 快速查詢節點依賴關係：
     ```bash
     python .agents/skills/codegraph-graphify/scripts/sync_graph.py <模組關鍵字>
     ```

2. **多模態圖譜對齊 (SQL + Code + UI)**
   - 關注全景拓撲中的 6 大社群樞紐：
     - **Community 0 (前端介面層)**: `static/index.html`（雷達、製造、猛獁、記帳、專精）
     - **Community 1 (服務路由層)**: `app.py`（FastAPI 端點與 Lifespan 背景掃描）
     - **Community 2 (計算引擎層)**: `scanner.py`（黑市擲骰公式、城市返還率、利潤排序）
     - **Community 3 (資料庫層)**: `items_database.py`（960 件裝備配方矩陣）
     - **Community 4 (持久化層)**: `ledger_manager.py`, `data/specs.json`, `data/記帳.xlsx`
     - **Community 5 (雲端部署層)**: `render.yaml`, `Dockerfile`, `Procfile`

3. **圖譜版本控制 (Graph as Code)**
   - 嚴格落實 `graphify-out/graph.json` 與 `graphify-out/GRAPH_REPORT.md` 納入 Git 版本控制。
   - 當架構發生重大變更（新增 Tab、新增 API 路由或修改核心計算依賴）時，更新拓撲圖並提交，免除團隊重複解析掃描。
