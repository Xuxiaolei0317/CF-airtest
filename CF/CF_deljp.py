# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

from datetime import datetime
from airtest.core.api import *
from airtest.core.android import *
from airtest.cli.parser import cli_setup
from poco.drivers.std import StdPoco

ST.SNAPSHOT_QUALITY = 20
# 暂时关闭截图
ST.SAVE_IMAGE = False

poco = StdPoco()
android = Android()

if not cli_setup():
    auto_setup(__file__, logdir=True, devices=["Android:///",])
#     auto_setup(__file__, logdir=True, devices=["Android:///127.0.0.1:7555",])
#     auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/d8c92411",])
#     auto_setup(__file__, logdir=True, devices=["android://127.0.0.1:5037/R5CW203G5VF",])

# debug按钮
debug = poco("Button",type="Button")
debug_theme = None
debug_theme_idlabel = None


# 继续截图
ST.SAVE_IMAGE = True

# poco("name").child("name").offspring("name") # 父节点选择

def if_click(name):
    """判断节点是否存在; 存在返回:True 并点击该节点; 节点不存在返回:False;"""
    if name.exists():
        name.click()
        return True
    else:
        return False

if __name__ == '__main__':
    print("====star====")
    

    