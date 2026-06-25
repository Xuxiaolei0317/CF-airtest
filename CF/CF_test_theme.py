#!/usr/bin/env python3
# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import sys
from pathlib import Path

from airtest.core.api import log, sleep

# 导入公共初始化模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, poco

# 导入节点和状态机
import CF_nodes
from CF_nodes import GameActions
from CF_state_machine import create_state_machine

# 打开截图功能
ST.SAVE_IMAGE = True

# 同步公共初始化里的 Poco，保证状态机和节点模块用同一个连接。
CF_nodes.poco = poco

# 初始化游戏动作工具
game_actions = GameActions(poco)
state_machine = create_state_machine(poco)


def enter_theme_by_state():
    """按状态机方式进入，并判断最终落在哪个页面。"""
    state_machine.recover_blockers()
    state = state_machine.detect_state(verbose=True)

    if state.name in {"THEME_HOME"}:
        return state

    if state.name == "LOBBY_HOME":
        return state_machine.go_to(
            {"THEME_HOME"},
            action=lambda: game_actions.click_lobby_theme(122),
            timeout=10,
        )
    return state


if __name__ == "__main__":
    log("==== start ====")
    # 使用lua脚本进入某个主题
    # game_actions.click_lobby_theme(122)
    # 测试脚本优先使用 GameActions 的点号路径入口，减少 group/key 参数重复。
    theme_bet_label = game_actions.text("theme.theme_totalbet_label")
    print(game_actions.extract_number(theme_bet_label))
    log("==== end ====")
