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
from CF_nodes import GameActions, common_nodes
from CF_state_machine import create_state_machine

# 打开截图功能
ST.SAVE_IMAGE = True

# 同步公共初始化里的 Poco，保证状态机和节点模块用同一个连接。
CF_nodes.poco = poco

# 初始化游戏动作工具
game_actions = GameActions(poco)
state_machine = create_state_machine(poco)


def cashgo_nodes():
    return common_nodes.cashgo().cg_build()


def enter_cash_go_by_state():
    """按状态机方式进入 Cash Go，并判断最终落在哪个 Cash Go 页面。"""
    state_machine.recover_blockers()
    state = state_machine.detect_state(verbose=True)

    if state.name in {"CASH_GO_BUILD", "CASH_GO_COMPLETE", "CASH_GO_OOC"}:
        return state

    if state.name == "LOBBY_HOME":
        return state_machine.go_to(
            {"CASH_GO_BUILD", "CASH_GO_COMPLETE", "CASH_GO_OOC"},
            action=lambda: game_actions.click("lobby.cash_go"),
            timeout=10,
        )

    state_machine.dump_unknown("before_enter_cash_go", state=state)
    return state


if __name__ == "__main__":
    log("==== start ====")
    theme_id = 122
    poco.agent.rpc.call(f"RunLua", f'LobbyThemeControl:getInstance():clickLobbyTheme({theme_id}, nil, "poco_automation")')
    log("==== end ====")
