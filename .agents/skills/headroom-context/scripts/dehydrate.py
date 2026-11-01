#!/usr/bin/env python3
"""
Headroom Context Dehydrator (Python CLI)
脫水壓縮工具：壓縮巨型 JSON、CLI 輸出與 Log，剔除 90% 冗餘 Token，保留高密度關鍵資訊。
"""
import sys
import json
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def dehydrate_json(data, max_list_items=2):
    """將大型 JSON 結構骨架化：保留 Schema、鍵值結構與極少數樣本"""
    if isinstance(data, list):
        count = len(data)
        if count == 0:
            return []
        sample = [dehydrate_json(item, max_list_items) for item in data[:max_list_items]]
        return {
            "__type__": f"Array(total_items={count})",
            "samples": sample
        }
    elif isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if isinstance(v, list) and len(v) > max_list_items:
                result[k] = {
                    "__type__": f"Array(total_items={len(v)})",
                    "sample": [dehydrate_json(x, 1) for x in v[:max_list_items]]
                }
            elif isinstance(v, dict) and len(v) > 10:
                result[k] = {
                    "__type__": f"Dict(total_keys={len(v)})",
                    "sample_keys": list(v.keys())[:5],
                    "content": {k2: dehydrate_json(v[k2], max_list_items) for k2 in list(v.keys())[:3]}
                }
            else:
                result[k] = dehydrate_json(v, max_list_items)
        return result
    return data

def dehydrate_log(text, max_context_lines=3):
    """過濾日誌：只保留 Exception、Traceback、Error、Warning 及鄰近上下文，刪除進度條與重複項"""
    lines = text.splitlines()
    error_indices = set()
    keywords = ["error", "exception", "traceback", "failed", "fatal", "critical", "warning"]

    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw in line_lower for kw in keywords):
            for i in range(max(0, idx - max_context_lines), min(len(lines), idx + max_context_lines + 1)):
                error_indices.add(i)

    if not error_indices:
        # 無明顯報錯時，保留首末 15 行
        if len(lines) <= 30:
            return text
        return "\n".join(lines[:15]) + f"\n... [已略過 {len(lines) - 30} 行中段日誌] ...\n" + "\n".join(lines[-15:])

    filtered_lines = []
    last_idx = -2
    for idx in sorted(error_indices):
        if idx > last_idx + 1 and last_idx != -2:
            filtered_lines.append(f"... [略過 {idx - last_idx - 1} 行非關鍵日誌] ...")
        filtered_lines.append(f"L{idx+1}: {lines[idx]}")
        last_idx = idx

    return "\n".join(filtered_lines)

def main():
    if len(sys.argv) > 1 and sys.argv[1] not in ("-", "--help"):
        with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    else:
        content = sys.stdin.read()

    trimmed = content.strip()
    if (trimmed.startswith("{") and trimmed.endswith("}")) or (trimmed.startswith("[") and trimmed.endswith("]")):
        try:
            parsed = json.loads(trimmed)
            dehydrated = dehydrate_json(parsed)
            print(json.dumps(dehydrated, ensure_ascii=False, indent=2))
            return
        except Exception:
            pass

    # 當作 Log / 文字處理
    print(dehydrate_log(content))

if __name__ == "__main__":
    main()
