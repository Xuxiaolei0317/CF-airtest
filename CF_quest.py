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
    

