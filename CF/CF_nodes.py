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


def _split_node_path(path):
    """统一解析 group.key 点号路径。"""
    if not isinstance(path, str) or "." not in path:
        raise ValueError("节点路径需使用 'group.key' 格式")

    group_name, node_key = path.split(".", 1)
    if not group_name or not node_key:
        raise ValueError(f"无效节点路径: {path}")
    return group_name, node_key


def node_spec(path):
    """获取 JSON 配置中的节点定义，统一使用 group.key 点号路径。"""
    group_name, key = _split_node_path(path)
    try:
        return _load_group_specs(group_name)[key]
    except KeyError as exc:
        raise KeyError(f"未找到节点配置: {path}") from exc


def resolve_node(path):
    """按 group.key 点号路径直接解析 Poco 节点或图片模板。"""
    return node_spec(path).resolve()


def node_text(path, default=""):
    """按 group.key 点号路径读取节点文本。"""
    return node_spec(path).text(default)


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
    """从 +100、9,999、1,350,000K 这类文本中提取整数。"""
    match = re.search(r"(\d[\d,]*)([KMBTQ]?)", text or "", re.IGNORECASE)
    if not match:
        return default

    # 游戏数值会用单位缩写展示，这里统一换算成完整整数。
    unit_multipliers = {
        "": 1,
        "K": 1_000,
        "M": 1_000_000,
        "B": 1_000_000_000,
        "T": 1_000_000_000_000,
        "Q": 1_000_000_000_000_000,
    }
    number = int(match.group(1).replace(",", ""))
    multiplier = unit_multipliers[match.group(2).upper()]
    return str(number * multiplier)


def extract_progress(text):
    """从 12/25 这类文本中提取当前值和最大值。"""
    match = re.search(r"(\d+)\s*/\s*(\d+)", text or "")
    return match.groups() if match else ("0", "0")

def run_lua(lua_content, poco_driver=None):
    """执行传入的 Lua 内容。"""
    runluapoco = poco_driver or poco
    try:
        result = runluapoco.agent.rpc.call("RunLua", lua_content)
        print(f"执行 Lua 成功：{lua_content}")
        return result
    except Exception as e:
        print(f"执行 Lua 失败：{lua_content} | {e}")
        return None


def click_lobby_theme(theme_id, poco_driver=None, source="poco_automation"):
    """通过 RunLua 点击指定大厅主题。"""
    lua_content = f'LobbyThemeControl:getInstance():clickLobbyTheme({theme_id}, nil, "{source}")'
    return run_lua(lua_content, poco_driver=poco_driver)


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
            self.cg_build_progress_text = node_text("cashgo.build_progress_label", "0/0")
            self.cg_build_progress_current, self.cg_build_progress_max = extract_progress(
                self.cg_build_progress_text
            )
            return self


class GameActions:
    """游戏通用操作封装。"""

    def __init__(self, poco_driver=None):
        self.poco = poco_driver or poco

    def click_node(self, node, timeout=2):
        return if_click(node, timeout=timeout)

    def node(self, path):
        """通过 group.key 点号路径获取节点对象。"""
        return resolve_node(path)

    def text(self, path, default=""):
        """通过 group.key 点号路径读取节点文本。"""
        return node_text(path, default)

    def click(self, path, timeout=2):
        """通过 group.key 点号路径点击节点。"""
        return self.click_node(self.node(path), timeout=timeout)

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

    def run_lua(self, lua_content):
        return run_lua(lua_content, poco_driver=self.poco)

    def click_lobby_theme(self, theme_id, source="poco_automation"):
        return click_lobby_theme(theme_id, poco_driver=self.poco, source=source)

    def extract_number(self, text, default="0"):
        """脚本常用数字提取入口，支持 K/M/B/T/Q 单位换算。"""
        return extract_number(text, default=default)

    def extract_progress(self, text):
        """脚本常用进度文本提取入口。"""
        return extract_progress(text)

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
                "common.btn_close",
                "common.close_btn",
                "cashgo.btn_close",
            ):
                if if_click(resolve_node(feature), label=feature):
                    sleep(0.2)
                    clicked = True
                    closed = True
            if not clicked:
                break
        return closed
