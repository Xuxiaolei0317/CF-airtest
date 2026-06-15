# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

from datetime import datetime
from airtest.core.api import *
from airtest.core.android import *
from airtest.cli.parser import cli_setup
from poco.drivers.std import StdPoco
ST.SNAPSHOT_QUALITY = 20
# ST.SAVE_IMAGE = False # 关
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


btnClose = poco("btnClose") # cash go 弹窗关闭按钮
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
cg_build = poco("slot_menu_img2") # cash go 的
slot_coins = Template(r"tpl1689661026884.png", record_pos=(-0.407, -0.906), resolution=(1080, 2316)) # 顶部 coins icon +号按钮
cg_btn = poco("Button")
cg_build_index = poco('bfl_pro')
num = None

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
def bd_indexs():
    max_retries = 3  # 最大重试次数
    for _ in range(max_retries):
        try:
            sleep(0.5)  # 适当延迟
            build_index = cg_build_index.get_text()
            if build_index:  # 检查文本是否为空
                cg_build_indexs = build_index.split('/', 1)[0]
                build_indexs = int(cg_build_indexs)
                return build_indexs
        except Exception as e:
            log(f"获取 build_index 失败: {e}")
    log("达到最大重试次数，未能获取有效的 build_index")
    return None


def update_node_status():
    """更新节点信息"""
    global btn_share_exists, btn_collect_exists, shop_img17_exists
    btn_share_exists = btnShare.exists()
    btn_collect_exists = btnCollect.exists()
    shop_img17_exists = shop_img17.exists()

def cash_go_build():
    """cash go 建造升级"""
    global btn_share_exists, btn_collect_exists, shop_img17_exists
    # 缓存节点信息
    update_node_status()
    
    while True:
        try:
            # 每次循环都重新获取 build_indexs 的值
            bds = bd_indexs()
            if bds != 25:
                ST.SAVE_IMAGE = True  # 开
                if_click(btnBuild)
                log(bds)
            elif btn_share_exists:
                if_click(btnCollect)
                sleep(6)
                log(bds)
            elif btn_collect_exists:
                if_click(btnCollect)
                log(bds)
            # 更新节点信息
            update_node_status()
        except Exception as e:
            log(f"发生异常: {e}")
            sleep(1)
            

       

if __name__ == '__main__':
    log("==== start ====")
    cash_go_build()
#     print(build_indexs)
    text("hello airtest")

    
 




















