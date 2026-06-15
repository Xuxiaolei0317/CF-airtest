#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Airtest 环境与设备初始化。业务脚本请勿在此导入节点模块。

使用方式:
    # 方法1: 直接导入 (推荐)
    from airtest_booststrap import ST, dev, poco, connect_device

    # 方法2: 指定设备序列号
    import os
    os.environ["ANDROID_SERIAL"] = "YOUR_DEVICE_ID"
    from airtest_booststrap import ST, dev, poco, connect_device

    # 方法3: 手动连接
    from airtest_booststrap import init_device
    dev = init_device("Android:///YOUR_DEVICE_ID")

配置说明:
    AIRTEST_RPC_DISABLE: 复用 RPC 连接，减少初始化开销 (默认 1)
    AIRTEST_NO_CLEANUP: 保留 ADB 端口转发，适合反复运行 (默认 1)
    SNAPSHOT_QUALITY: 截图质量 0-30 (默认 20)
    ANDROID_SERIAL: 设备序列号，优先从环境变量读取
"""
from airtest.core.api import *  # Airtest 全局配置、日志初始化与设备连接
from poco.drivers.std import StdPoco  # 标准 Poco 驱动，用于查询和操作游戏 UI 控件树
from airtest.core.cv import Template  # 业务脚本可复用的图片模板类型
from airtest.cli.parser import cli_setup  # 命令行参数解析
import os  # 读取设备序列号环境变量
import logging  # 控制第三方库日志级别
import re  # 解析设备序列号


# ============================================================
# 配置常量
# ============================================================

# 默认设备序列号 (从环境变量读取，支持多设备切换)
_DEFAULT_ANDROID_SERIAL = os.environ.get("ANDROID_SERIAL", "R5CYA29D4SP")

# 设备序列号映射表 (别名 -> 实际序列号)
DEVICE_MAP = {
    "dev1": "R5CYA29D4SP",       # 开发机1
    "dev2": "YOUR_DEV2_SERIAL",   # 开发机2
    "ci": "CI_DEVICE_SERIAL",     # CI/CD 环境设备
}

# 降低第三方库日志噪音
for logger_name in ["airtest", "root", "adb", "rotation", "nbsp", "touch_methods", "poco"]:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.ERROR)


# ============================================================
# 核心函数
# ============================================================

def resolve_serial(serial=None):
    """解析设备序列号，支持别名映射和环境变量覆盖。
    
    优先级: 参数 > 环境变量 > 别名映射 > 默认值
    """
    if serial:
        # 参数优先
        return DEVICE_MAP.get(serial, serial)
    
    # 环境变量覆盖
    env_serial = os.environ.get("ANDROID_SERIAL")
    if env_serial:
        return DEVICE_MAP.get(env_serial, env_serial)
    
    # 别名映射
    if _DEFAULT_ANDROID_SERIAL in DEVICE_MAP:
        return DEVICE_MAP[_DEFAULT_ANDROID_SERIAL]
    
    return _DEFAULT_ANDROID_SERIAL


def resolve_device_uri(serial=None, platform=None):
    """构建设备连接 URI。
    
    Args:
        serial: 设备序列号或别名
        platform: 平台类型，None 则自动检测
    
    Returns:
        完整的设备连接 URI 字符串
    """
    serial = resolve_serial(serial)
    
    # 自动检测平台
    if platform is None:
        platform = detect_platform(serial)
    
    if platform == "android":
        return f"Android:///{serial}?cap_method=JAVACAP&touch_method=MINITOUCH"
    elif platform == "ios":
        return f"iOS:///{serial}"
    elif platform == "windows":
        return f"Windows:///"
    else:
        raise ValueError(f"不支持的平台类型: {platform}")


def detect_platform(serial=None):
    """根据设备信息检测平台类型。
    
    简单判断: 尝试通过 adb 获取设备信息。
    """
    try:
        from airtest.core.android.android import Android
        android = Android()
        devices = android.list_app()
        if devices:
            return "android"
    except Exception:
        pass
    
    return "android"  # 默认 Android


def init_device(serial=None, device_uri=None):
    """初始化和连接设备。
    
    Args:
        serial: 设备序列号或别名
        device_uri: 完整的设备 URI (覆盖 serial 参数)
    
    Returns:
        连接的设备对象
    """
    if device_uri:
        dev = connect_device(device_uri)
    else:
        device_uri = resolve_device_uri(serial)
        dev = connect_device(device_uri)
    
    # 复用 RPC 连接
    os.environ["AIRTEST_RPC_DISABLE"] = "1"
    os.environ["AIRTEST_NO_CLEANUP"] = "1"
    
    # 配置截图质量
    ST.SNAPSHOT_QUALITY = 20
    ST.SAVE_IMAGE = True
    
    # 优化图像识别和点击参数
    ST.THRESHOLD_STRICT = 0.65
    ST.FIND_TIMEOUT = 2
    ST.TOUCH_DURATION = 0.05
    
    return dev


def init_poco(device, auto_refresh=True, refresh_rate=0.5):
    """初始化 Poco 驱动。
    
    Args:
        device: 已连接的设备对象
        auto_refresh: 是否自动刷新控件树 (建议 False 以提速)
        refresh_rate: 控件树刷新间隔 (秒)
    
    Returns:
        Poco 驱动对象
    """
    return StdPoco(
        device=device,
        refresh_rate=refresh_rate,
        timeout=3,
        auto_refresh=auto_refresh,
        implicit_refresh=False,
    )


def close_all_popups(poco, max_tries=3, interval=0.3):
    """关闭所有常见弹窗。
    
    Args:
        poco: Poco 驱动对象
        max_tries: 最大尝试次数
        interval: 每次尝试间隔 (秒)
    
    Returns:
        True 如果关闭了弹窗，False 否则
    """
    closed = False
    close_node_names = ["btn_close", "close_btn", "mask_close", "btnCancel", "btnCancel2"]
    
    for _ in range(max_tries):
        clicked = False
        for name in close_node_names:
            try:
                node = poco(name)
                if node.exists():
                    node.click()
                    sleep(0.2)
                    clicked = True
                    closed = True
            except Exception:
                pass
        if not clicked:
            break
    
    return closed


# ============================================================
# 自动初始化 (直接导入时执行)
# ============================================================

# 日志初始化
auto_setup(__file__, logdir=True)

# 连接设备
dev = init_device()

# 初始化 Poco
poco = init_poco(dev, auto_refresh=False)

# 导出公共接口
__all__ = ["ST", "dev", "poco", "init_device", "init_poco", "resolve_serial", 
           "resolve_device_uri", "close_all_popups", "detect_platform", "DEVICE_MAP"]
