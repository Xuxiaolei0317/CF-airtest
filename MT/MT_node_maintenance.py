# -*- encoding=utf8 -*-
"""MT Poco 节点维护脚本。

用途：
1. 逐页进入 MT 多模块页面；
2. 复用 MT_quest_test.dump_current_nodes 导出真实 Poco 节点；
3. 点击核对关键候选节点的真实用途；
4. 只将点击验证过的节点维护到 MT_nodes.py 的自动维护区。
"""

import argparse
import json
import pprint
import re
import sys
from datetime import datetime
from pathlib import Path

from airtest.core.api import sleep

# 允许从 CF 子目录直接运行脚本时导入上一级的公共初始化模块。
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST

from MT_nodes import common_nodes as mt
from MT_quest_test import dump_current_nodes, if_click, node_display_name, node_exists, safe_close_popups


ST.SAVE_IMAGE = True

BASE_DIR = Path(__file__).resolve().parent
NODES_FILE = BASE_DIR / "MT_nodes.py"
SUMMARY_DIR = BASE_DIR / "node_dumps" / "maintenance"
CATALOG_START = "    # AUTO DISCOVERED NODE CATALOG START"
CATALOG_END = "    # AUTO DISCOVERED NODE CATALOG END"


def enter_main():
    """停留在当前主界面并先尝试关闭遮挡弹窗。"""
    safe_close_popups()
    return True


def enter_build():
    return if_click(mt.mt_main().mt_ft_build, "main.mt_ft_build")


def enter_spin():
    return if_click(mt.mt_main().mt_ft_spin, "main.mt_ft_spin")


def enter_guild():
    return if_click(mt.mt_main().mt_ft_guild_friend, "main.mt_ft_guild_friend")


def enter_stamp():
    return if_click(mt.mt_main().mt_ft_stamp, "main.mt_ft_stamp")


def enter_store():
    return if_click(mt.mt_main().mt_ft_store, "main.mt_ft_store")


PAGE_SPECS = {
    "main": {
        "label": "主界面",
        "enter": enter_main,
        "keywords": ["MainGameScene", "header", "footer", "node_", "btn_"],
    },
    "build": {
        "label": "建造",
        "enter": enter_build,
        "keywords": ["build", "map", "main_coin", "repair", "upgrade", "gift"],
    },
    "spin": {
        "label": "Spin",
        "enter": enter_spin,
        "keywords": ["slot", "spin", "attack", "steal", "bet", "result"],
    },
    "guild": {
        "label": "公会/好友",
        "enter": enter_guild,
        "keywords": ["guild", "club", "friends", "chat", "btn_", "input"],
    },
    "stamp": {
        "label": "邮票",
        "enter": enter_stamp,
        "keywords": ["stamp", "card", "album", "scroll", "btn_"],
    },
    "store": {
        "label": "商店",
        "enter": enter_store,
        "keywords": ["store", "shop", "product", "pay", "btn_"],
    },
}
DEFAULT_PAGES = ("main", "build", "spin", "guild", "stamp", "store")


def make_action(field, purpose, node_factory, risk="safe"):
    """定义一个需要点击核对的候选节点。risk=stateful 的节点默认只记录不点击。"""
    return {
        "field": field,
        "purpose": purpose,
        "node_factory": node_factory,
        "risk": risk,
    }


VERIFY_ACTIONS = {
    "main": (
        make_action(
            "mt_ft_store",
            "主界面 footer 商店入口，点击后应进入商店页面",
            lambda: mt.mt_main().mt_ft_store,
        ),
        make_action(
            "mt_ft_build",
            "主界面 footer 建造入口，点击后应进入建造地图页面",
            lambda: mt.mt_main().mt_ft_build,
        ),
        make_action(
            "mt_ft_spin",
            "主界面 footer Spin 入口，点击后应回到 Spin 主区域",
            lambda: mt.mt_main().mt_ft_spin,
        ),
        make_action(
            "mt_ft_guild_friend",
            "主界面 footer 公会/好友入口，点击后应进入 friends_main/club 相关页面",
            lambda: mt.mt_main().mt_ft_guild_friend,
        ),
        make_action(
            "mt_ft_stamp",
            "主界面 footer 邮票入口，点击后应进入 stamp/card 相关页面",
            lambda: mt.mt_main().mt_ft_stamp,
        ),
    ),
    "build": (
        make_action(
            "mt_build_map_center_btn",
            "建造地图中心提示入口，点击后应定位到可建造/可收集目标",
            lambda: mt.mt_build().mt_build_map_center_btn,
        ),
        make_action(
            "mt_main_coin_collect_btn",
            "建造金币收集按钮，点击会领取地图金币",
            lambda: mt.mt_build().mt_main_coin_collect_btn,
            risk="stateful",
        ),
        make_action(
            "mt_build_upgrade_btn",
            "建造升级按钮，点击可能消耗金币升级建筑",
            lambda: mt.mt_build().mt_build_upgrade_btn,
            risk="stateful",
        ),
        make_action(
            "mt_build_build_btn",
            "建造按钮，点击可能消耗金币建造建筑",
            lambda: mt.mt_build().mt_build_build_btn,
            risk="stateful",
        ),
        make_action(
            "mt_build_repair_btn",
            "建造维修按钮，点击可能消耗/触发维修",
            lambda: mt.mt_build().mt_build_repair_btn,
            risk="stateful",
        ),
    ),
    "spin": (
        make_action(
            "mt_spin_bet_add_btn",
            "Spin bet 增加按钮，点击后 bet 数值应变大",
            lambda: mt.mt_slot().mt_spin_bet_add_btn,
            risk="stateful",
        ),
        make_action(
            "mt_spin_bet_sub_btn",
            "Spin bet 减少按钮，点击后 bet 数值应变小",
            lambda: mt.mt_slot().mt_spin_bet_sub_btn,
            risk="stateful",
        ),
        make_action(
            "mt_spin_btn",
            "Spin 按钮，点击会消耗 spins 并触发结果",
            lambda: mt.mt_slot().mt_spin_btn,
            risk="stateful",
        ),
    ),
    "guild": (
        make_action(
            "guild_chat_tab",
            "公会 My Club/聊天页 tab，点击后应展示聊天区域",
            lambda: mt.mt_guild().guild_chat_tab,
        ),
        make_action(
            "guild_shop_tab_btn",
            "公会 Shop tab，点击后应展示公会商店",
            lambda: mt.mt_guild().guild_shop_tab_btn,
        ),
        make_action(
            "guild_friends_tab_btn",
            "公会 Friends tab，点击后应展示好友列表",
            lambda: mt.mt_guild().guild_friends_tab_btn,
        ),
        make_action(
            "guild_chat_btn",
            "公会聊天输入入口，点击后应出现输入框/发送区域",
            lambda: mt.mt_guild().guild_chat_btn,
        ),
        make_action(
            "guild_request_spins_btn",
            "公会请求 spins 按钮，点击可能发起请求",
            lambda: mt.mt_guild().guild_request_spins_btn,
            risk="stateful",
        ),
        make_action(
            "guild_request_card_btn",
            "公会请求邮票按钮，点击可能发起请求",
            lambda: mt.mt_guild().guild_request_card_btn,
            risk="stateful",
        ),
    ),
    "stamp": (
        make_action(
            "stamp_list",
            "邮票列表容器，点击后应保持在邮票页或选中列表内容",
            lambda: mt.mt_stamp().stamp_list,
        ),
        make_action(
            "stamp_list_alt",
            "邮票可滚动列表兼容容器，点击后应保持在邮票页或选中列表内容",
            lambda: mt.mt_stamp().stamp_list_alt,
        ),
    ),
    "store": (
        make_action(
            "store_page",
            "商店主页面容器，点击后应保持在商店页面",
            lambda: mt.mt_store().store_page,
        ),
        make_action(
            "store_page_alt",
            "商店页面兼容容器，点击后应保持在 shop/store 页面",
            lambda: mt.mt_store().store_page_alt,
        ),
    ),
}


def load_dump_data(dump_path):
    with Path(dump_path).open("r", encoding="utf-8") as file:
        return json.load(file)


def dump_node_sets(dump_path):
    data = load_dump_data(dump_path)
    names = set()
    texts = set()
    paths = set()
    for item in data.get("flat_nodes", []):
        if item.get("name"):
            names.add(item["name"])
        if item.get("text"):
            texts.add(str(item["text"]))
        if item.get("path"):
            paths.add(item["path"])
    return names, texts, paths


def analyze_page_state(page_name, dump_path):
    """根据 dump 内容识别当前页面状态，后续点击必须服从状态判断。"""
    names, texts, paths = dump_node_sets(dump_path)
    state = {
        "page": page_name,
        "dump": str(dump_path),
        "state": "unknown",
        "signals": [],
        "blocking": False,
    }

    if page_name == "build":
        has_damage_dialog = any("damage_dialog" in path for path in paths)
        has_repair = "repair_node" in names or "repair_btn" in names
        has_build_content = any(name in names for name in ("main_coin_cost", "main_coin_collect"))
        has_center_tip = "main_tip" in names

        if has_damage_dialog or has_repair:
            state.update({
                "state": "build_damage_repair_required",
                "blocking": True,
                "signals": ["damage_dialog", "repair_node", "repair_btn"],
            })
        elif has_build_content:
            state.update({
                "state": "build_content_visible",
                "signals": ["main_coin_cost", "main_coin_collect"],
            })
        elif has_center_tip:
            state.update({
                "state": "build_center_tip_visible",
                "signals": ["main_tip"],
            })
        return state

    if page_name == "guild" and any(name in names for name in ("friends_main", "club", "chat_layer")):
        state.update({"state": "guild_visible", "signals": ["friends_main/club/chat_layer"]})
    elif page_name == "stamp" and any("stamp" in name or "card" in name for name in names):
        state.update({"state": "stamp_visible", "signals": ["stamp/card"]})
    elif page_name == "store" and any(name in names for name in ("store", "shop")):
        state.update({"state": "store_visible", "signals": ["store/shop"]})
    elif page_name == "spin" and any(name in names for name in ("node_spin", "btn_spin", "node_slot")):
        state.update({"state": "spin_visible", "signals": ["node_spin/btn_spin/node_slot"]})
    elif page_name == "main":
        state.update({"state": "main_or_footer_visible", "signals": ["footer/root"]})

    return state


def click_and_dump(node, page_name, field, reason, keywords):
    clicked = if_click(node, f"{page_name}.{field}")
    sleep(0.8)
    safe_close_popups()
    dump_path = dump_current_nodes(
        f"{reason}_{'clicked' if clicked else 'click_failed'}",
        keywords=keywords,
    )
    return clicked, dump_path


def recover_build_page_if_needed(dump_path):
    """建造页被攻击遮挡时，先修复再重新采集建造内容。"""
    states = [analyze_page_state("build", dump_path)]
    recovery_actions = []
    current_dump = dump_path

    if states[-1]["state"] != "build_damage_repair_required":
        print(f"📌 建造页状态：{states[-1]['state']} | signals={states[-1]['signals']}")
        return current_dump, states, recovery_actions

    print("📌 建造页状态：被攻击维修态，先点击 repair_btn 恢复后再维护建造节点")
    try:
        repair_node = mt.mt_build().mt_build_repair_btn
        clicked, after_dump = click_and_dump(
            repair_node,
            "build",
            "mt_build_repair_btn",
            "maintenance_build_after_repair",
            ["build", "repair", "main_coin", "upgrade", "btn_build", "main_tip"],
        )
    except Exception as e:
        recovery_actions.append({
            "field": "mt_build_repair_btn",
            "purpose": "建造被攻击状态修复按钮",
            "clicked": False,
            "verified": False,
            "error": str(e),
        })
        return current_dump, states, recovery_actions

    recovery_actions.append({
        "field": "mt_build_repair_btn",
        "purpose": "建造被攻击状态修复按钮，点击后应关闭 damage_dialog 并露出建造内容",
        "risk": "recovery_stateful",
        "selector": node_display_name(repair_node),
        "clicked": bool(clicked),
        "verified": bool(clicked and after_dump),
        "after_dump": str(after_dump) if after_dump else "",
    })

    if after_dump:
        current_dump = after_dump
        states.append(analyze_page_state("build", current_dump))
        print(f"📌 修复后建造页状态：{states[-1]['state']} | signals={states[-1]['signals']}")

    return current_dump, states, recovery_actions


def safe_attr_name(page_name, node_name):
    """把真实节点名转成可读的候选字段名，便于人工提升为正式节点。"""
    raw_name = re.sub(r"\W+", "_", node_name).strip("_").lower()
    if not raw_name:
        return ""
    if raw_name[0].isdigit():
        raw_name = f"node_{raw_name}"
    return f"{page_name}_{raw_name}"


def summarize_dump(dump_path, page_name, max_nodes):
    with Path(dump_path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    nodes = {}
    for item in data.get("flat_nodes", []):
        node_name = item.get("name") or ""
        if not node_name:
            continue

        node = nodes.setdefault(
            node_name,
            {
                "candidate_field": safe_attr_name(page_name, node_name),
                "count": 0,
                "texts": [],
                "paths": [],
            },
        )
        node["count"] += 1

        text_value = item.get("text")
        if text_value and text_value not in node["texts"] and len(node["texts"]) < 5:
            node["texts"].append(text_value)

        path_value = item.get("path")
        if path_value and path_value not in node["paths"] and len(node["paths"]) < 5:
            node["paths"].append(path_value)

    ordered_nodes = dict(
        sorted(nodes.items(), key=lambda pair: (-pair[1]["count"], pair[0]))[:max_nodes]
    )
    return {
        "dump": str(dump_path),
        "screenshot": data.get("screenshot"),
        "node_count": data.get("node_count", 0),
        "raw_candidate_count": len(ordered_nodes),
        "raw_candidates": ordered_nodes,
    }


def verify_action(page_name, action, include_stateful):
    if action["risk"] != "safe" and not include_stateful:
        try:
            node = action["node_factory"]()
            exists_before = node_exists(node)
            selector = node_display_name(node)
        except Exception as e:
            exists_before = False
            selector = ""
            print(f"⚠️ 节点初始化异常，跳过验证：{page_name}.{action['field']} | {e}")
        return {
            "field": action["field"],
            "purpose": action["purpose"],
            "risk": action["risk"],
            "selector": selector,
            "exists_before_click": exists_before,
            "clicked": False,
            "verified": False,
            "skip_reason": "stateful_action_requires_--include-stateful-actions",
        }

    try:
        node = action["node_factory"]()
    except Exception as e:
        print(f"❌ 节点初始化失败：{page_name}.{action['field']} | {e}")
        return {
            "field": action["field"],
            "purpose": action["purpose"],
            "risk": action["risk"],
            "selector": "",
            "exists_before_click": False,
            "clicked": False,
            "verified": False,
            "error": str(e),
        }

    exists_before = node_exists(node)
    selector = node_display_name(node)
    if not exists_before:
        print(f"⚠️ 候选节点不存在，未点击：{page_name}.{action['field']} -> {selector}")
        return {
            "field": action["field"],
            "purpose": action["purpose"],
            "risk": action["risk"],
            "selector": selector,
            "exists_before_click": False,
            "clicked": False,
            "verified": False,
            "skip_reason": "node_not_found",
        }

    print(f"🔎 点击核对节点用途：{page_name}.{action['field']} | {action['purpose']}")
    clicked = if_click(node, f"{page_name}.{action['field']}")
    sleep(0.8)
    safe_close_popups()
    dump_path = dump_current_nodes(
        f"verify_{page_name}_{action['field']}_{'clicked' if clicked else 'click_failed'}",
        keywords=[page_name, action["field"], *re.findall(r"[0-9A-Za-z_\u4e00-\u9fa5]+", action["purpose"])],
    )

    after_summary = summarize_dump(dump_path, page_name, 30) if dump_path else {}
    return {
        "field": action["field"],
        "purpose": action["purpose"],
        "risk": action["risk"],
        "selector": selector,
        "exists_before_click": True,
        "clicked": bool(clicked),
        "verified": bool(clicked and dump_path),
        "after_dump": str(dump_path) if dump_path else "",
        "after_screenshot": after_summary.get("screenshot", ""),
        "after_node_count": after_summary.get("node_count", 0),
    }


def verify_page_actions(page_name, include_stateful, page_states=None):
    spec = PAGE_SPECS[page_name]
    verified_nodes = []
    skipped_nodes = []
    latest_state = (page_states or [{}])[-1].get("state", "unknown")

    if page_name == "build" and latest_state == "build_damage_repair_required":
        for action in VERIFY_ACTIONS.get(page_name, ()):
            skipped_nodes.append({
                "field": action["field"],
                "purpose": action["purpose"],
                "risk": action["risk"],
                "clicked": False,
                "verified": False,
                "skip_reason": "blocked_by_build_damage_repair_state",
            })
        return verified_nodes, skipped_nodes

    for action in VERIFY_ACTIONS.get(page_name, ()):
        if action["risk"] != "safe" and not include_stateful:
            result = verify_action(page_name, action, include_stateful)
            skipped_nodes.append(result)
            continue

        if page_name != "main" and page_name != "build":
            spec["enter"]()
            sleep(0.5)
            safe_close_popups()

        result = verify_action(page_name, action, include_stateful)
        if result.get("verified"):
            verified_nodes.append(result)
        else:
            skipped_nodes.append(result)

    return verified_nodes, skipped_nodes


def collect_page(page_name, max_nodes, include_stateful):
    spec = PAGE_SPECS[page_name]
    print(f"====================== 维护节点：{page_name}({spec['label']}) ======================")
    safe_close_popups()

    entered = spec["enter"]()
    sleep(0.8)
    safe_close_popups()

    reason = f"maintenance_{page_name}_{'entered' if entered else 'enter_failed'}"
    dump_path = dump_current_nodes(reason, keywords=spec["keywords"])
    if not dump_path:
        return {
            "enter_passed": bool(entered),
            "error": "dump_current_nodes_failed",
            "nodes": {},
        }

    page_states = [analyze_page_state(page_name, dump_path)]
    state_actions = []
    effective_dump_path = dump_path
    if page_name == "build":
        effective_dump_path, page_states, state_actions = recover_build_page_if_needed(dump_path)

    page_summary = summarize_dump(effective_dump_path, page_name, max_nodes)
    page_summary["initial_dump"] = str(dump_path)
    page_summary["enter_passed"] = bool(entered)
    page_summary["label"] = spec["label"]
    page_summary["page_states"] = page_states
    page_summary["state_actions"] = state_actions
    verified_nodes, skipped_nodes = verify_page_actions(page_name, include_stateful, page_states)
    page_summary["verified_count"] = len(verified_nodes)
    page_summary["recovery_verified_count"] = len([item for item in state_actions if item.get("verified")])
    page_summary["verified_nodes"] = verified_nodes
    page_summary["skipped_nodes"] = skipped_nodes
    return page_summary


def collect_pages(page_names, max_nodes, include_stateful):
    catalog = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "MT_node_maintenance.py",
        "policy": "only nodes clicked and dumped by verification actions are maintained as verified_nodes",
        "pages": {},
    }
    for page_name in page_names:
        catalog["pages"][page_name] = collect_page(page_name, max_nodes, include_stateful)
    return catalog


def format_catalog_block(catalog):
    catalog_repr = pprint.pformat(catalog, width=120, sort_dicts=False)
    catalog_repr = catalog_repr.replace("\n", "\n        ")
    return "\n".join(
        [
            CATALOG_START,
            "    class mt_discovered():",
            "        '''真实设备点击验证过的页面节点目录，由 MT_node_maintenance.py 自动更新。'''",
            f"        GENERATED_PAGES = {catalog_repr}",
            "",
            "        @classmethod",
            "        def page_names(cls):",
            "            return tuple(cls.GENERATED_PAGES.get(\"pages\", {}).keys())",
            "",
            "        @classmethod",
            "        def verified_nodes(cls, page_name):",
            "            page = cls.GENERATED_PAGES.get(\"pages\", {}).get(page_name, {})",
            "            return tuple(page.get(\"verified_nodes\", ()))",
            CATALOG_END,
        ]
    )


def build_maintenance_catalog(catalog):
    """写入 MT_nodes.py 前去掉原始候选，只保留点击验证后的维护结果。"""
    pages = {}
    for page_name, page_data in catalog.get("pages", {}).items():
        pages[page_name] = {
            "label": page_data.get("label", ""),
            "enter_passed": page_data.get("enter_passed", False),
            "initial_dump": page_data.get("initial_dump", ""),
            "dump": page_data.get("dump", ""),
            "screenshot": page_data.get("screenshot", ""),
            "node_count": page_data.get("node_count", 0),
            "page_states": page_data.get("page_states", []),
            "state_actions": page_data.get("state_actions", []),
            "verified_count": page_data.get("verified_count", 0),
            "recovery_verified_count": page_data.get("recovery_verified_count", 0),
            "verified_nodes": page_data.get("verified_nodes", []),
            "skipped_nodes": page_data.get("skipped_nodes", []),
        }
    return {
        "generated_at": catalog.get("generated_at", ""),
        "source": catalog.get("source", ""),
        "policy": catalog.get("policy", ""),
        "pages": pages,
    }


def merge_existing_maintenance_catalog(catalog):
    """分页面维护时保留 MT_nodes.py 里已有页面结果，只替换本轮执行页面。"""
    try:
        existing = mt.mt_discovered.GENERATED_PAGES
    except AttributeError:
        existing = {}

    merged = {
        "generated_at": catalog.get("generated_at", ""),
        "source": catalog.get("source", ""),
        "policy": catalog.get("policy", ""),
        "pages": dict(existing.get("pages", {})),
    }
    merged["pages"].update(catalog.get("pages", {}))
    return merged


def update_nodes_file(catalog):
    merged_catalog = merge_existing_maintenance_catalog(build_maintenance_catalog(catalog))
    block = format_catalog_block(merged_catalog)
    content = NODES_FILE.read_text(encoding="utf-8")
    if CATALOG_START in content and CATALOG_END in content:
        pattern = re.compile(
            rf"{re.escape(CATALOG_START)}.*?{re.escape(CATALOG_END)}",
            flags=re.S,
        )
        new_content = pattern.sub(block, content)
    else:
        insert_before = "\nclass objects:"
        if insert_before not in content:
            raise RuntimeError("未找到 MT_nodes.py 的 class objects 插入点")
        new_content = content.replace(insert_before, f"\n{block}\n{insert_before}", 1)

    NODES_FILE.write_text(new_content, encoding="utf-8")
    print(f"✅ 已更新真实节点目录：{NODES_FILE}")


def write_summary(catalog):
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = SUMMARY_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_node_catalog.json"
    summary_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 已保存节点维护汇总：{summary_path}")
    return summary_path


def parse_pages(value):
    pages = tuple(item.strip() for item in value.split(",") if item.strip())
    unknown_pages = [page for page in pages if page not in PAGE_SPECS]
    if unknown_pages:
        raise argparse.ArgumentTypeError(
            f"未知页面：{', '.join(unknown_pages)}；可选：{', '.join(PAGE_SPECS)}"
        )
    return pages


def parse_args():
    parser = argparse.ArgumentParser(description="遍历 MT 页面，点击核对候选节点用途，并更新 MT_nodes.py。")
    parser.add_argument(
        "mode",
        nargs="?",
        default="update",
        choices=("update", "collect"),
        help="update 会写回 MT_nodes.py；collect 只导出 dump 和汇总 JSON。",
    )
    parser.add_argument(
        "--pages",
        type=parse_pages,
        default=DEFAULT_PAGES,
        help=f"逗号分隔页面列表，默认：{','.join(DEFAULT_PAGES)}",
    )
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=200,
        help="每个页面最多保留的原始候选节点数量；写回维护区时仍以 verified_nodes 为准。",
    )
    parser.add_argument(
        "--include-stateful-actions",
        action="store_true",
        help="同时点击会改变游戏状态的节点，例如 build、spin、公会请求。默认跳过。",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    catalog = collect_pages(args.pages, args.max_nodes, args.include_stateful_actions)
    write_summary(catalog)
    if args.mode == "update":
        update_nodes_file(catalog)
    print("====================== 节点维护完成 ======================")
    for page_name, page_data in catalog["pages"].items():
        status = "PASS" if page_data.get("enter_passed") else "ENTER_FAILED"
        print(
            f"{page_name}: {status}, "
            f"node_count={page_data.get('node_count', 0)}, "
            f"raw_candidates={page_data.get('raw_candidate_count', 0)}, "
            f"verified={page_data.get('verified_count', 0)}"
        )
    return True


if __name__ == "__main__":
    main()
