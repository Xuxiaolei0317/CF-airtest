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
        self.close_btn = poco("close_btn")  # 通用关闭按钮2
        

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
            

    class B_activity:
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
        '''mansion 节点'''
        def __init__(self):
            # self.mansion_btn = poco("mansion_node") #
            self.mansion_star_label = poco("star_label") # 刷子数量
            self.mansion_task_btn = poco("task_btn") # PLAY按钮
            self.mansion_bc_btn = poco("bc_btn") # BC按钮
            
            self.mansion_task_pop = poco("mansion_task_pop") # 房间奖励界面节点，用来判断是否在房间奖励界面
            self.mansion_do_btn = poco("do_btn")  # 使用刷子建造
            self.mansion_close_btn = poco("close_btn") # 房间奖励界面关闭按钮
            
            self.mansion_item_btn = poco("item_btn") # 三选一，选择一个装饰
            self.mansion_ensure_btn = poco("btn_ensure") # 三选一确认
            self.mansion_cancel_btn = poco("btn_cancel") # 三选一取消
            
            self.mansion_dialog_btn = poco("dialog_btn") # 剧情对话按钮
    
    class mission_pass:
        '''mission pass 节点'''
        def __init__(self):
            pass
    class a_steamp:
        '''A级 邮票 节点'''
        def __init__(self):
            pass
    class a_byd:
        '''A级  byg 节点'''
        def __init__(self):
            pass
    class a_atw:
        '''A级  atw 节点'''
        def __init__(self):
            pass
    class a_royal:
        '''成就 节点'''
        def __init__(self):
            pass
    class cashgo:
        '''cash go 节点'''
        def cg_build(self):
            self.btnClose = poco("btnClose")  # cash go 弹窗关闭按钮
            self.btnBuild = poco("btnBuild")  # cash go 建造按钮
            self.btnShare = poco("btnShare")  # 小岛完成后的分享按钮
            self.cg_btn_spin = poco("btn_spin")  # spin按钮
            self.cg_btn_add = poco("btn_add")  # bet +
            self.cg_btn_rud = poco("btn_rud")  # bet -
            self.build_btn = poco("nd_btn_build")
            self.ft_build_icon = poco("nd_create").child(type="Layout")
            self.ft_build_btn = poco("btnFix")
            self.ft_build_coin = poco("btnFix")
            self.ft_build_coin_btn = poco("btnFix")
            self.ft_build_coin_9999 = poco(nameMatches=".*bflPrice",textMatches="9,999")
            return self
    
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


    



