# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import json
from airtest.core.api import *
from airtest.core.android import *
from airtest.cli.parser import cli_setup
from poco.drivers.std import StdPoco
import CF_nodes as cf

ST.SNAPSHOT_QUALITY = 20
ST.SAVE_IMAGE = False  # 关

poco = StdPoco()
android = Android()
'''
log截图：开关
ST.SAVE_IMAGE = True # 开
ST.SAVE_IMAGE = False # 关
'''

if not cli_setup():
#     auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/5ca91dd2",])
    auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/127.0.0.1:16480",])

cf_man = cf.common_nodes().mansion()
cf_obj = cf.objects()
# 点击 PLAY按钮
# cf_obj.if_click(cf_man.mansion_task_btn)
# sleep(1)
# # 点击可以选择的装饰，使用刷子建造
# cf_obj.if_click(cf_man.mansion_do_btn)
# sleep(1)
# # 装饰三选一确认
cf_obj.if_click(cf_man.mansion_item_btn)
# sleep(1)
# 剧情对话，点击确认
# cf_obj.if_click(cf_man.mansion_dialog_btn)
# num = 0
# while num < 30:
#     log("==== start ====")
#     # cf_man.mansion_task_btn
#     # 点击 PLAY按钮
#     cf_obj.if_click(cf_man.mansion_task_btn)
#     # 点击可以选择的装饰，使用刷子建造
#     cf_obj.if_click(cf_man.mansion_do_btn)
#     # 装饰三选一确认
#     cf_obj.if_click(cf_man.mansion_ensure_btn)
    
#     if cf_obj.if_exists(cf_man.mansion_ensure_btn):
#         # 装饰三选一确认
#         cf_obj.if_click(cf_man.mansion_ensure_btn)
#         # 剧情对话，点击确认
#         cf_obj.if_click(cf_man.mansion_dialog_btn)
    
#     num += 1