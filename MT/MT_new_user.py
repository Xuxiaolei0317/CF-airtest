#!/usr/bin/env python3
# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import sys
from pathlib import Path
from airtest.core.api import *

# 导入公共初始化模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, dev, poco

# 导入节点和通用方法
from MT_main import GameActions , LaunchActions

# 打开截图功能
ST.SAVE_IMAGE = True

# 初始化游戏动作工具
GA = GameActions(poco)
LA = LaunchActions(dev, poco_driver=poco)

def print_guide_word(timeout=5):
    GA.wait_for_node(GA.node("new_user.new_user_guide_word_label"), timeout=timeout)
    print(GA.text("new_user.new_user_guide_word_label"))
    GA.click("new_user.new_user_guide_mask_btn")


def finish_business_task():
    progress_value = int(GA.text("new_user.new_user_guide_progress_label", "0"))
    if progress_value > 0:
        for _ in range(progress_value):
            GA.click("new_user.new_user_guide_coins_btn")
            print(GA.text("new_user.new_user_guide_coins_label"))
            sleep(0.5)
    else:
        GA.click("new_user.new_user_guide_collect_btn")


print("MT 新手流程测试开始")
# LA.launch_game()
# sleep(5)
# LA.tap_launch_confirm()
# 点击 Let's Play 按钮
GA.click("new_user.letsplay_btn")
# 等待新手引导出现,10s
GA.wait_for_node(GA.node("new_user.new_user_guide_start_btn_1"), timeout=10)
# 新手引导第一步 start 按钮
GA.click("new_user.new_user_guide_start_btn_1")
# 新手引导第2步 start 按钮
GA.click("new_user.new_user_guide_start_btn_2")
# 新手引导第三步 ,打印对话内容,然后点击对话框跳过按钮
print_guide_word()
# 新手引导第四步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
print_guide_word()
# 新手引导第五步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
print_guide_word()
# 新手引导第六步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
print_guide_word()
# 新手引导第七步,打印金币文本,然后点击收集按钮
print(GA.text("new_user.new_user_guide_coin_label"))
GA.click("new_user.new_user_guide_collect_btn")
# 新手引导第八步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
print_guide_word()
# 新手引导第九步，开始模拟经营1任务，打印任务文本,然后点击金币按钮次数用任务进度值决定，打印消耗金币值，对比金币余额，如果余额不足，则点击收集金币按钮
finish_business_task()
# 新手引导第十步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
print_guide_word()
# 新手引导第十一步，开始模拟经营2任务，打印任务文本,然后点击金币按钮次数用任务进度值决定，打印消耗金币值，对比金币余额，如果余额不足，则点击收集金币按钮
finish_business_task()
# 新手引导第十二步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
print_guide_word()
# 新手引导第十三步，开始模拟经营3任务，打印任务文本,然后点击金币按钮次数用任务进度值决定，打印消耗金币值，对比金币余额，如果余额不足，则点击收集金币按钮
finish_business_task()
# 新手引导第十四步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
print_guide_word()
# 新手引导第十五步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
print_guide_word()
# 新手引导第十六步,点击footer上的spin入口
GA.click("main.footer_spin")
# 对话框出现，打印对话内容,然后点击对话框跳过按钮
print_guide_word()
# 新手引导第十七步,一直点击spin按钮，直到出现偷钱对话框，点击对话框，进入偷钱流程，偷钱结束后继续spin
while True:
    GA.click("slot.spin_btn")
    GA.wait_for_node(GA.node("slot.slot_win_label"), timeout=5)
    slot_win_text = GA.text("slot.slot_win_label")
    print(f"spin结果为：{slot_win_text}")
    if slot_win_text == "STEAL":
        GA.click("slot.slot_win_label")
        GA.wait_for_node(GA.node("slot.slot_win_label"), timeout=5)
        print(f"spin结果为：{GA.text('slot.slot_win_label')}")
        break
    sleep(0.5)

print("MT 新手流程测试结束")
