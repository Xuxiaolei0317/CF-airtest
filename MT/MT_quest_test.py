# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from airtest.core.api import *

# 允许从 CF 子目录直接运行脚本时导入上一级的公共初始化模块。
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, dev, poco

import MT_nodes
import MT_main
import MT_test
from MT_nodes import common_nodes as mt
from MT_test import close_popups

# 打开截图功能
ST.SAVE_IMAGE = True

SCENARIOS = ("guide", "bottle", "build", "quest", "spin")
FLOW_SCENARIOS = SCENARIOS + ("guild", "stamp", "store", "footer_flow")
APP_PACKAGE = MT_main.APP_PACKAGE
MANAGE_APP_LIFECYCLE = MT_main.MANAGE_APP_LIFECYCLE
GUILD_NAME = "GGboy"
GUILD_MESSAGE = "hello"
NODE_DUMP_DIR = Path(__file__).resolve().parent / "node_dumps"
SCREENSHOT_DIR = Path(__file__).resolve().parent / "screenshots"


def launch_actions():
    """创建通用启动模块，并把重连后的 Poco 同步回当前脚本。"""
    return MT_main.LaunchActions(
        dev,
        poco_driver=poco,
        sync_modules=(MT_nodes, MT_test, sys.modules[__name__]),
        capture_callback=capture_screen,
        dump_callback=dump_current_nodes,
    )


def reset_poco_connection():
    """兼容旧调用：应用冷启动后重建 Poco 连接。"""
    return launch_actions().reset_poco_connection()


def screen_point(relative_point):
    """兼容旧调用：把启动页相对坐标转换为当前设备坐标。"""
    return launch_actions().screen_point(relative_point)


def tap_relative(relative_point, label):
    """兼容旧调用：点击启动页相对坐标。"""
    return launch_actions().tap_relative(relative_point, label)


def parse_relative_point(raw_value):
    """兼容旧调用：解析 x,y 相对坐标。"""
    return MT_main.LaunchActions.parse_relative_point(raw_value)


def parse_launch_options(raw_value):
    """兼容旧调用：解析启动页开关配置。"""
    return MT_main.LaunchActions.parse_launch_options(raw_value)


def launch_option_enabled(option_name):
    """兼容旧调用：判断启动页开关状态。"""
    return launch_actions().launch_option_enabled(option_name)


def set_launch_options():
    """兼容旧调用：按需设置启动页开关。"""
    return launch_actions().set_launch_options()


def select_launch_server():
    """兼容旧调用：按需切换启动页服务器。"""
    return launch_actions().select_launch_server()


def tap_launch_confirm():
    """兼容旧调用：点击测试包启动页 Confirm。"""
    return launch_actions().tap_launch_confirm()


def launch_game():
    """兼容旧调用：冷启动游戏。"""
    return launch_actions().launch_game()


def close_game():
    """兼容旧调用：关闭游戏。"""
    return launch_actions().close_game()


def node_display_name(node):
    """格式化 Poco 节点名称，便于日志定位字段。"""
    node_text = str(node)
    prefix = 'UIObjectProxy of "'
    if node_text.startswith(prefix) and node_text.endswith('"'):
        return node_text[len(prefix):-1]
    return node_text


def node_exists(node):
    """兼容 Poco 节点、Airtest Template、布尔状态的存在性判断。"""
    try:
        if isinstance(node, bool):
            return node
        if hasattr(node, "exists"):
            return node.exists()
        return bool(exists(node))
    except Exception as e:
        print(f"❌ 节点检查异常：{node_display_name(node)} | {e}")
        return False


def node_text(node, default=""):
    """安全读取节点文本，避免冒烟检查被单个节点打断。"""
    try:
        return node.get_text() if node.exists() else default
    except Exception as e:
        print(f"❌ 文本读取异常：{node_display_name(node)} | {e}")
        return default


def capture_screen(reason):
    """保存当前屏幕截图，便于验证流程是否到达预期页面。"""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    safe_reason = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fa5-]+", "_", reason).strip("_") or "screen"
    file_path = SCREENSHOT_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_reason}.png"
    try:
        snapshot(filename=str(file_path), msg=reason)
        print(f"✅ 已保存屏幕截图：{file_path}")
        return str(file_path)
    except Exception as e:
        print(f"❌ 屏幕截图失败：{reason} | {e}")
        return None


def dump_current_nodes(reason, keywords=None):
    """保存当前 Poco 节点树，便于节点名失配时反查相似节点。"""
    NODE_DUMP_DIR.mkdir(parents=True, exist_ok=True)
    safe_reason = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fa5-]+", "_", reason).strip("_") or "unknown"
    file_path = NODE_DUMP_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_reason}.json"
    screenshot_path = capture_screen(reason)

    try:
        hierarchy = poco.agent.hierarchy.dump()
    except Exception as e:
        print(f"❌ Poco 节点树导出失败：{e}")
        return None

    flat_nodes = []

    def walk(node, path="root"):
        if not isinstance(node, dict):
            return
        name = node.get("name") or node.get("type") or ""
        payload = node.get("payload") if isinstance(node.get("payload"), dict) else {}
        text_value = payload.get("text") or node.get("text") or ""
        current_path = f"{path}/{name}" if name else path
        flat_nodes.append({
            "path": current_path,
            "name": name,
            "type": node.get("type", ""),
            "text": text_value,
            "visible": payload.get("visible", node.get("visible", "")),
            "clickable": payload.get("clickable", node.get("clickable", "")),
            "pos": payload.get("pos", node.get("pos", "")),
        })
        for child in node.get("children", []) or []:
            walk(child, current_path)

    walk(hierarchy)
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
        "screenshot": screenshot_path,
        "keywords": tokens,
        "node_count": len(flat_nodes),
        "similar_count": len(similar_nodes),
        "similar_nodes": similar_nodes,
        "flat_nodes": flat_nodes,
        "hierarchy": hierarchy,
    }
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, default=str)
    print(f"✅ 已导出当前节点 JSON：{file_path}")
    print(f"   节点总数：{len(flat_nodes)}，相似节点：{len(similar_nodes)}")
    return file_path


def if_click(node, label=None):
    """节点存在则点击，返回是否点击成功。"""
    name = label or node_display_name(node)
    if node_exists(node):
        try:
            node.click()
            print(f"✅ 点击节点：{name}")
            return True
        except AttributeError:
            pos = exists(node)
            if pos:
                touch(pos)
                print(f"✅ 点击图片节点：{name}")
                return True
        except Exception as e:
            print(f"❌ 点击节点异常：{name} | {e}")
            return False
    print(f"❌ 节点不存在：{name}")
    return False


def click_first(nodes, label):
    """按顺序点击第一个存在的候选节点。"""
    for index, node in enumerate(nodes):
        if if_click(node, f"{label}[{index}]"):
            return True
    dump_current_nodes(f"missing_{label}")
    return False


def adb_shell(args, timeout=5):
    """执行 adb shell 命令，主要用于处理系统输入法弹窗。"""
    try:
        result = subprocess.run(
            ["adb", "shell", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.stdout or ""
    except Exception as e:
        print(f"⚠️ adb shell 执行异常：{' '.join(args)} | {e}")
        return ""


def adb_command(args, timeout=10):
    """执行 adb 命令，读取 logcat 等非 shell 子命令输出。"""
    try:
        result = subprocess.run(
            ["adb", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.stdout or ""
    except Exception as e:
        print(f"⚠️ adb 命令执行异常：{' '.join(args)} | {e}")
        return ""


def print_latest_lua_error_log():
    """从 logcat 中打印最近一次 Lua/Char Error 的完整节点路径日志。"""
    logcat = adb_command(["logcat", "-d", "-v", "time"], timeout=12)
    lines = logcat.splitlines()
    error_indices = [
        index
        for index, line in enumerate(lines)
        if "Char Error:" in line or "[Lua Error]" in line or "Lua Error" in line
    ]
    if not error_indices:
        print("⚠️ logcat 未找到 Lua Error / Char Error 相关日志")
        return False

    start = error_indices[-1]
    block = []
    for line in lines[start:start + 16]:
        if any(keyword in line for keyword in (
            "Char Error",
            "Lua Error",
            "MainGameScene",
            "Header_Node",
            "node_bill",
            "label_bill",
            "showStr",
            "letter",
            "fntPath",
            "[LUA-print]",
        )):
            block.append(line)

    print("====================== Lua Error log ======================")
    for line in block or lines[start:start + 8]:
        print(line)
    print("===========================================================")
    return True


def check_lua_error_popup():
    """检测游戏内 [Lua Error] 弹窗，存在则截图并打印最近的完整路径日志。"""
    try:
        hierarchy = poco.agent.hierarchy.dump()
        hierarchy_text = json.dumps(hierarchy, ensure_ascii=False, default=str)
    except Exception as e:
        print(f"⚠️ Lua Error 弹窗检查失败：{e}")
        return False

    if "[Lua Error]" not in hierarchy_text and "Lua Error" not in hierarchy_text and "Char Error" not in hierarchy_text:
        return False

    capture_screen("lua_error_popup")
    print("❌ 检测到 [Lua Error] 报错弹窗")
    print_latest_lua_error_log()
    return True


def screen_size(default=(1080, 2340)):
    output = adb_shell(["wm", "size"])
    match = re.search(r"Physical size:\s*(\d+)x(\d+)", output)
    return (int(match.group(1)), int(match.group(2))) if match else default


def tap_screen_ratio(x_ratio, y_ratio):
    width, height = screen_size()
    adb_shell(["input", "tap", str(int(width * x_ratio)), str(int(height * y_ratio))])


def clear_yosemite_cache_if_needed():
    """Airtest 输入法异常时，清理 Yosemite 缓存并让后续 text() 重试。"""
    ui_xml = adb_shell(["uiautomator", "dump", "/dev/tty"], timeout=8)
    if "Yosemite" not in ui_xml and "清除缓存" not in ui_xml:
        return False
    capture_screen("yosemite_cache_dialog")
    tap_screen_ratio(0.72, 0.835)
    sleep(1.0)
    print("✅ 已清除 Yosemite 缓存弹窗")
    return True


def input_text_to_first(nodes, value, label):
    """点击第一个存在的输入节点并输入文本。"""
    for index, node in enumerate(nodes):
        if if_click(node, f"{label}[{index}]"):
            for attempt in range(2):
                try:
                    text(value)
                    if clear_yosemite_cache_if_needed():
                        continue
                    print(f"✅ 输入文本：{label} -> {value}")
                    return True
                except Exception as e:
                    print(f"⚠️ 输入文本异常，第 {attempt + 1} 次：{label} | {e}")
                    if not clear_yosemite_cache_if_needed():
                        break
            dump_current_nodes(f"failed_input_{label}")
            return False
    print(f"❌ 未找到输入节点：{label}")
    dump_current_nodes(f"missing_{label}")
    return False


def safe_close_popups():
    """关闭通用弹窗，Poco RPC 不稳定时不让流程崩溃。"""
    try:
        return close_popups()
    except Exception as e:
        print(f"⚠️ 关闭弹窗异常，继续流程：{e}")
        return False


def extract_int(value, default=0):
    """从 X20、20、20 spins 等文本中提取整数。"""
    match = re.search(r"\d[\d,]*", str(value or ""))
    return int(match.group().replace(",", "")) if match else default


def smoke_check_node(module, field, node, read_text=False, required=True):
    """输出单个节点的冒烟检查结果。"""
    exists_result = node_exists(node)
    status = "PASS" if exists_result else ("FAIL" if required else "SKIP")
    text = node_text(node) if exists_result and read_text and hasattr(node, "get_text") else ""
    detail = f" | text={text}" if text else ""
    print(f"[{status}] {module}.{field} -> {node_display_name(node)}{detail}")
    return exists_result or not required


def smoke_check_nodes():
    """维护 Poco 节点后先跑的轻量冒烟检查。"""
    print("====================== smoke start ======================")
    safe_close_popups()

    common_obj = mt()
    main_obj = mt.mt_main()
    slot_obj = mt.mt_slot()
    build_obj = mt.mt_build()
    guide_obj = mt.mt_guide()
    bottle_obj = mt.mt_bottle()
    quest_obj = mt.mt_quest()

    checks = [
        ("common", "btn_close", common_obj.btn_close, False, False),
        ("common", "close_btn", common_obj.close_btn, False, False),
        ("common", "btn_collect", common_obj.btn_collect, False, False),
        ("main", "mt_ft_store_node", main_obj.mt_ft_store_node, False, True),
        ("main", "mt_ft_build_node", main_obj.mt_ft_build_node, False, True),
        ("main", "mt_ft_spin_node", main_obj.mt_ft_spin_node, False, True),
        ("main", "mt_ft_guild_friend_node", main_obj.mt_ft_guild_friend_node, False, True),
        ("main", "mt_ft_stamp_node", main_obj.mt_ft_stamp_node, False, True),
        ("main", "mt_ft_store", main_obj.mt_ft_store, False, True),
        ("main", "mt_ft_build", main_obj.mt_ft_build, False, True),
        ("main", "mt_ft_spin", main_obj.mt_ft_spin, False, True),
        ("main", "mt_ft_guild_friend", main_obj.mt_ft_guild_friend, False, True),
        ("main", "mt_ft_stamp", main_obj.mt_ft_stamp, False, True),
        ("main", "mt_hd_coin", main_obj.mt_hd_coin, True, False),
        ("main", "mt_hd_bill", main_obj.mt_hd_bill, True, False),
        ("main", "mt_hd_shield", main_obj.mt_hd_shield, True, False),
        ("slot", "mt_spin_btn", slot_obj.mt_spin_btn, False, True),
        ("slot", "mt_slot_win_label", slot_obj.mt_slot_win_label, True, False),
        ("slot", "mt_attack_dialog", slot_obj.mt_attack_dialog, False, False),
        ("slot", "mt_steal_node", slot_obj.mt_steal_node, False, False),
        ("build", "mt_build_map_btn", build_obj.mt_build_map_btn, False, False),
        ("build", "mt_build_map_center_btn", build_obj.mt_build_map_center_btn, False, False),
        ("build", "mt_main_coin_cost_btn", build_obj.mt_main_coin_cost_btn, False, False),
        ("guide", "guide_dialog", guide_obj.guide_dialog, False, False),
        ("guide", "guide_skip_btn", guide_obj.guide_skip_btn, False, False),
        ("bottle", "bottle_node", bottle_obj.bottle_node, False, False),
        ("bottle", "bottle_dialog", bottle_obj.bottle_dialog, False, False),
        ("quest", "quest_dialog", quest_obj.quest_dialog, False, False),
        ("quest", "quest_index_label", quest_obj.quest_index_label, True, False),
        ("quest", "quest_spin_btn", quest_obj.quest_spin_btn, False, False),
    ]

    results = [
        smoke_check_node(module, field, node, read_text, required)
        for module, field, node, read_text, required in checks
    ]
    passed = all(results)
    print(f"====================== smoke {'pass' if passed else 'fail'} ======================")
    return passed


def run_step(name, func, retries=1, required=False):
    """统一执行单个场景，失败时关闭弹窗并重试。"""
    for index in range(retries + 1):
        try:
            print(f"====================== {name} start ({index + 1}/{retries + 1}) ======================")
            if func():
                check_lua_error_popup()
                print(f"✅ {name} 完成")
                return True
        except Exception as e:
            print(f"❌ {name} 异常：{e}")
            check_lua_error_popup()

        safe_close_popups()
        check_lua_error_popup()
        sleep(0.5)
        print(f"⚠️ {name} 第 {index + 1} 次执行未完成")

    if required:
        print(f"❌ {name} 连续失败，停止强依赖流程")
    else:
        print(f"⚠️ {name} 未完成，继续后续非强依赖流程")
    return False


# 新手引导流程，漂流瓶流程，建造流程，spin流程，quest流程
def test_guide(max_steps=5):
    guide_obj = mt.mt_guide()
    clicked = False
    for _ in range(max_steps):
        if if_click(guide_obj.guide_next_btn, "guide.guide_next_btn"):
            clicked = True
        elif if_click(guide_obj.tap_to_continue, "guide.tap_to_continue"):
            clicked = True
        elif if_click(guide_obj.guide_skip_btn, "guide.guide_skip_btn"):
            clicked = True
        else:
            break
        sleep(0.5)
    return clicked or not node_exists(guide_obj.guide_dialog)


def test_bottle():
    bottle_obj = mt.mt_bottle()
    if not if_click(bottle_obj.bottle_node, "bottle.bottle_node"):
        return False
    sleep(0.5)
    if_click(bottle_obj.bottle_open_btn, "bottle.bottle_open_btn")
    sleep(0.5)
    if if_click(bottle_obj.bottle_collect_btn, "bottle.bottle_collect_btn"):
        return True
    return if_click(bottle_obj.bottle_close_btn, "bottle.bottle_close_btn")


def test_build():
    build_obj = mt.mt_build()
    if if_click(build_obj.mt_build_map_btn, "build.mt_build_map_btn"):
        return True
    if if_click(build_obj.mt_build_map_center_btn, "build.mt_build_map_center_btn"):
        return True
    if if_click(build_obj.mt_main_coin_collect_btn, "build.mt_main_coin_collect_btn"):
        return True
    return False


def test_quest(max_steps=3):
    quest_obj = mt.mt_quest()
    completed = False
    for _ in range(max_steps):
        if if_click(quest_obj.quest_spin_btn, "quest.quest_spin_btn"):
            completed = True
            sleep(0.5)
        elif if_click(quest_obj.quest_collect_btn, "quest.quest_collect_btn"):
            completed = True
            sleep(0.5)
        else:
            break
    return completed or not node_exists(quest_obj.quest_dialog)


def test_attack(timeout=12):
    """处理攻击分支，避免结算弹窗未出现时无限等待。"""
    attack_obj = mt.mt_slot()
    attack_buttons = list(attack_obj.mt_attack_btns)
    if attack_buttons:
        attack_buttons[0].click()
        print("✅ 点击攻击目标：slot.mt_attack_btns[0]")
    else:
        dump_current_nodes("missing_slot.mt_attack_btns")
        return False

    deadline = time.time() + timeout
    while time.time() < deadline:
        attack_obj = mt.mt_slot()
        if node_exists(attack_obj.mt_attack_pop):
            attack_coin = node_text(attack_obj.mt_attack_coin_label, "0")
            print(f"本次攻击赢钱：{attack_coin}")
            if_click(attack_obj.mt_attack_collect_btn, "slot.mt_attack_collect_btn")
            capture_screen("after_attack_collect")
            return True
        if not node_exists(attack_obj.mt_attack_dialog):
            print("攻击界面已关闭，继续后续流程")
            return True
        sleep(0.5)

    dump_current_nodes("timeout_slot.attack")
    safe_close_popups()
    return False


def test_steal(max_clicks=8, timeout=8):
    """处理偷钱分支，限制点击和等待次数。"""
    steal_obj = mt.mt_slot()
    for index in range(max_clicks):
        if not if_click(steal_obj.mt_steal_box_btn, "slot.mt_steal_box_btn"):
            dump_current_nodes("missing_slot.mt_steal_box_btn")
            return False

        deadline = time.time() + timeout
        while time.time() < deadline:
            steal_obj = mt.mt_slot()
            if node_exists(steal_obj.mt_steal_popup):
                steal_coin = node_text(steal_obj.mt_steal_coin_label, "0")
                print(f"本次偷钱赢钱：{steal_coin}")
                if_click(steal_obj.mt_steal_collect_btn, "slot.mt_steal_collect_btn")
                capture_screen("after_steal_collect")
                return True
            sleep(0.3)
        print(f"偷钱第 {index + 1}/{max_clicks} 次未结算，继续尝试")

    dump_current_nodes("timeout_slot.steal")
    safe_close_popups()
    return False


def test_spin(max_times=5):
    main_obj = mt.mt_main()
    if_click(main_obj.mt_ft_slot, "main.mt_ft_slot")
    completed = False

    for index in range(max_times):
        safe_close_popups()
        slot_obj = mt.mt_slot()
        if not if_click(slot_obj.mt_spin_btn, "slot.mt_spin_btn"):
            return completed
        completed = True
        sleep(0.5)

        slot_obj = mt.mt_slot()
        if slot_obj.mt_slot_win_text == "ATTACK" or slot_obj.mt_attack_dialog.exists():
            test_attack()
        elif slot_obj.mt_slot_win_text == "STEAL" or slot_obj.slot_steal:
            test_steal()
        else:
            print(f"spin 第 {index + 1} 次结果：{slot_obj.mt_slot_win_text}")
    return completed


def test_build_times(max_times=20):
    main_obj = mt.mt_main()
    if not if_click(main_obj.mt_ft_build, "main.mt_ft_build"):
        dump_current_nodes("missing_main.mt_ft_build")
        return False
    sleep(0.8)

    completed = 0
    for index in range(max_times):
        safe_close_popups()
        build_obj = mt.mt_build()
        if click_first(build_obj.mt_build_action_candidates, "build.action"):
            completed += 1
            print(f"建造第 {index + 1}/{max_times} 次完成")
            sleep(0.6)
            safe_close_popups()
        else:
            print(f"❌ 建造第 {index + 1}/{max_times} 次未找到可点击节点")
            break
    capture_screen(f"after_build_{completed}_of_{max_times}")
    return completed == max_times


def set_spin_bet(target_bet=20, max_steps=20):
    main_obj = mt.mt_main()
    if not if_click(main_obj.mt_ft_spin, "main.mt_ft_spin"):
        dump_current_nodes("missing_main.mt_ft_spin")
        return False
    sleep(0.8)

    for _ in range(max_steps):
        slot_obj = mt.mt_slot()
        current_bet = extract_int(slot_obj.mt_spin_bet_num)
        print(f"当前 bet：{current_bet}，目标 bet：{target_bet}")
        if current_bet == target_bet:
            capture_screen(f"after_set_spin_bet_{target_bet}_matched")
            return True

        if current_bet > target_bet:
            if not if_click(slot_obj.mt_spin_bet_sub_btn, "slot.mt_spin_bet_sub_btn"):
                dump_current_nodes("missing_slot.mt_spin_bet_sub_btn")
                return False
        else:
            if not if_click(slot_obj.mt_spin_bet_add_btn, "slot.mt_spin_bet_add_btn"):
                dump_current_nodes("missing_slot.mt_spin_bet_add_btn")
                return False
        sleep(0.3)

    slot_obj = mt.mt_slot()
    matched = extract_int(slot_obj.mt_spin_bet_num) == target_bet
    capture_screen(f"after_set_spin_bet_{target_bet}_{'matched' if matched else 'unmatched'}")
    return matched


def test_spin_with_bet(max_times=20, target_bet=20):
    if not set_spin_bet(target_bet):
        print(f"⚠️ 未能确认 bet 已设置为 {target_bet}，继续尝试 spin")

    completed = 0
    for index in range(max_times):
        safe_close_popups()
        slot_obj = mt.mt_slot()
        if not if_click(slot_obj.mt_spin_btn, "slot.mt_spin_btn"):
            dump_current_nodes("missing_slot.mt_spin_btn")
            break

        completed += 1
        sleep(0.6)
        slot_obj = mt.mt_slot()
        if slot_obj.mt_slot_win_text == "ATTACK" or slot_obj.mt_attack_dialog.exists():
            test_attack()
        elif slot_obj.mt_slot_win_text == "STEAL" or slot_obj.slot_steal:
            test_steal()
        else:
            print(f"20 bet spin 第 {index + 1}/{max_times} 次结果：{slot_obj.mt_slot_win_text}")
    capture_screen(f"after_spin_{completed}_of_{max_times}_bet_{target_bet}")
    return completed == max_times


def send_guild_message(message=GUILD_MESSAGE):
    guild_obj = mt.mt_guild()
    if_click(guild_obj.guild_chat_btn, "guild.guild_chat_btn")
    if_click(guild_obj.guild_chat_tab, "guild.guild_chat_tab")
    sleep(0.5)
    guild_obj = mt.mt_guild()
    if not input_text_to_first(
        (
            guild_obj.guild_message_input,
            guild_obj.guild_message_input_alt,
            guild_obj.guild_message_input_edit,
        ),
        message,
        "guild.message_input",
    ):
        return False
    sleep(0.2)
    if not click_first((guild_obj.guild_send_btn, guild_obj.guild_send_btn_alt), "guild.send"):
        dump_current_nodes("missing_guild.guild_send_btn")
        return False
    capture_screen("after_send_guild_message")
    return True


def join_guild(guild_name=GUILD_NAME):
    guild_obj = mt.mt_guild()
    click_first(guild_obj.guild_not_joined_candidates, "guild.not_joined")
    sleep(0.5)
    guild_obj = mt.mt_guild()

    input_text_to_first(
        (guild_obj.guild_search_input, guild_obj.guild_search_input_alt),
        guild_name,
        "guild.search_input",
    )
    sleep(0.2)
    click_first(
        (guild_obj.guild_search_confirm_btn, guild_obj.guild_search_btn),
        "guild.search_confirm",
    )
    sleep(1.0)

    guild_obj = mt.mt_guild()
    joined = click_first(guild_obj.guild_join_candidates, "guild.join")
    if joined:
        common_obj = mt()
        sleep(0.5)
        if_click(common_obj.btn_confirm, "common.btn_confirm")
        capture_screen(f"after_join_guild_{guild_name}")
    return joined


def test_guild_flow():
    main_obj = mt.mt_main()
    if not if_click(main_obj.mt_ft_guild_friend, "main.mt_ft_guild_friend"):
        dump_current_nodes("missing_main.mt_ft_guild_friend")
        return False
    sleep(1.0)
    safe_close_popups()

    guild_obj = mt.mt_guild()
    if if_click(guild_obj.guild_collect_btn, "guild.guild_collect_btn"):
        sleep(0.8)
        guild_obj = mt.mt_guild()

    in_guild = (
        node_exists(guild_obj.guild_main)
        or node_exists(guild_obj.guild_chat_layer)
        or node_exists(guild_obj.guild_home)
        or node_exists(guild_obj.guild_message_input)
        or node_exists(guild_obj.guild_message_input_alt)
    )
    if in_guild:
        print("已在公会中，发送公会消息")
        return send_guild_message("test message")

    print(f"未检测到已加入公会状态，搜索并加入公会：{GUILD_NAME}")
    return join_guild()


def test_stamp_flow():
    main_obj = mt.mt_main()
    if not if_click(main_obj.mt_ft_stamp, "main.mt_ft_stamp"):
        dump_current_nodes("missing_main.mt_ft_stamp")
        return False
    sleep(0.8)
    safe_close_popups()
    swipe((540, 1700), (540, 700), duration=0.5)
    sleep(0.5)
    swipe((540, 700), (540, 1700), duration=0.5)
    sleep(0.5)
    capture_screen("after_stamp_swipe")
    return True


def test_return_store():
    main_obj = mt.mt_main()
    if not if_click(main_obj.mt_ft_store, "main.mt_ft_store"):
        dump_current_nodes("missing_main.mt_ft_store")
        return False
    sleep(0.8)
    capture_screen("after_return_store")
    return True


def run_footer_flow():
    """建造20次、20 bet spin20次、公会处理、邮票滑动，最后回商店。"""
    steps = [
        ("build_20", lambda: test_build_times(20)),
        ("spin_20_bet_20", lambda: test_spin_with_bet(20, 20)),
        ("guild", test_guild_flow),
        ("stamp", test_stamp_flow),
        ("store", test_return_store),
    ]
    results = []
    for name, func in steps:
        passed = run_step(name, func, retries=0)
        capture_screen(f"step_{name}_{'pass' if passed else 'fail'}")
        results.append((name, passed))

    print("====================== footer flow summary ======================")
    for name, passed in results:
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    return all(passed for _, passed in results)


def run_single_scenario(name):
    scenario_map = {
        "guide": test_guide,
        "bottle": test_bottle,
        "build": test_build,
        "quest": test_quest,
        "spin": test_spin,
        "guild": test_guild_flow,
        "stamp": test_stamp_flow,
        "store": test_return_store,
        "footer_flow": run_footer_flow,
    }
    if name not in scenario_map:
        print(f"❌ 未知场景：{name}，可选：{', '.join(FLOW_SCENARIOS)}")
        return False
    retries = 0 if name in ("footer_flow", "guild", "stamp", "store") else 1
    return run_step(name, scenario_map[name], retries=retries)


def run_full_flow():
    """维护节点后按冒烟、单场景、完整流程三阶段执行。"""
    smoke_passed = smoke_check_nodes()
    if not smoke_passed:
        print("⚠️ 冒烟检查存在失败项，继续执行非强依赖场景用于收集更多日志")

    results = []
    for name in SCENARIOS:
        results.append((name, run_single_scenario(name)))

    print("====================== summary ======================")
    for name, passed in results:
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    return all(passed for _, passed in results)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "launch":
        return launch_game()
    if mode == "close":
        return close_game()

    valid_modes = {"smoke", "single", "full", *FLOW_SCENARIOS}
    if mode not in valid_modes:
        print("用法：python MT_quest_test.py [launch|close|smoke|single <scene>|guide|bottle|build|quest|spin|guild|stamp|store|footer_flow|full]")
        return False

    if MANAGE_APP_LIFECYCLE and not launch_game():
        return False

    try:
        if mode == "smoke":
            return smoke_check_nodes()
        if mode == "single":
            scenario = sys.argv[2] if len(sys.argv) > 2 else "quest"
            return run_single_scenario(scenario)
        if mode in FLOW_SCENARIOS:
            return run_single_scenario(mode)
        if mode == "full":
            return run_full_flow()
    finally:
        if MANAGE_APP_LIFECYCLE:
            close_game()

    return False

if __name__ == "__main__":
    main()