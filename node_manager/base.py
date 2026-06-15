# -*- encoding=utf8 -*-
"""
node_manager.base - 底层基础工具

功能：
- capture_screen: 截图并保存到截图目录
- dump_current_nodes: 截图 + 导出当前 Poco 节点树为 JSON
- get_poco_hierarchy: 通过 Poco agent 获取完整节点树
- flatten_hierarchy: 将层级节点树展平为列表（带 path）

供 CF 和 MT 两项目复用。
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

from airtest.core.api import capture_screen, sleep


# ============================================================
# 截图
# ============================================================

def capture_screen(reason, screenshot_dir=None):
    """截图并保存到截图目录。

    Args:
        reason: 截图原因，用于文件名。
        screenshot_dir: 截图保存目录，None 则使用当前脚本所在目录的 screenshots/。

    Returns:
        截图文件绝对路径。
    """
    if screenshot_dir is None:
        screenshot_dir = Path(__file__).resolve().parent.parent / "screenshots"
    screenshot_dir = Path(screenshot_dir)
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    safe_reason = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fa5-]+", "_", reason).strip("_") or "unknown"
    file_path = screenshot_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_reason}.png"

    try:
        capture_screen(str(file_path))
        print(f"📸 已保存截图：{file_path}")
    except Exception as e:
        print(f"❌ 截图失败：{e}")
        return None

    return str(file_path)


# ============================================================
# Poco 节点树导出
# ============================================================

def get_poco_hierarchy(poco_instance=None):
    """通过 Poco agent 的 hierarchy dump 获取当前完整节点树。

    Args:
        poco_instance: Poco 实例，None 则尝试从全局导入。

    Returns:
        层级结构的 dict，获取失败返回 None。
    """
    if poco_instance is None:
        try:
            from poco.drivers.std import StdPoco
            from airtest.core.api import connect_platform
            connect_platform()
            poco_instance = StdPoco()
        except Exception:
            pass

    if poco_instance is None:
        print("❌ 无法获取 Poco 实例")
        return None

    try:
        hierarchy = poco_instance.agent.hierarchy.dump()
        return hierarchy
    except Exception as e:
        print(f"❌ Poco 节点树导出失败：{e}")
        return None


def flatten_hierarchy(hierarchy, path="root"):
    """将层级节点树展平为扁平列表，每个元素包含 path、name、type、text 等。

    Args:
        hierarchy: Poco hierarchy dump 结果（dict）。
        path: 当前路径前缀。

    Returns:
        list[dict]: 展平后的节点列表。
    """
    flat_nodes = []

    def walk(node, current_path):
        if not isinstance(node, dict):
            return
        name = node.get("name") or node.get("type") or ""
        payload = node.get("payload") if isinstance(node.get("payload"), dict) else {}
        text_value = payload.get("text") or node.get("text") or ""
        final_path = f"{current_path}/{name}" if name else current_path
        flat_nodes.append({
            "path": final_path,
            "name": name,
            "type": node.get("type", ""),
            "text": text_value,
            "visible": payload.get("visible", node.get("visible", "")),
            "clickable": payload.get("clickable", node.get("clickable", "")),
            "pos": payload.get("pos", node.get("pos", "")),
        })
        for child in node.get("children", []) or []:
            walk(child, final_path)

    walk(hierarchy, path)
    return flat_nodes


# ============================================================
# 完整 dump：截图 + JSON
# ============================================================

def dump_current_nodes(
    reason,
    poco_instance=None,
    keywords=None,
    screenshot_dir=None,
    dump_dir=None,
):
    """截图 + 导出当前 Poco 节点树为 JSON，便于节点名失配时反查相似节点。

    Args:
        reason: 描述本次 dump 的原因。
        poco_instance: Poco 实例。
        keywords: 关键词列表，用于过滤相似节点。
        screenshot_dir: 截图保存目录。
        dump_dir: JSON dump 保存目录。

    Returns:
        JSON 文件绝对路径，失败返回 None。
    """
    if dump_dir is None:
        dump_dir = Path(__file__).resolve().parent.parent / "node_dumps"
    dump_dir = Path(dump_dir)
    dump_dir.mkdir(parents=True, exist_ok=True)

    if screenshot_dir is None:
        screenshot_dir = Path(__file__).resolve().parent.parent / "screenshots"

    # 生成安全文件名
    safe_reason = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fa5-]+", "_", reason).strip("_") or "unknown"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = dump_dir / f"{timestamp}_{safe_reason}.json"

    # 截图
    screenshot_path = capture_screen(reason, screenshot_dir=screenshot_dir)

    # 获取 Poco 节点树
    hierarchy = get_poco_hierarchy(poco_instance)
    if hierarchy is None:
        print("❌ Poco 节点树获取失败，仅保存截图")
        return str(file_path)

    flat_nodes = flatten_hierarchy(hierarchy)

    # 关键词过滤：提取相似节点
    tokens = [
        token.lower()
        for token in (keywords or re.findall(r"[0-9A-Za-z_\u4e00-\u9fa5]+", reason))
        if len(token) > 1
    ]

    def is_similar(item):
        haystack = " ".join(str(item.get(key, "")) for key in ("path", "name", "text")).lower()
        return any(token in haystack for token in tokens)

    similar_nodes = [item for item in flat_nodes if is_similar(item)]

    data = {
        "reason": reason,
        "timestamp": timestamp,
        "screenshot": screenshot_path,
        "keywords": tokens,
        "node_count": len(flat_nodes),
        "similar_count": len(similar_nodes),
        "similar_nodes": similar_nodes,
        "flat_nodes": flat_nodes,
        "hierarchy": hierarchy,
    }

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    print(f"✅ 已导出当前节点 JSON：{file_path}")
    print(f"   节点总数：{len(flat_nodes)}，相似节点：{len(similar_nodes)}")
    return str(file_path)
