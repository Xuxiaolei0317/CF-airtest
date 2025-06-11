# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

# 删除下面这行
# from datetime import datetime
from airtest.core.api import *
from airtest.core.android import *
from airtest.cli.parser import cli_setup
from poco.drivers.std import StdPoco
ST.SNAPSHOT_QUALITY = 20
ST.SAVE_IMAGE = False # 关
poco = StdPoco()
android = Android()

'''
log截图：开关
ST.SAVE_IMAGE = True # 开
ST.SAVE_IMAGE = False # 关
'''

if not cli_setup():
#     auto_setup(__file__, logdir=True, devices=["Android:///",])
    auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/127.0.0.1:16416",])
    # auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/5ca91dd2",])
#     auto_setup(__file__, logdir=True, devices=["android://127.0.0.1:5037/R5CW203G5VF",])

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
cg_shop_coins_9999 = poco("bflPrice",type="Label",text="9,999") # cash go 商店 coins 9999档
btnBuy = poco("btnBuy") # 购买按钮
btnShare = poco("btnShare") # 小岛完成后的分享按钮
prize_lbl1 = poco("prize_lbl1") # 领奖按钮
btnCollect = poco("btnCollect") # 领奖按钮
label_id = poco("label_id") # ID的label
level_label = poco("level_label") # 等级的label
setting = poco(text="setting_node").child(text="enter_btn") # 大厅的setting按钮
cg_build = poco("slot_menu_img2") # cash go 的
bfl_pro = poco("bfl_pro")
slot_coins = poco("btn_add_coins")# 顶部 coins icon +号按钮
cg_btn_spin = poco("btn_spin") # spin按钮
cg_btn_add = poco("btn_add") # bet +
cg_btn_rud = poco("btn_rud") # bet -
cg_btn = poco("Button")
num = 1

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

def buy_coins_and_collect_optimized():
    """优化后的购买金币并领奖函数"""
    coin_template = Template(r"tpl1743048545890.png", record_pos=(0.322, 0.138), resolution=(1080, 2340))
    buy_template = Template(r"tpl1743048578447.png", record_pos=(0.006, 0.286), resolution=(1080, 2340))
    for _ in range(3):
        touch(coin_template)
        touch(buy_template)
        if_click(prize_lbl1)
        sleep(1)

def cash_go_build_ooc():
    """cash go 建造过程中金币不足, 触发ooc后的商店购买金币操作"""
    # 暂时关闭截图
    ST.SAVE_IMAGE = False
    if_click(btnClose)  # 关闭ooc
    sleep(1)
    touch(slot_coins)  # 点击右上角+号按钮，跳转商店
    sleep(1)
    buy_coins_and_collect_optimized()
    if_click(cg_build)  # 点击build页签返回建造界面，此处用的build的红点定位的

def update_node_status():
    """更新节点信息"""
    global btn_share_exists, btn_collect_exists, shop_img17_exists
    btn_share_exists = btnShare.exists()
    btn_collect_exists = btnCollect.exists()
    shop_img17_exists = shop_img17.exists()

def cash_go_build():
    """cash go 建造升级"""
    # 缓存节点信息
    update_node_status()

    while True:
        try:
            '''死循环，一直建造小岛'''
            if btn_share_exists:
                # 从UI元素中获取文本内容
                text = poco("bfl_rank_num").get_text()
                # 以 # 号为分隔符，提取等级信息
                cg_kingdom_index = text.split('#')[-1]
                # 将小岛等级转换为整数
                kingdom_level = int(cg_kingdom_index)
                # 判断小岛等级是否达到 168
                if kingdom_level == 71:
                    log(f'建造到{cg_kingdom_index}级结束，退出程序')
                    if_click(btnCollect)
                    break
                log(f'{cg_kingdom_index}级小岛完成')
                if_click(btnCollect)
                sleep(6)
                # 更新节点信息
                update_node_status()
            elif btn_collect_exists:
                if_click(btnCollect)
                # 更新节点信息
                update_node_status()
            elif shop_img17_exists and if_click(shop_img17):
                cash_go_build_ooc()
                # 更新节点信息
                update_node_status()
                continue
            else:
                ST.SAVE_IMAGE = True  # 开
                if_click(btnBuild)
                if_click(btnBuild)
                # 更新节点信息
                update_node_status()
        except Exception as e:
            log(f"发生异常: {e}")
            sleep(1)

if __name__ == '__main__':
    log("==== start ====")
    cash_go_build()
    # if_click(cg_btn)









