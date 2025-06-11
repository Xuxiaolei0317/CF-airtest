# -*- encoding=utf8 -*-
# 设定文件的编码格式为 UTF-8，确保代码文件能正确处理各种字符。
__author__ = "Xiaolei"
# 声明代码作者为 Xiaolei。

from airtest.core.api import *
# 从 airtest 核心 API 模块导入所有功能，方便后续使用 Airtest 提供的各种操作方法。
from airtest.core.android import *
# 从 airtest 安卓核心模块导入所有功能，用于操作 Android 设备。
from airtest.cli.parser import cli_setup
# 从 airtest 命令行解析模块导入 cli_setup 函数，用于命令行参数设置。
from poco.drivers.std import StdPoco
# 从 poco 标准驱动模块导入 StdPoco 类，用于 UI 元素的定位和操作。
from .CF_nodes import objects, common_nodes 
# 私有函数，整合的CF通用节点和
# 从当前目录导入 objects 和 common_nodes 模块，用于创建对象实例和调用方法。

ST.SNAPSHOT_QUALITY = 20
# 设置截图的质量为 20，数值越低，截图质量越差，文件体积越小。
ST.SAVE_IMAGE = False  # 关
# 关闭自动保存截图功能，运行过程中不会自动保存截图到日志中。

poco = StdPoco()
# 创建 StdPoco 实例，用于后续对 UI 元素进行定位和操作。
android = Android()
# 创建 Android 设备实例，用于后续对 Android 设备进行操作。
'''
log截图：开关
ST.SAVE_IMAGE = True # 开
ST.SAVE_IMAGE = False # 关
'''
# 注释说明如何开启和关闭日志截图功能。

if not cli_setup():
    # 检查命令行参数设置是否成功，如果未成功则进行自动设置。
    auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/RZ8R81D20ZT",])
    # 自动设置 Airtest 环境，指定日志目录，连接指定的 Android 设备。
#     auto_setup(__file__, logdir=True, devices=["Android://127.0.0.1:5037/127.0.0.1:16384",])
# 注释掉的自动设置语句，可用于连接另一个 Android 设备。

cf = objects()
cf_cn = common_nodes()
cf_lf = cf_cn.mansion().mansion_bc_btn
# 注释掉的代码，原本用于创建对象实例和调用方法，可能后续会启用。

if __name__ == '__main__':
    # 判断当前脚本是否作为主程序运行。
    log("==== start ====")
    # 在日志中记录程序开始运行的信息。
    text("hello airtest")
    # 在设备上模拟输入文本 "hello airtest"。    
    


    
        


    
    
    
    
    








