#!/usr/bin/env python3
# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import sys
from pathlib import Path
from airtest.core.api import ST

# 导入公共初始化模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import poco

# 导入节点和通用方法
from MT_main import GameActions

# 打开截图功能
ST.SAVE_IMAGE = True

# 初始化游戏动作工具
GA = GameActions(poco)

if __name__ == "__main__":
    print("MT 测试开始")
    GA.click("main.footer_guild_friend")
    GA.click("main.footer_stamp")
    GA.click("main.footer_spin")
    
    print("MT 测试结束")
