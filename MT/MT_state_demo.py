#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MT 状态机最小接入示例。

默认假设游戏已经在主界面；如果要让脚本负责启动，可取消 launch_game 相关注释。
"""

import sys
from pathlib import Path

from airtest.core.api import sleep

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import dev, poco

from MT_main import GameActions, LaunchActions
from MT_state_machine import create_state_machine


GA = GameActions(poco)
LA = LaunchActions(dev, poco_driver=poco)
SM = create_state_machine(poco)


def enter_guild_by_state():
    """演示同一个公会入口进入后，由状态机判断已加入/未加入两种状态。"""
    state = SM.detect_state(verbose=True)
    if state.name == "UNKNOWN":
        SM.dump_unknown("before_enter_guild")

    result = SM.go_to(
        {"GUILD_HOME", "GUILD_NOT_JOINED"},
        action=lambda: GA.click("main.footer_guild_friend"),
        timeout=10,
    )

    if result.name == "GUILD_HOME":
        print("✅ 已进入公会主页，可以继续执行公会内任务")
        return True
    if result.name == "GUILD_NOT_JOINED":
        print("✅ 当前账号未加入公会，可以进入加入/申请公会流程")
        return True

    print(f"❌ 进入公会失败，当前状态：{result.name}")
    SM.dump_unknown("enter_guild_failed", state=result)
    return False


if __name__ == "__main__":
    print("MT 状态机示例开始")
    # LA.launch_game()
    # sleep(5)
    # LA.tap_launch_confirm()
    sleep(0.5)
    enter_guild_by_state()
    print("MT 状态机示例结束")
