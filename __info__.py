# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

from airtest.core.api import *
from airtest.core.android import *
from airtest.cli.parser import cli_setup
from poco.drivers.std import StdPoco
from typing import Any

poco = StdPoco()
android = Android()

'''
log截图：开关
ST.SAVE_IMAGE = True # 开
ST.SAVE_IMAGE = False # 关
'''

if not cli_setup():
    #     auto_setup(__file__, logdir=True, devices=["Android:///", ])
    #     auto_setup(__file__, logdir=True, devices=["Android:///127.0.0.1:7555/127.0.0.1:16416",])
    auto_setup(__file__, logdir=True, devices=[
               "Android://127.0.0.1:5037/5ca91dd2",])

btn_close = poco("btn_close")  # 活动关闭按钮
close_btn = poco("close_btn")  # 活动中心关闭按钮
desc = poco("desc")  # lobby 气泡
btnClose = poco("btnClose")  # cash go 弹窗关闭按钮
level_label = poco("level_label")  # 等级显示
buy_btn_2 = poco("buy_btn_2")  # 商店入口
deal_btn_1 = poco("deal_btn_1")  # deal入口
btnBuild = poco("btnBuild")  # cash go 建造按钮
shop_img17 = poco("shop_img17")  # coins OOC 弹窗
slot_coins_img2 = poco("spAdd")  # 顶部 coins icon
cg_shop_coins_9999 = poco("bflPrice", type="Label",
                          text="9,999")  # cash go 商店 coins 9999档
btnBuy = poco("btnBuy")  # 购买按钮
btnShare = poco("btnShare")  # 小岛完成后的分享按钮
prize_lbl1 = poco("prize_lbl1")  # 领奖按钮
btnCollect = poco("btnCollect")  # 领奖按钮
label_id = poco("label_id")  # ID的label
level_label = poco("level_label")  # 等级的label
setting = poco(text="setting_node").child(text="enter_btn")  # 大厅的setting按钮
cg_build = poco("slot_menu_img2")  # cash go 的
bfl_pro = poco("bfl_pro")
slot_coins = Template(r"tpl1689661026884.png", record_pos=(-0.407, -
                      0.906), resolution=(1080, 2316))  # 顶部 coins icon +号按钮
cg_btn_spin = poco("btn_spin")  # spin按钮
cg_btn_add = poco("btn_add")  # bet +
cg_btn_rud = poco("btn_rud")  # bet -
cg_btn = poco("Button")


# 定义大厅中 mission pass 功能对应的图标节点
lobby_mp_icon = poco("mission_pass_node")
# 定义大厅中每日任务面板功能对应的图标节点
lobby_mission_icon = poco("dashboard_node")
# 定义大厅中 A 设置功能对应的图标节点
lobby_Aset_icon = poco("a_set_node")
# 定义大厅中 成就 功能对应的图标节点
lobby_royal_icon = poco("royal_node")
# 定义大厅中 公会 功能对应的图标节点
lobby_club_icon = poco("club_node")
# 定义大厅中 inbox 功能对应的图标节点
lobby_inbox_icon = poco("inbox_node")
# 定义大厅中 B级 默认功能对应的图标节点
lobby_B_icon = poco("bDefault_node")
# 定义大厅中 每日分享 功能对应的图标节点
lobby_Share_icon = poco("dailyShare_node")
# 定义大厅中 小游戏中心 功能对应的图标节点
lobby_game_center_icon = poco("game_center_node")
# 定义大厅中 高级房 功能对应的图标节点
lobby_lounge_icon = poco("lobby_node")
# 定义大厅中 VIP 功能对应的图标节点
lobby_vip_icon = poco("vip_node")
# 定义大厅中 Cash Go 功能对应的图标节点
lobby_Cash_Go_icon = poco("cash_go_node")
# 定义大厅中 mansion quest 功能对应的图标节点
lobby_mansion_icon = poco("mansion_node")
# 定义大厅中 Facebook 功能对应的图标节点
lobby_facebook_icon = poco("facebook_node")
# 定义大厅中 money 功能对应的图标节点
lobby_money_bank_icon = poco("money_bank_node")
# 定义大厅中 奖励中心 功能对应的图标节点
lobby_rewards_icon = poco("rewards_center_node")
# 定义大厅中 lobby入口展开按钮 对应的图标节点
lobby_middle_icon = poco("middle_node")
# 定义大厅中 活动中心 功能对应的图标节点
lobby_eao_icon = poco("eao_node")
# 定义大厅中 设置 功能对应的图标节点
lobby_setting_icon = poco("setting_node")




# lobby_eao_icon = poco("node")
# lobby_eao_icon = poco("node")
# lobby_eao_icon = poco("node")

def if_exists(name):
    """
    检查指定 UI 节点是否存在，若存在则进行点击操作。

    :param name: 待检查的 UI 节点对象
    """
    # 获取传入节点对象的名称
    jd_name = name.get_name()
    # 检查指定名称的节点是否存在，设置超时时间为 3 秒
    exists(jd_name,timeout=3)
    # 若节点存在，点击该节点
    touch(jd_name)

def if_click(name):
    """
    判断节点是否存在，若存在则点击该节点并返回 True；若不存在则返回 False。

    :param name: 要检查和点击的 UI 节点对象
    :return: 节点存在返回 True，不存在返回 False
    """
    # 判断节点是否存在
    if name.exists():
        # 若节点存在，执行点击操作
        name.click()
        # 返回 True 表示节点存在且已点击
        return True



def if_exists(name):
    jd_name = name.get_name()
    exists(jd_name,timeout=3)
    touch(jd_name)

def if_click(name):
    """判断节点是否存在; 存在返回:True 并点击该节点; 节点不存在返回:False;"""
    if name.exists():
        name.click()
        return True
    else:
        return False

poco("b_list").child("main_item")[2].offspring("icon_sp")

poco("b_list").child("main_item")[2].child("btn_choose")