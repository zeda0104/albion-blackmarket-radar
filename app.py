"""
Albion Online 黑市製造利潤計算機 - 本機服務主程式
"""

import os
import sys
import time
import threading
import webbrowser
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from scanner import MarketScanner
from items_database import calculate_quality_chances, EQUIPMENT_DEFINITIONS, get_item_focus_cost
import ledger_manager
import json

SPECS_FILE = os.path.join("data", "specs.json")

def load_saved_specs() -> Dict[str, Any]:
    """從 data/specs.json 載入使用者專精與食物設定，避免瀏覽器快取清除遺失"""
    if os.path.exists(SPECS_FILE):
        try:
            with open(SPECS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[警告] 讀取專精檔案失敗: {e}")
    return {
        "inner_spec": 100,
        "outer_spec": 100,
        "food_type": "potato",
        "item_specs": {},
        "mastery_specs": {}
    }

def save_specs_to_file(data: Dict[str, Any]) -> bool:
    """持久化保存使用者專精與食物設定至 data/specs.json"""
    os.makedirs("data", exist_ok=True)
    try:
        with open(SPECS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[錯誤] 儲存專精檔案失敗: {e}")
        return False

scanner = MarketScanner(server_key="east")
# 系統啟動時載入本機已儲存專精數據
_init_specs = load_saved_specs()
scanner.inner_spec = _init_specs.get("inner_spec", 100)
scanner.outer_spec = _init_specs.get("outer_spec", 100)
scanner.food = _init_specs.get("food_type", "potato")
os.makedirs("static", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    def background_first_scan():
        print("[系統] 正在抓取最新市場行情...")
        scanner.run_full_scan()
        print("[系統] 市場行情已更新完畢。")
        
    threading.Thread(target=background_first_scan, daemon=True).start()
    yield

app = FastAPI(title="阿爾比恩黑市製造利潤計算機", lifespan=lifespan)

class ConfigRequest(BaseModel):
    server: Optional[str] = None
    rrr_no_focus: Optional[float] = None
    rrr_focus: Optional[float] = None
    tax: Optional[float] = None
    order_fee: Optional[float] = None
    sell_mode: Optional[str] = None
    price_basis: Optional[str] = None
    journal_subsidy: Optional[bool] = None
    journal_mode: Optional[str] = None
    inner_spec: Optional[int] = None
    outer_spec: Optional[int] = None
    food: Optional[str] = None
    safe_batch_pct: Optional[float] = None
    safe_batch_cap: Optional[int] = None
    bubble_threshold: Optional[float] = None

class LedgerRequest(BaseModel):
    date: Optional[str] = None
    type: str = "支出"
    tier: str = "T4.0"
    name: str
    quality: str = "一般"
    qty: int = 1
    price: int = 0
    fee: int = 0
    sell_mode: Optional[str] = None
    mode: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def get_index():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if not os.path.exists(index_path):
        index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>找不到前端頁面 static/index.html</h1>"

@app.get("/api/status")
def get_status():
    return {
        "server": scanner.server_key,
        "rrr_no_focus": scanner.rrr_no_focus,
        "rrr_focus": scanner.rrr_focus,
        "tax": scanner.tax,
        "order_fee": scanner.order_fee,
        "sell_mode": scanner.sell_mode,
        "journal_subsidy": scanner.journal_subsidy,
        "journal_mode": scanner.journal_mode,
        "inner_spec": scanner.inner_spec,
        "outer_spec": scanner.outer_spec,
        "food": scanner.food,
        "price_basis": scanner.price_basis,
        "safe_batch_pct": scanner.safe_batch_pct,
        "safe_batch_cap": scanner.safe_batch_cap,
        "bubble_threshold": scanner.bubble_threshold,
        "is_scanning": scanner.is_scanning,
        "scan_progress": scanner.scan_progress,
        "last_scan_time": scanner.last_scan_time,
        "total_items": len(scanner.equipment_cache)
    }

@app.post("/api/scan")
def trigger_scan():
    if scanner.is_scanning:
        return {"success": False, "message": "正在更新中，請稍候..."}
    return scanner.run_full_scan()

@app.get("/api/radar")
def get_radar_data():
    if not scanner.equipment_cache:
        scanner.run_full_scan()
        
    return {
        "last_scan_time": scanner.last_scan_time,
        "server": scanner.server_key,
        "rrr_no_focus": scanner.rrr_no_focus,
        "rrr_focus": scanner.rrr_focus,
        "tax": scanner.tax,
        "order_fee": scanner.order_fee,
        "sell_mode": scanner.sell_mode,
        "journal_subsidy": scanner.journal_subsidy,
        "journal_mode": scanner.journal_mode,
        "inner_spec": scanner.inner_spec,
        "outer_spec": scanner.outer_spec,
        "food": scanner.food,
        "safe_batch_pct": scanner.safe_batch_pct,
        "safe_batch_cap": scanner.safe_batch_cap,
        "bubble_threshold": scanner.bubble_threshold,
        "quality_stats": calculate_quality_chances(scanner.inner_spec, scanner.outer_spec, scanner.food, False),
        "materials": scanner.materials_cache,
        "equipments": scanner.equipment_cache,
        "equipment_definitions": EQUIPMENT_DEFINITIONS
    }

@app.get("/api/config")
def get_config():
    return {
        "server": scanner.server_key,
        "rrr_no_focus": scanner.rrr_no_focus,
        "rrr_focus": scanner.rrr_focus,
        "tax": scanner.tax,
        "order_fee": scanner.order_fee,
        "sell_mode": scanner.sell_mode,
        "journal_subsidy": scanner.journal_subsidy,
        "journal_mode": scanner.journal_mode,
        "inner_spec": scanner.inner_spec,
        "outer_spec": scanner.outer_spec,
        "food": scanner.food,
        "price_basis": scanner.price_basis,
        "safe_batch_pct": scanner.safe_batch_pct,
        "safe_batch_cap": scanner.safe_batch_cap,
        "bubble_threshold": scanner.bubble_threshold
    }

@app.post("/api/config")
def update_config(cfg: ConfigRequest):
    need_rescan = (cfg.server is not None and cfg.server != scanner.server_key) or \
                  (cfg.price_basis is not None and cfg.price_basis != scanner.price_basis)
    
    scanner.set_config(
        server_key=cfg.server,
        rrr_no_focus=cfg.rrr_no_focus,
        rrr_focus=cfg.rrr_focus,
        tax=cfg.tax,
        order_fee=cfg.order_fee,
        sell_mode=cfg.sell_mode,
        price_basis=cfg.price_basis,
        journal_subsidy=cfg.journal_subsidy,
        journal_mode=cfg.journal_mode,
        inner_spec=cfg.inner_spec,
        outer_spec=cfg.outer_spec,
        food=cfg.food,
        safe_batch_pct=cfg.safe_batch_pct,
        safe_batch_cap=cfg.safe_batch_cap,
        bubble_threshold=cfg.bubble_threshold
    )
    
    if need_rescan:
        scanner.run_full_scan()
    elif scanner.materials_cache and scanner.equipment_cache:
        # 重新計算成本與利潤
        effective_tax = (scanner.tax + scanner.order_fee) if scanner.sell_mode == "order" else scanner.tax
        fee_factor = 1.0 - effective_tax
        q_calc = calculate_quality_chances(scanner.inner_spec, scanner.outer_spec, scanner.food, False)
        q_chances = q_calc["chances"]
        
        for eq in scanner.equipment_cache:
            raw = eq["raw_cost"]
            c_nf = int(round(raw * (1.0 - scanner.rrr_no_focus))) if raw > 0 else 0
            c_f = int(round(raw * (1.0 - scanner.rrr_focus))) if raw > 0 else 0
            eq["cost_no_focus"] = c_nf
            eq["cost_focus"] = c_f
            
            # 更新批量期望價
            eq["expected_craft_price"] = int(round(
                eq.get("eff_normal", 0) * q_chances[1] +
                eq.get("eff_good", 0) * q_chances[2] +
                eq.get("eff_outstanding", 0) * q_chances[3] +
                eq.get("eff_excellent", 0) * q_chances[4] +
                eq.get("eff_masterpiece", 0) * q_chances[5]
            ))
            
            c_max = eq.get("compat_max_price", 0)
            c_7d = eq.get("common_7d_avg", 0)
            
            # 穩健掛單價與保本計算 (掛單扣 6.5% 稅費後不可低於成本)
            order_fee_factor = 1.0 - (scanner.tax + scanner.order_fee)
            base_ord = max(c_max, c_7d) if (c_max > 0 or c_7d > 0) else 0
            breakeven_ord = int(round(c_nf / order_fee_factor)) if (c_nf > 0 and order_fee_factor > 0) else 0
            order_sell_price = max(base_ord, breakeven_ord) if base_ord > 0 else breakeven_ord

            eq["instant_sell_price"] = c_max
            eq["order_sell_price"] = order_sell_price
            
            # 依銷售模式取基準價 (掛單模式以穩健掛單價為準，即時模式優先向下相容價，無單時自動回退週均價保底)
            price_is_history = False
            if scanner.sell_mode == "order":
                bm = order_sell_price
            else:
                if c_max > 0:
                    bm = c_max
                elif c_7d > 0:
                    bm = c_7d
                    price_is_history = True
                elif eq.get("common_max_price", 0) > 0:
                    bm = eq.get("common_max_price", 0)
                else:
                    bm = 0
                
            p_nf = int(round(bm * fee_factor - c_nf)) if bm > 0 and c_nf > 0 else 0
            p_f = int(round(bm * fee_factor - c_f)) if bm > 0 and c_f > 0 else 0
            eq["profit_no_focus"] = p_nf
            eq["profit_focus"] = p_f
            eq["roi_no_focus"] = round((p_nf / c_nf) * 100, 1) if c_nf > 0 and bm > 0 else 0.0
            eq["roi_focus"] = round((p_f / c_f) * 100, 1) if c_f > 0 and bm > 0 else 0.0
            daily_vol = eq.get("daily_avg_vol", 0.0)
            
            unit_sub = eq.get("journal", {}).get("market_subsidy", 0) if scanner.journal_mode != "off" else 0
            net_u_prof = p_nf + unit_sub

            # 重新計算安全批量 (階梯比例 + 上限封頂)
            safe_qty = scanner.calculate_safe_batch(daily_vol)
            eq["safe_batch_qty"] = safe_qty
            
            # 單批安全利潤與穩健日潛力
            safe_profit = int(round(net_u_prof * safe_qty)) if net_u_prof > 0 else 0
            eq["safe_batch_profit"] = safe_profit
            eq["realistic_daily_potential"] = safe_profit * 2
            eq["daily_profit_potential"] = int(round(net_u_prof * daily_vol)) if net_u_prof > 0 and daily_vol > 0 else 0
            eq["price_is_history"] = price_is_history
            eq["weekly_unit_profit_nf"] = int(round(c_7d * fee_factor - c_nf + unit_sub)) if c_7d > 0 and c_nf > 0 else 0

            # 重新計算專注效率 (銀/點)
            f_cost = get_item_focus_cost(eq["tier"], eq.get("recipe", {}), scanner.inner_spec, scanner.outer_spec)
            eq["focus_cost"] = f_cost
            marg = p_f - p_nf
            eq["silver_per_focus"] = round(marg / f_cost, 1) if (f_cost > 0 and marg > 0) else 0.0
            
            if c_max > 0 and c_7d > 0:
                b_ratio = round((c_max - c_7d) / float(c_7d), 3)
                eq["bubble_ratio"] = b_ratio
                if b_ratio >= scanner.bubble_threshold:
                    pct_val = int(round(b_ratio * 100))
                    eq["bubble_risk"] = "high_risk"
                    eq["bubble_badge"] = f"⚠️ 暴漲 +{pct_val}%"
                    eq["rec_instant_qty"] = min(safe_qty, 2)
                    eq["rec_order_qty"] = max(0, safe_qty - eq["rec_instant_qty"])
                    eq["bubble_tip"] = f"即時買單 ({c_max:,} 銀) 遠高於 7 天均價 ({c_7d:,} 銀)！黑市頂部買單量通常極少。建議即時砸單 {eq['rec_instant_qty']} 件吃頂部現折，其餘 {eq['rec_order_qty']} 件以穩健價 ({order_sell_price:,} 銀) 掛單出貨，切勿盲目大批量直接砸單！"
                elif b_ratio <= -0.15:
                    pct_val = int(round(b_ratio * 100))
                    eq["bubble_risk"] = "trough"
                    eq["bubble_badge"] = f"💎 買單低谷 {pct_val}%"
                    eq["rec_instant_qty"] = safe_qty
                    eq["rec_order_qty"] = safe_qty
                    eq["bubble_tip"] = f"當前買單 ({c_max:,} 銀) 低於 7 天均價 ({c_7d:,} 銀)，黑市目前吸收價偏低，建議以穩健價 ({order_sell_price:,} 銀) 掛單出貨等待 NPC 買價回升。"
                else:
                    eq["bubble_risk"] = "stable"
                    eq["bubble_badge"] = "🟢 價格穩健"
                    eq["rec_instant_qty"] = safe_qty
                    eq["rec_order_qty"] = safe_qty
                    eq["bubble_tip"] = "即時買單與一週均價相當吻合，流動性消化正常，適宜依安全批量穩定出貨。"
            else:
                eq["rec_instant_qty"] = safe_qty
                eq["rec_order_qty"] = safe_qty
            
            if bm == 0:
                eq["status"] = "無收單"
            elif p_nf > 0:
                eq["status"] = "週均可賺" if price_is_history else "無專注可賺"
            elif p_f > 0:
                eq["status"] = "下專注才賺"
            else:
                eq["status"] = "虧損"

            # 重新計算皇家城市製造指標
            r_raw = eq.get("royal_raw_cost", 0)
            r_rrr_nf = eq.get("royal_rrr_no_focus", 0.248)
            r_rrr_f = eq.get("royal_rrr_focus", 0.479)
            r_c_nf = int(round(r_raw * (1.0 - r_rrr_nf))) if r_raw > 0 else 0
            r_c_f = int(round(r_raw * (1.0 - r_rrr_f))) if r_raw > 0 else 0
            eq["royal_cost_no_focus"] = r_c_nf
            eq["royal_cost_focus"] = r_c_f

            r_p_nf = int(round(bm * fee_factor - r_c_nf)) if bm > 0 and r_c_nf > 0 else 0
            r_p_f = int(round(bm * fee_factor - r_c_f)) if bm > 0 and r_c_f > 0 else 0
            eq["royal_profit_no_focus"] = r_p_nf
            eq["royal_profit_focus"] = r_p_f
            eq["royal_roi_no_focus"] = round((r_p_nf / r_c_nf) * 100, 1) if r_c_nf > 0 and bm > 0 else 0.0
            eq["royal_roi_focus"] = round((r_p_f / r_c_f) * 100, 1) if r_c_f > 0 and bm > 0 else 0.0

            extra_nf = r_p_nf - p_nf
            eq["extra_profit_no_focus"] = extra_nf
            eq["extra_profit_focus"] = r_p_f - p_f
            c_saving = c_nf - r_c_nf
            eq["cost_saving_silver"] = c_saving
            eq["cost_saving_pct"] = round((c_saving / c_nf) * 100, 1) if c_nf > 0 and c_saving > 0 else 0.0
            eq["profit_boost_pct"] = round((extra_nf / abs(p_nf)) * 100, 1) if p_nf != 0 else (100.0 if r_p_nf > 0 else 0.0)

            unit_subsidy = eq.get("journal", {}).get("market_subsidy", 0) if scanner.journal_mode != "off" else 0
            eq["royal_daily_potential"] = int(round((r_p_nf + unit_subsidy) * daily_vol)) if (r_p_nf + unit_subsidy) > 0 and daily_vol > 0 else 0
            r_safe_profit = int(round((r_p_nf + unit_subsidy) * safe_qty)) if (r_p_nf + unit_subsidy) > 0 else 0
            eq["royal_safe_batch_profit"] = r_safe_profit
            eq["royal_realistic_potential"] = r_safe_profit * 2
            eq["royal_weekly_unit_profit_nf"] = int(round(c_7d * fee_factor - r_c_nf + unit_subsidy)) if c_7d > 0 and r_c_nf > 0 else 0

            if bm == 0:
                eq["royal_status"] = "無收單"
            elif r_p_nf > 0:
                eq["royal_status"] = "週均可賺" if price_is_history else "無專注可賺"
            elif r_p_f > 0:
                eq["royal_status"] = "下專注才賺"
            else:
                eq["royal_status"] = "虧損"

    return {"success": True, "config": get_config()}

@app.get("/api/ledger")
def get_ledger():
    return ledger_manager.get_ledger_records()

@app.post("/api/ledger")
def add_ledger(rec: LedgerRequest):
    success = ledger_manager.add_ledger_record(rec.model_dump())
    if not success:
        raise HTTPException(status_code=500, detail="寫入記帳本失敗，請確認檔案未被鎖定")
    return {"success": True, "data": ledger_manager.get_ledger_records()}

@app.delete("/api/ledger/{record_id}")
def delete_ledger(record_id: int):
    success = ledger_manager.delete_ledger_record(record_id)
    if not success:
        raise HTTPException(status_code=500, detail="刪除記錄失敗")
    return {"success": True, "data": ledger_manager.get_ledger_records()}

@app.get("/api/export-excel")
def export_excel():
    if os.path.exists(ledger_manager.LEDGER_FILE):
        return FileResponse(
            ledger_manager.LEDGER_FILE,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="記帳.xlsx"
        )
    raise HTTPException(status_code=404, detail="記帳本檔案不存在")


class SpecsRequest(BaseModel):
    inner_spec: Optional[int] = 100
    outer_spec: Optional[int] = 100
    food_type: Optional[str] = "potato"
    item_specs: Optional[Dict[str, int]] = {}
    mastery_specs: Optional[Dict[str, int]] = {}

@app.get("/api/specs")
def get_specs():
    """取得持久化儲存之專精設定 (data/specs.json)"""
    return load_saved_specs()

@app.post("/api/specs")
def save_specs(req: SpecsRequest):
    """保存使用者專精程度至檔案 (data/specs.json) 以免遺失"""
    data = req.model_dump()
    success = save_specs_to_file(data)
    if not success:
        raise HTTPException(status_code=500, detail="儲存專精檔案失敗")
    
    if req.inner_spec is not None:
        scanner.inner_spec = req.inner_spec
    if req.outer_spec is not None:
        scanner.outer_spec = req.outer_spec
    if req.food_type is not None:
        scanner.food = req.food_type
        
    return {"success": True, "message": "專精配置已成功儲存至 data/specs.json", "data": data}


app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    import socket
    
    port = int(os.environ.get("PORT", 8000))
    is_cloud = bool(os.environ.get("PORT") or os.environ.get("RENDER"))
    
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    local_ip = get_local_ip()

    print("=" * 60)
    print("  ⚔️ 阿爾比恩 黑市製造利潤計算機 ⚔️")
    print(f"  本機網址: http://localhost:{port}")
    if local_ip != "127.0.0.1":
        print(f"  區網其他裝置 (手機/平板/筆電): http://{local_ip}:{port}")
    print("=" * 60)
    
    def open_browser():
        time.sleep(1.2)
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass
        
    def free_port(p):
        try:
            import subprocess
            out = subprocess.check_output(f'netstat -ano | findstr :{p}', shell=True).decode()
            for line in out.splitlines():
                if 'LISTENING' in line:
                    parts = line.strip().split()
                    pid = parts[-1]
                    if int(pid) != os.getpid():
                        print(f"  [提示] 發現舊程序 (PID: {pid}) 占用 {p} 埠，正在自動清除釋放...")
                        subprocess.call(f'taskkill /F /PID {pid}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        time.sleep(0.5)
        except Exception:
            pass

    if not is_cloud:
        free_port(port)
        threading.Thread(target=open_browser, daemon=True).start()
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except OSError as e:
        if '10048' in str(e):
            print(f"\n⚠️ 連接埠 {port} 被占用。黑市雷達已在背景執行中，請直接於瀏覽器輸入: http://localhost:{port}")
        else:
            raise e
