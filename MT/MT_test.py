#!/usr/bin/env python3
# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

from socket import gaierror
import sys
import random
import time
from pathlib import Path
from airtest.core.api import *

# 导入公共初始化模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, dev, poco

# 导入节点和通用方法
# from MT_nodes import common_nodes as mt_nodes
# from MT_main import GameActions , LaunchActions

# 打开截图功能
ST.SAVE_IMAGE = True

# 初始化游戏动作工具
# GA = GameActions(poco)
# LA = LaunchActions(dev, poco_driver=poco)

if __name__ == "__main__":
    print("MT 测试开始")
    poco("node_footer").child("node_club").child("icon").click()

    poco("node_footer").child("node_stamp").child("icon").click()

    poco("node_footer").child("node_slot").child("btn").click()
    
    print("MT 测试结束")
