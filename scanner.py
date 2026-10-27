"""
Albion Online 黑市製造利潤掃描引擎
資料來源：Albion Data Client / AODP API
計算基準：以一般(Normal)、優良(Good)、出眾(Outstanding)為實戰參考，排除不實用的傑作灌水
"""

import time
import requests
import concurrent.futures
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from items_database import (
    TIERS, QUALITY_MAP, MATERIAL_TYPES,
    EQUIPMENT_DEFINITIONS, get_all_material_ids, get_all_equipment_items,
    get_journal_stats, calculate_quality_chances, get_item_focus_cost,
    MATERIAL_REFINING_CITIES, CITY_CRAFTING_BONUSES, get_item_royal_city_info
)

SERVERS = {
    "east": "https://east.albion-online-data.com/api/v2/stats",
    "west": "https://west.albion-online-data.com/api/v2/stats",
    "europe": "https://europe.albion-online-data.com/api/v2/stats"
}

# 紅城製造返還率
RRR_NO_FOCUS = 0.152   # 無專注 15.2%
RRR_FOCUS = 0.479      # 專注 47.9%
MARKET_TAX = 0.04      # 即時砸單特權稅 4.0%
ORDER_SETUP_FEE = 0.025 # 批量掛單設定費 2.5%

class MarketScanner:
    def __init__(self, server_key: str = "east"):
        self.server_key = server_key
        self.base_url = SERVERS.get(server_key, SERVERS["east"])
        self.rrr_no_focus = RRR_NO_FOCUS
        self.rrr_focus = RRR_FOCUS
        self.tax = MARKET_TAX
        self.order_fee = ORDER_SETUP_FEE
        self.sell_mode = "instant"    # 'instant' (4%) 或 'order' (6.5%)
        self.price_basis = "sell_min" # 'sell_min' 或 'buy_max'
        self.journal_subsidy = True
        self.journal_mode = "laborer" # 'laborer' (工人資源產出) 或 'sell' (日誌市價折現) 或 'off'
        self.inner_spec = 100         # 內圈母節點專精 (0~100)
        self.outer_spec = 100         # 外圈單品專精 (0~100)
        self.food = "potato"          # 'none', 'potato' (+100), 'kraken' (+200)
        self.safe_batch_pct = 0.30    # 安全批量比例 (預設 30% 日均消化量)
        self.bubble_threshold = 0.35  # 暴漲 / 泡泡 / 壓單風險警示門檻 (+35%)
        
        # 快取
        self.last_scan_time: Optional[float] = None
        self.materials_cache: List[Dict[str, Any]] = []
        self.equipment_cache: List[Dict[str, Any]] = []
        self.is_scanning: bool = False
        self.scan_progress: str = "就緒"

    def set_config(self, server_key: Optional[str] = None, 
                   rrr_no_focus: Optional[float] = None,
                   rrr_focus: Optional[float] = None,
                   tax: Optional[float] = None, 
                   order_fee: Optional[float] = None,
                   sell_mode: Optional[str] = None,
                   price_basis: Optional[str] = None,
                   journal_subsidy: Optional[bool] = None,
                   journal_mode: Optional[str] = None,
                   inner_spec: Optional[int] = None,
                   outer_spec: Optional[int] = None,
                   food: Optional[str] = None,
                   safe_batch_pct: Optional[float] = None,
                   bubble_threshold: Optional[float] = None):
        if server_key and server_key in SERVERS:
            self.server_key = server_key
            self.base_url = SERVERS[server_key]
        if rrr_no_focus is not None:
            self.rrr_no_focus = float(rrr_no_focus)
        if rrr_focus is not None:
            self.rrr_focus = float(rrr_focus)
        if tax is not None:
            self.tax = float(tax)
        if order_fee is not None:
            self.order_fee = float(order_fee)
        if sell_mode in ["instant", "order"]:
            self.sell_mode = sell_mode
        if price_basis in ["sell_min", "buy_max"]:
            self.price_basis = price_basis
        if journal_subsidy is not None:
            self.journal_subsidy = bool(journal_subsidy)
        if journal_mode in ["laborer", "sell", "off"]:
            self.journal_mode = journal_mode
        if inner_spec is not None:
            self.inner_spec = int(inner_spec)
        if outer_spec is not None:
            self.outer_spec = int(outer_spec)
        if food in ["none", "potato", "kraken"]:
            self.food = food
        if safe_batch_pct is not None:
            self.safe_batch_pct = max(0.05, min(1.0, float(safe_batch_pct)))
        if bubble_threshold is not None:
            self.bubble_threshold = max(0.10, min(2.0, float(bubble_threshold)))

    def fetch_materials(self) -> Dict[tuple, Dict[str, Any]]:
        mat_map = get_all_material_ids()
        all_ids = list(mat_map.values())
        headers = {'User-Agent': 'AlbionRadar/2.0'}
        mat_prices = {}
        
        chunk_size = 50
        chunks = [all_ids[i:i + chunk_size] for i in range(0, len(all_ids), chunk_size)]
        
        # 同時抓取紅城與五大皇家精煉產地城行情
        locations_str = "Caerleon,Fort%20Sterling,Lymhurst,Bridgewatch,Martlock,Thetford"
        for chunk in chunks:
            ids_str = ",".join(chunk)
            url = f"{self.base_url}/prices/{ids_str}?locations={locations_str}&qualities=1"
            try:
                resp = requests.get(url, headers=headers, timeout=12)
                if resp.status_code == 200:
                    for item in resp.json():
                        item_id = item.get("item_id")
                        city = item.get("city", "Caerleon")
                        s_min = item.get("sell_price_min", 0)
                        b_max = item.get("buy_price_max", 0)
                        key = (item_id, city)
                        mat_prices[key] = {
                            "sell_min": s_min if s_min > 0 else 0,
                            "buy_max": b_max if b_max > 0 else 0,
                            "updated_at": item.get("sell_price_min_date", "")
                        }
            except Exception as e:
                print(f"Error fetching materials: {e}")

        structured_materials = {}
        for (mat_type, tier), api_id in mat_map.items():
            # 1. 紅城本地價格
            caer_info = mat_prices.get((api_id, "Caerleon"), {"sell_min": 0, "buy_max": 0, "updated_at": ""})
            caer_p = caer_info[self.price_basis] if caer_info[self.price_basis] > 0 else caer_info["sell_min"]
            
            # 2. 對應皇家精煉加成產地城價格 (木材->白城, 皮革->藍城, 布料->綠城, 鐵錠->紫城, 石磚->黃城)
            refining_meta = MATERIAL_REFINING_CITIES.get(mat_type, {})
            refining_city = refining_meta.get("city", "Caerleon")
            refining_city_zh = refining_meta.get("name_zh", refining_city)
            refining_city_short = refining_meta.get("short_name", refining_city)
            
            ref_info = mat_prices.get((api_id, refining_city), {"sell_min": 0, "buy_max": 0, "updated_at": ""})
            ref_p = ref_info[self.price_basis] if ref_info[self.price_basis] > 0 else ref_info["sell_min"]
            
            # 若產地價格為 0 (無數據)，安全保底退回紅城價
            if ref_p <= 0:
                ref_p = caer_p

            # 價差與省錢幅度
            price_diff = caer_p - ref_p if (caer_p > 0 and ref_p > 0) else 0
            price_diff_pct = round((price_diff / caer_p) * 100, 1) if caer_p > 0 and price_diff > 0 else 0.0

            # 彙整五大城行情快照
            all_city_prices = {}
            for c_name in ["Caerleon", "Fort Sterling", "Martlock", "Lymhurst", "Thetford", "Bridgewatch"]:
                c_data = mat_prices.get((api_id, c_name), {"sell_min": 0, "buy_max": 0})
                all_city_prices[c_name] = c_data

            structured_materials[(mat_type, tier)] = {
                "mat_type": mat_type,
                "mat_name": MATERIAL_TYPES[mat_type],
                "tier": tier,
                "api_id": api_id,
                # 紅城本地行情 (相容既有模型)
                "sell_min": caer_info["sell_min"],
                "buy_max": caer_info["buy_max"],
                "price": caer_p if caer_p > 0 else caer_info["sell_min"],
                "caerleon_price": caer_p if caer_p > 0 else caer_info["sell_min"],
                # 皇家精煉產地直供行情
                "refining_city": refining_city,
                "refining_city_zh": refining_city_zh,
                "refining_city_short": refining_city_short,
                "refining_price": ref_p,
                "refining_sell_min": ref_info["sell_min"],
                "refining_buy_max": ref_info["buy_max"],
                "price_diff": price_diff,
                "price_diff_pct": price_diff_pct,
                "city_prices": all_city_prices
            }

        return structured_materials

    def fetch_journal_prices(self) -> Dict[str, int]:
        """抓取紅城集市日誌（空本與滿本）即時掛賣最低價，提供最精確的日誌折現補貼依據"""
        journal_types = ["HUNTER", "MAGE", "WARRIOR", "TOOLMAKER"]
        tiers = [4, 5, 6]
        ids = []
        for j in journal_types:
            for t in tiers:
                ids.append(f"T{t}_JOURNAL_{j}_EMPTY")
                ids.append(f"T{t}_JOURNAL_{j}_FULL")

        headers = {'User-Agent': 'AlbionRadar/2.0'}
        url = f"{self.base_url}/prices/{','.join(ids)}?locations=Caerleon"
        prices = {}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                for item in resp.json():
                    iid = item.get("item_id")
                    s_min = item.get("sell_price_min", 0)
                    if s_min > 0:
                        prices[iid] = s_min
        except Exception as e:
            print(f"Error fetching journal prices: {e}")
        return prices

    def fetch_black_market_prices(self, item_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        headers = {'User-Agent': 'AlbionRadar/2.0'}
        results = {api_id: {"prices": {}, "dates": {}} for api_id in item_ids}
        
        chunk_size = 50
        chunks = [item_ids[i:i + chunk_size] for i in range(0, len(item_ids), chunk_size)]
        
        def fetch_chunk(chunk):
            ids_str = ",".join(chunk)
            url = f"{self.base_url}/prices/{ids_str}?locations=Black%20Market"
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    return resp.json()
            except Exception as e:
                print(f"Error fetching prices chunk: {e}")
            return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            future_to_chunk = {executor.submit(fetch_chunk, ch): ch for ch in chunks}
            for future in concurrent.futures.as_completed(future_to_chunk):
                items_data = future.result()
                if items_data:
                    for data in items_data:
                        api_id = data.get("item_id")
                        q = data.get("quality", 1)
                        # 黑市是賣給 NPC 收購單 (立即出售)，必須取 buy_price_max。
                        price = data.get("buy_price_max", 0)
                        date_str = data.get("buy_price_max_date", "")
                        if api_id in results and price > 0:
                            current = results[api_id]["prices"].get(q, 0)
                            if price > current:
                                results[api_id]["prices"][q] = price
                                results[api_id]["dates"][q] = date_str

        return results

    def fetch_black_market_history(self, item_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        headers = {'User-Agent': 'AlbionRadar/2.0'}
        results = {api_id: {
            "total_7d_vol": 0,
            "daily_avg_vol": 0.0,
            "avg_price_7d": 0,
            "common_7d_avg": 0,
            "liquidity_rating": "低流通",
            "by_q": {}
        } for api_id in item_ids}
        
        chunk_size = 50
        chunks = [item_ids[i:i + chunk_size] for i in range(0, len(item_ids), chunk_size)]
        
        def fetch_h_chunk(chunk):
            ids_str = ",".join(chunk)
            url = f"{self.base_url}/history/{ids_str}?locations=Black%20Market&time-scale=24"
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    return resp.json()
            except Exception as e:
                print(f"Error fetching history chunk: {e}")
            return []

        raw_entries = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            future_to_chunk = {executor.submit(fetch_h_chunk, ch): ch for ch in chunks}
            for future in concurrent.futures.as_completed(future_to_chunk):
                data = future.result()
                if data:
                    raw_entries.extend(data)

        # 整理統計各裝備歷史數據
        item_stats = {}
        for entry in raw_entries:
            api_id = entry.get("item_id")
            if not api_id or api_id not in results:
                continue
            q = entry.get("quality", 1)
            pts = entry.get("data", [])[-7:]
            if not pts:
                continue
            
            if api_id not in item_stats:
                item_stats[api_id] = {"total_vol": 0, "total_rev": 0, "by_q": {}}
                
            q_vol = sum(p.get("item_count", 0) for p in pts)
            q_rev = sum(p.get("item_count", 0) * p.get("avg_price", 0) for p in pts)
            
            item_stats[api_id]["total_vol"] += q_vol
            item_stats[api_id]["total_rev"] += q_rev
            item_stats[api_id]["by_q"][q] = {
                "vol": q_vol,
                "avg": int(round(q_rev / q_vol)) if q_vol > 0 else 0
            }

        for api_id, s in item_stats.items():
            tot = s["total_vol"]
            avg_7d = int(round(s["total_rev"] / tot)) if tot > 0 else 0
            daily_vol = round(tot / 7.0, 1)
            
            q1 = s["by_q"].get(1, {"avg": 0, "vol": 0})
            q2 = s["by_q"].get(2, {"avg": 0, "vol": 0})
            common_vol = q1["vol"] + q2["vol"]
            common_rev = (q1["avg"] * q1["vol"]) + (q2["avg"] * q2["vol"])
            common_avg = int(round(common_rev / common_vol)) if common_vol > 0 else avg_7d
            
            if daily_vol >= 50:
                liq = "高流通"
            elif daily_vol >= 10:
                liq = "中流通"
            else:
                liq = "低流通"
                
            results[api_id] = {
                "total_7d_vol": tot,
                "daily_avg_vol": daily_vol,
                "avg_price_7d": avg_7d,
                "common_7d_avg": common_avg,
                "liquidity_rating": liq,
                "by_q": s["by_q"]
            }

        return results

    def run_full_scan(self) -> Dict[str, Any]:
        self.is_scanning = True
        self.scan_progress = "正在並發抓取材料行情、黑市即時買單與一週歷史深度..."
        t_start = time.time()
        
        try:
            equipments = get_all_equipment_items()
            all_equipment_ids = [eq["api_id"] for eq in equipments]
            
            # 並發執行四個核心網路查詢任務 (材料、黑市收單、一週歷史深度、紅城日誌市價)
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                fut_mat = executor.submit(self.fetch_materials)
                fut_bm = executor.submit(self.fetch_black_market_prices, all_equipment_ids)
                fut_hist = executor.submit(self.fetch_black_market_history, all_equipment_ids)
                fut_journal = executor.submit(self.fetch_journal_prices)
                
                mat_dict = fut_mat.result()
                bm_prices = fut_bm.result()
                bm_history = fut_hist.result()
                journal_prices = fut_journal.result()
            
            self.scan_progress = "正在計算利潤、向下相容保底與日誌工人收益..."
            processed_equipments = []
            
            # 手續費因子：即時砸單 4.0%，批量掛單 4.0% + 2.5% = 6.5%
            effective_tax = (self.tax + self.order_fee) if self.sell_mode == "order" else self.tax
            fee_factor = 1.0 - effective_tax
            
            for eq in equipments:
                api_id = eq["api_id"]
                tier = eq["tier"]
                recipe = eq["recipe"]
                
                # 直購材料原成本
                raw_cost = 0
                for mat_type, count in recipe.items():
                    mat_info = mat_dict.get((mat_type, tier))
                    p = mat_info["price"] if mat_info else 0
                    if p > 0:
                        raw_cost += count * p
                
                # 無專注 (15.2% 返還) 與 專注 (47.9% 返還) 實質成本
                cost_no_focus = int(round(raw_cost * (1.0 - self.rrr_no_focus))) if raw_cost > 0 else 0
                cost_focus = int(round(raw_cost * (1.0 - self.rrr_focus))) if raw_cost > 0 else 0
                
                # ================== 皇家五大城市製造模型 ==================
                royal_info = get_item_royal_city_info(eq["subcat"], eq.get("id"))
                royal_city = royal_info["city_id"]
                royal_city_zh = royal_info["name_zh"]
                royal_city_short = royal_info["short_name"]
                royal_city_badge = royal_info["badge_class"]
                royal_city_icon = royal_info.get("icon", "🏰")
                royal_rrr_nf = royal_info["rrr_no_focus"]  # 0.248 (或紅城 0.152)
                royal_rrr_f = royal_info["rrr_focus"]      # 0.479

                # 皇家精煉產地原成本
                royal_raw_cost = 0
                royal_mats_breakdown = []
                for mat_type, count in recipe.items():
                    mat_info = mat_dict.get((mat_type, tier))
                    ref_p = mat_info.get("refining_price", 0) if mat_info else 0
                    ref_city_zh = mat_info.get("refining_city_zh", "產地城") if mat_info else "產地城"
                    caer_p = mat_info.get("caerleon_price", 0) if mat_info else 0
                    if ref_p > 0:
                        subtotal = count * ref_p
                        royal_raw_cost += subtotal
                        royal_mats_breakdown.append({
                            "mat_type": mat_type,
                            "mat_name": MATERIAL_TYPES.get(mat_type, mat_type),
                            "count": count,
                            "city_zh": ref_city_zh,
                            "unit_price": ref_p,
                            "caerleon_unit_price": caer_p,
                            "subtotal": subtotal
                        })

                # 皇家加成城市實質成本 (完全無運費/物流扣除)
                royal_cost_no_focus = int(round(royal_raw_cost * (1.0 - royal_rrr_nf))) if royal_raw_cost > 0 else 0
                royal_cost_focus = int(round(royal_raw_cost * (1.0 - royal_rrr_f))) if royal_raw_cost > 0 else 0
                
                # 即時黑市原始收單價與時間戳記
                item_bm = bm_prices.get(api_id, {"prices": {}, "dates": {}})
                q_prices = item_bm.get("prices", {})
                q_dates = item_bm.get("dates", {})

                # 時效性解析
                target_date = q_dates.get(2) or q_dates.get(1) or (list(q_dates.values())[0] if q_dates else "")
                price_age_hours = 999.0
                if target_date and not str(target_date).startswith("0001"):
                    try:
                        dt_clean = str(target_date).replace("Z", "").split(".")[0]
                        dt_obj = datetime.fromisoformat(dt_clean).replace(tzinfo=timezone.utc)
                        now_utc = datetime.now(timezone.utc)
                        price_age_hours = max(0.0, (now_utc - dt_obj).total_seconds() / 3600.0)
                    except Exception:
                        price_age_hours = 999.0

                if price_age_hours <= 1.0:
                    price_age_badge = "⚡ 1小時內"
                    price_age_level = "fresh"
                elif price_age_hours <= 24.0:
                    price_age_badge = f"🕒 {int(round(price_age_hours))}小時前"
                    price_age_level = "recent"
                elif price_age_hours < 999.0:
                    d = int(round(price_age_hours / 24.0))
                    price_age_badge = f"⚠️ {d}天前"
                    price_age_level = "stale"
                else:
                    price_age_badge = "無記錄"
                    price_age_level = "unknown"

                p_normal = q_prices.get(1, 0)       # 一般 (Normal, Q1)
                p_good = q_prices.get(2, 0)         # 優良 (Good, Q2)
                p_outstanding = q_prices.get(3, 0)  # 出眾/優秀 (Outstanding, Q3)
                p_excellent = q_prices.get(4, 0)    # 卓越 (Excellent, Q4)
                p_masterpiece = q_prices.get(5, 0)  # 傑作 (Masterpiece, Q5)
                
                # ================== 3. 黑市向下相容機制 ==================
                # 當黑市發布低品質買單，高品質裝備可以直接砸入！
                # 故有效保底價為：max(自身品質價, 更低品質的買單價)
                eff_normal = p_normal
                eff_good = max(eff_normal, p_good)
                eff_outstanding = max(eff_good, p_outstanding)
                eff_excellent = max(eff_outstanding, p_excellent)
                eff_masterpiece = max(eff_excellent, p_masterpiece)
                
                # 向下相容後的常規最高收購價
                compat_max_price = max(eff_normal, eff_good)
                
                # 官方多重擲骰品質機率模型 (計算專精與沙拉加成)
                q_calc = calculate_quality_chances(self.inner_spec, self.outer_spec, self.food, False)
                q_chances = q_calc["chances"]
                
                # 大量批量製作加權期望售價 (向下相容有效保底價 × 多重擲骰品質機率)
                expected_craft_price = int(round(
                    eff_normal * q_chances[1] +
                    eff_good * q_chances[2] +
                    eff_outstanding * q_chances[3] +
                    eff_excellent * q_chances[4] +
                    eff_masterpiece * q_chances[5]
                ))
                
                # 原始常規品質收購價 (未相容)
                common_max_price = max(p_normal, p_good)
                valid_common = [p for p in [p_normal, p_good] if p > 0]
                common_avg_price = int(round(sum(valid_common) / len(valid_common))) if valid_common else 0
                valid_top3 = [p for p in [p_normal, p_good, p_outstanding] if p > 0]
                top3_avg_price = int(round(sum(valid_top3) / len(valid_top3))) if valid_top3 else 0

                # ================== 1. 一週歷史均價與深度數據 ==================
                hist_info = bm_history.get(api_id, {
                    "total_7d_vol": 0, "daily_avg_vol": 0.0,
                    "avg_price_7d": 0, "common_7d_avg": 0,
                    "liquidity_rating": "低流通", "by_q": {}
                })
                avg_price_7d = hist_info.get("avg_price_7d", 0)
                common_7d_avg = hist_info.get("common_7d_avg", 0)
                daily_avg_vol = hist_info.get("daily_avg_vol", 0.0)
                total_7d_vol = hist_info.get("total_7d_vol", 0)
                liquidity_rating = hist_info.get("liquidity_rating", "低流通")
                
                # ================== 4. 日誌補貼與紅城島工人產出 ==================
                journal_info = get_journal_stats(eq["cat"], tier, recipe, journal_prices=journal_prices)
                
                # ================== 5. 黑市風控定價引擎與雙軌建議 ==================
                # 穩健掛單價邏輯：
                # 1. 基準價：取 當前收單價 (compat_max_price) 與 7天均價 (common_7d_avg) 的較大者
                #    當價格暴漲時，市場掛單落在 compat_max_price 附近（玩家在黑市掛單競爭），絕不可退回歷史低均價拋售；
                #    當買單處於低谷時，掛在 7天均價 等待 NPC 買價回升。
                base_order_price = max(compat_max_price, common_7d_avg) if (compat_max_price > 0 or common_7d_avg > 0) else 0
                order_fee_factor = 1.0 - (self.tax + self.order_fee)
                
                # 2. 保本防線：掛單扣除 6.5% 稅費後，絕不應低於成本！
                #    若成本高於基準價，掛單價至少需以保本價 (成本 / order_fee_factor) 為底線，避免推薦虧損出貨
                breakeven_order_price = int(round(cost_no_focus / order_fee_factor)) if (cost_no_focus > 0 and order_fee_factor > 0) else 0
                order_sell_price = max(base_order_price, breakeven_order_price) if base_order_price > 0 else breakeven_order_price
                instant_sell_price = compat_max_price

                # 預設基準價格：若為掛單模式以穩健掛單價為準，否則採用向下相容後最高價
                if self.sell_mode == "order":
                    benchmark_price = order_sell_price
                else:
                    benchmark_price = compat_max_price if compat_max_price > 0 else common_max_price
                
                # 計算基準利潤 (扣除當前模式手續費)
                profit_no_focus = int(round(benchmark_price * fee_factor - cost_no_focus)) if benchmark_price > 0 and cost_no_focus > 0 else 0
                profit_focus = int(round(benchmark_price * fee_factor - cost_focus)) if benchmark_price > 0 and cost_focus > 0 else 0
                
                roi_no_focus = round((profit_no_focus / cost_no_focus) * 100, 1) if cost_no_focus > 0 and benchmark_price > 0 else 0.0
                roi_focus = round((profit_focus / cost_focus) * 100, 1) if cost_focus > 0 and benchmark_price > 0 else 0.0
                
                # 每日暴利潛力指數 (日均消化量 × 單件利潤，日誌補貼以市場真實折現計算)
                unit_subsidy = journal_info.get("market_subsidy", 0) if self.journal_mode != "off" else 0
                net_unit_profit = profit_no_focus + unit_subsidy
                daily_profit_potential = int(round(net_unit_profit * daily_avg_vol)) if net_unit_profit > 0 and daily_avg_vol > 0 else 0

                # 穩健估算：以穩健掛單價為基準 (扣6.5%掛單稅費)，防範盲目砸單回落，且保證不為負
                profit_hist = int(round(order_sell_price * order_fee_factor - cost_no_focus)) if order_sell_price > 0 and cost_no_focus > 0 else 0
                realistic_daily_potential = int(round((profit_hist + unit_subsidy) * daily_avg_vol)) if (profit_hist + unit_subsidy) > 0 and daily_avg_vol > 0 else 0

                # ================== 皇家五大城市製造收益 (無運費/物流扣除) ==================
                royal_profit_no_focus = int(round(benchmark_price * fee_factor - royal_cost_no_focus)) if benchmark_price > 0 and royal_cost_no_focus > 0 else 0
                royal_profit_focus = int(round(benchmark_price * fee_factor - royal_cost_focus)) if benchmark_price > 0 and royal_cost_focus > 0 else 0

                royal_roi_no_focus = round((royal_profit_no_focus / royal_cost_no_focus) * 100, 1) if royal_cost_no_focus > 0 and benchmark_price > 0 else 0.0
                royal_roi_focus = round((royal_profit_focus / royal_cost_focus) * 100, 1) if royal_cost_focus > 0 and benchmark_price > 0 else 0.0

                extra_profit_no_focus = royal_profit_no_focus - profit_no_focus
                extra_profit_focus = royal_profit_focus - profit_focus
                cost_saving_silver = cost_no_focus - royal_cost_no_focus
                cost_saving_pct = round((cost_saving_silver / cost_no_focus) * 100, 1) if cost_no_focus > 0 and cost_saving_silver > 0 else 0.0
                profit_boost_pct = round((extra_profit_no_focus / abs(profit_no_focus)) * 100, 1) if profit_no_focus != 0 else (100.0 if royal_profit_no_focus > 0 else 0.0)

                # 皇家每日暴利潛力 (以皇家淨利 × 日銷量)
                royal_daily_potential = int(round((royal_profit_no_focus + unit_subsidy) * daily_avg_vol)) if (royal_profit_no_focus + unit_subsidy) > 0 and daily_avg_vol > 0 else 0

                if benchmark_price == 0:
                    royal_status = "無收單"
                elif royal_profit_no_focus > 0:
                    royal_status = "無專注可賺"
                elif royal_profit_focus > 0:
                    royal_status = "下專注才賺"
                else:
                    royal_status = "虧損"
                
                # 判斷狀態
                if benchmark_price == 0:
                    status = "無收單"
                elif profit_no_focus > 0:
                    status = "無專注可賺"
                elif profit_focus > 0:
                    status = "下專注才賺"
                else:
                    status = "虧損"

                # 各品質明細 (含原始價、向下相容保底價與相容補貼差額)
                eff_map = {1: eff_normal, 2: eff_good, 3: eff_outstanding, 4: eff_excellent, 5: eff_masterpiece}
                qualities_data = []
                for q_level, q_name in QUALITY_MAP.items():
                    bp = q_prices.get(q_level, 0)
                    eff_p = eff_map.get(q_level, bp)
                    compat_bonus = eff_p - bp if (eff_p > bp and bp > 0) else (eff_p if bp == 0 and eff_p > 0 else 0)
                    
                    np_nf = int(round(eff_p * fee_factor - cost_no_focus)) if eff_p > 0 and cost_no_focus > 0 else 0
                    np_f = int(round(eff_p * fee_factor - cost_focus)) if eff_p > 0 and cost_focus > 0 else 0
                    
                    q_hist = hist_info.get("by_q", {}).get(q_level, {"avg": 0, "vol": 0})
                    
                    qualities_data.append({
                        "quality": q_level,
                        "quality_name": q_name,
                        "bm_price": bp,                     # 原始買單價
                        "eff_price": eff_p,                 # 向下相容有效保底價
                        "compat_bonus": compat_bonus,       # 相容提升溢價
                        "profit_no_focus": np_nf,
                        "profit_focus": np_f,
                        "is_profitable": np_nf > 0 or np_f > 0,
                        "hist_avg_price": q_hist.get("avg", 0),
                        "hist_vol": q_hist.get("vol", 0)
                    })
                
                # 安全批量與泡泡風險分析
                safe_batch_qty = max(1, int(round(daily_avg_vol * self.safe_batch_pct))) if daily_avg_vol >= 1.0 else 1
                
                bubble_ratio = 0.0
                bubble_risk = "stable"
                bubble_badge = "🟢 價格穩健"
                bubble_tip = "即時買單與週均價接近，市場流動消化正常。"
                
                if compat_max_price > 0 and common_7d_avg > 0:
                    bubble_ratio = round((compat_max_price - common_7d_avg) / float(common_7d_avg), 3)
                    if bubble_ratio >= self.bubble_threshold:
                        pct_val = int(round(bubble_ratio * 100))
                        bubble_risk = "high_risk"
                        bubble_badge = f"⚠️ 暴漲 +{pct_val}%"
                    elif bubble_ratio <= -0.15:
                        pct_val = int(round(bubble_ratio * 100))
                        bubble_risk = "trough"
                        bubble_badge = f"💎 買單低谷 {pct_val}%"
                        bubble_tip = f"當前買單 ({compat_max_price:,} 銀) 低於 7 天均價 ({common_7d_avg:,} 銀)，黑市目前吸收價偏低，建議以穩健價 ({order_sell_price:,} 銀) 掛單出貨等待 NPC 買價回升。"
                elif compat_max_price > 0 and common_7d_avg == 0:
                    bubble_risk = "low_history"
                    bubble_badge = "🆕 歷史單少"
                    bubble_tip = "此商品過去一週黑市成交量極少，建議小批量試水溫。"

                # 雙軌出貨定價與件數拆單規劃
                if bubble_risk == "high_risk":
                    rec_instant_qty = min(safe_batch_qty, 2)
                    rec_order_qty = max(0, safe_batch_qty - rec_instant_qty)
                    bubble_tip = f"即時買單 ({compat_max_price:,} 銀) 遠高於 7 天均價 ({common_7d_avg:,} 銀)！黑市頂部高價買單通常僅有少數件數。建議少量 ({rec_instant_qty} 件) 即時砸單吃頂部現折，其餘 ({rec_order_qty} 件) 以穩健價 ({order_sell_price:,} 銀) 掛單出貨，切勿盲目大批量低價砸穿盤口！"
                else:
                    rec_instant_qty = safe_batch_qty
                    rec_order_qty = safe_batch_qty

                # ================== 6. 專注效率與邊際銀/點 ==================
                focus_cost = get_item_focus_cost(tier, recipe, self.inner_spec, self.outer_spec)
                marginal_profit = profit_focus - profit_no_focus
                silver_per_focus = round(marginal_profit / focus_cost, 1) if (focus_cost > 0 and marginal_profit > 0) else 0.0

                processed_equipments.append({
                    "api_id": api_id,
                    "base_id": eq["base_id"],
                    "name": eq["name"],
                    "tier": tier,
                    "cat": eq["cat"],
                    "subcat": eq["subcat"],
                    "recipe": eq["recipe"],
                    "recipe_str": eq["recipe_str"],
                    
                    # 成本
                    "raw_cost": raw_cost,
                    "cost_no_focus": cost_no_focus,
                    "cost_focus": cost_focus,
                    
                    # 原始即時買單價
                    "p_normal": p_normal,
                    "p_good": p_good,
                    "p_outstanding": p_outstanding,
                    "p_excellent": p_excellent,
                    "p_masterpiece": p_masterpiece,
                    "common_max_price": common_max_price,
                    "common_avg_price": common_avg_price,
                    "top3_avg_price": top3_avg_price,
                    
                    # 3. 向下相容有效買單價與加權期望售價
                    "eff_normal": eff_normal,
                    "eff_good": eff_good,
                    "eff_outstanding": eff_outstanding,
                    "eff_excellent": eff_excellent,
                    "eff_masterpiece": eff_masterpiece,
                    "compat_max_price": compat_max_price,
                    "expected_craft_price": expected_craft_price,
                    
                    # 1. 歷史一週均價與黑市銷量深度
                    "avg_price_7d": avg_price_7d,
                    "common_7d_avg": common_7d_avg,
                    "daily_avg_vol": daily_avg_vol,
                    "total_7d_vol": total_7d_vol,
                    "liquidity_rating": liquidity_rating,
                    
                    # 4. 製作日誌與紅城島工人產出
                    "journal": journal_info,
                    
                    # 暴利綜合指標
                    "daily_profit_potential": daily_profit_potential,
                    "realistic_daily_potential": realistic_daily_potential,
                    
                    # 利潤 (無專注 vs 專注)
                    "profit_no_focus": profit_no_focus,
                    "profit_focus": profit_focus,
                    "roi_no_focus": roi_no_focus,
                    "roi_focus": roi_focus,

                    # 5. 黑市風控定價引擎
                    "safe_batch_qty": safe_batch_qty,
                    "bubble_ratio": bubble_ratio,
                    "bubble_risk": bubble_risk,
                    "bubble_badge": bubble_badge,
                    "bubble_tip": bubble_tip,
                    "instant_sell_price": instant_sell_price,
                    "order_sell_price": order_sell_price,
                    "rec_instant_qty": rec_instant_qty,
                    "rec_order_qty": rec_order_qty,
                    "price_age_hours": round(price_age_hours, 1),
                    "price_age_badge": price_age_badge,
                    "price_age_level": price_age_level,

                    # 6. 專注效率
                    "focus_cost": focus_cost,
                    "silver_per_focus": silver_per_focus,
                    
                    "status": status,
                    "qualities": qualities_data,

                    # 7. 皇家城市製造專用指標 (加成城製造 + 精煉產地直供 + 黑市無運費扣除)
                    "royal_city": royal_city,
                    "royal_city_zh": royal_city_zh,
                    "royal_city_short": royal_city_short,
                    "royal_city_badge": royal_city_badge,
                    "royal_city_icon": royal_city_icon,
                    "royal_rrr_no_focus": royal_rrr_nf,
                    "royal_rrr_focus": royal_rrr_f,
                    "royal_raw_cost": royal_raw_cost,
                    "royal_cost_no_focus": royal_cost_no_focus,
                    "royal_cost_focus": royal_cost_focus,
                    "royal_profit_no_focus": royal_profit_no_focus,
                    "royal_profit_focus": royal_profit_focus,
                    "royal_roi_no_focus": royal_roi_no_focus,
                    "royal_roi_focus": royal_roi_focus,
                    "extra_profit_no_focus": extra_profit_no_focus,
                    "extra_profit_focus": extra_profit_focus,
                    "cost_saving_silver": cost_saving_silver,
                    "cost_saving_pct": cost_saving_pct,
                    "profit_boost_pct": profit_boost_pct,
                    "royal_daily_potential": royal_daily_potential,
                    "royal_status": royal_status,
                    "royal_mats_breakdown": royal_mats_breakdown
                })

            materials_list = list(mat_dict.values())
            self.materials_cache = materials_list
            self.equipment_cache = processed_equipments
            self.last_scan_time = time.time()
            elapsed = time.time() - t_start
            self.scan_progress = f"更新完成 (耗時 {elapsed:.2f} 秒，共 {len(processed_equipments)} 件裝備)"
            
            return {
                "success": True,
                "elapsed": elapsed,
                "total_items": len(processed_equipments),
                "timestamp": self.last_scan_time,
                "materials": materials_list,
                "equipments": processed_equipments
            }
        except Exception as e:
            self.scan_progress = f"掃描失敗: {str(e)}"
            return {"success": False, "error": str(e)}
        finally:
            self.is_scanning = False
