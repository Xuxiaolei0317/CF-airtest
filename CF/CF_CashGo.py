# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import sys
import random
from pathlib import Path
from airtest.core.api import *

# 允许从 CF 子目录直接运行脚本时导入上一级的公共初始化模块。
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, poco

from CF_nodes import common_nodes as cf
# mt = common_nodes()

# 打开截图功能
ST.SAVE_IMAGE = True
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
build_finish_dialog = poco("build_finish_dialog") # 建造完成弹窗
build_chest_show_dialog = poco("build_chest_show_dialog") # 建造宝箱弹窗
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

def is_ooc_popup_exists():
    """判断金币不足 OOC 弹窗是否出现。"""
    return shop_img17.exists() or btnClose.exists()

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
    # ST.SAVE_IMAGE = True
    if_click(btnClose)  # 关闭ooc
    sleep(1)
    if_click(slot_coins)  # 点击右上角+号按钮，跳转商店
    sleep(1)
    buy_coins_and_collect_optimized()
    if_click(cg_build)  # 点击build页签返回建造界面，此处用的build的红点定位的

def update_node_status():
    """更新节点信息"""
    global btn_share_exists, build_finish_dialog_exists, build_chest_show_dialog_exists, shop_img17_exists
    btn_share_exists = btnShare.exists()
    build_finish_dialog_exists = build_finish_dialog.exists()
    build_chest_show_dialog_exists = build_chest_show_dialog.exists()
    shop_img17_exists = is_ooc_popup_exists()

def cash_go_build(kingdom_max):
    """cash go 建造升级"""
    # 缓存节点信息
    update_node_status()

    while True:
        try:
            '''死循环，一直建造小岛'''
            # 通过分享按钮存在，判断小岛等级是否达到最大等级，达到则领取奖励并退出程序
            if btn_share_exists:
                # 从UI元素中获取文本内容
                text = poco("bfl_rank_num").get_text()
                # 以 # 号为分隔符，提取等级信息
                cg_kingdom_index = text.split('#')[-1]
                # 将小岛等级转换为整数
                kingdom_level = int(cg_kingdom_index)
                # 判断小岛等级是否达到 168
                if kingdom_level == kingdom_max:
                    print(f'建造到{cg_kingdom_index}级结束，退出程序')
                    btnCollect.wait(2).click()
                    break
                print(f'{cg_kingdom_index}级小岛完成')
                sleep(6)
                btnCollect.wait(5).click()
                # 更新节点信息
                update_node_status()

            # elif build_finish_dialog_exists:
            #     if_click(btnCollect)
            #     # 更新节点信息
            #     update_node_status()
            #     sleep(6)
            #     if build_chest_show_dialog_exists:
            #         if_click(btnCollect)
            #         # 更新节点信息
            #         update_node_status()
            elif shop_img17_exists:
                cash_go_build_ooc()
                # 更新节点信息
                update_node_status()
                continue
            else:
                # ST.SAVE_IMAGE = True  # 开
                if_click(btnBuild)
                sleep(0.5)
                # 更新节点信息
                update_node_status()
                # print(f'add 1')
        except Exception as e:
            print(f"发生异常: {e}")
            sleep(1)

if __name__ == '__main__':
    print("==== start ====")
    cash_go_build(180)
    # if_click(cg_btn)












