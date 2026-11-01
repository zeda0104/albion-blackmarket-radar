#!/usr/bin/env python3
"""
CodeGraph & Graphify 拓撲檢查與同步工具
可快速查詢指定模組的上下游依賴關係，避免跨模組改動造成盲目 Tool Calls。
"""
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[4]
GRAPH_JSON = ROOT / "graphify-out" / "graph.json"

def inspect_node(query_name: str):
    if not GRAPH_JSON.exists():
        print(f"[!] 找不到圖譜檔案：{GRAPH_JSON}")
        return

    with open(GRAPH_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    links = data.get("links", [])

    matched_nodes = [n for n in nodes if query_name.lower() in n.get("id", "").lower() or query_name.lower() in n.get("name", "").lower()]
    if not matched_nodes:
        print(f"[-] 未在拓撲圖中找到符合「{query_name}」的節點。")
        return

    for node in matched_nodes:
        node_id = node.get("id")
        print(f"\n==================================================")
        print(f"[NODE] 節點: {node_id} (分類: {node.get('group', 'N/A')})")
        print(f"       摘要: {node.get('description', '無')}")
        
        # 尋找直接調用 (Out-degree)
        callees = [l.get("target") for l in links if l.get("source") == node_id]
        # 尋找被調用 (In-degree)
        callers = [l.get("source") for l in links if l.get("target") == node_id]

        print(f"       -> 呼叫依賴 (Callees): {', '.join(callees) if callees else '無'}")
        print(f"       <- 被誰依賴 (Callers): {', '.join(callers) if callers else '無'}")

def main():
    if len(sys.argv) < 2:
        print("用法: python sync_graph.py <模組或檔案關鍵字>")
        print("範例: python sync_graph.py scanner.py")
        return
    inspect_node(sys.argv[1])

if __name__ == "__main__":
    main()
