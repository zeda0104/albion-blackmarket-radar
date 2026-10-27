"""
Albion Online 黑市套利雷達 - 裝備與材料資料庫
包含 4.0 ~ 6.3 所有無神器裝備（獵人小屋、法師之塔、戰士鐵匠鋪、冒險者配件）
"""

# 支援的階級與附魔等級
TIERS = [
    "4.0", "4.1", "4.2", "4.3",
    "5.0", "5.1", "5.2", "5.3",
    "6.0", "6.1", "6.2", "6.3"
]

QUALITY_MAP = {
    1: "一般 (Normal)",
    2: "優良 (Good)",
    3: "出眾 (Outstanding)",
    4: "卓越 (Excellent)",
    5: "傑作 (Masterpiece)"
}

# 基礎裝備定義 (80 項無神器裝備)
EQUIPMENT_DEFINITIONS = [
    # ================== 🏹 獵人小屋 (Hunter's Lodge) ==================
    # 弓箭
    {"id": "2H_BOW", "name": "弓箭", "cat": "獵人小屋", "subcat": "弓箭", "recipe": {"PLANKS": 32}},
    {"id": "2H_WARBOW", "name": "戰弓", "cat": "獵人小屋", "subcat": "弓箭", "recipe": {"PLANKS": 32}},
    {"id": "2H_LONGBOW", "name": "長弓", "cat": "獵人小屋", "subcat": "弓箭", "recipe": {"PLANKS": 32}},
    # 長矛
    {"id": "MAIN_SPEAR", "name": "長矛", "cat": "獵人小屋", "subcat": "長矛", "recipe": {"PLANKS": 16, "METALBAR": 8}},
    {"id": "2H_SPEAR", "name": "長槍", "cat": "獵人小屋", "subcat": "長矛", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    {"id": "2H_GLAIVE", "name": "長刀", "cat": "獵人小屋", "subcat": "長矛", "recipe": {"PLANKS": 12, "METALBAR": 20}},
    # 匕首
    {"id": "MAIN_DAGGER", "name": "匕首", "cat": "獵人小屋", "subcat": "匕首", "recipe": {"METALBAR": 12, "LEATHER": 12}},
    {"id": "2H_DAGGERPAIR", "name": "雙匕首", "cat": "獵人小屋", "subcat": "匕首", "recipe": {"METALBAR": 16, "LEATHER": 16}},
    {"id": "2H_CLAWPAIR", "name": "鉤爪", "cat": "獵人小屋", "subcat": "匕首", "recipe": {"METALBAR": 12, "LEATHER": 20}},
    # 鐵頭棍
    {"id": "2H_QUARTERSTAFF", "name": "鐵頭棍", "cat": "獵人小屋", "subcat": "鐵頭棍", "recipe": {"METALBAR": 12, "LEATHER": 20}},
    {"id": "2H_IRONCLADEDSTAFF", "name": "鐵甲棍", "cat": "獵人小屋", "subcat": "鐵頭棍", "recipe": {"METALBAR": 12, "LEATHER": 20}},
    {"id": "2H_DOUBLEBLADEDSTAFF", "name": "雙刃棍", "cat": "獵人小屋", "subcat": "鐵頭棍", "recipe": {"METALBAR": 12, "LEATHER": 20}},
    # 自然法杖
    {"id": "MAIN_NATURESTAFF", "name": "自然法杖", "cat": "獵人小屋", "subcat": "自然法杖", "recipe": {"PLANKS": 16, "CLOTH": 8}},
    {"id": "2H_NATURESTAFF", "name": "自然長杖", "cat": "獵人小屋", "subcat": "自然法杖", "recipe": {"PLANKS": 20, "CLOTH": 12}},
    {"id": "2H_WILDSTAFF", "name": "荒野法杖", "cat": "獵人小屋", "subcat": "自然法杖", "recipe": {"PLANKS": 20, "CLOTH": 12}},
    # 皮甲防具 (各部位獨立星盤大師與單品專精)
    {"id": "HEAD_LEATHER_SET1", "name": "傭兵兜帽", "cat": "獵人小屋", "subcat": "皮甲兜帽", "recipe": {"LEATHER": 8}},
    {"id": "HEAD_LEATHER_SET2", "name": "獵人兜帽", "cat": "獵人小屋", "subcat": "皮甲兜帽", "recipe": {"LEATHER": 8}},
    {"id": "HEAD_LEATHER_SET3", "name": "刺客兜帽", "cat": "獵人小屋", "subcat": "皮甲兜帽", "recipe": {"LEATHER": 8}},
    {"id": "ARMOR_LEATHER_SET1", "name": "傭兵外套", "cat": "獵人小屋", "subcat": "皮外套", "recipe": {"LEATHER": 16}},
    {"id": "ARMOR_LEATHER_SET2", "name": "獵人外套", "cat": "獵人小屋", "subcat": "皮外套", "recipe": {"LEATHER": 16}},
    {"id": "ARMOR_LEATHER_SET3", "name": "刺客外套", "cat": "獵人小屋", "subcat": "皮外套", "recipe": {"LEATHER": 16}},
    {"id": "SHOES_LEATHER_SET1", "name": "傭兵鞋子", "cat": "獵人小屋", "subcat": "皮鞋", "recipe": {"LEATHER": 8}},
    {"id": "SHOES_LEATHER_SET2", "name": "獵人鞋子", "cat": "獵人小屋", "subcat": "皮鞋", "recipe": {"LEATHER": 8}},
    {"id": "SHOES_LEATHER_SET3", "name": "刺客鞋子", "cat": "獵人小屋", "subcat": "皮鞋", "recipe": {"LEATHER": 8}},
    # 副手
    {"id": "OFF_TORCH", "name": "火炬", "cat": "獵人小屋", "subcat": "副手", "recipe": {"PLANKS": 4, "CLOTH": 4}},

    # ================== 🔮 法師之塔 (Mage's Tower) ==================
    # 火焰法杖
    {"id": "MAIN_FIRESTAFF", "name": "火焰法杖", "cat": "法師之塔", "subcat": "火焰法杖", "recipe": {"PLANKS": 16, "METALBAR": 8}},
    {"id": "2H_FIRESTAFF", "name": "火焰長杖", "cat": "法師之塔", "subcat": "火焰法杖", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    {"id": "2H_INFERNOSTAFF", "name": "地獄法杖", "cat": "法師之塔", "subcat": "火焰法杖", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    # 神聖法杖
    {"id": "MAIN_HOLYSTAFF", "name": "神聖法杖", "cat": "法師之塔", "subcat": "神聖法杖", "recipe": {"PLANKS": 16, "CLOTH": 8}},
    {"id": "2H_HOLYSTAFF", "name": "神聖長杖", "cat": "法師之塔", "subcat": "神聖法杖", "recipe": {"PLANKS": 20, "CLOTH": 12}},
    {"id": "2H_DIVINESTAFF", "name": "神性法杖", "cat": "法師之塔", "subcat": "神聖法杖", "recipe": {"PLANKS": 20, "CLOTH": 12}},
    # 祕術法杖
    {"id": "MAIN_ARCANESTAFF", "name": "祕術法杖", "cat": "法師之塔", "subcat": "祕術法杖", "recipe": {"PLANKS": 16, "METALBAR": 8}},
    {"id": "2H_ARCANESTAFF", "name": "祕術長杖", "cat": "法師之塔", "subcat": "祕術法杖", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    {"id": "2H_ENIGMATICSTAFF", "name": "謎團法杖", "cat": "法師之塔", "subcat": "祕術法杖", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    # 寒冰法杖
    {"id": "MAIN_FROSTSTAFF", "name": "寒冰法杖", "cat": "法師之塔", "subcat": "寒冰法杖", "recipe": {"PLANKS": 16, "METALBAR": 8}},
    {"id": "2H_FROSTSTAFF", "name": "寒冰長杖", "cat": "法師之塔", "subcat": "寒冰法杖", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    {"id": "2H_GLACIALSTAFF", "name": "冰川法杖", "cat": "法師之塔", "subcat": "寒冰法杖", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    # 詛咒法杖
    {"id": "MAIN_CURSEDSTAFF", "name": "詛咒法杖", "cat": "法師之塔", "subcat": "詛咒法杖", "recipe": {"PLANKS": 16, "METALBAR": 8}},
    {"id": "2H_CURSEDSTAFF", "name": "詛咒長杖", "cat": "法師之塔", "subcat": "詛咒法杖", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    {"id": "2H_DEMONICSTAFF", "name": "惡魔法杖", "cat": "法師之塔", "subcat": "詛咒法杖", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    # 布甲防具 (各部位獨立星盤大師與單品專精)
    {"id": "HEAD_CLOTH_SET1", "name": "學者風帽", "cat": "法師之塔", "subcat": "布甲風帽", "recipe": {"CLOTH": 8}},
    {"id": "HEAD_CLOTH_SET2", "name": "牧師風帽", "cat": "法師之塔", "subcat": "布甲風帽", "recipe": {"CLOTH": 8}},
    {"id": "HEAD_CLOTH_SET3", "name": "法師風帽", "cat": "法師之塔", "subcat": "布甲風帽", "recipe": {"CLOTH": 8}},
    {"id": "ARMOR_CLOTH_SET1", "name": "學者長袍", "cat": "法師之塔", "subcat": "布長袍", "recipe": {"CLOTH": 16}},
    {"id": "ARMOR_CLOTH_SET2", "name": "牧師長袍", "cat": "法師之塔", "subcat": "布長袍", "recipe": {"CLOTH": 16}},
    {"id": "ARMOR_CLOTH_SET3", "name": "法師長袍", "cat": "法師之塔", "subcat": "布長袍", "recipe": {"CLOTH": 16}},
    {"id": "SHOES_CLOTH_SET1", "name": "學者便鞋", "cat": "法師之塔", "subcat": "布便鞋", "recipe": {"CLOTH": 8}},
    {"id": "SHOES_CLOTH_SET2", "name": "牧師便鞋", "cat": "法師之塔", "subcat": "布便鞋", "recipe": {"CLOTH": 8}},
    {"id": "SHOES_CLOTH_SET3", "name": "法師便鞋", "cat": "法師之塔", "subcat": "布便鞋", "recipe": {"CLOTH": 8}},
    # 副手
    {"id": "OFF_BOOK", "name": "咒法之書", "cat": "法師之塔", "subcat": "副手", "recipe": {"CLOTH": 4, "LEATHER": 4}},

    # ================== ⚔️ 戰士鐵匠鋪 (Warrior's Forge) ==================
    # 劍
    {"id": "MAIN_SWORD", "name": "闊劍", "cat": "戰士鐵匠鋪", "subcat": "劍", "recipe": {"METALBAR": 16, "LEATHER": 8}},
    {"id": "2H_CLAYMORE", "name": "闊刃大劍", "cat": "戰士鐵匠鋪", "subcat": "劍", "recipe": {"METALBAR": 20, "LEATHER": 12}},
    {"id": "2H_DUALSWORD", "name": "雙劍", "cat": "戰士鐵匠鋪", "subcat": "劍", "recipe": {"METALBAR": 20, "LEATHER": 12}},
    # 斧
    {"id": "MAIN_AXE", "name": "戰斧", "cat": "戰士鐵匠鋪", "subcat": "斧", "recipe": {"PLANKS": 8, "METALBAR": 16}},
    {"id": "2H_AXE", "name": "大斧", "cat": "戰士鐵匠鋪", "subcat": "斧", "recipe": {"PLANKS": 12, "METALBAR": 20}},
    {"id": "2H_HALBERD", "name": "長柄斧", "cat": "戰士鐵匠鋪", "subcat": "斧", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    # 鎚
    {"id": "MAIN_HAMMER", "name": "戰鎚", "cat": "戰士鐵匠鋪", "subcat": "鎚", "recipe": {"METALBAR": 24}},
    {"id": "2H_POLEHAMMER", "name": "長柄鎚", "cat": "戰士鐵匠鋪", "subcat": "鎚", "recipe": {"METALBAR": 20, "CLOTH": 12}},
    {"id": "2H_HAMMER", "name": "大鎚", "cat": "戰士鐵匠鋪", "subcat": "鎚", "recipe": {"METALBAR": 20, "CLOTH": 12}},
    # 釘頭槌
    {"id": "MAIN_MACE", "name": "錘矛", "cat": "戰士鐵匠鋪", "subcat": "錘矛", "recipe": {"METALBAR": 16, "CLOTH": 8}},
    {"id": "2H_MACE", "name": "重型錘矛", "cat": "戰士鐵匠鋪", "subcat": "錘矛", "recipe": {"METALBAR": 20, "CLOTH": 12}},
    {"id": "2H_FLAIL", "name": "連枷/晨星", "cat": "戰士鐵匠鋪", "subcat": "錘矛", "recipe": {"METALBAR": 20, "CLOTH": 12}},
    # 十字弓
    {"id": "MAIN_1HCROSSBOW", "name": "輕型十字弓", "cat": "戰士鐵匠鋪", "subcat": "十字弓", "recipe": {"PLANKS": 16, "METALBAR": 8}},
    {"id": "2H_CROSSBOW", "name": "十字弓", "cat": "戰士鐵匠鋪", "subcat": "十字弓", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    {"id": "2H_CROSSBOWLARGE", "name": "重型十字弓", "cat": "戰士鐵匠鋪", "subcat": "十字弓", "recipe": {"PLANKS": 20, "METALBAR": 12}},
    # 拳套 / 戰拳
    {"id": "2H_KNUCKLES_SET1", "name": "格鬥家手套", "cat": "戰士鐵匠鋪", "subcat": "戰拳", "recipe": {"METALBAR": 12, "LEATHER": 20}},
    {"id": "2H_KNUCKLES_SET2", "name": "戰鬥手套", "cat": "戰士鐵匠鋪", "subcat": "戰拳", "recipe": {"METALBAR": 12, "LEATHER": 20}},
    {"id": "2H_KNUCKLES_SET3", "name": "刺刃手套", "cat": "戰士鐵匠鋪", "subcat": "戰拳", "recipe": {"METALBAR": 12, "LEATHER": 20}},
    # 板甲防具 (各部位獨立星盤大師與單品專精)
    {"id": "HEAD_PLATE_SET1", "name": "士兵頭盔", "cat": "戰士鐵匠鋪", "subcat": "板甲頭盔", "recipe": {"METALBAR": 8}},
    {"id": "HEAD_PLATE_SET2", "name": "騎士頭盔", "cat": "戰士鐵匠鋪", "subcat": "板甲頭盔", "recipe": {"METALBAR": 8}},
    {"id": "HEAD_PLATE_SET3", "name": "守護者頭盔", "cat": "戰士鐵匠鋪", "subcat": "板甲頭盔", "recipe": {"METALBAR": 8}},
    {"id": "ARMOR_PLATE_SET1", "name": "士兵護甲", "cat": "戰士鐵匠鋪", "subcat": "板甲護甲", "recipe": {"METALBAR": 16}},
    {"id": "ARMOR_PLATE_SET2", "name": "騎士護甲", "cat": "戰士鐵匠鋪", "subcat": "板甲護甲", "recipe": {"METALBAR": 16}},
    {"id": "ARMOR_PLATE_SET3", "name": "守護者護甲", "cat": "戰士鐵匠鋪", "subcat": "板甲護甲", "recipe": {"METALBAR": 16}},
    {"id": "SHOES_PLATE_SET1", "name": "士兵長靴", "cat": "戰士鐵匠鋪", "subcat": "板甲長靴", "recipe": {"METALBAR": 8}},
    {"id": "SHOES_PLATE_SET2", "name": "騎士長靴", "cat": "戰士鐵匠鋪", "subcat": "板甲長靴", "recipe": {"METALBAR": 8}},
    {"id": "SHOES_PLATE_SET3", "name": "守護者長靴", "cat": "戰士鐵匠鋪", "subcat": "板甲長靴", "recipe": {"METALBAR": 8}},
    # 副手
    {"id": "OFF_SHIELD", "name": "盾牌", "cat": "戰士鐵匠鋪", "subcat": "副手", "recipe": {"PLANKS": 4, "METALBAR": 4}},

    # ================== 🎒 工匠 / 冒險者配件 (Toolmaker / Accessories) ==================
    {"id": "BAG", "name": "背包", "cat": "工匠", "subcat": "背包", "recipe": {"CLOTH": 8, "LEATHER": 8}},
    {"id": "CAPE", "name": "披風", "cat": "工匠", "subcat": "披風", "recipe": {"CLOTH": 4, "LEATHER": 4}},
]

# 材料類別與顯示名稱
MATERIAL_TYPES = {
    "PLANKS": "木材",
    "LEATHER": "皮革",
    "METALBAR": "金屬條",
    "CLOTH": "布料"
}

REVERSE_MAT_TYPES = {
    "木材": "PLANKS", "木": "PLANKS", "木板": "PLANKS", "PLANKS": "PLANKS",
    "皮革": "LEATHER", "皮": "LEATHER", "LEATHER": "LEATHER",
    "金屬條": "METALBAR", "金屬": "METALBAR", "鐵": "METALBAR", "鐵條": "METALBAR", "METALBAR": "METALBAR",
    "布料": "CLOTH", "布": "CLOTH", "CLOTH": "CLOTH"
}

import os
import math
import openpyxl

def load_definitions_from_excel():
    """若本機存在 '武器材料名稱對照表.xlsx'，優先讀取並覆蓋裝備名稱與材料配方（支援 data/ 目錄與根目錄）"""
    excel_path = os.path.join("data", "武器材料名稱對照表.xlsx")
    if not os.path.exists(excel_path):
        excel_path = "武器材料名稱對照表.xlsx"
    if not os.path.exists(excel_path):
        return
    try:
        wb = openpyxl.load_workbook(excel_path, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) <= 1:
            return

        headers = [str(c or "").strip() for c in rows[0]]
        if "內部代碼(Base ID)" not in headers and "Base ID" not in headers:
            return

        base_id_idx = headers.index("內部代碼(Base ID)") if "內部代碼(Base ID)" in headers else headers.index("Base ID")
        name_idx = headers.index("裝備名稱") if "裝備名稱" in headers else 2
        cat_idx = headers.index("工坊類別") if "工坊類別" in headers else 0
        subcat_idx = headers.index("子類別") if "子類別" in headers else 1
        m1_idx = headers.index("主要材料") if "主要材料" in headers else 4
        c1_idx = headers.index("主要數量") if "主要數量" in headers else 5
        m2_idx = headers.index("次要材料") if "次要材料" in headers else 6
        c2_idx = headers.index("次要數量") if "次要數量" in headers else 7

        id_map = {eq["id"]: eq for eq in EQUIPMENT_DEFINITIONS}

        for r in rows[1:]:
            if not r or len(r) <= base_id_idx or not r[base_id_idx]:
                continue
            base_id = str(r[base_id_idx]).strip()
            if base_id in id_map:
                eq = id_map[base_id]
                if len(r) > name_idx and r[name_idx]:
                    eq["name"] = str(r[name_idx]).strip()
                if len(r) > cat_idx and r[cat_idx]:
                    eq["cat"] = str(r[cat_idx]).strip()
                if len(r) > subcat_idx and r[subcat_idx]:
                    eq["subcat"] = str(r[subcat_idx]).strip()

                new_recipe = {}
                if len(r) > c1_idx and r[m1_idx] and r[c1_idx]:
                    m1 = str(r[m1_idx]).strip()
                    c1 = str(r[c1_idx]).strip()
                    if c1.isdigit() and int(c1) > 0:
                        mat_key1 = REVERSE_MAT_TYPES.get(m1, m1)
                        if mat_key1 in MATERIAL_TYPES:
                            new_recipe[mat_key1] = int(c1)

                if len(r) > c2_idx and r[m2_idx] and r[c2_idx]:
                    m2 = str(r[m2_idx]).strip()
                    c2 = str(r[c2_idx]).strip()
                    if c2.isdigit() and int(c2) > 0:
                        mat_key2 = REVERSE_MAT_TYPES.get(m2, m2)
                        if mat_key2 in MATERIAL_TYPES:
                            new_recipe[mat_key2] = int(c2)

                if new_recipe:
                    eq["recipe"] = new_recipe
    except Exception as e:
        print(f"[提示] 讀取武器材料名稱對照表.xlsx: {e}")

# 初始嘗試載入 Excel 自訂設定
load_definitions_from_excel()

def get_equipment_api_id(base_id: str, tier: str) -> str:
    """
    根據階級 (例如 '4.0', '5.2') 與基礎 ID 生成 API 查詢 ID
    例如: '2H_BOW', '4.2' -> 'T4_2H_BOW@2'
    """
    base_tier = tier.split(".")[0]
    enchant = tier.split(".")[1] if "." in tier else "0"
    suffix = f"@{enchant}" if enchant not in ["0", ""] else ""
    return f"T{base_tier}_{base_id}{suffix}"

def get_material_api_id(mat_type: str, tier: str) -> str:
    """
    根據階級與材料類型生成材料的 API 查詢 ID
    例如: 'PLANKS', '4.2' -> 'T4_PLANKS_LEVEL2@2'
          'LEATHER', '5.0' -> 'T5_LEATHER'
    """
    base_tier = tier.split(".")[0]
    enchant = tier.split(".")[1] if "." in tier else "0"
    suffix = f"_LEVEL{enchant}@{enchant}" if enchant not in ["0", ""] else ""
    return f"T{base_tier}_{mat_type}{suffix}"

def get_all_material_ids():
    """獲取 4.0~6.3 全部材料 ID 字典 (mat_type, tier) -> api_id"""
    mat_ids = {}
    for tier in TIERS:
        for mat_type in MATERIAL_TYPES.keys():
            mat_ids[(mat_type, tier)] = get_material_api_id(mat_type, tier)
    return mat_ids

def get_all_equipment_items():
    """獲取全部 80 項裝備在 12 個階級下的完整清單 (共 960 項)"""
    load_definitions_from_excel()
    all_items = []
    for eq in EQUIPMENT_DEFINITIONS:
        for tier in TIERS:
            api_id = get_equipment_api_id(eq["id"], tier)
            recipe_readable = " + ".join([f"{count} {MATERIAL_TYPES[m]}" for m, count in eq["recipe"].items()])
            all_items.append({
                "api_id": api_id,
                "base_id": eq["id"],
                "name": f"T{tier} {eq['name']}",
                "tier": tier,
                "cat": eq["cat"],
                "subcat": eq["subcat"],
                "recipe": eq["recipe"],
                "recipe_str": recipe_readable
            })
    return all_items


# ================== 📜 製作日誌與島嶼工人產出對照 ==================
WORKSHOP_JOURNAL_MAP = {
    "獵人小屋": {
        "type": "HUNTER",
        "name": "獵人日誌",
        "laborer": "獵人工人",
        "yield_ratios": {"LEATHER": 0.50, "PLANKS": 0.25, "METALBAR": 0.25}
    },
    "戰士鐵匠鋪": {
        "type": "BLACKSMITH",
        "name": "鐵匠日誌",
        "laborer": "鐵匠工人",
        "yield_ratios": {"METALBAR": 0.50, "PLANKS": 0.25, "CLOTH": 0.25}
    },
    "法師之塔": {
        "type": "IMBUER",
        "name": "法師日誌",
        "laborer": "法師工人",
        "yield_ratios": {"CLOTH": 0.50, "PLANKS": 0.25, "METALBAR": 0.25}
    },
    "工匠": {
        "type": "TINKER",
        "name": "工匠日誌",
        "laborer": "工匠工人",
        "yield_ratios": {"PLANKS": 0.50, "LEATHER": 0.25, "METALBAR": 0.25}
    }
}

def calculate_quality_chances(inner_spec: int = 0, outer_spec: int = 0, food: str = "none", is_focus: bool = False) -> dict:
    """
    依據阿爾比恩官方多重擲骰機制 (Multi-Roll System) 精確計算各品質產出機率：
    - 基礎機率 (0 加成, 1 次擲骰):
      Q1 普通: 68.9%, Q2 優良: 25.0%, Q3 出眾: 5.0%, Q4 傑出: 1.0%, Q5 神作: 0.1%
    - Crafting Quality Bonus (QB) 來源:
      - 內圈 (Mastery 0~100): +0.3 點/級 (滿級 +30)
      - 外圈 (Spec 0~100): +2.5 點/級 (滿級 +250)
      - 食物 (Food): "potato" (T6 馬鈴薯沙拉/豬肉沙拉) +100, "kraken" (阿瓦隆海怪沙拉) +200, "none" +0
      - 專注 (Focus): +50 點
    - 擲骰次數 N = 1.0 + (QB / 100.0)
    - 累計機率公式: P(>= X) = 1.0 - (1.0 - p_base)^N
    """
    qb = 0.0
    qb += max(0, min(100, int(inner_spec or 0))) * 0.3
    qb += max(0, min(100, int(outer_spec or 0))) * 2.5
    if food == "potato":
        qb += 100.0
    elif food == "kraken":
        qb += 200.0
    if is_focus:
        qb += 50.0

    n_rolls = 1.0 + (qb / 100.0)

    # 基礎累計閾值
    p_q5_base = 0.001
    p_q4_plus = 0.011  # 0.010 + 0.001
    p_q3_plus = 0.061  # 0.050 + 0.010 + 0.001
    p_q2_plus = 0.311  # 0.250 + 0.050 + 0.010 + 0.001

    p_q5 = 1.0 - (1.0 - p_q5_base) ** n_rolls
    p_q4 = (1.0 - (1.0 - p_q4_plus) ** n_rolls) - p_q5
    p_q3 = (1.0 - (1.0 - p_q3_plus) ** n_rolls) - (p_q4 + p_q5)
    p_q2 = (1.0 - (1.0 - p_q2_plus) ** n_rolls) - (p_q3 + p_q4 + p_q5)
    p_q1 = max(0.0, 1.0 - (p_q2 + p_q3 + p_q4 + p_q5))

    return {
        "quality_bonus": round(qb, 1),
        "n_rolls": round(n_rolls, 2),
        "chances": {
            1: p_q1,
            2: p_q2,
            3: p_q3,
            4: p_q4,
            5: p_q5
        },
        "chances_pct": {
            "q1": round(p_q1 * 100, 2),
            "q2": round(p_q2 * 100, 2),
            "q3": round(p_q3 * 100, 2),
            "q4": round(p_q4 * 100, 2),
            "q5": round(p_q5 * 100, 2)
        }
    }

def get_journal_stats(cat: str, tier: str, recipe: dict, journal_prices: dict = None) -> dict:
    """
    計算單件裝備製作時的日誌聲望填充、可填本數、真實市場直售淨收益與紅城島工人產能換算。
    日誌無品質與附魔等級，高附魔裝備僅加速填充；單本市價依紅城實際買賣價格計算。
    """
    try:
        tier_str = str(tier)
        base_tier = int(tier_str.split(".")[0])
        enchant = int(tier_str.split(".")[1]) if "." in tier_str else 0
    except Exception:
        base_tier = 4
        enchant = 0

    total_mats = sum(recipe.values()) if recipe else 0

    # 官方聲望基準 (每單位原料) 與 日誌容量 (製造類日誌無附魔，附魔裝備倍增聲望加速填充)
    # 官方基礎聲望: T4: 22.5, T5: 90.0, T6: 270.0, T7: 810.0, T8: 2430.0
    fame_per_mat = {4: 22.5, 5: 90.0, 6: 270.0, 7: 810.0, 8: 2430.0}.get(base_tier, 22.5)
    enchant_mult = {0: 1.0, 1: 2.0, 2: 4.0, 3: 8.0}.get(enchant, 1.0)
    craft_fame = total_mats * fame_per_mat * enchant_mult

    # 官方製造日誌聲望容量 (T4: 3600, T5: 7200, T6: 14400, T7: 28800, T8: 57600)
    journal_capacity = {4: 3600, 5: 7200, 6: 14400, 7: 28800, 8: 57600}.get(base_tier, 3600)
    journals_filled = craft_fame / journal_capacity if journal_capacity > 0 else 0.0

    cfg = WORKSHOP_JOURNAL_MAP.get(cat, WORKSHOP_JOURNAL_MAP["獵人小屋"])
    j_type = cfg["type"]
    is_hunter = (cat == "獵人小屋")
    is_hunter_t6 = (is_hunter and base_tier == 6)

    # 取得真實紅城日誌市價 (滿日誌售價與空日誌購入價)
    fallback_prices = {
        4: {"full": 5800, "empty": 2000, "net": 3400},
        5: {"full": 11500, "empty": 3500, "net": 7200},
        6: {"full": 28500, "empty": 8500, "net": 18100},
    }.get(base_tier, {"full": 5800, "empty": 2000, "net": 3400})

    full_id = f"T{base_tier}_JOURNAL_{j_type}_FULL"
    empty_id = f"T{base_tier}_JOURNAL_{j_type}_EMPTY"

    full_p = 0
    empty_p = 0
    if journal_prices:
        full_p = journal_prices.get(full_id, 0)
        empty_p = journal_prices.get(empty_id, 0)

    if full_p <= 0:
        full_p = fallback_prices["full"]
    if empty_p <= 0:
        empty_p = fallback_prices["empty"]

    # 滿日誌以 6.5% 掛單稅費折抵後減去空書成本，即為每本市場實質純利
    unit_net_journal = max(0, int(round(full_p * 0.935 - empty_p)))
    market_subsidy = int(round(journals_filled * unit_net_journal))

    # 紅城島 15 位 T6 獵人工人循環換算 (單日上限 15 本，產出 200k~300k 純利)
    crafts_for_15_journals = int(math.ceil(15.0 / journals_filled)) if journals_filled > 0 else 0
    suggested_action = "優先分流 15 本給島嶼獵人 (+250k)，其餘市場直售" if is_hunter_t6 else "黑市/集市掛單直售 (不佔島嶼工人額度)"

    return {
        "journal_type": cfg["type"],
        "journal_name": f"T{base_tier} {cfg['name']}",
        "laborer_name": cfg["laborer"],
        "is_hunter": is_hunter,
        "is_hunter_t6": is_hunter_t6,
        "suggested_action": suggested_action,
        "craft_fame": int(round(craft_fame)),
        "journals_filled": round(journals_filled, 3),
        "crafts_for_15_journals": crafts_for_15_journals,
        "unit_net_journal": unit_net_journal,
        "full_journal_price": full_p,
        "empty_journal_price": empty_p,
        "market_subsidy": market_subsidy,
        "laborer_daily_net": 250000 if is_hunter_t6 else 0
    }

# ================== 官方裝備製造專注點數計算模型 ==================
# 阿爾比恩官方裝備製造每單位材料之基礎專注點數 (Base Focus Per Material)
# 依據等效階級 (Equivalent Tier = Tier + Enchantment Level)
# 官方數據 (ao-bin-dumps):
# - T4.0 (Teq 4): 53.625 (8件裝備=429, 16件=858, 24件=1286, 32件=1715)
# - T5.0 / T4.1 (Teq 5): 93.75 (8件=750, 16件=1501, 24件=2251, 32件=3001)
# - T6.0 / T5.1 / T4.2 (Teq 6): 164.125 (8件=1313, 16件=2626, 24件=3939, 32件=5252)
# - T7.0 / T6.1 / T5.2 / T4.3 (Teq 7): 287.25 (8件=2298, 16件=4596, 24件=6893, 32件=9191)
# - T8.0 / T7.1 / T6.2 / T5.3 / T4.4 (Teq 8): 502.625 (8件=4021, 16件=8042, 24件=12064, 32件=16085)
# - T8.1 / T7.2 / T6.3 / T5.4 (Teq 9): 879.625 (8件=7037)
# - T8.2 / T7.3 / T6.4 (Teq 10): 1539.375 (8件=12315)
# - T8.3 / T7.4 (Teq 11): 2693.875 (8件=21551)
# - T8.4 (Teq 12): 4714.375 (8件=37715)
CRAFTING_BASE_FOCUS_PER_MAT = {
    4: 53.625,
    5: 93.75,
    6: 164.125,
    7: 287.25,
    8: 502.625,
    9: 879.625,
    10: 1539.375,
    11: 2693.875,
    12: 4714.375
}

def get_item_focus_cost(tier: str, recipe: dict, mastery_spec: int = 100, item_spec: int = 100) -> int:
    """
    依據阿爾比恩官方專注點數公式計算單件裝備製造所需之專注點 (Focus Cost)：
    Focus Cost = Base Focus * (0.5 ^ (Efficiency / 10000))
    - 基礎專注 (Base Focus)：依裝備總材料數 × 官方製造每材料基礎專注 (依等效階級 Tier+Enchantment)
    - 專精效率點數 (Efficiency)：
      * 內圈星盤製造大師 (0~100) * 30
      * 外圈單品專精 (0~100) * 250
    """
    try:
        parts = str(tier).split(".")
        t = int(parts[0])
        e = int(parts[1]) if len(parts) > 1 else 0
    except Exception:
        t = 4
        e = 0

    total_mats = sum(recipe.values()) if recipe else 8
    equiv_tier = t + e
    if equiv_tier in CRAFTING_BASE_FOCUS_PER_MAT:
        base_per_mat = CRAFTING_BASE_FOCUS_PER_MAT[equiv_tier]
    elif equiv_tier < 4:
        base_per_mat = 53.625 * (0.57 ** (4 - equiv_tier))
    else:
        base_per_mat = 4714.375 * (1.75 ** (equiv_tier - 12))

    base_focus = total_mats * base_per_mat

    m_spec = max(0, min(100, int(mastery_spec if mastery_spec is not None else 100)))
    i_spec = max(0, min(100, int(item_spec if item_spec is not None else 100)))
    eff = (m_spec * 30) + (i_spec * 250)

    # 官方減免指數曲線：每 10,000 點效率減半
    ratio = 0.5 ** (eff / 10000.0)
    focus_cost = int(round(base_focus * ratio))
    return max(1, focus_cost)

# ================== 皇家五大城市「精煉與製造加成」定義 ==================

# 原物料精煉加成城市 (+40% 產量加成，基礎返還率 36.7%)
MATERIAL_REFINING_CITIES = {
    "PLANKS": {
        "city": "Fort Sterling",
        "name_zh": "白城 (Fort Sterling)",
        "short_name": "白城",
        "color": "sky",
        "badge_class": "bg-sky-950 text-sky-300 border-sky-700/60"
    },
    "LEATHER": {
        "city": "Martlock",
        "name_zh": "藍城 (Martlock)",
        "short_name": "藍城",
        "color": "blue",
        "badge_class": "bg-blue-950 text-blue-300 border-blue-700/60"
    },
    "CLOTH": {
        "city": "Lymhurst",
        "name_zh": "綠城 (Lymhurst)",
        "short_name": "綠城",
        "color": "emerald",
        "badge_class": "bg-emerald-950 text-emerald-300 border-emerald-700/60"
    },
    "METALBAR": {
        "city": "Thetford",
        "name_zh": "紫城 (Thetford)",
        "short_name": "紫城",
        "color": "purple",
        "badge_class": "bg-purple-950 text-purple-300 border-purple-700/60"
    },
    "STONEBLOCK": {
        "city": "Bridgewatch",
        "name_zh": "黃城 (Bridgewatch)",
        "short_name": "黃城",
        "color": "amber",
        "badge_class": "bg-amber-950 text-amber-300 border-amber-700/60"
    }
}

# 皇家大陸各城市裝備製造加成 (+15% 基礎製造加成，無專注 24.8% RRR，專注 47.9% RRR)
CITY_CRAFTING_BONUSES = {
    "Fort Sterling": {
        "city_id": "Fort Sterling",
        "name_zh": "白城 (Fort Sterling)",
        "short_name": "白城",
        "color": "sky",
        "badge_class": "bg-sky-950 text-sky-300 border-sky-700/60",
        "icon": "🏰",
        "subcats": ["鎚", "長矛", "神聖法杖", "板甲頭盔", "布長袍"],
        "rrr_no_focus": 0.248,
        "rrr_focus": 0.479
    },
    "Thetford": {
        "city_id": "Thetford",
        "name_zh": "紫城 (Thetford)",
        "short_name": "紫城",
        "color": "purple",
        "badge_class": "bg-purple-950 text-purple-300 border-purple-700/60",
        "icon": "🔮",
        "subcats": ["錘矛", "自然法杖", "火焰法杖", "皮外套", "布甲風帽"],
        "rrr_no_focus": 0.248,
        "rrr_focus": 0.479
    },
    "Lymhurst": {
        "city_id": "Lymhurst",
        "name_zh": "綠城 (Lymhurst)",
        "short_name": "綠城",
        "color": "emerald",
        "badge_class": "bg-emerald-950 text-emerald-300 border-emerald-700/60",
        "icon": "🌲",
        "subcats": ["劍", "弓箭", "祕術法杖", "皮甲兜帽", "皮鞋"],
        "rrr_no_focus": 0.248,
        "rrr_focus": 0.479
    },
    "Bridgewatch": {
        "city_id": "Bridgewatch",
        "name_zh": "黃城 (Bridgewatch)",
        "short_name": "黃城",
        "color": "amber",
        "badge_class": "bg-amber-950 text-amber-300 border-amber-700/60",
        "icon": "🏜️",
        "subcats": ["十字弓", "匕首", "詛咒法杖", "板甲護甲", "布便鞋"],
        "rrr_no_focus": 0.248,
        "rrr_focus": 0.479
    },
    "Martlock": {
        "city_id": "Martlock",
        "name_zh": "藍城 (Martlock)",
        "short_name": "藍城",
        "color": "blue",
        "badge_class": "bg-blue-950 text-blue-300 border-blue-700/60",
        "icon": "🛡️",
        "subcats": ["斧", "鐵頭棍", "寒冰法杖", "板甲長靴", "副手"],
        "rrr_no_focus": 0.248,
        "rrr_focus": 0.479
    },
    "Caerleon": {
        "city_id": "Caerleon",
        "name_zh": "紅城 (Caerleon)",
        "short_name": "紅城",
        "color": "red",
        "badge_class": "bg-red-950 text-red-300 border-red-700/60",
        "icon": "👑",
        "subcats": ["戰拳", "背包", "披風"],
        "rrr_no_focus": 0.152,
        "rrr_focus": 0.479
    }
}

def get_item_royal_city_info(subcat: str, item_id: str = "") -> dict:
    """
    根據子類別 (subcat) 或裝備代碼取得阿爾比恩皇家大陸對應製造加成城市資訊
    """
    for city_id, info in CITY_CRAFTING_BONUSES.items():
        if subcat in info["subcats"]:
            return info
    
    # 預設落點
    return CITY_CRAFTING_BONUSES["Caerleon"]



