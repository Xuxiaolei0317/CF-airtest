# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

from datetime import datetime
from airtest.core.api import *
from airtest.core.android import *
from airtest.cli.parser import cli_setup
from poco.drivers.std import StdPoco

poco = StdPoco()

class common_nodes:
    '''通用节点'''
    def __init__(self):
        self.btn_close = poco("btn_close")  # 通用关闭按钮1
        self.close_btn = poco("close_btn")  # 活动中心关闭按钮
        self.desc = poco("desc")  # lobby 气泡
        self.btnClose = poco("btnClose")  # cash go 弹窗关闭按钮
        self.level_label = poco("level_label")  # 等级显示
        self.buy_btn_2 = poco("buy_btn_2")  # 商店入口
        self.deal_btn_1 = poco("deal_btn_1")  # deal入口
        self.btnBuild = poco("btnBuild")  # cash go 建造按钮
        self.shop_img17 = poco("shop_img17")  # coins OOC 弹窗
        self.slot_coins_img2 = poco("spAdd")  # 顶部 coins icon
        self.cg_shop_coins_9999 = poco("bflPrice", type="Label", text="9,999")  # cash go 商店 coins 9999档
        self.btnBuy = poco("btnBuy")  # 购买按钮
        self.btnShare = poco("btnShare")  # 小岛完成后的分享按钮
        self.prize_lbl1 = poco("prize_lbl1")  # 领奖按钮
        self.btnCollect = poco("btnCollect")  # 领奖按钮
        self.label_id = poco("label_id")  # ID的label
        self.level_label = poco("level_label")  # 等级的label
        self.setting = poco(text="setting_node").child(text="enter_btn")  # 大厅的setting按钮
        self.cg_build = poco("slot_menu_img2")  # cash go 的
        self.bfl_pro = poco("bfl_pro")
        self.slot_coins = Template(r"tpl1689661026884.png", record_pos=(-0.407, -0.906), resolution=(1080, 2316))  # 顶部 coins icon +号按钮
        self.cg_btn_spin = poco("btn_spin")  # spin按钮
        self.cg_btn_add = poco("btn_add")  # bet +
        self.cg_btn_rud = poco("btn_rud")  # bet -
        self.cg_btn = poco("Button")

    class lobby_footer_nodes:
        '''大厅 Lobby Footer 节点'''
        def __init__(self):
            # 定义大厅中 mission pass 功能对应的图标节点
            self.lobby_mp_icon = poco("mission_pass_node")
            # 定义大厅中每日任务面板功能对应的图标节点
            self.lobby_mission_icon = poco("dashboard_node")
            # 定义大厅中 A 设置功能对应的图标节点
            self.lobby_Aset_icon = poco("a_set_node")
            # 定义大厅中 成就 功能对应的图标节点
            self.lobby_royal_icon = poco("royal_node")
            # 定义大厅中 公会 功能对应的图标节点
            self.lobby_club_icon = poco("club_node")
            # 定义大厅中 inbox 功能对应的图标节点
            self.lobby_inbox_icon = poco("inbox_node")
            # 定义大厅中 B级 默认功能对应的图标节点
            self.lobby_B_icon = poco("bDefault_node")
            # 定义大厅中 每日分享 功能对应的图标节点
            self.lobby_Share_icon = poco("dailyShare_node")
            # 定义大厅中 小游戏中心 功能对应的图标节点
            self.lobby_game_center_icon = poco("game_center_node")
            # 定义大厅中 高级房 功能对应的图标节点
            self.lobby_lounge_icon = poco("lobby_node")
            # 定义大厅中 VIP 功能对应的图标节点
            self.lobby_vip_icon = poco("vip_node")
            # 定义大厅中 Cash Go 功能对应的图标节点
            self.lobby_Cash_Go_icon = poco("cash_go_node")
            # 定义大厅中 mansion quest 功能对应的图标节点
            self.lobby_mansion_icon = poco("mansion_node")
            # 定义大厅中 Facebook 功能对应的图标节点
            self.lobby_facebook_icon = poco("facebook_node")
            # 定义大厅中 money 功能对应的图标节点
            self.lobby_money_bank_icon = poco("money_bank_node")
            # 定义大厅中 奖励中心 功能对应的图标节点
            self.lobby_rewards_icon = poco("rewards_center_node")
            # 定义大厅中 lobby入口展开按钮 对应的图标节点
            self.lobby_middle_icon = poco("middle_node")
            # 定义大厅中 活动中心 功能对应的图标节点
            self.lobby_eao_icon = poco("eao_node")
            # 定义大厅中 设置 功能对应的图标节点
            self.lobby_setting_icon = poco("setting_node")

    class B_activity():
        '''B级模块节点'''
        def cz(self):
            '''B级CHALLENGE ZONE界面节点'''
            self.archer = poco("b_list").child("main_item")[2].child("btn_choose")
            self.bingo = poco("b_list").child("main_item")[0].child("btn_choose")
            self.pick = poco("b_list").child("main_item")[1].child("btn_choose")
            self.cooking = poco("b_list").child("main_item")[6].child("btn_choose")
            self.makeover = poco("b_list").child("main_item")[3].child("btn_choose")
            self.rocker = poco("b_list").child("main_item")[4].child("btn_choose")
            self.plinko = poco("b_list").child("main_item")[5].child("btn_choose")
            self.journey = poco("b_list").child("main_item")[8].child("btn_choose")
            self.mow = poco("b_list").child("main_item")[9].child("btn_choose")
            self.diamond = poco("b_list").child("main_item")[7].child("btn_choose")
            self.tower = poco("b_list").child("main_item")[10].child("btn_choose")
            self.coin_mania = poco("b_list").child("main_item")[11].child("btn_choose")
            self.merge = poco("b_list").child("main_item")[12].child("btn_choose")
            
            self.cz_b_pass = poco("pass_node")
            self.cz_btn_rank = poco("btn_rank")
            self.cz_b_store = poco("btn_b_store")
            self.cz_get_b_token = poco("token_node").child(type="Label").get_text()
            self.cz_play_btn = poco("btn_play")
            
            
    
    
class objects:
    '''封装的一些判断函数'''
    def if_exists(self, name):
        """
        检查指定 UI 节点是否存在，若存在则进行点击操作。

        :param name: 待检查的 UI 节点对象
        """
        # 获取传入节点对象的名称
        jd_name = name.get_name()
        # 检查指定名称的节点是否存在，设置超时时间为 3 秒
        exists(jd_name, timeout=3)
        # 若节点存在，点击该节点
        jd_name.click()

    def if_click(self, name):
        """
        判断节点是否存在，若存在则点击该节点并返回 True; 若不存在则返回 False。

        :param name: 要检查和点击的 UI 节点对象
        :return: 节点存在返回 True, 不存在返回 False
        """
        # 判断节点是否存在
        if name.exists():
            # 若节点存在，执行点击操作
            name.click()
            # 返回 True 表示节点存在且已点击
            return True
