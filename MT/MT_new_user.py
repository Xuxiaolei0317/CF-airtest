#!/usr/bin/env python3
# -*- encoding=utf8 -*-
__author__ = "Xiaolei"

import sys
import random
import time
from pathlib import Path
from airtest.core.api import *

# 导入公共初始化模块
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, dev, poco

# 导入节点和通用方法
from MT_nodes import common_nodes as mt_nodes
from MT_main import GameActions , LaunchActions

# 打开截图功能
ST.SAVE_IMAGE = True

# 初始化游戏动作工具
GA = GameActions(poco)
LA = LaunchActions(dev, poco_driver=poco)

print("MT 新手流程测试开始")
# LA.launch_game()
# sleep(5)
# LA.tap_launch_confirm()
# 点击 Let's Play 按钮
GA.click_node(mt_nodes().letsplay_btn)
# 等待新手引导出现,10s
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_start_btn_1, timeout=10)
# 新手引导第一步 start 按钮
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_start_btn_1)
# 新手引导第2步 start 按钮
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_start_btn_2)
# 新手引导第三步 ,打印对话内容,然后点击对话框跳过按钮
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_word_label, timeout=5)
print(mt_nodes.mt_new_user_guide().new_user_guide_word_label.text())
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_mask_btn)
# 新手引导第四步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_word_label, timeout=5)
print(mt_nodes.mt_new_user_guide().new_user_guide_word_label.text())
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_mask_btn)
# 新手引导第五步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_word_label, timeout=5)
print(mt_nodes.mt_new_user_guide().new_user_guide_word_label.text())
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_mask_btn)
# 新手引导第六步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_word_label, timeout=5)
print(mt_nodes.mt_new_user_guide().new_user_guide_word_label.text())
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_mask_btn)
# 新手引导第七步,打印金币文本,然后点击收集按钮
print(mt_nodes.mt_new_user_guide().new_user_guide_coin_label.text())
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_collect_btn)
# 新手引导第八步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_word_label, timeout=5)
print(mt_nodes.mt_new_user_guide().new_user_guide_word_label.text())
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_mask_btn)
# 新手引导第九步，开始模拟经营1任务，打印任务文本,然后点击金币按钮次数用任务进度值决定，打印消耗金币值，对比金币余额，如果余额不足，则点击收集金币按钮
progress_value = mt_nodes.mt_new_user_guide().new_user_guide_progress_label.text()
progress_value = int(progress_value)
if progress_value > 0:
    for i in range(progress_value):
        GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_coins_btn)
        print(mt_nodes.mt_new_user_guide().new_user_guide_coins_label.text())
        sleep(0.5)
else:
    GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_collect_btn)
# 新手引导第十步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_word_label, timeout=5)
print(mt_nodes.mt_new_user_guide().new_user_guide_word_label.text())
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_mask_btn)
# 新手引导第十一步，开始模拟经营2任务，打印任务文本,然后点击金币按钮次数用任务进度值决定，打印消耗金币值，对比金币余额，如果余额不足，则点击收集金币按钮
progress_value = mt_nodes.mt_new_user_guide().new_user_guide_progress_label.text()
progress_value = int(progress_value)
if progress_value > 0:
    for i in range(progress_value):
        GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_coins_btn)
        print(mt_nodes.mt_new_user_guide().new_user_guide_coins_label.text())
        sleep(0.5)
else:
    GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_collect_btn)
# 新手引导第十二步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_word_label, timeout=5)
print(mt_nodes.mt_new_user_guide().new_user_guide_word_label.text())
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_mask_btn)
# 新手引导第十三步，开始模拟经营3任务，打印任务文本,然后点击金币按钮次数用任务进度值决定，打印消耗金币值，对比金币余额，如果余额不足，则点击收集金币按钮
progress_value = mt_nodes.mt_new_user_guide().new_user_guide_progress_label.text()
progress_value = int(progress_value)
if progress_value > 0:
    for i in range(progress_value):
        GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_coins_btn)
        print(mt_nodes.mt_new_user_guide().new_user_guide_coins_label.text())
        sleep(0.5)
else:
    GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_collect_btn)
# 新手引导第十四步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_word_label, timeout=5)
print(mt_nodes.mt_new_user_guide().new_user_guide_word_label.text())
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_mask_btn)
# 新手引导第十五步,等待下一个对话框出现,5s,打印对话内容,然后点击对话框跳过按钮
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_word_label, timeout=5)
print(mt_nodes.mt_new_user_guide().new_user_guide_word_label.text())
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_mask_btn)
# 新手引导第十六步,点击footer上的spin入口
GA.click_node(mt_nodes.mt_main().mt_ft_slot)
# 对话框出现，打印对话内容,然后点击对话框跳过按钮
GA.wait_for_node(mt_nodes.mt_new_user_guide().new_user_guide_word_text, timeout=5)
print(mt_nodes.mt_new_user_guide().new_user_guide_word_text)
GA.click_node(mt_nodes.mt_new_user_guide().new_user_guide_mask_btn)
# 新手引导第十七步,一直点击spin按钮，直到出现偷钱对话框，点击对话框，进入偷钱流程，偷钱结束后继续spin
while True:
    GA.click_node(mt_nodes.mt_main().mt_btn_spin)
    GA.wait_for_node(mt_nodes.mt_main().mt_slot_win_text, timeout=5)
    print(f"spin结果为：{mt_nodes.safe_text().mt_slot_win_text}")
    if mt_nodes.mt_main().mt_slot_win_text == "STEAL":
        GA.click_node(mt_nodes.mt_main().mt_slot_win_text)
        GA.wait_for_node(mt_nodes.mt_main().mt_slot_win_text, timeout=5)
        print(f"spin结果为：{mt_nodes.safe_text().mt_slot_win_text}")
        break
    else:
        continue
    sleep(0.5)

print("MT 新手流程测试结束")
