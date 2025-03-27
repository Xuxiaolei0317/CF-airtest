# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

from datetime import datetime
from airtest.core.api import *
from airtest.core.android import *
from airtest.cli.parser import cli_setup
from poco.drivers.std import StdPoco
ST.SNAPSHOT_QUALITY = 20
ST.SAVE_IMAGE = False # 关
poco = StdPoco()
android = Android()


poco = StdPoco()
android = Android()

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=["Android:///",])
#     auto_setup(__file__, logdir=True, devices=["Android:///127.0.0.1:7555",])
#     auto_setup(__file__, logdir=True, devices=["Android:///127.0.0.1:5555",])
#     auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/d8c92411",])
#     auto_setup(__file__, logdir=True, devices=["android://127.0.0.1:5037/R5CW203G5VF?cap_method=MINICAP&touch_method=MAXTOUCH&",])

btn_close = poco("btn_close") # 活动关闭按钮
close_btn = poco("close_btn") # 活动中心关闭按钮
desc = poco("desc") # lobby 气泡
btnClose = poco("btnClose") # cash go 弹窗关闭按钮
B_zone = poco(name="title_label",text="CHALLENGE")
# 继续截图
# ST.SAVE_IMAGE = True
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


# shell("am force-stop slots.pcg.casino.games.free.android")

if __name__ == '__main__':
    print("==========star===========")
    # if_exists(close_btn)
    touch(B_zone)
    


