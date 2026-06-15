# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

from airtest.core.api import *
from poco.drivers.std import StdPoco
from airtest.core.cv import Template
from dataclasses import dataclass
from pathlib import Path
import re

poco = StdPoco()
MT_DIR = Path(__file__).resolve().parent


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

NEW_USER_NODES = {
    "letsplay_btn": ImageSpec("letsplay_btn.png", record_pos=(-0.144, -0.219), resolution=(1080, 2340), desc="Let's Play 按钮"),
    # start_btn
    "new_user_guide_start_btn_1": NodeSpec("guide_dialog", (child("start_btn"),), desc="新手引导第一步 start 按钮"),
    "new_user_guide_start_btn_2": NodeSpec("guide_dialog", (child("start_btn"),), desc="新手引导第2步 start 按钮"),
    "new_user_guide_mask_btn": NodeSpec("guide_dialog", (child("word_node"), child("mask_btn")), desc="新手引导第三步 对话框跳过按钮"),
    "new_user_guide_word_label": NodeSpec("guide_dialog", (child("word_node"), child("word_label")), desc="对话框文本"),
    # "new_user_guide_name_label": NodeSpec("guide_dialog", (child("word_node"), child("name_label")), desc="对话框，小猪的name"),
    "new_user_guide_coin_label": NodeSpec("guide_dialog", (child("collect_node"), child("coin_label")), desc="新手引导第四步 金币文本"),
    "new_user_guide_collect_btn": NodeSpec("guide_dialog", (child("collect_node"), child("collect_btn")), desc="新手引导第四步 收集按钮"),
    # 模拟经营
    "new_user_guide_task_label": NodeSpec("guide_dialog", (child("task_node"), child("task_label")), desc="模拟经营任务1文本"),
    "new_user_guide_progress_label": NodeSpec("guide_dialog", (child("task_node"), child("progress_label")), desc="模拟经营任务1进度"),
    "new_user_guide_coins_btn": NodeSpec("guide_dialog", (child("task_node"), child("coins_btn")), desc="模拟经营任务1金币按钮"),
    "new_user_guide_coins_label": NodeSpec("task_node", (child("coins_btn"), child("coins_label")), desc="模拟经营任务1消耗金币值"),    
}

COMMON_NODES = {
    "btn_close": NodeSpec("btn_close", desc="通用关闭按钮1"),
    "close_btn": NodeSpec("close_btn", desc="通用关闭按钮2"),
    "btn_collect": NodeSpec("common_btn_auto_green", (child("button"),), "通用自动收集按钮"),
    "btn_confirm": NodeSpec("btn_confirm", desc="通用确认按钮"),
    "btn_cancel": NodeSpec("btn_cancel", desc="通用取消按钮"),
    "btn_skip": NodeSpec("btn_skip", desc="通用跳过按钮"),
    "tap_to_continue": NodeSpec("spTap", desc="Tap to continue 文案/按钮"),
    "mask_close": NodeSpec("mask", (child("btn_close"),), "通用遮罩关闭按钮"),
}


MAIN_NODES = {
    "footer_store": NodeSpec("node_store", (child("btn"),), "商店入口按钮"),
    "footer_build": NodeSpec("node_map", (child("btn"),), "建造入口按钮"),
    "footer_slot": NodeSpec("node_slot", (child("btn"),), "slot入口按钮"),
    "footer_club": NodeSpec("node_club", (child("btn"),), "公会/好友入口按钮"),
    "footer_stamp": NodeSpec("node_stamp", (child("btn"),), "邮票入口"),
    "btn_spin": NodeSpec("node_spin", (child("btn_spin"),), desc="spin按钮"),
    "btn_add": NodeSpec("btn_add", desc="bet +"),
    "btn_sub": NodeSpec("btn_sub", desc="bet -"),
    "header_coin_label": NodeSpec("node_coin", (child("label_coin"),), "header 金币文本"),
    "header_bill_label": NodeSpec("node_bill", (child("label_bill"),), "header 现金文本"),
    "header_shield_label": NodeSpec("node_shield", (child("label_shield"),), "header 护盾文本"),
    "header_menu": NodeSpec("header_1", (child("btn_menu"),), "设置按钮"),
    "login_bonus_dialog": NodeSpec("nd_login_bonus_dialog", desc="login bonus界面"),
    "login_bonus_progress": NodeSpec("ndTop", (child("bflPro"),), "login bonus 月领取进度"),
    "news_message_dialog": NodeSpec("news_message_dialog", desc="news 界面"),
    "news_message_close_btn": NodeSpec(
        "news_message_dialog",
        (child("root"), offspring("btn_close")),
        "news 界面关闭按钮",
    ),
}


QUEST_NODES = {
    "quest_dialog": NodeSpec("quest", desc="quest 界面"),
    "quest_slot_node": NodeSpec("slot_node", desc="quest slot节点"),
    "quest_index_label": NodeSpec("slot_node", (child("lbl_num"),), "quest节点索引"),
    "quest_spin_btn": NodeSpec("btn_spin", desc="quest spin按钮"),
    "quest_collect_btn": NodeSpec("common_btn_auto_green", (child("button"),), "quest领奖按钮"),
    "quest_close_btn": NodeSpec("btn_close", desc="quest关闭按钮"),
}


SLOT_NODES = {
    "slot_root": NodeSpec("node_slot", desc="slot 节点"),
    "spin_root": NodeSpec("node_spin", desc="spin 区域节点"),
    "spin_bet_label": NodeSpec("node_spin", (child("label_bet"),), "当前 spin bet 文本"),
    "spin_bet_add_btn": NodeSpec("node_spin", (child("btn_add"),), "增加 bet 按钮"),
    "spin_bet_sub_btn": NodeSpec("node_spin", (child("btn_sub"),), "减少 bet 按钮"),
    "btn_spin": NodeSpec("node_spin", (child("btn_spin"),), desc="spin 按钮"),
    "slot_result_node": NodeSpec("node_result", desc="slot 结果区域"),
    "slot_win_label": NodeSpec("node_result", (child("label"),), "slot 结果文本"),
    "slot_progress_node": NodeSpec("node_result", (offspring("node_progress"),), "能量进度区域"),
    "slot_progress_label": NodeSpec("node_result", (offspring("label_progress"),), "基础能量文本"),
    "slot_extra_spin_label": NodeSpec("node_result", (offspring("label_left"),), "额外能量文本"),
    "steal_dialog": NodeSpec("slot_steal", desc="偷钱界面"),
    "steal_box_list": NodeSpec("node_boxlist", desc="偷钱按钮列表"),
    "steal_box_btn": NodeSpec("btn_choose", desc="偷钱按钮"),
    "steal_popup": NodeSpec("steal_prize", desc="偷钱结算弹窗"),
    "steal_coin_label": NodeSpec("steal_prize", (offspring("label_coin"),), "偷钱赢钱文本"),
    "steal_collect_btn": NodeSpec("common_btn_auto_green", (child("button"),), "偷钱结算 Collect 按钮"),
    "attack_dialog": NodeSpec("map_dialog", desc="攻击界面"),
    "attack_btns": NodeSpec("map_dialog", (offspring("btn_attack"),), "攻击按钮集合"),
    "attack_player_name": NodeSpec("node_player", (child("label_name"),), "攻击对象名称"),
    "attack_switch_btn": NodeSpec("node_player", (child("btn_switch"),), "切换攻击对象按钮"),
    "attack_choose_target_pop": NodeSpec("choose_target_pop", desc="攻击选择界面"),
    "attack_revenge_btn": NodeSpec("btn_revenge", desc="复仇列表按钮"),
    "attack_friends_btn": NodeSpec("btn_friends", desc="好友列表按钮"),
    "attack_pop": NodeSpec("successful_attack_pop", desc="攻击收奖弹窗"),
    "attack_collect_btn": NodeSpec("common_btn_auto_green", (child("button"),), "攻击结算 Collect 按钮"),
    "attack_coin_label": NodeSpec("successful_attack_pop", (offspring("label_coin"),), "攻击赢钱文本"),
    "quest_entry": NodeSpec("task_node", (child("btn_icon"),), "quest 入口节点"),
    "quest_dialog": NodeSpec("quest", desc="quest 界面"),
    "quest_spin_btn": NodeSpec("btn_spin", desc="quest spin 按钮"),
    "quest_index_label": NodeSpec("slot_node", (child("lbl_num"),), "quest 节点索引"),
}


BUILD_NODES = {
    "map_btn": ImageSpec("build_button.png", record_pos=(-0.144, -0.219), resolution=(1080, 2340), desc="建造地图图片按钮"),
    "map_center_btn": NodeSpec("main_tip", desc="建造地图居中按钮"),
    "repair_btn": NodeSpec("repair_btn", desc="建造维修按钮"),
    "coin_collect_btn": NodeSpec("main_coin_collect", desc="coin 收集按钮"),
    "coin_collect_label": NodeSpec("main_coin_collect", (child("coin_label"),), "可收集金币数量"),
    "coin_cost_btn": NodeSpec("main_coin_cost", desc="coin 消耗按钮"),
    "coin_cost_label": NodeSpec("main_coin_cost", (child("coin_label"),), "建造消耗金币数量"),
    "gift_box_btn": NodeSpec("gift_box_1", (child("btn"),), "建造礼盒"),
    "upgrade_btn": NodeSpec("btn_upgrade", desc="建造升级按钮"),
    "build_btn": NodeSpec("btn_build", desc="建造按钮"),
    "confirm_btn": NodeSpec("btn_confirm", desc="建造确认按钮"),
    "free_btn": NodeSpec("btn_free", desc="免费建造/维修按钮"),
}


BOTTLE_NODES = {
    "bottle_node": NodeSpec("map_drift_node", desc="漂流瓶入口/地图节点"),
    "bottle_dialog": NodeSpec("drift_bottle_dialog", desc="漂流瓶弹窗"),
    "bottle_open_btn": NodeSpec("btn_open", desc="打开漂流瓶"),
    "bottle_collect_btn": NodeSpec("common_btn_auto_green", (child("button"),), "漂流瓶领取按钮"),
    "bottle_close_btn": NodeSpec("btn_close", desc="漂流瓶关闭按钮"),
}


GUILD_NODES = {
    "guild_main": NodeSpec("friends_main", desc="公会/好友主界面"),
    "guild_root": NodeSpec("friends_main", (child("root"),), "公会/好友主界面 root"),
    "guild_layer_root": NodeSpec("friends_main", (child("root"), child("layer_root")), "公会/好友内容层"),
    "guild_page": NodeSpec("club", desc="公会页面"),
    "guild_page_alt": NodeSpec("club_dialog", desc="公会页面兼容命名"),
    "guild_home": NodeSpec("club_home", desc="已加入公会后的主页"),
    "guild_chat_layer": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer")), "公会聊天层"),
    "guild_chat_list": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("chat_list")), "公会聊天列表"),
    "guild_chat_gift": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("chat_gift")), "公会礼物入口"),
    "guild_chat_gift_btn": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("chat_gift"), child("btn_bg")), "公会礼物按钮"),
    "guild_info_node": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("info_node")), "公会信息区域"),
    "guild_name_label": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("info_node"), child("label_name")), "当前公会名"),
    "guild_info_btn": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("info_node"), child("btn_info")), "CLUB INFO 按钮"),
    "guild_bottom_node": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("bottom_node")), "公会底部操作区"),
    "guild_bottom_btn_node": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("bottom_node"), child("btn_node")), "公会底部按钮容器"),
    "guild_top_node": NodeSpec("friends_main", (child("root"), child("top_node")), "公会顶部 tab 区域"),
    "guild_tab_node": NodeSpec("friends_main", (child("root"), child("top_node"), child("tab_node")), "公会 tab 容器"),
    "guild_in_club_tab_group": NodeSpec("friends_main", (child("root"), child("top_node"), child("tab_node"), child("in_club")), "已加入公会 tab 组"),
    "guild_collect_pop": NodeSpec("club_chat_collect_pop", desc="公会帮助领取弹窗"),
    "guild_collect_btn": NodeSpec("club_chat_collect_pop", (child("root"), child("btn_collect")), "帮助领取按钮"),
    "guild_chat_tab": NodeSpec("friends_main", (child("root"), child("top_node"), child("tab_node"), child("in_club"), child("nd_club_chat")), "My Club tab"),
    "guild_shop_tab": NodeSpec("friends_main", (child("root"), child("top_node"), child("tab_node"), child("in_club"), child("nd_club_shop")), "Shop tab"),
    "guild_friends_tab": NodeSpec("friends_main", (child("root"), child("top_node"), child("tab_node"), child("in_club"), child("nd_friends")), "Friends tab"),
    "guild_shop_tab_btn": NodeSpec("friends_main", (child("root"), child("top_node"), child("tab_node"), child("in_club"), child("nd_club_shop"), child("btn")), "Shop tab 按钮"),
    "guild_friends_tab_btn": NodeSpec("friends_main", (child("root"), child("top_node"), child("tab_node"), child("in_club"), child("nd_friends"), child("btn")), "Friends tab 按钮"),
    "guild_chat_btn": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("bottom_node"), child("btn_node"), child("btn_chat")), "聊天输入入口"),
    "guild_request_spins_btn": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("bottom_node"), child("btn_node"), child("btn_energy")), "请求 spins 按钮"),
    "guild_request_card_btn": NodeSpec("friends_main", (child("root"), child("layer_root"), offspring("chat_layer"), child("bottom_node"), child("btn_node"), child("btn_card")), "请求邮票按钮"),
    "guild_search_btn": NodeSpec("btn_search", desc="搜索按钮"),
    "guild_search_input": NodeSpec("input_search", desc="搜索输入框"),
    "guild_search_input_alt": NodeSpec("search_input", desc="搜索输入框兼容命名"),
    "guild_search_confirm_btn": NodeSpec("btn_search_confirm", desc="确认搜索按钮"),
    "guild_join_btn": NodeSpec("btn_join", desc="加入公会按钮"),
    "guild_apply_btn": NodeSpec("btn_apply", desc="申请加入按钮"),
    "guild_message_input": NodeSpec("input_chat", desc="公会消息输入框候选"),
    "guild_message_input_alt": NodeSpec("chat_input", desc="公会消息输入框候选"),
    "guild_message_input_edit": NodeSpec("editbox", desc="已验证聊天输入框"),
    "guild_message_input_field": NodeSpec("input", desc="宽泛输入框候选"),
    "guild_send_btn": NodeSpec("btn_send", desc="发送消息按钮"),
    "guild_send_btn_alt": NodeSpec("send_btn", desc="发送消息按钮兼容命名"),
    "guild_help_spin_btn": NodeSpec("chat_ask_spins", (offspring("btn_help"),), "帮助公会成员 spins 请求"),
    "guild_help_card_btn": NodeSpec("chat_ask_card", (offspring("btn_help"),), "帮助公会成员邮票请求"),
    "guild_search_page": NodeSpec("club_search", desc="未加入公会搜索页"),
    "guild_recommend_page": NodeSpec("club_recommend", desc="未加入公会推荐页"),
}


STAMP_NODES = {
    "stamp_page": NodeSpec("stamp", desc="邮票页面"),
    "stamp_page_alt": NodeSpec("stamp_dialog", desc="邮票页面兼容命名"),
    "stamp_list": NodeSpec("stamp_list", desc="邮票列表"),
    "stamp_list_alt": NodeSpec("scroll_view", desc="可滚动列表兼容命名"),
}


STORE_NODES = {
    "store_page": NodeSpec("store", desc="商店页面"),
    "store_page_alt": NodeSpec("shop", desc="商店页面兼容命名"),
}


BUSINESS_NODES = {
    "business_root": NodeSpec("management_main", (child("root"),), "事件任务主界面 root"),
    "business_progress_label": NodeSpec("uncompleted_node", (child("progress_label"),), "当前任务进度值"),
    "business_time_label": NodeSpec("time_node", (child("time_node_yellow"), child("label")), "事件任务倒计时"),
    "business_label_cur": NodeSpec("root", (child("push_node"), child("label_cur")), "当前进度值"),
    "business_label_stage2": NodeSpec("root", (child("push_node"), child("label_stage2")), "当前目标值"),
    "business_label_count": NodeSpec("reward_p", (child("reward_progress"), child("label_count")), "当前任务徽章奖励"),
    "business_label": NodeSpec("reward_regular", (child("rid4"), child("label")), "当前任务能量奖励"),
    "business_label_desc": NodeSpec("node_task", (child("task_node"), child("label_desc")), "当前任务描述"),
}


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


def extract_number(text, default="0"):
    """从 +100、+34389 spins 这类文本中提取数字。"""
    match = re.search(r"\d[\d,]*", text or "")
    return match.group().replace(",", "") if match else default


def extract_progress(text):
    """从 50/50 这类文本中提取当前值和最大值。"""
    match = re.search(r"(\d+)\s*/\s*(\d+)", text or "")
    return match.groups() if match else ("0", "0")


def _assign_slot_nodes(target):
    target.mt_slot = SLOT_NODES["slot_root"].resolve()
    target.mt_spin_node = SLOT_NODES["spin_root"].resolve()
    target.mt_spin_bet_label = SLOT_NODES["spin_bet_label"].resolve()
    spin_bet_text = _safe_text(target.mt_spin_bet_label, "X0")
    target.mt_spin_bet_num = spin_bet_text.split("X", 1)[1] if "X" in spin_bet_text else spin_bet_text
    target.mt_spin_bet_add_btn = SLOT_NODES["spin_bet_add_btn"].resolve()
    target.mt_spin_bet_sub_btn = SLOT_NODES["spin_bet_sub_btn"].resolve()
    target.mt_spin_btn = SLOT_NODES["spin_btn"].resolve()
    target.mt_slot_result_node = SLOT_NODES["slot_result_node"].resolve()
    target.mt_slot_win_label = SLOT_NODES["slot_win_label"].resolve()
    target.mt_slot_win_text = _safe_text(target.mt_slot_win_label, "0")
    target.mt_slot_progress_node = SLOT_NODES["slot_progress_node"].resolve()
    target.mt_slot_progress_label = SLOT_NODES["slot_progress_label"].resolve()
    target.mt_slot_progress_text = _safe_text(target.mt_slot_progress_label, "0/0")
    target.mt_slot_progress_current, target.mt_slot_progress_max = extract_progress(target.mt_slot_progress_text)
    target.mt_slot_extra_spin_label = SLOT_NODES["slot_extra_spin_label"].resolve()
    target.mt_slot_extra_spin_num = extract_number(_safe_text(target.mt_slot_extra_spin_label, "0"))
    target.mt_espin = target.mt_slot_extra_spin_num
    target.mt_espins = target.mt_slot_progress_current

    target.slot_steal = _safe_exists(SLOT_NODES["steal_dialog"].resolve())
    target.mt_steal_node = SLOT_NODES["steal_box_list"].resolve()
    target.mt_steal = _safe_exists(target.mt_steal_node)
    target.mt_steal_box_btn = SLOT_NODES["steal_box_btn"].resolve()
    target.mt_steal_popup = SLOT_NODES["steal_popup"].resolve()
    target.mt_steal_coin_label = SLOT_NODES["steal_coin_label"].resolve()
    target.mt_steal_collect_btn = SLOT_NODES["steal_collect_btn"].resolve()

    target.mt_attack_dialog = SLOT_NODES["attack_dialog"].resolve()
    target.mt_btn_switch = _safe_exists(target.mt_attack_dialog)
    target.mt_attack_btns = SLOT_NODES["attack_btns"].resolve()
    target.mt_attack_player_name = SLOT_NODES["attack_player_name"].resolve()
    target.mt_attack_switch_btn = SLOT_NODES["attack_switch_btn"].resolve()
    target.mt_attack_choose_target_pop = SLOT_NODES["attack_choose_target_pop"].resolve()
    target.mt_attack_revenge_btn = SLOT_NODES["attack_revenge_btn"].resolve()
    target.mt_attack_friends_btn = SLOT_NODES["attack_friends_btn"].resolve()
    target.mt_attack_pop = SLOT_NODES["attack_pop"].resolve()
    target.mt_attack_collect_btn = SLOT_NODES["attack_collect_btn"].resolve()
    target.mt_attack_coin_label = SLOT_NODES["attack_coin_label"].resolve()
    target.mt_attack_coin_num = _safe_text(target.mt_attack_coin_label, "0")

    target.mt_quest_node = SLOT_NODES["quest_entry"].resolve()
    target.mt_quest = _safe_exists(SLOT_NODES["quest_dialog"].resolve())
    target.mt_quest_btn = SLOT_NODES["quest_spin_btn"].resolve()
    target.mt_quest_index = SLOT_NODES["quest_index_label"].resolve()


def _assign_bottle_nodes(target):
    target.bottle_node = BOTTLE_NODES["bottle_node"].resolve()
    target.bottle_dialog = BOTTLE_NODES["bottle_dialog"].resolve()
    target.bottle_open_btn = BOTTLE_NODES["bottle_open_btn"].resolve()
    target.bottle_collect_btn = BOTTLE_NODES["bottle_collect_btn"].resolve()
    target.bottle_close_btn = BOTTLE_NODES["bottle_close_btn"].resolve()


class common_nodes:
    '''通用节点'''
    safe_text = staticmethod(_safe_text)

    def __init__(self):
        self.btn_close = COMMON_NODES["btn_close"].resolve()
        self.close_btn = COMMON_NODES["close_btn"].resolve()
        self.btn_collect = COMMON_NODES["btn_collect"].resolve()
        self.btn_confirm = COMMON_NODES["btn_confirm"].resolve()
        self.btn_cancel = COMMON_NODES["btn_cancel"].resolve()
        self.btn_skip = COMMON_NODES["btn_skip"].resolve()
        self.tap_to_continue = COMMON_NODES["tap_to_continue"].resolve()
        self.mask_close = COMMON_NODES["mask_close"].resolve()
        self.letsplay_btn = NEW_USER_NODES["letsplay_btn"].resolve()
        _assign_slot_nodes(self)

    class mt_main():
        '''MT 主界面节点'''
        def __init__(self):
            self.mt_ft_store = MAIN_NODES["footer_store"].resolve()
            self.mt_ft_build = MAIN_NODES["footer_build"].resolve()
            self.mt_ft_slot = MAIN_NODES["footer_slot"].resolve()
            self.mt_ft_club = MAIN_NODES["footer_club"].resolve()
            self.mt_ft_stamp = MAIN_NODES["footer_stamp"].resolve()

            self.mt_btn_spin = MAIN_NODES["btn_spin"].resolve()
            self.mt_btn_add = MAIN_NODES["btn_add"].resolve()
            self.mt_btn_sud = MAIN_NODES["btn_sud"].resolve()

            self.mt_hd_coin = MAIN_NODES["header_coin_label"].resolve()
            self.mt_hd_coin_num = MAIN_NODES["header_coin_label"].text("0")
            self.mt_hd_bill = MAIN_NODES["header_bill_label"].resolve()
            self.mt_hd_bill_num = MAIN_NODES["header_bill_label"].text("0")
            self.mt_hd_shield = MAIN_NODES["header_shield_label"].resolve()
            shield_text = MAIN_NODES["header_shield_label"].text("0")
            self.mt_hd_shield_num = shield_text[0] if shield_text else "0"
            self.mt_hd_menu = MAIN_NODES["header_menu"].resolve()

            self.mt_loginbonus = MAIN_NODES["login_bonus_dialog"].resolve()
            self.mt_Tapto = COMMON_NODES["tap_to_continue"].resolve()
            self.mt_loginbonus_progress = MAIN_NODES["login_bonus_progress"].resolve()
            self.mt_loginbonus_progress_text = MAIN_NODES["login_bonus_progress"].text("0/0")
            self.mt_loginbonus_progress_current, self.mt_loginbonus_progress_max = extract_progress(
                self.mt_loginbonus_progress_text
            )
            self.mt_news_message_dialog = MAIN_NODES["news_message_dialog"].resolve()
            self.mt_news_message_dialog_close_btn = MAIN_NODES["news_message_close_btn"].resolve()

            _assign_slot_nodes(self)

    class mt_slot():
        '''MT slot、攻击、偷钱节点'''
        def __init__(self):
            _assign_slot_nodes(self)

    class mt_build():
        '''MT 建造节点'''
        def __init__(self):
            self.mt_build_map_btn = BUILD_NODES["map_btn"].resolve()
            self.mt_build_map_center_btn = BUILD_NODES["map_center_btn"].resolve()
            self.mt_build_repair_btn = BUILD_NODES["repair_btn"].resolve()
            self.mt_main_coin_collect_btn = BUILD_NODES["coin_collect_btn"].resolve()
            self.mt_main_coin_collect = BUILD_NODES["coin_collect_label"].text("0")
            self.mt_main_coin_cost_btn = BUILD_NODES["coin_cost_btn"].resolve()
            self.mt_main_coin_cost = BUILD_NODES["coin_cost_label"].text("0")
            self.mt_build_box = BUILD_NODES["gift_box_btn"].resolve()
            self.mt_build_upgrade_btn = BUILD_NODES["upgrade_btn"].resolve()
            self.mt_build_build_btn = BUILD_NODES["build_btn"].resolve()
            self.mt_build_confirm_btn = BUILD_NODES["confirm_btn"].resolve()
            self.mt_build_free_btn = BUILD_NODES["free_btn"].resolve()
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
        '''MT 漂流瓶节点'''
        def __init__(self):
            _assign_bottle_nodes(self)

    class mt_new_user_guide():
        '''MT 新手引导节点'''
        def __init__(self):
            self.new_user_guide_start_btn_1 = NEW_USER_NODES["new_user_guide_start_btn_1"].resolve()
            self.new_user_guide_start_btn_2 = NEW_USER_NODES["new_user_guide_start_btn_2"].resolve()
            self.new_user_guide_mask_btn = NEW_USER_NODES["new_user_guide_mask_btn"].resolve()
            self.new_user_guide_word_label = NEW_USER_NODES["new_user_guide_word_label"].resolve()
            self.new_user_guide_word_text = NEW_USER_NODES["new_user_guide_word_label"].text("0")
            self.new_user_guide_name_label = NEW_USER_NODES["new_user_guide_name_label"].resolve()
            self.new_user_guide_coin_label = NEW_USER_NODES["new_user_guide_coin_label"].resolve()
            self.new_user_guide_collect_btn = NEW_USER_NODES["new_user_guide_collect_btn"].resolve()
            self.new_user_guide_task_label = NEW_USER_NODES["new_user_guide_task_label"].resolve()
            self.new_user_guide_progress_label = NEW_USER_NODES["new_user_guide_progress_label"].resolve()
            self.new_user_guide_coins_btn = NEW_USER_NODES["new_user_guide_coins_btn"].resolve()
            self.new_user_guide_coins_label = NEW_USER_NODES["new_user_guide_coins_label"].resolve()

    class mt_quest():
        '''MT Quest 节点'''
        def __init__(self):
            self.quest_dialog = QUEST_NODES["quest_dialog"].resolve()
            self.quest_slot_node = QUEST_NODES["quest_slot_node"].resolve()
            self.quest_index_label = QUEST_NODES["quest_index_label"].resolve()
            self.quest_index_text = QUEST_NODES["quest_index_label"].text("0")
            self.quest_spin_btn = QUEST_NODES["quest_spin_btn"].resolve()
            self.quest_collect_btn = QUEST_NODES["quest_collect_btn"].resolve()
            self.quest_close_btn = QUEST_NODES["quest_close_btn"].resolve()

    class mt_guild():
        '''MT 公会/好友节点'''
        def __init__(self):
            _resolve_all(self, GUILD_NODES)
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
                COMMON_NODES["btn_collect"].resolve(),
            )

    mt_club = mt_guild

    class mt_stamp():
        '''MT 邮票节点'''
        def __init__(self):
            _resolve_all(self, STAMP_NODES)

    class mt_store():
        '''MT 商店节点'''
        def __init__(self):
            _resolve_all(self, STORE_NODES)

    class mt_business():
        '''MT 事件任务节点'''
        def __init__(self):
            _resolve_all(self, BUSINESS_NODES)