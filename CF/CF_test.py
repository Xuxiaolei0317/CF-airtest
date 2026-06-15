#!/usr/bin/env python3
# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import sys
import time
from pathlib import Path
from airtest.core.api import auto_setup, exists, log, touch, sleep

# 导入公共初始化模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, dev, poco

# 导入节点
from CF_nodes import common_nodes, GameActions

# 打开截图功能
ST.SAVE_IMAGE = True

# 初始化游戏动作工具
game_actions = GameActions(poco)


def if_click(name):
    '''判断节点是否存在; 存在返回:True 并点击该节点; 节点不存在返回:False;'''
    if name.exists():
        name.click()
        return True
    else:
        return False


def wait_and_click(name, timeout=3):
    '''等待节点出现并点击'''
    end_time = time.time() + timeout
    while time.time() < end_time:
        if name.exists():
            name.click()
            return True
        sleep(0.3)
    return False


if __name__ == "__main__":
    log("==== start ====")
    
    # 获取建造按钮
    btnBuild = poco("btnBuild")  # cash go 建造按钮
    
    if wait_and_click(btnBuild, timeout=5):
        log("成功点击建造按钮")
    else:
        log("未找到建造按钮")
    
    log("==== end ====")
