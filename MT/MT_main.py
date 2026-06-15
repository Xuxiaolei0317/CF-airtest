# -*- coding: utf-8 -*-
__author__ = "Xiaolei"

import logging
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from airtest.core.api import *
from airtest.core.cv import Template
from poco.drivers.std import StdPoco

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, dev, poco

import MT_nodes
from MT_nodes import common_nodes


# MT_main.py 是 MT 项目的方法中心；MT_nodes.py 只维护节点分组。
mt = common_nodes()

# 要启动的 MT Android 包名；可用环境变量切换不同安装包。
APP_PACKAGE = os.environ.get("MT_APP_PACKAGE", "com.play2ever.megatycoon.android")
# 启动 App 后等待的秒数，给游戏加载启动页和首屏 UI 留时间。
APP_START_WAIT_SECONDS = float(os.environ.get("MT_APP_START_WAIT_SECONDS", "5"))
# 点击启动确认后继续等待的秒数，给进入游戏过程留时间。
APP_CONFIRM_WAIT_SECONDS = float(os.environ.get("MT_APP_CONFIRM_WAIT_SECONDS", "8"))
# 是否处理启动确认页；设置 MT_CONFIRM_LAUNCH_SCREEN=0 可跳过这一步。
CONFIRM_LAUNCH_SCREEN = os.environ.get("MT_CONFIRM_LAUNCH_SCREEN", "1") != "0"
# 需要勾选的启动选项，通常用于 fps、debug 等一次性开关。
LAUNCH_OPTIONS = os.environ.get("MT_LAUNCH_OPTIONS", "")
# 需要切换状态的启动选项，适合只在当前状态不符合时再点击。
LAUNCH_TOGGLE_OPTIONS = os.environ.get("MT_LAUNCH_TOGGLE_OPTIONS", "")
# 启动页要选择的服务器名称。
LAUNCH_SERVER = os.environ.get("MT_LAUNCH_SERVER", "").strip()
# 服务器列表中服务器位置的手动点击坐标，自动选服失败时可用。
LAUNCH_SERVER_TAP = os.environ.get("MT_LAUNCH_SERVER_TAP", "").strip()
# 选服后确认按钮的手动点击坐标，自动点击失败时可用。
LAUNCH_SERVER_CONFIRM_TAP = os.environ.get("MT_LAUNCH_SERVER_CONFIRM_TAP", "").strip()
# 启动确认按钮的手动点击坐标，图片识别或默认坐标不准时可用。
LAUNCH_CONFIRM_TAP = os.environ.get("MT_LAUNCH_CONFIRM_TAP", "").strip()
# 是否由脚本负责启动和停止 App；设置 MT_MANAGE_APP=0 可只跑当前游戏进程。
MANAGE_APP_LIFECYCLE = os.environ.get("MT_MANAGE_APP", "1") != "0"
# 自动化过程中截图保存目录。
SCREENSHOT_DIR = Path(__file__).resolve().parent / "screenshots"
# 启动确认按钮的图片模板，用于识别并点击确认按钮。
CONFIRM_TEMPLATE = Path(__file__).resolve().parent / "confirm.png"

LAUNCH_OPTION_POINTS = {
    "fps": (0.067, 0.471),
    "pc": (0.067, 0.506),
    "debug": (0.067, 0.541),
    "sofdec": (0.067, 0.576),
    "f-120": (0.067, 0.611),
    "sa": (0.067, 0.646),
    "relogin": (0.067, 0.681),
    "iphonex": (0.300, 0.471),
    "win": (0.300, 0.506),
    "package": (0.300, 0.576),
    "ads": (0.300, 0.611),
    "astc-e": (0.300, 0.681),
    "island": (0.533, 0.471),
    "push": (0.533, 0.506),
    "clear": (0.533, 0.541),
    "coinerr": (0.533, 0.576),
    "fb-l": (0.533, 0.611),
    "logger": (0.533, 0.646),
    "astc-s": (0.533, 0.681),
    "poco": (0.767, 0.471),
    "testnotif": (0.767, 0.506),
    "login": (0.767, 0.541),
    "l-disk": (0.767, 0.576),
    "l-mem": (0.767, 0.611),
    "ads-t": (0.767, 0.646),
}
LAUNCH_CHANGE_POINT = (0.150, 0.930)
LAUNCH_CONFIRM_POINT = (0.500, 0.930)

for logger_name in ["airtest", "root", "adb", "rotation", "nbsp", "touch_methods", "poco"]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

ST.SNAPSHOT_QUALITY = 20
ST.THRESHOLD_STRICT = 0.65
ST.FIND_TIMEOUT = 2
ST.TOUCH_DURATION = 0.05


def sync_poco_driver(poco_driver):
    """同步 Poco 实例，保证节点模块和调用脚本使用同一个连接。"""
    global poco, mt
    poco = poco_driver
    MT_nodes.poco = poco_driver
    mt = common_nodes()
    return poco_driver


def node_display_name(node):
    """格式化 Poco 节点名称，避免日志里只看到 UIObjectProxy 包装文本。"""
    node_text = str(node)
    prefix = 'UIObjectProxy of "'
    if node_text.startswith(prefix) and node_text.endswith('"'):
        return node_text[len(prefix):-1]
    return node_text


def node_exists(node, timeout=None):
    """兼容 Poco 节点、Airtest Template、布尔状态的存在性判断。"""
    try:
        if isinstance(node, bool):
            return node
        if hasattr(node, "exists"):
            if timeout is None:
                return node.exists()
            end_time = time.time() + timeout
            while time.time() < end_time:
                if node.exists():
                    return True
                sleep(0.2)
            return node.exists()
        return bool(exists(node))
    except Exception as e:
        print(f"❌ 节点检查异常：{node_display_name(node)} | {e}")
        return False


def node_text(node, default="0"):
    """安全读取节点文本。"""
    try:
        return node.get_text() if node_exists(node) else default
    except Exception as e:
        print(f"❌ 文本读取异常：{node_display_name(node)} | {e}")
        return default


def if_click(node, label=None, timeout=None):
    """节点存在则点击，返回是否点击成功。"""
    name = label or node_display_name(node)
    if not node_exists(node, timeout=timeout):
        print(f"❌ 节点不存在：{name}")
        return False

    try:
        node.click()
        print(f"✅ 点击节点成功：{name}")
        return True
    except AttributeError:
        pos = exists(node)
        if pos:
            touch(pos)
            print(f"✅ 点击图片成功：{name}")
            return True
    except Exception as e:
        print(f"❌ 点击节点异常：{name} | {e}")
    return False


def int_coin(value):
    """将金币、现金、spin 等展示文本转换为整数。"""
    if value is None:
        return 0

    text = str(value).strip().replace(",", "").replace("spins", "").replace("spin", "")
    match = re.search(r"[-+]?\d+(?:\.\d+)?", text)
    if not match:
        return 0

    number = float(match.group())
    suffix = text[match.end():].strip().upper()[:1]
    multiplier = {
        "K": 1_000,
        "M": 1_000_000,
        "B": 1_000_000_000,
        "T": 1_000_000_000_000,
        "Q": 1_000_000_000_000_000,
    }.get(suffix, 1)
    return int(number * multiplier)


def close_popups(max_tries=3):
    """关闭常见弹窗，避免活动、奖励或资源不足弹窗阻塞流程。"""
    closed = False
    for _ in range(max_tries):
        common_obj = common_nodes()
        clicked = False
        for close_btn in (common_obj.btn_close, common_obj.close_btn, common_obj.mask_close):
            if if_click(close_btn):
                sleep(0.3)
                clicked = True
                closed = True
        if not clicked:
            break
    return closed


def collect_reward():
    """点击通用领取/确认/继续按钮。"""
    common_obj = common_nodes()
    for reward_btn in (common_obj.btn_collect, common_obj.btn_confirm, common_obj.tap_to_continue):
        if if_click(reward_btn):
            sleep(0.5)
            return True
    return False


class LaunchActions:
    """MT 启动页和应用生命周期通用操作封装。"""

    def __init__(
        self,
        device=dev,
        poco_driver=None,
        sync_modules=None,
        capture_callback=None,
        dump_callback=None,
        app_package=APP_PACKAGE,
    ):
        self.device = device
        self.poco = poco_driver or poco
        self.sync_modules = tuple(sync_modules or ())
        self.capture_callback = capture_callback
        self.dump_callback = dump_callback
        self.app_package = app_package

    def reset_poco_connection(self):
        """应用冷启动后重建 Poco 连接，并同步给调用方模块使用。"""
        self.poco = StdPoco(
            device=self.device,
            refresh_rate=0.5,
            timeout=3,
            auto_refresh=False,
            implicit_refresh=False,
        )
        sync_poco_driver(self.poco)
        for module in self.sync_modules:
            if module is not None:
                setattr(module, "poco", self.poco)
        return self.poco

    def screen_point(self, relative_point):
        """把启动页相对坐标转换为当前设备坐标。"""
        width, height = self.device.get_current_resolution()
        return int(width * relative_point[0]), int(height * relative_point[1])

    def tap_relative(self, relative_point, label):
        """点击启动页相对坐标，适配不同分辨率。"""
        touch(self.screen_point(relative_point))
        print(f"✅ 已点击启动页：{label}")

    @staticmethod
    def parse_relative_point(raw_value):
        """解析 x,y 相对坐标，取值范围 0~1。"""
        try:
            x_value, y_value = [float(item.strip()) for item in raw_value.split(",", 1)]
        except ValueError:
            print(f"⚠️ 启动页坐标格式错误：{raw_value}，应为 x,y，例如 0.5,0.5")
            return None
        if not 0 <= x_value <= 1 or not 0 <= y_value <= 1:
            print(f"⚠️ 启动页坐标超出范围：{raw_value}，x/y 应在 0~1 之间")
            return None
        return x_value, y_value

    @staticmethod
    def parse_launch_options(raw_value):
        """解析 Debug=on,FPS=off 形式的启动页开关配置。"""
        targets = {}
        for item in raw_value.split(","):
            item = item.strip()
            if not item:
                continue
            if "=" not in item:
                print(f"⚠️ 忽略启动页开关配置：{item}，应为 name=on/off")
                continue
            name, value = [part.strip().lower() for part in item.split("=", 1)]
            if value not in ("on", "off", "true", "false", "1", "0"):
                print(f"⚠️ 忽略启动页开关配置：{item}，取值应为 on/off")
                continue
            targets[name] = value in ("on", "true", "1")
        return targets

    def launch_option_enabled(self, option_name):
        """通过启动页复选框颜色粗略判断开关状态：黄为开，蓝为关。"""
        relative_point = LAUNCH_OPTION_POINTS.get(option_name)
        if not relative_point:
            return None
        try:
            image = self.device.snapshot()
            x_pos, y_pos = self.screen_point(relative_point)
            pixel = image[y_pos][x_pos][:3]
            red, green, blue = [int(channel) for channel in pixel]
            return red > blue and green > 120
        except Exception as e:
            print(f"⚠️ 启动页开关状态读取失败：{option_name} | {e}")
            return None

    def set_launch_options(self):
        """按需设置启动页开关；默认不改任何开关。"""
        for option_name, expected in self.parse_launch_options(LAUNCH_OPTIONS).items():
            relative_point = LAUNCH_OPTION_POINTS.get(option_name)
            if not relative_point:
                print(f"⚠️ 未知启动页开关：{option_name}")
                continue
            current = self.launch_option_enabled(option_name)
            if current is None:
                print(f"⚠️ 无法判断 {option_name} 当前状态，跳过自动设置")
                continue
            if current != expected:
                self.tap_relative(relative_point, f"{option_name}={'on' if expected else 'off'}")
                sleep(0.2)
            else:
                print(f"✅ 启动页开关已符合预期：{option_name}={'on' if expected else 'off'}")

        for option_name in [item.strip().lower() for item in LAUNCH_TOGGLE_OPTIONS.split(",") if item.strip()]:
            relative_point = LAUNCH_OPTION_POINTS.get(option_name)
            if not relative_point:
                print(f"⚠️ 未知启动页开关：{option_name}")
                continue
            self.tap_relative(relative_point, f"toggle {option_name}")
            sleep(0.2)

    def select_launch_server(self):
        """按需切换启动页服务器；未显式指定时不改变环境。"""
        if not LAUNCH_SERVER and not LAUNCH_SERVER_TAP:
            return

        self.tap_relative(LAUNCH_CHANGE_POINT, "Change")
        sleep(1.0)

        if LAUNCH_SERVER_TAP:
            relative_point = self.parse_relative_point(LAUNCH_SERVER_TAP)
            if relative_point:
                self.tap_relative(relative_point, f"server coordinate {LAUNCH_SERVER_TAP}")
                sleep(0.5)
        elif LAUNCH_SERVER:
            self.reset_poco_connection()
            server_node = self.poco(text=LAUNCH_SERVER)
            if server_node.exists():
                server_node.click()
                print(f"✅ 已选择启动页服务器：{LAUNCH_SERVER}")
                sleep(0.5)
            else:
                print(f"❌ 未找到启动页服务器：{LAUNCH_SERVER}")
                if self.dump_callback:
                    self.dump_callback(f"missing_launch_server_{LAUNCH_SERVER}", [LAUNCH_SERVER])

        if LAUNCH_SERVER_CONFIRM_TAP:
            relative_point = self.parse_relative_point(LAUNCH_SERVER_CONFIRM_TAP)
            if relative_point:
                self.tap_relative(relative_point, f"server confirm {LAUNCH_SERVER_CONFIRM_TAP}")
                sleep(0.5)

    def tap_launch_confirm(self):
        """测试包启动页需要点击 Confirm 才会进入游戏。"""
        if not CONFIRM_LAUNCH_SCREEN:
            return True
        if LAUNCH_CONFIRM_TAP:
            relative_point = self.parse_relative_point(LAUNCH_CONFIRM_TAP)
            if relative_point:
                self.tap_relative(relative_point, f"launch confirm {LAUNCH_CONFIRM_TAP}")
                sleep(APP_CONFIRM_WAIT_SECONDS)
                return True

        confirm_template = Template(str(CONFIRM_TEMPLATE), record_pos=(-0.144, -0.219), resolution=(1080, 2340))
        confirm_pos = exists(confirm_template)
        if confirm_pos:
            touch(confirm_pos)
            print("✅ 已点击启动确认按钮")
            sleep(APP_CONFIRM_WAIT_SECONDS)
            return True

        print("❌ 未找到启动确认按钮，无法进入游戏")
        return False

    def capture_screen(self, reason):
        if self.capture_callback:
            return self.capture_callback(reason)
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

    def launch_game(self):
        """冷启动游戏，确保 Poco 节点查询前应用已进入前台。"""
        try:
            print(f"====================== launch app: {self.app_package} ======================")
            start_app(self.app_package)
            sleep(APP_START_WAIT_SECONDS)
            self.reset_poco_connection()
            self.capture_screen("after_launch_game")
            return True
        except Exception as e:
            print(f"❌ 启动游戏失败：{self.app_package} | {e}")
            return False

    def close_game(self):
        """测试结束后关闭游戏，避免下次运行残留状态。"""
        try:
            print(f"====================== close app: {self.app_package} ======================")
            stop_app(self.app_package)
            sleep(0.5)
            return True
        except Exception as e:
            print(f"⚠️ 关闭游戏异常：{self.app_package} | {e}")
            return False


class GameActions:
    """MT 游戏通用操作封装，供各测试脚本复用。"""

    def __init__(self, poco_driver=None):
        self.poco = poco_driver or poco

    def click_node(self, node, timeout=2):
        return if_click(node, timeout=timeout)

    def wait_for_node(self, node, timeout=10, interval=0.5):
        end_time = time.time() + timeout
        while time.time() < end_time:
            if node_exists(node):
                return True
            sleep(interval)
        return False

    def safe_click_by_name(self, node_name, timeout=3):
        try:
            return self.click_node(self.poco(node_name), timeout=timeout)
        except Exception as e:
            print(f"❌ 点击 {node_name} 失败: {e}")
            return False

    def close_all_common_popups(self, max_tries=3):
        return close_popups(max_tries=max_tries)

    def get_coin_value(self, text):
        return int_coin(text)


def print_resource_values():
    """打印主界面资源和 slot 能量数值。"""
    slot_obj = mt.mt_slot()
    main_obj = mt.mt_main()
    print(f"额外能量点数：{int_coin(slot_obj.mt_espin)}")
    print(f"基础能量点数：{int_coin(slot_obj.mt_espins)}")
    print(f"现金数：{int_coin(main_obj.mt_hd_bill_num)}")
    print(f"护盾数：{int_coin(main_obj.mt_hd_shield_num)}")
    print(f"金币数：{int_coin(main_obj.mt_hd_coin_num)}")


def test_print():
    """兼容旧调用：打印所有数值。"""
    print_resource_values()


def handle_attack():
    """处理 spin 触发的攻击流程。"""
    slot_obj = mt.mt_slot()
    attack_buttons = list(slot_obj.mt_attack_btns)
    if not attack_buttons:
        print("❌ 未找到攻击按钮")
        return False

    attack_buttons[random.randint(0, len(attack_buttons) - 1)].click()
    print("✅ 已点击攻击目标")
    sleep(1)

    slot_obj = mt.mt_slot()
    if if_click(slot_obj.mt_attack_collect_btn):
        print(f"本次攻击赢钱：{node_text(slot_obj.mt_attack_coin_label, '0')}")
    return True


def handle_steal(max_clicks=8):
    """处理 spin 触发的偷钱流程。"""
    for index in range(max_clicks):
        slot_obj = mt.mt_slot()
        if not if_click(slot_obj.mt_steal_box_btn):
            print("❌ 未找到偷钱按钮")
            return False
        sleep(0.5)

        slot_obj = mt.mt_slot()
        if node_exists(slot_obj.mt_steal_popup):
            print(f"本次偷钱赢钱：{node_text(slot_obj.mt_steal_coin_label, '0')}")
            if_click(slot_obj.mt_steal_collect_btn)
            return True
        print(f"偷钱第 {index + 1}/{max_clicks} 次未结算，继续尝试")
    return False



def handle_quest():
    """处理 quest 页面的一次 spin/领取。"""
    quest_obj = mt.mt_quest()
    if if_click(quest_obj.quest_spin_btn):
        sleep(1)
        collect_reward()
        print(f"quest 节点：{quest_obj.quest_index_text}")
        return True
    return False


def spin(times=10):
    """循环点击 spin，并处理攻击、偷钱、quest 或通用领奖。"""
    for index in range(times):
        close_popups()
        slot_obj = mt.mt_slot()
        if_click(slot_obj.mt_spin_btn)
        print(f"第 {index + 1}/{times} 次 spin，金币数：{mt.mt_main().mt_hd_coin_num}")
        sleep(0.5)

        slot_obj = mt.mt_slot()
        if slot_obj.mt_slot_win_text == "ATTACK" or node_exists(slot_obj.mt_attack_dialog):
            handle_attack()
        elif slot_obj.mt_slot_win_text == "STEAL" or slot_obj.slot_steal:
            handle_steal()
        elif slot_obj.mt_quest:
            handle_quest()
        else:
            collect_reward()


def test_build(times=40, click_delay=0.3):
    """执行建造/维修/收集候选按钮，按当前金币和消耗做基础判断。"""
    ST.SAVE_IMAGE = True
    print(f"===== 开始测试建造，循环 {times} 次，点击延迟 {click_delay} 秒 =====")

    for index in range(times):
        try:
            build_obj = mt.mt_build()
            main_obj = mt.mt_main()
            current_coin = int_coin(main_obj.mt_hd_coin_num)
            cost_coin = int_coin(build_obj.mt_main_coin_cost)

            clicked = False
            for action_btn in build_obj.mt_build_action_candidates:
                if if_click(action_btn):
                    clicked = True
                    print(
                        f"✅ 第 {index + 1} 次建造操作成功 | 当前金币：{current_coin} | 建造消耗：{cost_coin}"
                    )
                    break

            if not clicked:
                if current_coin < cost_coin:
                    print(f"❌ 金币不足，无法建造 | 当前金币：{current_coin} | 需消耗：{cost_coin}")
                else:
                    print("❌ 未找到建造/维修/收集候选按钮")
        except Exception as e:
            print(f"❌ 第 {index + 1} 次建造操作异常：{str(e)[:80]}，继续下一次")
        time.sleep(click_delay)

    ST.SAVE_IMAGE = False
    print("===== 建造测试结束 =====")


def xxltest():
    """持续处理 slot 触发的攻击、偷钱、quest；按 Ctrl+C 终止。"""
    print("======================start========================")
    while True:
        close_popups()
        slot_obj = mt.mt_slot()

        if slot_obj.mt_btn_switch or node_exists(slot_obj.mt_attack_dialog):
            handle_attack()
            print("攻击完成，等待 20 秒后继续")
            time.sleep(20)
        elif slot_obj.mt_steal or slot_obj.slot_steal:
            handle_steal()
            print("偷钱完成，等待 15 秒后继续")
            time.sleep(15)
        elif slot_obj.mt_quest:
            handle_quest()
            print("quest 完成节点")
        else:
            print("⚠️ 攻击/偷钱/任务均未识别，10 秒后重试")
            time.sleep(10)


if __name__ == "__main__":
    try:
        xxltest()
    except KeyboardInterrupt:
        print("\n程序被手动终止（Ctrl+C）")
    except Exception as e:
        print(f"\n程序异常终止，原因: {str(e)}")

