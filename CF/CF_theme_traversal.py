#!/usr/bin/env python3
# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from airtest.core.api import log, sleep, start_app, stop_app, touch
from pocounit.addons.poco.action_tracking import ActionTracker
from pocounit.case import PocoTestCase

# 导入公共初始化模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, dev, poco

# 导入节点和状态机
import CF_nodes
from CF_nodes import GameActions
from CF_state_machine import create_state_machine


ST.SAVE_IMAGE = True

# 同步公共初始化里的 Poco，保证状态机和节点模块用同一个连接。
CF_nodes.poco = poco

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "log" / "theme_traversal"
DEFAULT_CF_APP_PACKAGE = "com.spinX.casino.cashfrenzy"

# 默认遍历列表：需要验证更多主题时直接补充这里，或运行时用 --theme-ids 覆盖。
THEME_IDS = [
  101, 102, 103, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
  120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137,
  138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155,
  156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173,
  174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191,
  192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209,
  210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227,
  228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245,
  246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263,
  264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281,
  282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299,
  300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317,
  318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335,
  336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353,
  354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371,
  372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389,
  390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407,
  408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425,
  426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443,
  444, 446, 447, 448, 449, 450,
  
  2001, 2002, 2003, 2004, 2005, 2006, 2007, 2019, 2020,
  3128, 3137, 3139, 3142,
  4200, 4204,
  
  10451, 10452, 10454, 10455, 10456, 10458, 10459, 10461, 10462, 10465, 10467, 10468, 10469,
  10470, 10471, 10472, 10473, 10474, 10475, 10476, 10477, 10479, 10480, 10481, 10482, 10483,
  10485, 10486, 10487, 10488, 10489, 10491, 10492, 10493, 10494, 10496, 10497,
  10503, 10505, 10506, 10511, 10513, 10514, 10516, 10517, 10518, 10519, 10520, 10521, 10523,
  10524, 10525, 10526, 10527, 10528, 10529, 10530, 10531, 10532, 10533, 10536, 10537, 10541,
  10546, 10547,
]

THEME_LOAD_TIMEOUT = 35
THEME_SELECT_TIMEOUT = 15
LOBBY_RETURN_TIMEOUT = 20
APP_RESTART_WAIT_SECONDS = 15
LAUNCH_CONFIRM_TIMEOUT = 15
LAUNCH_CONFIRM_TAP = os.environ.get("CF_LAUNCH_CONFIRM_TAP", "0.500,0.400").strip()
DEFAULT_STAY_SECONDS = 15

game_actions = GameActions(poco)
state_machine = create_state_machine(poco)


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


def wait_for_lobby(timeout=30):
    """直接等待大厅关键节点出现，避免状态机反复遍历所有状态。"""
    return wait_for_any_path(
        ("lobby.setting", "lobby.middle"),
        timeout=timeout,
        interval=0.5,
    )


def wait_for_theme_home(timeout=THEME_LOAD_TIMEOUT):
    """直接等待主题页关键节点出现，用于判断主题已经进入成功。"""
    return wait_for_any_path(
        ("theme.theme_enter_btn", "theme.theme_bet_label", "theme.theme_label_win"),
        timeout=timeout,
        interval=0.5,
    )


def wait_for_any_path(paths, timeout, interval=0.5):
    """等待任一节点出现；只查指定节点，保证遍历速度。"""
    end_time = datetime.now().timestamp() + timeout
    while datetime.now().timestamp() < end_time:
        for path in paths:
            try:
                if game_actions.node(path).exists():
                    return True
            except Exception:
                pass
        sleep(interval)
    return False


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
        click_launch_confirm_button(timeout=LAUNCH_CONFIRM_TIMEOUT)
        sleep(APP_RESTART_WAIT_SECONDS)
        return wait_for_lobby(timeout=45)
    except Exception as e:
        print(f"重启游戏失败：{app_package} | {e}")
        return False


def click_launch_confirm_button(timeout=LAUNCH_CONFIRM_TIMEOUT):
    """处理 debug 启动页 Confirm 按钮，优先用坐标点击避免图片识别点偏移。"""
    if LAUNCH_CONFIRM_TAP:
        relative_point = parse_relative_point(LAUNCH_CONFIRM_TAP)
        if relative_point:
            tap_relative(relative_point, f"launch confirm {LAUNCH_CONFIRM_TAP}")
            return True

    try:
        node = game_actions.node("common.Confirm_btn")
        if game_actions.wait_for_node(node, timeout=timeout):
            return game_actions.click_node(node, timeout=2)
    except KeyError as e:
        print(f"启动页 Confirm 配置读取失败：{e}")
    except Exception as e:
        print(f"点击启动页 Confirm 异常：{e}")
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


def enter_theme(theme_id):
    """进入主题：返回 success/no_config/load_failed，便于主流程快速分流。"""
    if not click_lobby_theme_and_enter_regular_room(theme_id):
        return "no_config"

    if wait_for_theme_home(timeout=THEME_LOAD_TIMEOUT):
        return "success"

    state_machine.dump_unknown(f"theme_{theme_id}_load_timeout")
    return "load_failed"


def click_lobby_theme_and_enter_regular_room(theme_id):
    """Lua 打开主题选 bet 界面后，点击低级房进入按钮才会真正进入主题。"""
    game_actions.click_lobby_theme(theme_id)
    if not click_theme_regular_enter_button(timeout=THEME_SELECT_TIMEOUT):
        print(f"主题未配置或无低级房入口，跳过：theme_id={theme_id}")
        return False
    return True


def click_theme_regular_enter_button(timeout=THEME_SELECT_TIMEOUT):
    """点击主题选 bet 界面的低级房进入按钮；配置异常时用 Poco 路径兜底。"""
    try:
        node = game_actions.node("theme.theme_regular_enter_btn")
        if game_actions.wait_for_node(node, timeout=timeout):
            return game_actions.click_node(node, timeout=2)
    except KeyError as e:
        print(f"低级房进入按钮配置读取失败，尝试 Poco 兜底路径：{e}")
    except Exception as e:
        print(f"点击低级房进入按钮异常，尝试 Poco 兜底路径：{e}")

    try:
        end_time = datetime.now().timestamp() + timeout
        node = poco("theme_node").child("play_btn_regular").child("btn_label")
        while datetime.now().timestamp() < end_time:
            if node.exists():
                node.click()
                print("点击低级房进入按钮成功：poco fallback")
                return True
            sleep(0.5)
    except Exception as e:
        print(f"点击低级房进入按钮失败：{e}")
    return False


def return_to_lobby(theme_id):
    """点击主题内返回大厅按钮，并用大厅关键节点确认返回成功。"""
    if not click_theme_return_button():
        state_machine.dump_unknown(f"theme_{theme_id}_return_button_missing")
        return False

    if wait_for_lobby(timeout=LOBBY_RETURN_TIMEOUT):
        return True

    state_machine.dump_unknown(f"theme_{theme_id}_return_lobby_timeout")
    return False


def click_theme_return_button():
    """点击主题返回大厅按钮；节点配置不可用时使用同路径 Poco 兜底。"""
    try:
        if game_actions.click("theme.theme_enter_btn", timeout=5):
            return True
    except KeyError as e:
        print(f"主题返回按钮配置读取失败，尝试 Poco 兜底路径：{e}")

    try:
        node = poco("header").child("lobby_node").child("enter_btn")
        if node.exists():
            node.click()
            print("点击主题返回大厅按钮成功：poco fallback")
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
    """按列表顺序遍历主题：未配置直接跳过，loading 超时才重启。"""
    failed_loading_theme_ids = []
    unconfigured_theme_ids = []

    for index, theme_id in enumerate(theme_ids, start=1):
        log(f"==== theme traversal {index}/{len(theme_ids)}: {theme_id} ====")
        enter_result = enter_theme(theme_id)
        if enter_result == "no_config":
            unconfigured_theme_ids.append(theme_id)
            continue
        if enter_result == "load_failed":
            failed_loading_theme_ids.append(theme_id)
            restart_game()
            continue

        sleep(stay_seconds)

        if not return_to_lobby(theme_id):
            print(f"主题返回大厅失败，重启后继续下一个主题：theme_id={theme_id}")
            restart_game()

    write_theme_ids("failed_loading_theme_ids", failed_loading_theme_ids, "loading 失败主题")
    write_theme_ids("unconfigured_theme_ids", unconfigured_theme_ids, "未配置主题")
    return failed_loading_theme_ids


def build_arg_parser():
    parser = argparse.ArgumentParser(description="遍历 CF 主题列表，记录 loading 卡住的主题 ID。")
    parser.add_argument("--theme-ids", default="", help="逗号分隔主题 ID，例如 122,123,124")
    parser.add_argument("--theme-file", default="", help="主题 ID 文件，支持逗号或换行分隔")
    parser.add_argument("--stay-seconds", type=int, default=DEFAULT_STAY_SECONDS, help="进入主题后停留秒数")
    return parser


if __name__ == "__main__":
    log("==== start CF theme traversal ====")
    args = build_arg_parser().parse_args()
    selected_theme_ids = load_theme_ids(args)
    traverse_theme_list(selected_theme_ids, stay_seconds=args.stay_seconds)
    log("==== end CF theme traversal ====")
