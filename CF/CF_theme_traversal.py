#!/usr/bin/env python3
# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# 从脚本开始计时，覆盖导入 airtest_booststrap 时的设备检测和 Poco 初始化耗时。
SCRIPT_START_AT = time.perf_counter()

from airtest.core.api import log, sleep, start_app, stop_app, touch
from pocounit.addons.poco.action_tracking import ActionTracker
from pocounit.case import PocoTestCase

# 导入公共初始化模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, dev, get_android_poco, init_poco, poco

BOOTSTRAP_READY_AT = time.perf_counter()

# 导入节点和状态机
import CF_nodes
from CF_nodes import GameActions
from CF_state_machine import create_state_machine
from CF_theme_traversal_tree import ThemeTraversalCallbacks, ThemeTraversalTree


ST.SAVE_IMAGE = False

# 同步公共初始化里的 Poco，保证状态机和节点模块用同一个连接。
CF_nodes.poco = poco

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "log" / "theme_traversal"
DEFAULT_CF_APP_PACKAGE = "slots.pcg.casino.games.free.android"

# 默认遍历列表：需要验证更多主题时直接补充这里，或运行时用 --theme-ids 覆盖。
# THEME_IDS = [122,255,340,326]
THEME_IDS = [
  122, 340, 276, 255, 326, 331, 10468, 366, 101, 244, 386, 107, 321, 141, 181, 388, 125, 295, 208, 213,
  363, 396, 406, 114, 346, 176, 217, 413, 204, 361, 416, 372, 257, 399, 180, 108, 203, 241, 341, 411,
  202, 118, 370, 124, 157, 209, 427, 350, 308, 239, 177, 111, 248, 391, 192, 289, 436, 263, 421, 357,
  253, 200, 163, 410, 102, 126, 375, 332, 232, 381, 227, 166, 424, 353, 405, 274, 270, 425, 356, 105,
  251, 407, 351, 292, 402, 299, 404, 103, 338, 376, 250, 398, 115, 165, 394, 378, 344, 212, 127, 10469,
  392, 272, 303, 128, 195, 10452, 368, 374, 106, 199, 349, 313, 367, 117, 249, 297, 190, 401, 329, 260,
  173, 109, 140, 278, 319, 354, 383, 233, 256, 327, 412, 271, 390, 380, 335, 328, 113, 193, 385, 224,
  426, 262, 431, 284, 110, 382, 218, 362, 311, 148, 358, 283, 147, 291, 418, 281, 296, 345, 379, 129,
  130, 132, 240, 143, 415, 287, 207, 339, 377, 397, 228, 191, 196, 286, 342, 314, 121, 235, 268, 408,
  384, 245, 307, 229, 236, 317, 119, 188, 277, 429, 123, 168, 323, 309, 373, 210, 280, 409, 365, 324,
  112, 187, 273, 318, 136, 167, 258, 310, 422, 206, 423, 220, 265, 316, 371, 144, 252, 10470, 438, 10477,
  264, 138, 175, 355, 158, 387, 389, 352, 275, 238, 325, 420, 116, 134, 211, 194, 395, 160, 444, 432,
  440, 149, 347, 315, 221, 172, 242, 234, 359, 267, 219, 330, 182, 247, 185, 214, 145, 294, 333, 300,
  360, 322, 298, 150, 137, 259, 414, 439, 442, 197, 146, 164, 169, 320, 139, 152, 189, 243, 285, 334,
  449, 443, 417, 198, 279, 174, 170, 10474, 135, 269, 282, 131, 222, 348, 10471, 428, 154, 171, 179, 337,
  261, 400, 403, 369, 302, 290, 230, 305, 162, 433, 446, 343, 205, 186, 266, 225, 10486, 201, 153, 178,
  10489, 435, 306, 223, 336, 441, 231, 215, 183, 393, 216, 434, 246, 161, 237, 304, 10472, 10475, 293, 254,
  184, 226, 301, 419, 288, 364, 133, 159, 312, 142, 10458, 10503, 10456, 10462, 10451, 447, 156, 10465, 450, 430,
  10505, 10476, 10506, 10513, 448, 10514, 10479, 10487, 10491, 10459, 10480, 10483, 10485, 437, 10455, 10488, 10494, 10496, 10492, 10493,
  10518, 10516, 10521, 10520, 10482, 10461, 10454, 10481, 10523, 10547, 10536, 10528, 10525, 10527, 10473, 10517, 10519, 10497, 10511, 10537,
  10524, 10546, 10530, 10532, 10529, 10467, 10531, 4200, 120, 151, 155, 4204, 2001, 2002, 2003
]
# 复测Id list ↓
# THEME_IDS = [ 375, 332, 232, 381, 227, 166, 424, 353, 405, 274, 270, 425, 356, 105, 251, 407, 351, 292, 402, 299, 404, 103, 338, 376, 250, 398, 115, 165, 394, 378, 344, 212, 127, 10469, 392, 272, 303, 128, 195, 10452, 368, 374, 106, 199, 349, 313, 367, 117, 249, 297, 190, 401, 329, 260, 173, 109, 140, 278, 319, 354, 383, 233, 256, 327, 412, 271, 390, 380, 335, 328, 113, 193, 385, 224, 426, 262, 431, 284, 110, 382, 218, 362, 311, 148, 358, 283, 147, 291, 418, 281, 296, 345, 379, 129, 130, 132, 240, 143, 415, 287, 207, 339, 377, 397, 228, 191, 196, 286, 342, 314, 121, 235, 268, 408, 384, 245, 307, 229, 236, 317, 119, 188, 277, 429, 123, 168, 323, 309, 373, 210, 280, 409, 365, 324, 112, 187, 273, 318, 136, 167, 258, 310, 422, 206, 423, 220, 265, 316, 371, 144, 252, 10470, 438, 10477, 264, 138, 175, 355, 158, 387, 389, 352, 275, 238, 325, 420, 116, 134, 211, 194, 395, 160, 444, 432, 440, 149, 347, 315, 221, 172, 242, 234, 359, 267, 219, 330, 182, 247, 185, 214, 145, 294, 333, 300, 360, 322, 298, 150, 137, 259, 414, 439, 442, 197, 146, 164, 169, 320, 139, 152, 189, 243, 285, 334, 449, 443, 417, 198, 279, 174, 170, 10474, 135, 269, 282, 131, 222, 348, 10471, 428]
THEME_LOAD_TIMEOUT = int(os.environ.get("CF_THEME_LOAD_TIMEOUT", "25"))
THEME_SELECT_TIMEOUT = 10
THEME_SELECT_OPEN_TIMEOUT = int(os.environ.get("CF_THEME_SELECT_OPEN_TIMEOUT", str(THEME_SELECT_TIMEOUT)))
SOCIAL_THEME_FLOW_TIMEOUT = int(os.environ.get("CF_SOCIAL_THEME_FLOW_TIMEOUT", "8"))
SOCIAL_THEME_ROLE_CONFIRM_TIMEOUT = float(os.environ.get("CF_SOCIAL_THEME_ROLE_CONFIRM_TIMEOUT", "3"))
SOCIAL_THEME_BEFORE_MACHINE_CLICK_DELAY = float(os.environ.get("CF_SOCIAL_THEME_BEFORE_MACHINE_CLICK_DELAY", "5"))
SOCIAL_THEME_RETURN_TIMEOUT = int(os.environ.get("CF_SOCIAL_THEME_RETURN_TIMEOUT", "8"))
try:
    SOCIAL_THEME_MACHINE_INDEX = int(os.environ.get("CF_SOCIAL_THEME_MACHINE_INDEX", "0"))
except ValueError:
    SOCIAL_THEME_MACHINE_INDEX = 0
LOBBY_RETURN_TIMEOUT = 10
LOBBY_RETURN_RETRY_COUNT = int(os.environ.get("CF_LOBBY_RETURN_RETRY_COUNT", "1"))
LOBBY_RETURN_RETRY_DELAY = float(os.environ.get("CF_LOBBY_RETURN_RETRY_DELAY", "2"))
LOBBY_PREPARE_TIMEOUT = 8
APP_RESTART_WAIT_SECONDS = 10
LAUNCH_CONFIRM_TIMEOUT = 10
LAUNCH_CONFIRM_TAP = os.environ.get("CF_LAUNCH_CONFIRM_TAP", "0.500,0.940").strip()
DEFAULT_STAY_SECONDS = 0
THEME_HOME_STABLE_SECONDS = 1.5
THEME_POPUP_CHECK_INTERVAL = 2
THEME_POPUP_RECOVER_TRIES = 4
SPIN_BEFORE_RETURN_COUNT = 2
SPIN_BEFORE_RETURN_INTERVAL = 1.0
LOBBY_HOME_PATHS = (
    "lobby.LobbyScene",
    "lobby.btn_swallow_bottom",
    # 首次启动或弹窗恢复后，LobbyScene/侧边栏可能未被 Poco 暴露，补充大厅常驻入口做兜底。
    "lobby.setting",
    "lobby.middle",
    "lobby.eao",
    "lobby.btn_touch",
)
THEME_HOME_REQUIRED_PATHS = (
    "theme.theme_enter_btn",
    "theme.theme_spin",
    "theme.theme_label_win",
)
THEME_LOADING_PATHS = (
    "theme.theme_loading2",
)
THEME_SELECT_BLOCKING_PATHS = (
    "theme.theme_regular_enter_btn",
    "theme.theme_high_enter_btn",
    "theme.theme_touch_node",
)
SOCIAL_ROLE_CONFIRM_PATHS = (
    "theme.btn_node",
)
SOCIAL_MACHINE_INDEXES = tuple(range(8))
SOCIAL_MACHINE_PATHS = tuple(f"theme.machine_{index}" for index in SOCIAL_MACHINE_INDEXES)
SOCIAL_MACHINE_ALT_PATHS = tuple(f"theme.machine_alt_{index}" for index in SOCIAL_MACHINE_INDEXES)
SOCIAL_MACHINE_SELECT_PATHS = (
    "theme.enmoji_btn",
    "theme.emoji_btn",
    "theme.machine",
    "theme.machine_alt",
    *SOCIAL_MACHINE_PATHS,
    *SOCIAL_MACHINE_ALT_PATHS,
)
SOCIAL_MACHINE_CLOSE_PATHS = (
    "theme.social_close_btn",
    "common.btn_close",
)
QUICK_POPUP_CLOSE_PATHS = (
    "common.btn_close",
    "common.close_btn",
    "common.mask_close",
    "common.btn_collect",
)
LUA_ERROR_KEYWORDS = ("[Lua Error]", "Lua Error", "Char Error", "RESOURCE_ERROR")

game_actions = GameActions(poco)
state_machine = create_state_machine(poco)
current_theme_is_social = False


def elapsed_seconds(start_at, end_at=None):
    """格式化耗时，统一输出秒级性能日志。"""
    end_at = time.perf_counter() if end_at is None else end_at
    return f"{end_at - start_at:.2f}s"


def perf_log(label, start_at=None):
    """打印主题遍历性能时间点，用于定位设备检测、准备大厅和进入主题耗时。"""
    detail = f"total={elapsed_seconds(SCRIPT_START_AT)}"
    if start_at is not None:
        detail = f"cost={elapsed_seconds(start_at)} | {detail}"
    print(f"[PERF] {label} | {detail}")


def reset_poco_connection(reason=""):
    """应用冷启动后重建游戏 Poco 连接，避免旧 RPC 管道 Broken pipe。"""
    global poco, game_actions, state_machine
    try:
        poco = init_poco(dev, auto_refresh=False)
        CF_nodes.poco = poco
        game_actions = GameActions(poco)
        state_machine = create_state_machine(poco)
        print(f"已重建 Poco 连接：{reason or 'manual'}")
        return True
    except Exception as e:
        print(f"重建 Poco 连接失败：{reason or 'manual'} | {e}")
        return False


def adb_command(args, timeout=10):
    """执行 adb 命令，用于读取 logcat 中最近的 Lua/Char Error 现场。"""
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
        print(f"读取 adb 日志异常：{' '.join(args)} | {e}")
        return ""


def print_latest_lua_error_log():
    """从 logcat 中打印最近一次 Lua/Char Error 的关键上下文。"""
    logcat = adb_command(["logcat", "-d", "-v", "time"], timeout=10)
    lines = logcat.splitlines()
    ignore_keywords = ("poco-uiautomation-framework", '"attr.*="')
    error_indices = [
        index
        for index, line in enumerate(lines)
        if not any(keyword in line for keyword in ignore_keywords)
        and (
            "RESOURCE_ERROR" in line
            or "Char Error:" in line
            or "[Lua Error]" in line
            or "Lua Error" in line
        )
    ]
    if not error_indices:
        print("logcat 未找到 Lua Error / Char Error 相关日志")
        return False

    start = error_indices[-1]
    block = []
    for line in lines[start:start + 16]:
        if any(keyword in line for keyword in (
            "RESOURCE_ERROR",
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


def hierarchy_has_lua_error(hierarchy):
    """把控件树统一转成文本后查 Lua/Char Error 关键字。"""
    hierarchy_text = json.dumps(hierarchy, ensure_ascii=False, default=str)
    return any(keyword in hierarchy_text for keyword in LUA_ERROR_KEYWORDS)


def android_lua_error_message_text(android_poco):
    """读取 Android 原生弹窗 message 节点文本，用于记录完整 Lua Error 现场。"""
    try:
        message_node = android_poco("android:id/message")
        if message_node.exists():
            return message_node.get_text()
    except Exception as e:
        print(f"读取 Android Lua Error message 节点失败：{e}")
    return ""


def write_lua_error_message_log(message_text, screenshot_path=None):
    """把 Android 原生 Lua Error 的 message 原文落盘，方便批量遍历后回查。"""
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    log_path = RESULT_DIR / f"lua_error_message_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    screenshot_line = screenshot_path or "截图保存失败或未生成"
    # 日志顶部带上对应截图路径，批量遍历后可以直接定位弹窗现场。
    log_path.write_text(
        f"screenshot_path: {screenshot_line}\n\n{message_text}",
        encoding="utf-8",
    )
    print(f"Android Lua Error message 记录：{log_path}")
    return log_path


def close_android_lua_error_popup(android_poco):
    """Lua Error 现场记录完成后点击原生确认按钮，避免弹窗阻塞后续流程。"""
    try:
        close_button = android_poco("android:id/button1")
        if close_button.exists():
            close_button.click()
            print("已点击 Android Lua Error 弹窗关闭按钮：android:id/button1")
            return True
    except Exception as e:
        print(f"点击 Android Lua Error 弹窗关闭按钮失败：{e}")
    print("Android Lua Error 弹窗关闭按钮不存在：android:id/button1")
    return False


def check_lua_error_popup():
    """只检测 Android 原生 Lua/Char Error 弹窗，存在则记录 message 文本和现场信息。"""
    try:
        android_poco = get_android_poco()
        if not hierarchy_has_lua_error(android_poco.agent.hierarchy.dump()):
            return False
    except Exception as e:
        print(f"Android 原生 Lua Error 弹窗检查失败：{e}")
        return False

    screenshot_path = state_machine.capture_screen("lua_error_popup")
    print("检测到 Android 原生 Lua Error / Char Error 报错弹窗")
    message_text = android_lua_error_message_text(android_poco)
    if message_text:
        print("====================== Android Lua Error message ======================")
        print(message_text)
        print("=======================================================================")
        write_lua_error_message_log(message_text, screenshot_path)
    else:
        print("Android Lua Error message 节点未读取到文本")
    print_latest_lua_error_log()
    close_android_lua_error_popup(android_poco)
    return True


def sleep_with_lua_error_check(seconds, interval=1.0):
    """主题内停留时低频检查报错弹窗，避免错误只在停留阶段出现却漏掉。"""
    end_time = time.time() + seconds
    detected = False
    while time.time() < end_time:
        if not detected:
            detected = check_lua_error_popup()
        sleep(min(interval, max(0, end_time - time.time())))
    return detected or check_lua_error_popup()


print(
    "[PERF] 设备检测/Poco初始化完成 | "
    f"cost={elapsed_seconds(SCRIPT_START_AT, BOOTSTRAP_READY_AT)} | "
    f"total={elapsed_seconds(SCRIPT_START_AT, BOOTSTRAP_READY_AT)}"
)


class CFThemeTraversalTest(PocoTestCase):
    def setUp(self):
        self.tracker = ActionTracker(self)

    def test_traverse_theme_list(self):
        traverse_theme_list(THEME_IDS)

    def tearDown(self):
        self.tracker.stop()


def parse_theme_ids(raw_value):
    """把 122,123 或换行分隔的主题 ID 转成整数列表。"""
    if not raw_value:
        return []

    theme_ids = []
    for item in raw_value.replace("\n", ",").split(","):
        value = item.strip()
        if value:
            theme_ids.append(int(value))
    return theme_ids


def load_theme_ids(args):
    """读取运行时传入的主题列表；未传入时使用脚本内默认 THEME_IDS。"""
    if args.theme_ids:
        return parse_theme_ids(args.theme_ids)

    if args.theme_file:
        return parse_theme_ids(Path(args.theme_file).read_text(encoding="utf-8"))

    env_theme_ids = os.environ.get("CF_THEME_IDS")
    if env_theme_ids:
        return parse_theme_ids(env_theme_ids)

    return list(THEME_IDS)


def wait_for_lobby(timeout=10):
    """直接等待大厅关键节点出现，避免状态机反复遍历所有状态。"""
    return wait_for_any_path(
        LOBBY_HOME_PATHS,
        timeout=timeout,
        interval=0.5,
    )


def is_lobby_home():
    """快速判断当前是否在大厅，用于行为树动作后的结果校验。"""
    return any_path_exists(LOBBY_HOME_PATHS)


def is_theme_loading():
    """进入动作后 loading2 仍可见，表示主题还卡在 loading 阶段。"""
    return any_path_visible(THEME_LOADING_PATHS)


def is_theme_select_blocking():
    """判断是否还停留在主题选房界面，避免误把选房页节点当主题 Home。"""
    return any_path_exists(THEME_SELECT_BLOCKING_PATHS)


def is_theme_select_open():
    """判断 Lua 打开主题后是否真的弹出了选 bet 界面。"""
    return any_path_exists(THEME_SELECT_BLOCKING_PATHS)


def is_theme_home():
    """快速判断当前是否在主题 Home，用于避免只依赖点击返回值。"""
    return (
        all_paths_exist(THEME_HOME_REQUIRED_PATHS)
        and not is_theme_select_blocking()
    )


def all_paths_exist(paths):
    """判断一组节点是否全部存在；节点异常按不存在处理。"""
    return all(path_exists(path) for path in paths)


def any_path_exists(paths):
    """判断任一节点是否存在；用于过滤 loading/选 bet 中间态。"""
    return any(path_exists(path) for path in paths)


def any_path_visible(paths):
    """判断任一节点是否可见；用于识别 loading2 还停留在屏幕上的异常状态。"""
    return any(path_visible(path) for path in paths)


def path_exists(path):
    """安全检查节点存在性，避免 Poco 临时异常打断等待循环。"""
    try:
        return game_actions.node(path).exists()
    except Exception:
        return False


def path_visible(path):
    """读取节点 visible 属性；属性不可用时退回 exists，兼容不同 Poco 节点实现。"""
    try:
        node = game_actions.node(path)
        if not node.exists():
            return False
        visible = node_visible_attr(node)
        return path_exists(path) if visible is None else normalize_visible(visible)
    except Exception:
        return False


def normalize_visible(value):
    """把 Poco 可能返回的布尔、数字或字符串 visible 值统一成 bool。"""
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "none"}
    return bool(value)


def node_visible_attr(node):
    """兼容 Poco 的 attr/get_attr 两种属性读取方式。"""
    for getter_name in ("attr", "get_attr"):
        getter = getattr(node, getter_name, None)
        if not getter:
            continue
        try:
            return getter("visible")
        except Exception:
            continue
    return None


def wait_for_any_path(paths, timeout, interval=0.5):
    """等待任一节点出现；只查指定节点，保证遍历速度。"""
    end_time = datetime.now().timestamp() + timeout
    while datetime.now().timestamp() < end_time:
        for path in paths:
            if path_exists(path):
                return True
        sleep(interval)
    return False


def social_machine_path_candidates():
    """按配置机台优先，其余机台兜底的顺序返回社交主题机台节点。"""
    if SOCIAL_THEME_MACHINE_INDEX in SOCIAL_MACHINE_INDEXES:
        ordered_indexes = [SOCIAL_THEME_MACHINE_INDEX]
    else:
        print(f"社交主题机台序号无效，改用 0 号机台：{SOCIAL_THEME_MACHINE_INDEX}")
        ordered_indexes = [0]

    ordered_indexes.extend(
        index
        for index in SOCIAL_MACHINE_INDEXES
        if index not in ordered_indexes
    )
    candidates = []
    for index in ordered_indexes:
        candidates.append(f"theme.machine_{index}")
        candidates.append(f"theme.machine_alt_{index}")
    return tuple(candidates)


def click_first_available_path(paths, label):
    """点击第一条存在的节点路径，用于社交主题中间页的可选分支。"""
    for path in paths:
        try:
            if not path_exists(path):
                continue
            if game_actions.click(path, timeout=1):
                print(f"{label} 点击成功：{path}")
                return True
        except Exception as e:
            print(f"{label} 点击异常：{path} | {e}")
    print(f"{label} 未找到可点击节点：{list(paths)}")
    return False


def click_social_role_confirm_if_present(timeout=SOCIAL_THEME_ROLE_CONFIRM_TIMEOUT):
    """社交主题优先处理角色确认；等待不到时允许直接进入机台选择。"""
    if wait_for_any_path(SOCIAL_ROLE_CONFIRM_PATHS, timeout=timeout, interval=0.3):
        return click_first_available_path(SOCIAL_ROLE_CONFIRM_PATHS, "社交主题角色确认")
    print(f"社交主题未出现角色确认，直接进入机台选择：wait={timeout}s")
    return None


def handle_social_theme_enter_flow(timeout=SOCIAL_THEME_FLOW_TIMEOUT):
    """处理社交主题从选 bet 后额外出现的角色确认和机台选择流程。"""
    global current_theme_is_social
    end_time = time.time() + timeout
    handled_social_step = False

    while time.time() < end_time:
        if is_theme_home() or is_theme_loading():
            return True

        if any_path_exists(SOCIAL_ROLE_CONFIRM_PATHS):
            # 社交主题会先进入角色选择页，必须确认后才会展示机台列表。
            handled_social_step = True
            current_theme_is_social = True
            if click_social_role_confirm_if_present(timeout=0.1) is False:
                return False
            sleep(0.5)
            continue

        if any_path_exists(SOCIAL_MACHINE_SELECT_PATHS):
            # 机台节点可能比角色确认更早暴露，先补等角色确认；没有确认页时再直接选机台。
            handled_social_step = True
            current_theme_is_social = True
            role_clicked = click_social_role_confirm_if_present()
            if role_clicked:
                sleep(0.5)
                continue
            if role_clicked is False:
                return False
            # 高级房进入后机台页可能先露节点但仍在 loading，先等界面稳定再点机台。
            print(f"社交主题选择机台前等待 loading 过渡：{SOCIAL_THEME_BEFORE_MACHINE_CLICK_DELAY}s")
            sleep(SOCIAL_THEME_BEFORE_MACHINE_CLICK_DELAY)
            if not click_first_available_path(social_machine_path_candidates(), "社交主题机台选择"):
                return False
            return True

        sleep(0.3)

    if handled_social_step:
        print("社交主题中间流程超时，可能停留在角色选择或机台选择界面")
        return False
    return True


def handle_social_theme_return_flow(timeout=SOCIAL_THEME_RETURN_TIMEOUT):
    """社交主题返回会先回机台选择页，需要再点一次关闭才会回到大厅。"""
    end_time = time.time() + timeout
    while time.time() < end_time:
        if is_lobby_home():
            return True

        if any_path_exists(SOCIAL_MACHINE_SELECT_PATHS) or any_path_exists(SOCIAL_MACHINE_CLOSE_PATHS):
            if click_first_available_path(SOCIAL_MACHINE_CLOSE_PATHS, "社交主题机台页关闭"):
                sleep(0.5)
                return True
            return False

        sleep(0.3)

    print("社交主题返回后未等到机台选择页关闭按钮，交回行为树继续判断")
    return True


def resolve_cf_app_package():
    """优先使用环境变量包名，未配置时尝试读取当前前台游戏包名。"""
    env_package = os.environ.get("CF_APP_PACKAGE")
    if env_package:
        return env_package

    try:
        top_activity = dev.get_top_activity()
        if isinstance(top_activity, (tuple, list)) and top_activity:
            return top_activity[0]
        if top_activity:
            return str(top_activity).split("/", 1)[0]
    except Exception as e:
        print(f"读取前台包名失败，使用默认 CF 包名：{e}")

    return DEFAULT_CF_APP_PACKAGE


def restart_game():
    """主题 loading 卡住时冷重启游戏，保证下一个主题从干净大厅状态开始。"""
    app_package = resolve_cf_app_package()
    log(f"==== restart app: {app_package} ====")
    try:
        stop_app(app_package)
        sleep(1)
        start_app(app_package)
        sleep(3)
        reset_poco_connection("app restarted before launch confirm")
        click_launch_confirm_button(timeout=LAUNCH_CONFIRM_TIMEOUT)
        sleep(APP_RESTART_WAIT_SECONDS)
        reset_poco_connection("app restarted before lobby wait")
        return wait_for_lobby(timeout=10)
    except Exception as e:
        print(f"重启游戏失败：{app_package} | {e}")
        return False


def click_launch_confirm_button(timeout=LAUNCH_CONFIRM_TIMEOUT):
    """处理 debug 启动页 Confirm 按钮，默认用相对坐标避免图片误识别。"""
    if LAUNCH_CONFIRM_TAP:
        relative_point = parse_relative_point(LAUNCH_CONFIRM_TAP)
        if relative_point:
            tap_relative(relative_point, f"launch confirm default {LAUNCH_CONFIRM_TAP}")
            sleep(1)
            if wait_for_lobby(timeout=5):
                print("启动页坐标点击成功：已进入大厅")
            else:
                print("已点击启动页默认坐标，后续等待大厅流程继续确认")
            return True
    print("启动页默认坐标未配置或格式错误，未执行点击")
    return False


def parse_relative_point(raw_value):
    """解析 x,y 相对坐标，取值范围 0~1。"""
    try:
        x_value, y_value = [float(item.strip()) for item in raw_value.split(",", 1)]
    except ValueError:
        print(f"启动页坐标格式错误：{raw_value}，应为 x,y，例如 0.5,0.4")
        return None
    if not 0 <= x_value <= 1 or not 0 <= y_value <= 1:
        print(f"启动页坐标超出范围：{raw_value}，x/y 应在 0~1 之间")
        return None
    return x_value, y_value


def tap_relative(relative_point, label):
    """按屏幕比例点击启动页按钮，适配不同分辨率。"""
    width, height = dev.get_current_resolution()
    point = (int(width * relative_point[0]), int(height * relative_point[1]))
    touch(point)
    print(f"已点击启动页坐标：{label} -> {point}")


def create_theme_traversal_tree():
    """创建主题遍历专用行为树，把点击动作和目标状态校验串起来。"""
    callbacks = ThemeTraversalCallbacks(
        is_theme_home=is_theme_home,
        is_theme_loading=is_theme_loading,
        is_lobby_home=is_lobby_home,
        detect_state=lambda: state_machine.detect_state(),
        recover_blockers=quick_recover_blockers,
        close_popups=quick_recover_blockers,
        dump_unknown=lambda reason: state_machine.dump_unknown(reason),
        open_theme_select=open_lobby_theme_select,
        click_high_enter=click_theme_high_enter_button,
        click_return_lobby=click_theme_return_button,
        check_lua_error=check_lua_error_popup,
    )
    return ThemeTraversalTree(
        callbacks,
        interval=0.5,
        state_check_interval=THEME_POPUP_CHECK_INTERVAL,
        popup_recover_tries=THEME_POPUP_RECOVER_TRIES,
        expected_stable_seconds=THEME_HOME_STABLE_SECONDS,
    )


def open_lobby_theme_select(theme_id):
    """通过 Lua 打开主题选房界面；未弹出时按主题未配置状态处理。"""
    started_at = time.perf_counter()
    lua_result = game_actions.click_lobby_theme(theme_id)
    perf_log(f"Lua打开主题选房完成 theme_id={theme_id}", started_at)
    # 主题 bet 界面打开后、高级房点击前先查一次 Lua Error，避免原生错误弹窗遮挡入口。
    check_lua_error_popup()
    if wait_for_any_path(
        THEME_SELECT_BLOCKING_PATHS,
        timeout=THEME_SELECT_OPEN_TIMEOUT,
        interval=0.5,
    ):
        print(f"主题选 bet 界面已出现：theme_id={theme_id}")
        return True

    # 部分主题没有初始化配置时 Lua 不会弹选 bet 窗，仍停留大厅；这里显式返回失败让主流程跳过。
    check_lua_error_popup()
    current_state = state_machine.detect_state(verbose=True)
    if is_lobby_home():
        print(
            f"主题选 bet 未弹出，按主题未配置跳过：theme_id={theme_id} "
            f"state={current_state.name} lua_result={lua_result}"
        )
    else:
        print(
            f"主题选 bet 未弹出，当前状态非大厅：theme_id={theme_id} "
            f"state={current_state.name} lua_result={lua_result}"
        )
    return False


def enter_theme(theme_id):
    """进入主题：返回 success/no_config/enter_failed，便于主流程快速分流。"""
    # 进入动作前优先处理 Android 原生 Lua Error，避免错误弹窗遮挡选房/进入按钮。
    check_lua_error_popup()
    return create_theme_traversal_tree().enter_theme(theme_id, timeout=THEME_LOAD_TIMEOUT)


def click_theme_high_enter_button(timeout=THEME_SELECT_TIMEOUT):
    """点击主题选 bet 界面的高级房进入按钮；配置异常时用 Poco 路径兜底。"""
    started_at = time.perf_counter()
    try:
        node = game_actions.node("theme.theme_high_enter_btn")
        if game_actions.wait_for_node(node, timeout=timeout):
            clicked = game_actions.click_node(node, timeout=2)
            if clicked and not handle_social_theme_enter_flow():
                print("高级房点击后社交主题进入流程处理失败")
                perf_log("点击高级房按钮完成 result=False social_flow", started_at)
                return False
            perf_log(f"点击高级房按钮完成 result={clicked}", started_at)
            return clicked
    except KeyError as e:
        print(f"高级房进入按钮配置读取失败，尝试 Poco 兜底路径：{e}")
    except Exception as e:
        print(f"点击高级房进入按钮异常，尝试 Poco 兜底路径：{e}")

    try:
        end_time = datetime.now().timestamp() + timeout
        node = poco("theme_node").child("play_btn_high").child("btn_label")
        while datetime.now().timestamp() < end_time:
            if node.exists():
                node.click()
                if not handle_social_theme_enter_flow():
                    print("高级房兜底点击后社交主题进入流程处理失败")
                    perf_log("点击高级房按钮完成 result=False fallback social_flow", started_at)
                    return False
                print("点击高级房进入按钮成功：poco fallback")
                perf_log("点击高级房按钮完成 result=True fallback", started_at)
                return True
            sleep(0.5)
    except Exception as e:
        print(f"点击高级房进入按钮失败：{e}")
    perf_log("点击高级房按钮完成 result=False", started_at)
    return False


def prepare_lobby_for_theme(theme_id):
    """每次 RunLua 前确认当前在大厅，避免在 loading/主题内误触发下一个主题。"""
    if wait_for_lobby(timeout=LOBBY_PREPARE_TIMEOUT):
        return True

    close_common_popups()
    if wait_for_lobby(timeout=LOBBY_PREPARE_TIMEOUT):
        return True

    print(f"进入主题前未回到大厅，记录现场后跳过：theme_id={theme_id}")
    state_machine.dump_unknown(f"theme_{theme_id}_lobby_prepare_failed")
    return False


def quick_recover_blockers(max_tries=2):
    """行为树循环内的轻量弹窗恢复：只查常见关闭节点，不跑完整状态机。"""
    recovered = False
    for _ in range(max_tries):
        clicked = False
        for path in QUICK_POPUP_CLOSE_PATHS:
            try:
                node = game_actions.node(path)
                if node.exists():
                    node.click()
                    print(f"快速关闭弹窗：{path}")
                    sleep(0.2)
                    clicked = True
                    recovered = True
            except Exception:
                continue
        if not clicked:
            break
    return recovered


def close_common_popups(max_tries=3):
    """关闭通用弹窗，优先用状态机识别，再用节点兜底补点关闭按钮。"""
    closed = False
    check_lua_error_popup()
    try:
        closed = state_machine.recover_blockers(max_tries=max_tries) or closed
    except Exception as e:
        print(f"状态机清理弹窗异常，继续使用通用关闭兜底：{e}")

    if not closed:
        try:
            closed = game_actions.close_all_common_popups(max_tries=max_tries) or closed
        except Exception as e:
            print(f"通用关闭弹窗异常，继续流程：{e}")

    if closed:
        sleep(0.5)
    return closed


def close_theme_popups(theme_id):
    """进入主题后先清理弹窗，保证返回大厅按钮可以被点击。"""
    # 关闭主题/返回大厅前优先记录并关闭 Lua Error，避免普通弹窗恢复误判。
    check_lua_error_popup()
    if quick_recover_blockers(max_tries=4):
        print(f"已清理主题内弹窗：theme_id={theme_id}")


def spin_before_return_lobby(theme_id, count=SPIN_BEFORE_RETURN_COUNT):
    """返回大厅前先点击指定次数 spin，覆盖主题内基础转动流程。"""
    completed = True
    for index in range(1, count + 1):
        # 每次点击后短暂等待，给 spin 按钮恢复可点和动画触发留出时间。
        try:
            clicked = game_actions.click("theme.theme_spin", timeout=3)
        except Exception as e:
            clicked = False
            print(f"返回大厅前第 {index}/{count} 次 spin 异常：theme_id={theme_id} | {e}")

        if clicked:
            print(f"返回大厅前第 {index}/{count} 次 spin 成功：theme_id={theme_id}")
        else:
            print(f"返回大厅前第 {index}/{count} 次 spin 未点击成功：theme_id={theme_id}")
            completed = False
        sleep(SPIN_BEFORE_RETURN_INTERVAL)
    return completed


def return_to_lobby(theme_id):
    """点击主题内返回大厅按钮；失败后清理一次现场并重试，减少残留页面影响下个主题。"""
    attempts = max(1, LOBBY_RETURN_RETRY_COUNT + 1)
    for attempt in range(1, attempts + 1):
        if attempt > 1:
            print(f"返回大厅第 {attempt}/{attempts} 次重试：theme_id={theme_id}")

        if create_theme_traversal_tree().return_to_lobby(theme_id, timeout=LOBBY_RETURN_TIMEOUT):
            return True

        if is_lobby_home():
            print(f"返回大厅重试前已检测到大厅：theme_id={theme_id}")
            return True

        if attempt < attempts:
            # 返回失败时先清理一次可能遮挡返回按钮的弹窗，再重新走返回行为树。
            print(f"返回大厅失败，清理阻塞后准备重试：theme_id={theme_id}")
            check_lua_error_popup()
            quick_recover_blockers(max_tries=THEME_POPUP_RECOVER_TRIES)
            close_common_popups(max_tries=2)
            sleep(LOBBY_RETURN_RETRY_DELAY)

    return False


def click_theme_return_button():
    """点击主题返回大厅按钮；节点配置不可用时使用同路径 Poco 兜底。"""
    try:
        if game_actions.click("theme.theme_enter_btn", timeout=5):
            if current_theme_is_social:
                return handle_social_theme_return_flow()
            return True
    except KeyError as e:
        print(f"主题返回按钮配置读取失败，尝试 Poco 兜底路径：{e}")

    try:
        node = poco("header").child("lobby_node").child("enter_btn")
        if node.exists():
            node.click()
            print("点击主题返回大厅按钮成功：poco fallback")
            if current_theme_is_social:
                return handle_social_theme_return_flow()
            return True
    except Exception as e:
        print(f"点击主题返回大厅按钮失败：{e}")
    return False


def write_theme_ids(filename_prefix, theme_ids, label):
    """把特定分类的主题 ID 落盘，便于测试结束后回归排查。"""
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    result_path = RESULT_DIR / f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    result_path.write_text(
        "\n".join(str(theme_id) for theme_id in theme_ids),
        encoding="utf-8",
    )
    print(f"{label}记录：{result_path}")
    return result_path


def traverse_theme_list(theme_ids, stay_seconds=DEFAULT_STAY_SECONDS):
    """按列表顺序遍历主题：记录准备大厅或进入主题失败的主题。"""
    global current_theme_is_social
    failed_theme_ids = []

    for index, theme_id in enumerate(theme_ids, start=1):
        current_theme_is_social = False
        theme_started_at = time.perf_counter()
        log(f"==== theme traversal {index}/{len(theme_ids)}: {theme_id} ====")
        perf_log(f"开始主题遍历 {index}/{len(theme_ids)} theme_id={theme_id}")

        prepare_started_at = time.perf_counter()
        if not prepare_lobby_for_theme(theme_id):
            perf_log(f"准备大厅失败 theme_id={theme_id}", prepare_started_at)
            failed_theme_ids.append(theme_id)
            continue
        perf_log(f"准备大厅完成 theme_id={theme_id}", prepare_started_at)

        enter_started_at = time.perf_counter()
        perf_log(f"开始执行进入主题 theme_id={theme_id}")
        enter_result = enter_theme(theme_id)
        perf_log(f"进入主题结束 theme_id={theme_id} result={enter_result}", enter_started_at)
        if enter_result == "no_config":
            print(f"主题入口或选 bet 界面未出现，跳过：theme_id={theme_id}")
            perf_log(f"结束主题遍历 theme_id={theme_id}", theme_started_at)
            continue
        if enter_result == "loading_stuck":
            failed_theme_ids.append(theme_id)
            print(f"主题 loading2 卡死，重启后继续下一个主题：theme_id={theme_id}")
            restart_game()
            perf_log(f"结束主题遍历 theme_id={theme_id}", theme_started_at)
            continue
        if enter_result == "enter_failed":
            failed_theme_ids.append(theme_id)
            perf_log(f"结束主题遍历 theme_id={theme_id}", theme_started_at)
            continue

        if stay_seconds > 0:
            sleep_with_lua_error_check(stay_seconds)
        close_theme_popups(theme_id)
        spin_before_return_lobby(theme_id)

        return_started_at = time.perf_counter()
        if not return_to_lobby(theme_id):
            perf_log(f"返回大厅失败 theme_id={theme_id}", return_started_at)
            print(f"主题返回大厅重试后仍失败，交给下一个主题的大厅准备检查：theme_id={theme_id}")
        else:
            perf_log(f"返回大厅完成 theme_id={theme_id}", return_started_at)
        perf_log(f"结束主题遍历 theme_id={theme_id}", theme_started_at)

    write_theme_ids("failed_theme_ids", failed_theme_ids, "进入失败主题")
    return failed_theme_ids


def build_arg_parser():
    parser = argparse.ArgumentParser(description="遍历 CF 主题列表，记录进入失败的主题 ID。")
    parser.add_argument("--theme-ids", default="", help="逗号分隔主题 ID，例如 122,123,124")
    parser.add_argument("--theme-file", default="", help="主题 ID 文件，支持逗号或换行分隔")
    parser.add_argument("--stay-seconds", type=int, default=DEFAULT_STAY_SECONDS, help="进入主题后停留秒数，默认不额外停留")
    return parser


if __name__ == "__main__":
    log("==== start CF theme traversal ====")
    args = build_arg_parser().parse_args()
    selected_theme_ids = load_theme_ids(args)
    traverse_theme_list(selected_theme_ids, stay_seconds=args.stay_seconds)
    log("==== end CF theme traversal ====")