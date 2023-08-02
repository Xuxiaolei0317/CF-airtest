# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

from datetime import datetime
from airtest.core.api import *
from airtest.core.android import *
from airtest.cli.parser import cli_setup
from poco.drivers.std import StdPoco


poco = StdPoco()
android = Android()

# log截图：开关
# ST.SAVE_IMAGE = True # 开
# ST.SAVE_IMAGE = False # 关

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=["Android:///",])
    # auto_setup(__file__, logdir=True, devices=["Android:///127.0.0.1:7555",])
    # auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/d8c92411",])
    # auto_setup(__file__, logdir=True, devices=["android://127.0.0.1:5037/R5CW203G5VF?cap_method=MINICAP&touch_method=MAXTOUCH&",])
    
    

# 节点

setting = poco(text="setting_node").child(text="enter_btn") # 大厅的setting按钮
SETTINGS_1 = poco(text("SETTINGS"))
Template(r"tpl1689748424604.png", record_pos=(0.434, -0.101), resolution=(1920, 1080)) # 设置按钮
Template(r"tpl1689748433894.png", record_pos=(0.265, -0.006), resolution=(1920, 1080)) # 切换多语按钮

label_id = poco("label_id") # ID的label
btn_close = poco("btn_close") # 活动关闭按钮
# cash_frenzy = poco("android.widget.TextView") # 桌面的CF图标
# English = poco(text="item_1".child(text="language_btn"))
def if_click(name):
    """判断节点是否存在; 存在返回:True 并点击该节点; 节点不存在返回:False;"""
    if name.exists():
        name.click()
        return True
    else:
        return False
    
print("========start=========")

# cash_frenzy.click()
if_click(setting)



