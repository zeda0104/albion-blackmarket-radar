# Graph Report - 阿爾比恩量化帝國 (2026-10-28 更新版)

## 系統全景概覽
- **模組總結**：31 個核心節點 · 42 條主調用關係 · 6 大架構社群
- **主架構升級**：
  1. 雲端化託管：Render.com (24hr Free Tier) + GitHub 自動 CI/CD 部署。
  2. 皇家城市製造分頁：支援 6 大城市製造加成（24.8% / 47.9%）與原產地原料成本計算。
  3. 猛獁之路任務樹：360M 目標進度試算、階段 I~IV 智慧選品、日常作戰 SOP。
  4. 專精持久化：`data/specs.json` 自動保存與載入。

## 核心社群樞紐 (Community Hubs)
1. **前端介面與交互層 (Community 0)**
   - `static/index.html` (黑市雷達、皇家製造、猛獁任務、批量採購、跨城行情、記帳本、專精配置)
2. **API 與服務入口層 (Community 1)**
   - `app.py` (FastAPI 路由、Lifespan 背景初次掃描、REST 端點)
3. **市場掃描與量化計算引擎 (Community 2)**
   - `scanner.py` (AODP 批次查詢、7天深度分析、向下相容多重擲骰模型、皇家加成推算、獵人工人折抵)
4. **裝備配方與常數資料庫 (Community 3)**
   - `items_database.py` (960 件裝備配方全集、6 大城市加成矩陣)
5. **資料持久化與儲存層 (Community 4)**
   - `ledger_manager.py`、`data/specs.json`、`data/記帳.xlsx`
6. **雲端部署與維運層 (Community 5)**
   - `render.yaml`、`Dockerfile`、`Procfile`、`[一鍵上傳GITHUB].bat`

## 廢棄與冗餘檔案清查摘要
- ❌ **`static/index.html.reconstructed`** (519 KB)：修復暫存檔，已徹底刪除。
- ⚠️ **`cloudflared.exe`** (55 MB) 與 **`[外網遠端連線]啟動雲端通道.bat`**：轉移至 Render 雲端後已冗餘，可安全移除。
- ⚠️ **`archive/`** (145 MB)：舊版 PyInstaller 打包產物，已自 Git 排除。

> 詳細圖文架構圖請參閱：[`docs/專案架構圖譜.md`](../docs/專案架構圖譜.md)
