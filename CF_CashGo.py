# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

from datetime import datetime
from airtest.core.api import *
from airtest.core.android import *
from airtest.cli.parser import cli_setup
from poco.drivers.std import StdPoco
ST.SNAPSHOT_QUALITY = 20

poco = StdPoco()
android = Android()

'''
log截图：开关
ST.SAVE_IMAGE = True # 开
ST.SAVE_IMAGE = False # 关
'''

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=["Android:///",])
    # auto_setup(__file__, logdir=True, devices=["Android:///127.0.0.1:7555",])
    # auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/d8c92411",])
    # auto_setup(__file__, logdir=True, devices=["android://127.0.0.1:5037/R5CW203G5VF?cap_method=MINICAP&touch_method=MAXTOUCH&",])

# poco("name").child("name").offspring("name") # 父节点选择

btn_close = poco("btn_close") # 活动关闭按钮
close_btn = poco("close_btn") # 活动中心关闭按钮
desc = poco("desc") # lobby 气泡
btnClose = poco("btnClose") # cash go 弹窗关闭按钮
level_label = poco("level_label") # 等级显示
buy_btn_2 = poco("buy_btn_2") # 商店入口
deal_btn_1 = poco("deal_btn_1") # deal入口
btnBuild = poco("btnBuild") # cash go 建造按钮
shop_img17 = poco("shop_img17") # coins OOC 弹窗
slot_coins_img2 = poco("spAdd") # 顶部 coins icon
cg_shop_coins_9999 = poco("bflPrice",type="TextBMFont",text="9,999") # cash go 商店 coins 9999档
btnBuy = poco("btnBuy") # 购买按钮
prize_lbl1 = poco("prize_lbl1") # 收奖确认点击
btnCollect = poco("btnCollect") # 领奖按钮
label_id = poco("label_id") # ID的label
level_label = poco("level_label") # 等级的label
setting = poco(text="setting_node").child(text="enter_btn") # 大厅的setting按钮
cg_build = poco("slot_menu_img2") # cash go 的
bfl_pro = poco("bfl_pro")
slot_coins = Template(r"tpl1689661026884.png", record_pos=(-0.407, -0.906), resolution=(1080, 2316)) # 顶部 coins icon +号按钮
cg_btn_spin = poco("Node").child("btn_spin") # spin按钮
cg_btn_add = poco("Node").child("btn_add") # bet +
cg_btn_rud = poco("Node").child("btn_rud") # bet -

def if_click(name):
    """判断节点是否存在; 存在返回:True 并点击该节点; 节点不存在返回:False;"""
    if name.exists():
        name.click()
        return True
    else:
        return False

def cash_go_build_ooc():
    """cash go 建造过程中金币不足, 触发ooc后的商店购买金币操作"""
    # 暂时关闭截图
    ST.SAVE_IMAGE = False
    if_click(btnClose) # 关闭ooc
    sleep(1)
    touch(slot_coins) # 点击右上角+号按钮，跳转商店
    sleep(1)
    if_click(cg_shop_coins_9999) # 点击金币9999档
    cg_shop_coins_9999.get_text()
    sleep(1)
    if_click(btnBuy) # 点击购买
    sleep(1)
    if_click(prize_lbl1) # 领奖
    sleep(1)
    if_click(cg_shop_coins_9999) # 点击金币9999档
    sleep(1)
    if_click(btnBuy) # 点击购买
    sleep(1)
    if_click(prize_lbl1) # 领奖
    sleep(1)
    if_click(cg_shop_coins_9999) # 点击金币9999档
    sleep(1)
    if_click(btnBuy) # 点击购买
    sleep(1)
    if_click(prize_lbl1) # 领奖
    sleep(1)
    if_click(cg_build) # 点击build页签返回建造界面，此处用的build的红点定位的
    
def cash_go_build():
    """cash go 建造升级"""
    while True:
        if if_click(btnCollect):
            cg_kingdom_index = poco("bfl_rank_num").get_text()[-2:]
            if_click(btnCollect)
            if_click(prize_lbl1)
            sleep(6)
            log(f'{cg_kingdom_index}级小岛完成')
        elif if_click(shop_img17):
            cash_go_build_ooc()
            continue
        else:
            ST.SAVE_IMAGE = True # 开
            if_click(btnBuild)

def cash_go_attack():
    """cash go 攻击"""
    # 点击一个可攻击的建筑
    if_click(poco("Button"))
    sleep(3)
    attck_name = poco("bflName").get_text()
    attck_coins = poco("bflCoins").get_text()
    log(f'攻击:{attck_name},获得:{attck_coins}金币')
    sleep(2)
    # 结算界面点击收奖
    if_click(btnCollect)    
def cash_go_steal():
    """cash go 偷钱"""
    pass
def cash_go_spin():
    cg_bet = int(poco("bfl_bet_mul").get_text()[1:]) # bet
    cg_spins = int(poco("bfl_time").get_text()[1:-6]) # 大于50次的spin次数
    cg_spin = int(poco("bfl_pro").get_text()[:-3]) # spin次数
    while cg_spin > 1:
        # 判断是否在攻击界面
        if if_click(poco("attack_img4")):
            cash_go_attack()
        # # 判断是否在偷钱界面
        # elif if_click():
        #     cash_go_steal()
        elif if_click(prize_lbl1):
            if_click(prize_lbl1)
        else:
            ST.SAVE_IMAGE = False # 关
            if_click(cg_btn_spin)
            ST.SAVE_IMAGE = True # 开
if __name__ == '__main__':
    log("==== start ====")
    cash_go_build()


