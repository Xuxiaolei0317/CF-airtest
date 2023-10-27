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
    auto_setup(__file__, logdir=True, devices=["Android:///127.0.0.1:7555",])
    # auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/d8c92411",])
#     auto_setup(__file__, logdir=True, devices=["android://127.0.0.1:5037/R5CW203G5VF?cap_method=MINICAP&touch_method=MAXTOUCH&",])


# 继续截图
ST.SAVE_IMAGE = True


# sleep(3)

# shell("am force-stop slots.pcg.casino.games.free.android")


if __name__ == '__main__':
    print("====star====")
    
