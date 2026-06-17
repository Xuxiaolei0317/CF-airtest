# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import json
import re
from dataclasses import dataclass
from pathlib import Path

from airtest.core.api import *
from airtest.core.cv import Template
from poco.drivers.std import StdPoco

poco = StdPoco()
MT_DIR = Path(__file__).resolve().parent
NODES_CONFIG_PATH = MT_DIR / "MT_nodes.json"


@dataclass(frozen=True)
class NodeSpec:
    """Poco 节点定位定义，运行时通过 resolve() 获取真实节点。"""
    root: str
    chain: tuple = ()
    desc: str = ""

    def resolve(self):
        node = poco(self.root)
        for method, name in self.chain:
            if method == "child":
                node = node.child(name)
            elif method == "offspring":
                node = node.offspring(name)
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
            path = MT_DIR / path
        return Template(str(path), record_pos=self.record_pos, resolution=self.resolution)


def child(name):
    return ("child", name)


def offspring(name):
    return ("offspring", name)


def _load_node_config():
    with NODES_CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


NODE_CONFIG = _load_node_config()


def _chain_from_config(chain):
    return tuple((method, name) for method, name in chain or ())


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
        config["root"],
        _chain_from_config(config.get("chain")),
        desc=config.get("desc", ""),
    )


def _load_group_specs(group_name):
    return {
        key: _spec_from_config(config)
        for key, config in NODE_CONFIG.get(group_name, {}).items()
    }


def _add_spec_alias(specs, alias, key):
    if key in specs:
        specs[alias] = specs[key]


COMMON_NODES = _load_group_specs("common")
NEW_USER_NODES = _load_group_specs("new_user")
MAIN_NODES = _load_group_specs("main")
QUEST_NODES = _load_group_specs("quest")
SLOT_NODES = _load_group_specs("slot")
BUILD_NODES = _load_group_specs("build")
BOTTLE_NODES = _load_group_specs("bottle")
GUILD_NODES = _load_group_specs("guild")
STAMP_NODES = _load_group_specs("stamp")
STORE_NODES = _load_group_specs("store")
BUSINESS_NODES = _load_group_specs("business")

_add_spec_alias(SLOT_NODES, "btn_spin", "spin_btn")
_add_spec_alias(MAIN_NODES, "btn_sud", "btn_sub")


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


def _safe_text(node, default="0"):
    """安全读取节点文本，节点不存在或读取失败时返回默认值。"""
    try:
        return node.get_text() if node.exists() else default
    except Exception as e:
        print(f"获取节点文本失败: {e}")
        return default


def _safe_exists(node, default=False):
    """安全判断节点存在性，避免节点驱动临时异常中断脚本。"""
    try:
        return node.exists()
    except Exception as e:
        print(f"检查节点存在失败: {e}")
        return default


def _resolve_all(target, specs):
    for attr, spec in specs.items():
        setattr(target, attr, spec.resolve())


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
    """从 +100、+34389 spins 这类文本中提取数字。"""
    match = re.search(r"\d[\d,]*", text or "")
    return match.group().replace(",", "") if match else default


def extract_progress(text):
    """从 50/50 这类文本中提取当前值和最大值。"""
    match = re.search(r"(\d+)\s*/\s*(\d+)", text or "")
    return match.groups() if match else ("0", "0")


def _assign_slot_nodes(target):
    _assign_config_nodes(target, "slot")

    spin_bet_text = _safe_text(target.mt_spin_bet_label, "X0")
    target.mt_spin_bet_num = spin_bet_text.split("X", 1)[1] if "X" in spin_bet_text else spin_bet_text

    target.mt_slot_win_text = _safe_text(target.mt_slot_win_label, "0")
    target.mt_slot_progress_text = _safe_text(target.mt_slot_progress_label, "0/0")
    target.mt_slot_progress_current, target.mt_slot_progress_max = extract_progress(
        target.mt_slot_progress_text
    )
    target.mt_slot_extra_spin_num = extract_number(_safe_text(target.mt_slot_extra_spin_label, "0"))
    target.mt_espin = target.mt_slot_extra_spin_num
    target.mt_espins = target.mt_slot_progress_current

    target.slot_steal = _safe_exists(target.mt_steal_dialog)
    target.mt_steal = _safe_exists(target.mt_steal_node)

    target.mt_btn_switch = _safe_exists(target.mt_attack_dialog)
    target.mt_attack_coin_num = _safe_text(target.mt_attack_coin_label, "0")

    target.mt_quest = _safe_exists(target.mt_quest_dialog)


def _assign_bottle_nodes(target):
    _assign_config_nodes(target, "bottle")


class common_nodes:
    """MT 节点入口。

    节点定义统一维护在 MT_nodes.json。新增普通节点只需要加一条 JSON 配置；
    如果要兼容旧属性名，在该条配置里写 attr 或 aliases 即可。
    """

    safe_text = staticmethod(_safe_text)
    node_spec = staticmethod(node_spec)
    resolve_node = staticmethod(resolve_node)
    node_text = staticmethod(node_text)

    def __init__(self):
        _assign_config_nodes(self, "common")
        self.letsplay_btn = resolve_node("new_user", "letsplay_btn")
        _assign_slot_nodes(self)

    class mt_main():
        """MT 主界面节点"""

        def __init__(self):
            _assign_config_nodes(self, "main")
            self.mt_Tapto = resolve_node("common", "tap_to_continue")

            self.mt_hd_coin_num = node_text("main", "header_coin_label", "0")
            self.mt_hd_bill_num = node_text("main", "header_bill_label", "0")
            shield_text = node_text("main", "header_shield_label", "0")
            self.mt_hd_shield_num = shield_text[0] if shield_text else "0"

            self.mt_loginbonus_progress_text = node_text("main", "login_bonus_progress", "0/0")
            self.mt_loginbonus_progress_current, self.mt_loginbonus_progress_max = extract_progress(
                self.mt_loginbonus_progress_text
            )

            _assign_slot_nodes(self)

    class mt_slot():
        """MT slot、攻击、偷钱节点"""

        def __init__(self):
            _assign_slot_nodes(self)

    class mt_build():
        """MT 建造节点"""

        def __init__(self):
            _assign_config_nodes(self, "build")
            self.mt_main_coin_collect = node_text("build", "coin_collect_label", "0")
            self.mt_main_coin_cost = node_text("build", "coin_cost_label", "0")
            self.mt_build_action_candidates = (
                self.mt_main_coin_cost_btn,
                self.mt_build_upgrade_btn,
                self.mt_build_build_btn,
                self.mt_build_repair_btn,
                self.mt_build_free_btn,
                self.mt_build_confirm_btn,
                self.mt_build_map_center_btn,
                self.mt_build_map_btn,
            )
            _assign_bottle_nodes(self)

    class mt_bottle():
        """MT 漂流瓶节点"""

        def __init__(self):
            _assign_bottle_nodes(self)

    class mt_new_user_guide():
        """MT 新手引导节点"""

        def __init__(self):
            _assign_config_nodes(self, "new_user")
            self.new_user_guide_word_text = node_text("new_user", "new_user_guide_word_label", "0")

    mt_guide = mt_new_user_guide

    class mt_quest():
        """MT Quest 节点"""

        def __init__(self):
            _assign_config_nodes(self, "quest")
            self.quest_index_text = node_text("quest", "quest_index_label", "0")

    class mt_guild():
        """MT 公会/好友节点"""

        def __init__(self):
            _assign_config_nodes(self, "guild")
            self.guild_not_joined_candidates = (
                self.guild_search_page,
                self.guild_recommend_page,
                self.guild_search_btn,
                self.guild_join_btn,
                self.guild_apply_btn,
            )
            self.guild_join_candidates = (
                self.guild_join_btn,
                self.guild_apply_btn,
                resolve_node("common", "btn_collect"),
            )

    mt_club = mt_guild

    class mt_stamp():
        """MT 邮票节点"""

        def __init__(self):
            _assign_config_nodes(self, "stamp")

    class mt_store():
        """MT 商店节点"""

        def __init__(self):
            _assign_config_nodes(self, "store")

    class mt_business():
        """MT 事件任务节点"""

        def __init__(self):
            _assign_config_nodes(self, "business")

    class objects:
        """预留给维护工具写入自动发现结果的锚点。"""
        pass
