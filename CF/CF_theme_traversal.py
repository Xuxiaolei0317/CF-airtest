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
      122,
      340,
      276,
      255,
      326,
      331,
      10468,
      366,
      101,
      244,
      386,
      107,
      321,
      141,
      181,
      388,
      125,
      295,
      208,
      213,
      363,
      396,
      406,
      114,
      346,
      176,
      217,
      413,
      204,
      361,
      416,
      372,
      257,
      399,
      180,
      108,
      203,
      241,
      341,
      411,
      202,
      118,
      370,
      124,
      157,
      209,
      427,
      350,
      308,
      239,
      177,
      111,
      248,
      391,
      192,
      289,
      436,
      263,
      421,
      357,
      253,
      200,
      163,
      410,
      102,
      126,
      375,
      332,
      232,
      381,
      227,
      166,
      424,
      353,
      405,
      274,
      270,
      425,
      356,
      105,
      251,
      407,
      351,
      292,
      402,
      299,
      404,
      103,
      338,
      376,
      250,
      398,
      115,
      165,
      394,
      378,
      344,
      212,
      127,
      10469,
      392,
      272,
      303,
      128,
      195,
      10452,
      368,
      374,
      106,
      199,
      349,
      313,
      367,
      117,
      249,
      297,
      190,
      401,
      329,
      260,
      173,
      109,
      140,
      278,
      319,
      354,
      383,
      233,
      256,
      327,
      412,
      271,
      390,
      380,
      335,
      328,
      113,
      193,
      385,
      224,
      426,
      262,
      431,
      284,
      110,
      382,
      218,
      362,
      311,
      148,
      358,
      283,
      147,
      291,
      418,
      281,
      296,
      345,
      379,
      129,
      130,
      132,
      240,
      143,
      415,
      287,
      207,
      339,
      377,
      397,
      228,
      191,
      196,
      286,
      342,
      314,
      121,
      235,
      268,
      408,
      384,
      245,
      307,
      229,
      236,
      317,
      119,
      188,
      277,
      429,
      123,
      168,
      323,
      309,
      373,
      210,
      280,
      409,
      365,
      324,
      112,
      187,
      273,
      318,
      136,
      167,
      258,
      310,
      422,
      206,
      423,
      220,
      265,
      316,
      371,
      144,
      252,
      10470,
      438,
      10477,
      264,
      138,
      175,
      355,
      158,
      387,
      389,
      352,
      275,
      238,
      325,
      420,
      116,
      134,
      211,
      194,
      395,
      160,
      444,
      432,
      440,
      149,
      347,
      315,
      221,
      172,
      242,
      234,
      359,
      267,
      219,
      330,
      182,
      247,
      185,
      214,
      145,
      294,
      333,
      300,
      360,
      322,
      298,
      150,
      137,
      259,
      414,
      439,
      442,
      197,
      146,
      164,
      169,
      320,
      139,
      152,
      189,
      243,
      285,
      334,
      449,
      443,
      417,
      198,
      279,
      174,
      170,
      10474,
      135,
      269,
      282,
      131,
      222,
      348,
      10471,
      428,
      154,
      171,
      179,
      337,
      261,
      400,
      403,
      369,
      302,
      290,
      230,
      305,
      162,
      433,
      446,
      343,
      205,
      186,
      266,
      225,
      10486,
      201,
      153,
      178,
      10489,
      435,
      306,
      223,
      336,
      441,
      231,
      215,
      183,
      393,
      216,
      434,
      246,
      161,
      237,
      304,
      10472,
      10475,
      293,
      254,
      184,
      226,
      301,
      419,
      288,
      364,
      133,
      159,
      312,
      142,
      10458,
      10503,
      10456,
      10462,
      10451,
      447,
      156,
      10465,
      450,
      430,
      10505,
      10476,
      10506,
      10513,
      448,
      10514,
      10479,
      10487,
      10491,
      10459,
      10480,
      10483,
      10485,
      437,
      10455,
      10488,
      10494,
      10496,
      10492,
      10493,
      10518,
      10516,
      10521,
      10520,
      10482,
      10461,
      10454,
      10481,
      10523,
      10547,
      10536,
      10528,
      10525,
      10527,
      10473,
      10517,
      10519,
      10497,
      10511,
      10537,
      10524,
      10546,
      10530,
      10532,
      10529,
      10467,
      10531,
      4200,
      120,
      151,
      155,
      4204,
      2001,
      2002,
      2003
    ]

THEME_LOAD_TIMEOUT = int(os.environ.get("CF_THEME_LOAD_TIMEOUT", "90"))
THEME_SELECT_TIMEOUT = 15
LOBBY_RETURN_TIMEOUT = 20
LOBBY_PREPARE_TIMEOUT = 8
APP_RESTART_WAIT_SECONDS = 15
LAUNCH_CONFIRM_TIMEOUT = 15
LAUNCH_CONFIRM_TAP = os.environ.get("CF_LAUNCH_CONFIRM_TAP", "0.500,0.400").strip()
DEFAULT_STAY_SECONDS = 15
THEME_HOME_STABLE_SECONDS = 1.5
THEME_HOME_REQUIRED_PATHS = (
    "theme.theme_enter_btn",
    "theme.theme_bet_label",
    "theme.theme_label_win",
)
THEME_LOADING_PATHS = (
    "theme.theme_loading_progress",
    "theme.theme_loading_progress_label",
    "theme.theme_loading_icon_progress",
)
THEME_SELECT_BLOCKING_PATHS = (
    "theme.theme_regular_enter_btn",
    "theme.theme_high_enter_btn",
    "theme.theme_touch_node",
)

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
    """等待主题下载/loading 结束，并确认真正进入主题 Home。"""
    end_time = datetime.now().timestamp() + timeout
    stable_start = None

    while datetime.now().timestamp() < end_time:
        if is_theme_loading_or_selecting():
            stable_start = None
            sleep(0.5)
            continue

        # Home 关键节点需要同时存在并保持一小段时间，避免 loading 过渡帧误判。
        if all_paths_exist(THEME_HOME_REQUIRED_PATHS):
            current_time = datetime.now().timestamp()
            if stable_start is None:
                stable_start = current_time
            if current_time - stable_start >= THEME_HOME_STABLE_SECONDS:
                return True
        else:
            stable_start = None

        sleep(0.5)

    return False


def is_theme_loading_or_selecting():
    """识别主题下载/loading 或选 bet 页，存在时不能执行下一个 RunLua。"""
    return any_path_exists(THEME_LOADING_PATHS) or any_path_exists(THEME_SELECT_BLOCKING_PATHS)


def all_paths_exist(paths):
    """判断一组节点是否全部存在；节点异常按不存在处理。"""
    return all(path_exists(path) for path in paths)


def any_path_exists(paths):
    """判断任一节点是否存在；用于过滤 loading/选 bet 中间态。"""
    return any(path_exists(path) for path in paths)


def path_exists(path):
    """安全检查节点存在性，避免 Poco 临时异常打断等待循环。"""
    try:
        return game_actions.node(path).exists()
    except Exception:
        return False


def wait_for_any_path(paths, timeout, interval=0.5):
    """等待任一节点出现；只查指定节点，保证遍历速度。"""
    end_time = datetime.now().timestamp() + timeout
    while datetime.now().timestamp() < end_time:
        for path in paths:
            if path_exists(path):
                return True
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
    if not click_lobby_theme_and_enter_high_room(theme_id):
        return "no_config"

    if wait_for_theme_home(timeout=THEME_LOAD_TIMEOUT):
        close_theme_popups(theme_id)
        return "success"

    state_machine.dump_unknown(f"theme_{theme_id}_load_timeout")
    return "load_failed"


def click_lobby_theme_and_enter_high_room(theme_id):
    """Lua 打开主题选 bet 界面后，点击高级房进入按钮才会真正进入主题。"""
    game_actions.click_lobby_theme(theme_id)
    if not click_theme_high_enter_button(timeout=THEME_SELECT_TIMEOUT):
        print(f"主题无高级房入口，跳过：theme_id={theme_id}")
        return False
    return True


def click_theme_high_enter_button(timeout=THEME_SELECT_TIMEOUT):
    """点击主题选 bet 界面的高级房进入按钮；配置异常时用 Poco 路径兜底。"""
    try:
        node = game_actions.node("theme.theme_high_enter_btn")
        if game_actions.wait_for_node(node, timeout=timeout):
            return game_actions.click_node(node, timeout=2)
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
                print("点击高级房进入按钮成功：poco fallback")
                return True
            sleep(0.5)
    except Exception as e:
        print(f"点击高级房进入按钮失败：{e}")
    return False


def prepare_lobby_for_theme(theme_id):
    """每次 RunLua 前确认当前在大厅，避免在 loading/主题内误触发下一个主题。"""
    if wait_for_lobby(timeout=LOBBY_PREPARE_TIMEOUT):
        return True

    close_common_popups()
    if wait_for_lobby(timeout=LOBBY_PREPARE_TIMEOUT):
        return True

    print(f"进入主题前未回到大厅，重启恢复后再继续：theme_id={theme_id}")
    if restart_game() and wait_for_lobby(timeout=LOBBY_PREPARE_TIMEOUT):
        return True

    state_machine.dump_unknown(f"theme_{theme_id}_lobby_prepare_failed")
    return False


def close_common_popups(max_tries=3):
    """关闭通用弹窗，优先用状态机识别，再用节点兜底补点关闭按钮。"""
    closed = False
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
    if close_common_popups(max_tries=4):
        print(f"已清理主题内弹窗：theme_id={theme_id}")


def return_to_lobby(theme_id):
    """点击主题内返回大厅按钮，并用大厅关键节点确认返回成功。"""
    close_theme_popups(theme_id)
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
    """按列表顺序遍历主题：只记录 loading/进入失败主题。"""
    failed_loading_theme_ids = []

    for index, theme_id in enumerate(theme_ids, start=1):
        log(f"==== theme traversal {index}/{len(theme_ids)}: {theme_id} ====")
        if not prepare_lobby_for_theme(theme_id):
            failed_loading_theme_ids.append(theme_id)
            continue

        enter_result = enter_theme(theme_id)
        if enter_result == "no_config":
            print(f"主题入口未出现，跳过：theme_id={theme_id}")
            continue
        if enter_result == "load_failed":
            failed_loading_theme_ids.append(theme_id)
            restart_game()
            continue

        sleep(stay_seconds)
        close_theme_popups(theme_id)

        if not return_to_lobby(theme_id):
            print(f"主题返回大厅失败，重启后继续下一个主题：theme_id={theme_id}")
            restart_game()

    write_theme_ids("failed_loading_theme_ids", failed_loading_theme_ids, "loading 失败主题")
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
