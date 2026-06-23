# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

from airtest.core.api import exists, sleep, touch
from airtest.core.cv import Template
from poco.drivers.std import StdPoco

poco = StdPoco()
CF_DIR = Path(__file__).resolve().parent
NODES_CONFIG_PATH = CF_DIR / "CF_nodes.json"


@dataclass(frozen=True)
class NodeSpec:
    """Poco 节点定位定义，运行时通过 resolve() 获取真实节点。"""

    root: str = None
    chain: tuple = ()
    desc: str = ""
    query: dict = None

    def resolve(self):
        node = poco(**self.query) if self.query else poco(self.root)
        for method, selector in self.chain:
            if isinstance(selector, dict):
                node = getattr(node, method)(**selector)
            elif method == "index":
                node = node[selector]
            elif method == "child":
                node = node.child(selector)
            elif method == "offspring":
                node = node.offspring(selector)
            else:
                raise ValueError(f"不支持的 Poco 节点链路方法: {method}")
        return node

    def text(self, default=""):
        return _safe_text(self.resolve(), default)


@dataclass(frozen=True)
class ImageSpec:
    """Airtest 图片模板定义，用于无法通过 Poco 稳定定位的图片按钮。"""

    filename: str
    record_pos: tuple = None
    resolution: tuple = None
    desc: str = ""

    def resolve(self):
        path = Path(self.filename)
        if not path.is_absolute():
            path = CF_DIR / path
        return Template(str(path), record_pos=self.record_pos, resolution=self.resolution)


def _load_node_config():
    with NODES_CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


NODE_CONFIG = _load_node_config()


def _chain_from_config(chain):
    return tuple((method, selector) for method, selector in chain or ())


def _tuple_or_none(value):
    return tuple(value) if value is not None else None


def _spec_from_config(config):
    if config.get("type") == "image":
        return ImageSpec(
            config["filename"],
            record_pos=_tuple_or_none(config.get("record_pos")),
            resolution=_tuple_or_none(config.get("resolution")),
            desc=config.get("desc", ""),
        )
    return NodeSpec(
        root=config.get("root"),
        chain=_chain_from_config(config.get("chain")),
        desc=config.get("desc", ""),
        query=config.get("query"),
    )


def _load_group_specs(group_name):
    return {
        key: _spec_from_config(config)
        for key, config in NODE_CONFIG.get(group_name, {}).items()
    }


def node_spec(group_name, key):
    """获取 JSON 配置中的节点定义，适合脚本里按参数动态取节点。"""
    try:
        return _load_group_specs(group_name)[key]
    except KeyError as exc:
        raise KeyError(f"未找到节点配置: {group_name}.{key}") from exc


def resolve_node(group_name, key):
    """按 group/key 直接解析 Poco 节点或图片模板。"""
    return node_spec(group_name, key).resolve()


def node_text(group_name, key, default=""):
    """按 group/key 读取节点文本。"""
    return node_spec(group_name, key).text(default)


def node_display_name(node):
    node_text_value = str(node)
    prefix = 'UIObjectProxy of "'
    if node_text_value.startswith(prefix) and node_text_value.endswith('"'):
        return node_text_value[len(prefix):-1]
    return node_text_value


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
        print(f"节点检查异常：{node_display_name(node)} | {e}")
        return False


def _safe_text(node, default="0"):
    """安全读取节点文本，节点不存在或读取失败时返回默认值。"""
    try:
        return node.get_text() if node_exists(node) else default
    except Exception as e:
        print(f"获取节点文本失败: {e}")
        return default


def if_click(node, label=None, timeout=None):
    """节点存在则点击，返回是否点击成功。"""
    name = label or node_display_name(node)
    if not node_exists(node, timeout=timeout):
        print(f"节点不存在：{name}")
        return False

    try:
        node.click()
        print(f"点击节点成功：{name}")
        return True
    except AttributeError:
        pos = exists(node)
        if pos:
            touch(pos)
            print(f"点击图片成功：{name}")
            return True
    except Exception as e:
        print(f"点击节点异常：{name} | {e}")
    return False


def _assign_config_nodes(target, group_name):
    group_config = NODE_CONFIG.get(group_name, {})
    group_specs = _load_group_specs(group_name)
    for key, config in group_config.items():
        node = group_specs[key].resolve()
        attr = config.get("attr", key)
        setattr(target, attr, node)
        for alias in config.get("aliases", ()):
            setattr(target, alias, node)


def extract_number(text, default="0"):
    """从 +100、9,999 这类文本中提取数字。"""
    match = re.search(r"\d[\d,]*", text or "")
    return match.group().replace(",", "") if match else default


def extract_progress(text):
    """从 12/25 这类文本中提取当前值和最大值。"""
    match = re.search(r"(\d+)\s*/\s*(\d+)", text or "")
    return match.groups() if match else ("0", "0")


class common_nodes:
    """CF 节点入口。

    节点定义统一维护在 CF_nodes.json。新增普通节点只需要加 JSON 配置；
    需要兼容旧属性名时，在该条配置里写 attr 或 aliases。
    """

    safe_text = staticmethod(_safe_text)
    node_spec = staticmethod(node_spec)
    resolve_node = staticmethod(resolve_node)
    node_text = staticmethod(node_text)

    def __init__(self):
        _assign_config_nodes(self, "common")

    class lobby_footer_nodes:
        """大厅 Lobby Footer 节点。"""

        def __init__(self):
            _assign_config_nodes(self, "lobby")

    class B_activity:
        """B级模块节点。"""

        def cz(self):
            _assign_config_nodes(self, "b_activity")
            self.cz_get_b_token = node_text("b_activity", "token_label", "0")
            return self

        def b_archer(self):
            pass

        def b_bingo(self):
            pass

        def b_pick(self):
            pass

        def b_cooking(self):
            pass

        def b_makeover(self):
            pass

        def b_rocker(self):
            pass

        def b_plinko(self):
            pass

        def b_journey(self):
            pass

        def b_mow(self):
            pass

        def b_diamond(self):
            pass

        def b_tower(self):
            pass

        def b_coin_mania(self):
            pass

        def b_merge(self):
            pass

    class mansion:
        """mansion 节点。"""

        def __init__(self):
            _assign_config_nodes(self, "mansion")

    class mission_pass:
        """mission pass 节点。"""

        def __init__(self):
            pass

    class a_steamp:
        """A级 邮票 节点。"""

        def __init__(self):
            pass

    class a_byd:
        """A级 byg 节点。"""

        def __init__(self):
            pass

    class a_atw:
        """A级 atw 节点。"""

        def __init__(self):
            pass

    class a_royal:
        """成就 节点。"""

        def __init__(self):
            pass

    class cashgo:
        """Cash Go 节点。"""

        def cg_build(self):
            _assign_config_nodes(self, "cashgo")
            self.cg_build_progress_text = node_text("cashgo", "build_progress_label", "0/0")
            self.cg_build_progress_current, self.cg_build_progress_max = extract_progress(
                self.cg_build_progress_text
            )
            return self


class objects:
    """封装的一些判断函数，兼容旧脚本调用。"""

    def if_exists(self, name):
        return node_exists(name, timeout=3)

    def if_click(self, name):
        return if_click(name)


class GameActions:
    """游戏通用操作封装。"""

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
            print(f"点击 {node_name} 失败: {e}")
            return False

    def swipe_center_to(self, target_node, duration=0.3):
        from airtest.utils.snake import Screen  # pyright: ignore[reportMissingImports]

        screen = Screen()
        center = (screen.width / 2, screen.height / 2)
        target_pos = target_node.get_touch_point()
        self.poco.swipe_vector((target_pos[0] - center[0], target_pos[1] - center[1]), duration=duration)

    def get_label_text(self, label_node):
        return _safe_text(label_node, "")

    def close_all_common_popups(self, max_tries=3):
        closed = False
        for _ in range(max_tries):
            clicked = False
            for feature in (
                ("common", "btn_close"),
                ("common", "close_btn"),
                ("cashgo", "btn_close"),
            ):
                if if_click(resolve_node(*feature), label=f"{feature[0]}.{feature[1]}"):
                    sleep(0.2)
                    clicked = True
                    closed = True
            if not clicked:
                break
        return closed
