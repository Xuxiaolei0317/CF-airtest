# -*- encoding=utf8 -*-
"""
node_manager.catalog - UI 节点库检索与更新

统一节点库文件格式（JSON）：
{
    "generated_at": "2026-06-11 15:00:00",
    "source": "MT_node_maintenance.py",
    "policy": "only nodes clicked and dumped by verification actions are maintained",
    "pages": {
        "main": {
            "label": "主界面",
            "enter_passed": true,
            "initial_dump": "/path/to/dump.json",
            "dump": "/path/to/dump.json",
            "screenshot": "/path/to/screenshot.png",
            "node_count": 988,
            "page_states": [
                {
                    "page": "main",
                    "dump": "...",
                    "state": "main_or_footer_visible",
                    "signals": ["footer/root"],
                    "blocking": false
                }
            ],
            "state_actions": [
                {
                    "field": "mt_ft_store",
                    "purpose": "主界面 footer 商店入口",
                    "risk": "safe",
                    "selector": "node_store/btn",
                    "clicked": true,
                    "verified": true,
                    "after_dump": "/path/after.json",
                    "after_screenshot": "/path/after.png",
                    "after_node_count": 167
                }
            ],
            "verified_count": 5,
            "recovery_verified_count": 0,
            "verified_nodes": [
                {
                    "field": "mt_ft_store",
                    "purpose": "主界面 footer 商店入口，点击后应进入商店页面",
                    "risk": "safe",
                    "selector": "node_store/btn",
                    "exists_before_click": true,
                    "clicked": true,
                    "verified": true,
                    "after_dump": "/path/after.json",
                    "after_screenshot": "/path/after.png",
                    "after_node_count": 167
                }
            ],
            "skipped_nodes": [
                {
                    "field": "mt_ft_build",
                    "purpose": "主界面 footer 建造入口",
                    "risk": "stateful",
                    "selector": "node_map/btn",
                    "exists_before_click": true,
                    "clicked": false,
                    "verified": false,
                    "skip_reason": "stateful_action_requires_--include-stateful-actions"
                }
            ]
        }
    }
}

功能：
- load_catalog   : 从 JSON 文件加载节点库
- save_catalog   : 将节点库写入 JSON 文件
- search_nodes   : 按页面、关键词、field 名称检索节点
- add_verified_node : 将新验证的节点追加到指定页面
- get_page_info  : 获取指定页面的完整信息
- list_pages     : 列出所有页面名称
- update_page_state : 更新页面状态
"""

import json
import re
from datetime import datetime
from pathlib import Path


# ============================================================
# 文件 I/O
# ============================================================

def load_catalog(catalog_path):
    """从 JSON 文件加载节点库。

    Args:
        catalog_path: catalog JSON 文件路径。

    Returns:
        dict: 节点库数据。如果文件不存在，返回空结构。
    """
    catalog_path = Path(catalog_path)
    if not catalog_path.exists():
        return {
            "generated_at": "",
            "source": "",
            "policy": "",
            "pages": {},
        }
    try:
        with catalog_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"❌ 读取 catalog 失败：{e}")
        return {
            "generated_at": "",
            "source": "",
            "policy": "",
            "pages": {},
        }


def save_catalog(catalog_data, catalog_path):
    """将节点库数据写入 JSON 文件。

    Args:
        catalog_data: 节点库 dict。
        catalog_path: catalog JSON 文件路径。
    """
    catalog_path = Path(catalog_path)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_data["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with catalog_path.open("w", encoding="utf-8") as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2, default=str)

    print(f"✅ 已保存 catalog：{catalog_path}")


# ============================================================
# 检索
# ============================================================

def list_pages(catalog):
    """列出所有已记录的页面名称。

    Args:
        catalog: 节点库 dict（load_catalog 返回）。

    Returns:
        tuple: 页面名称元组。
    """
    return tuple(catalog.get("pages", {}).keys())


def get_page_info(catalog, page_name):
    """获取指定页面的完整信息。

    Args:
        catalog: 节点库 dict。
        page_name: 页面名称。

    Returns:
        dict: 页面信息，不存在返回 None。
    """
    return catalog.get("pages", {}).get(page_name)


def search_nodes(catalog, page_name=None, keyword=None, field_name=None, only_verified=False):
    """在节点库中检索匹配的节点。

    可以按页面、关键词（匹配 purpose/field/selector）、field 名称精确匹配过滤。

    Args:
        catalog: 节点库 dict。
        page_name: 指定页面名，None 则搜索所有页面。
        keyword: 关键词，匹配 purpose、field、selector 字段。
        field_name: 精确匹配 field 名称。
        only_verified: 只返回已验证的节点。

    Returns:
        list[dict]: 匹配的节点列表，每个元素包含 {'page', 'node', 'matched_field'}。
    """
    results = []
    pages = catalog.get("pages", {})

    if page_name and page_name not in pages:
        print(f"⚠️  页面 '{page_name}' 不存在。可用页面：{list(pages.keys())}")
        return results

    target_pages = {page_name: pages[page_name]} if page_name else pages

    for page, page_data in target_pages.items():
        # 搜索 verified_nodes
        for node in page_data.get("verified_nodes", []):
            if field_name and node.get("field") != field_name:
                continue
            if keyword and not _match_keyword(node, keyword):
                continue
            results.append({"page": page, "node": node, "matched_field": "verified_nodes"})

        # 搜索 skipped_nodes
        if not only_verified:
            for node in page_data.get("skipped_nodes", []):
                if field_name and node.get("field") != field_name:
                    continue
                if keyword and not _match_keyword(node, keyword):
                    continue
                results.append({"page": page, "node": node, "matched_field": "skipped_nodes"})

    return results


def _match_keyword(node, keyword):
    """检查 keyword 是否匹配节点的 purpose、field 或 selector。"""
    keyword_lower = keyword.lower()
    for field in ("purpose", "field", "selector"):
        value = str(node.get(field, "")).lower()
        if keyword_lower in value:
            return True
    return False


# ============================================================
# 更新
# ============================================================

def add_verified_node(catalog, page_name, field, purpose, selector,
                      risk="safe", clicked=True, verified=True,
                      after_dump=None, after_screenshot=None, after_node_count=None,
                      exists_before_click=None):
    """将一个新验证的节点追加到 catalog 的 verified_nodes。

    Args:
        catalog: 节点库 dict（会被修改）。
        page_name: 页面名称。
        field: 字段名（如 mt_ft_store）。
        purpose: 节点用途描述。
        selector: Poco 选择器路径。
        risk: 风险等级（safe / stateful / recovery_stateful）。
        clicked: 是否成功点击。
        verified: 是否验证通过。
        after_dump: 点击后 dump 文件路径。
        after_screenshot: 点击后截图路径。
        after_node_count: 点击后节点数。
        exists_before_click: 点击前是否存在。

    Returns:
        dict: 写入 verified_nodes 的节点记录。
    """
    if page_name not in catalog.get("pages", {}):
        print(f"⚠️  页面 '{page_name}' 不存在，已自动创建")
        catalog.setdefault("pages", {})[page_name] = {
            "label": page_name,
            "enter_passed": False,
            "initial_dump": "",
            "dump": "",
            "screenshot": "",
            "node_count": 0,
            "page_states": [],
            "state_actions": [],
            "verified_count": 0,
            "recovery_verified_count": 0,
            "verified_nodes": [],
            "skipped_nodes": [],
        }

    page = catalog["pages"][page_name]

    node_record = {
        "field": field,
        "purpose": purpose,
        "risk": risk,
        "selector": selector,
    }
    if exists_before_click is not None:
        node_record["exists_before_click"] = exists_before_click
    node_record["clicked"] = clicked
    node_record["verified"] = verified

    if after_dump is not None:
        node_record["after_dump"] = after_dump
    if after_screenshot is not None:
        node_record["after_screenshot"] = after_screenshot
    if after_node_count is not None:
        node_record["after_node_count"] = after_node_count

    # 避免重复 field
    for existing in page.get("verified_nodes", []):
        if existing.get("field") == field:
            print(f"⚠️  field '{field}' 已存在于 {page_name}，已更新")
            page["verified_nodes"] = [
                n if n.get("field") != field else node_record
                for n in page["verified_nodes"]
            ]
            break
    else:
        page.setdefault("verified_nodes", []).append(node_record)
        page["verified_count"] = page.get("verified_count", 0) + 1

    return node_record


def add_skipped_node(catalog, page_name, field, purpose, selector,
                     risk="safe", clicked=False, verified=False,
                     exists_before_click=None, skip_reason=""):
    """将一个未验证/跳过的节点记录到 catalog 的 skipped_nodes。

    Args:
        catalog: 节点库 dict。
        page_name: 页面名称。
        field: 字段名。
        purpose: 节点用途描述。
        selector: Poco 选择器路径。
        risk: 风险等级。
        clicked: 是否尝试点击。
        verified: 是否验证通过。
        exists_before_click: 点击前是否存在。
        skip_reason: 跳过原因。

    Returns:
        dict: 写入 skipped_nodes 的节点记录。
    """
    if page_name not in catalog.get("pages", {}):
        catalog.setdefault("pages", {})[page_name] = {
            "label": page_name,
            "enter_passed": False,
            "initial_dump": "",
            "dump": "",
            "screenshot": "",
            "node_count": 0,
            "page_states": [],
            "state_actions": [],
            "verified_count": 0,
            "recovery_verified_count": 0,
            "verified_nodes": [],
            "skipped_nodes": [],
        }

    page = catalog["pages"][page_name]

    node_record = {
        "field": field,
        "purpose": purpose,
        "risk": risk,
        "selector": selector,
        "exists_before_click": exists_before_click if exists_before_click is not None else None,
        "clicked": clicked,
        "verified": verified,
        "skip_reason": skip_reason,
    }

    page.setdefault("skipped_nodes", []).append(node_record)
    return node_record


def update_page_state(catalog, page_name, state, signals=None, blocking=False,
                      dump_path=None, screenshot_path=None, node_count=None):
    """更新页面的当前状态记录。

    Args:
        catalog: 节点库 dict。
        page_name: 页面名称。
        state: 状态描述（如 build_damage_repair_required）。
        signals: 状态信号列表。
        blocking: 是否阻塞操作。
        dump_path: 当前 dump 文件路径。
        screenshot_path: 当前截图路径。
        node_count: 当前节点数。
    """
    if page_name not in catalog.get("pages", {}):
        print(f"⚠️  页面 '{page_name}' 不存在")
        return

    page = catalog["pages"][page_name]
    page["dump"] = dump_path or page.get("dump", "")
    page["screenshot"] = screenshot_path or page.get("screenshot", "")
    if node_count is not None:
        page["node_count"] = node_count

    state_entry = {
        "page": page_name,
        "state": state,
        "signals": signals or [],
        "blocking": blocking,
    }
    if dump_path:
        state_entry["dump"] = dump_path

    page.setdefault("page_states", []).append(state_entry)


def node_display_name(node):
    """获取节点的显示名称（name 或 type）。"""
    try:
        if hasattr(node, 'get_name'):
            return node.get_name()
        if hasattr(node, 'name'):
            return node.name
    except Exception:
        pass
    return "unknown"


def node_exists(node, default_timeout=2):
    """安全判断节点是否存在。"""
    try:
        return node.exists(timeout=default_timeout)
    except Exception:
        return False


def if_click(node, description=""):
    """判断节点是否存在，存在则点击并返回 True；不存在返回 False。

    Args:
        node: Poco 节点对象。
        description: 描述信息，用于日志。

    Returns:
        bool: 是否成功点击。
    """
    try:
        if node.exists():
            node.click()
            return True
        return False
    except Exception as e:
        print(f"❌ if_click 失败 [{description}]：{e}")
        return False


def safe_close_popups(poco_instance=None, max_tries=3, close_names=None):
    """关闭所有常见弹窗/遮罩。

    Args:
        poco_instance: Poco 实例。
        max_tries: 最大重试次数。
        close_names: 关闭按钮名称列表。

    Returns:
        bool: 是否关闭了至少一个弹窗。
    """
    close_names = close_names or ["btn_close", "close_btn", "btnClose", "mask_close"]
    closed = False

    if poco_instance is None:
        try:
            from poco.drivers.std import StdPoco
            poco_instance = StdPoco()
        except Exception:
            return False

    for _ in range(max_tries):
        clicked = False
        for name in close_names:
            try:
                node = poco_instance(name)
                if node.exists():
                    node.click()
                    sleep(0.2)
                    clicked = True
                    closed = True
            except Exception:
                pass
        if not clicked:
            break
    return closed
