# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

from airtest.core.api import *
from airtest.core.android import *
from airtest.cli.parser import cli_setup
from poco.drivers.std import StdPoco
# from CF_nodes import objects

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
    auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/5ca91dd2",])

# cf = objects()
# cf_cn = cf_common_nodes()
# cf_lf = cf_cn.cf_lobby_footer_nodes()


if __name__ == '__main__':
    log("==== start ====")
    b_archer_token = poco("token_node").child(type="Label").get_text()[]
    print(b_archer_token)
#     new = poco("new_sp")
#     cf.if_click(new)

    
    
    
    
    

