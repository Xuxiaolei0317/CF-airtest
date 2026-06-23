#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airtest 自动化测试统一入口。

用法:
    python run_tests.py                          # 运行 MT 维护流程测试
    python run_tests.py --game cf                # 运行 CF 系列测试
    python run_tests.py --game mt                # 运行 MT 系列测试
    python run_tests.py --game cf --module CashGo  # 运行 CF CashGo 模块
    python run_tests.py --serial YOUR_DEVICE_ID   # 指定设备序列号
    python run_tests.py --list                   # 列出所有可用测试
"""
import sys
import os
import argparse
import runpy
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
AIRTEST_ROOT = PROJECT_ROOT


def list_tests():
    """列出所有可用的测试模块"""
    print("可用测试模块:")
    print()
    
    # CF 测试
    cf_dir = AIRTEST_ROOT / "CF"
    if cf_dir.exists():
        print("  CF (Cash Frenzy):")
        for f in sorted(cf_dir.glob("CF_*.py")):
            name = f.stem.replace("CF_", "")
            print(f"    --game cf --module {name}  ({f.name})")
        print()
    
    # MT 测试
    mt_dir = AIRTEST_ROOT / "MT"
    if mt_dir.exists():
        print("  MT (Mansion Quest):")
        for f in sorted(mt_dir.glob("MT_*.py")):
            name = f.stem.replace("MT_", "")
            print(f"    --game mt --module {name}  ({f.name})")
        print()


def resolve_script_path(game, module):
    """根据游戏和模块名找到实际脚本文件，兼容 main 与 MT_main 写法。"""
    game_dir = AIRTEST_ROOT / game.upper()
    prefix = f"{game.upper()}_"
    module_stem = module if module.startswith(prefix) else f"{prefix}{module}"
    script_path = game_dir / f"{module_stem}.py"

    if not script_path.exists():
        available = ", ".join(sorted(f.stem for f in game_dir.glob(f"{prefix}*.py")))
        raise FileNotFoundError(
            f"找不到模块脚本: {script_path}\n"
            f"可用模块: {available or '无'}"
        )

    return game_dir, script_path


def run_test(game, module, serial):
    """运行指定的测试模块"""
    # 设置设备序列号
    if serial:
        os.environ["ANDROID_SERIAL"] = serial

    try:
        game_dir, script_path = resolve_script_path(game, module)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False

    # 子脚本大量使用同目录导入，例如 from MT_nodes import ...
    for path in (str(game_dir), str(AIRTEST_ROOT), str(PROJECT_ROOT)):
        if path not in sys.path:
            sys.path.insert(0, path)

    old_argv = sys.argv[:]
    try:
        sys.argv = [str(script_path)]
        runpy.run_path(str(script_path), run_name="__main__")
        print(f"✅ {game.upper()} 模块 {script_path.stem} 运行完成")
    except ImportError as e:
        print(f"❌ 无法导入模块 {script_path.stem}: {e}")
        return False
    finally:
        sys.argv = old_argv

    return True


def main():
    parser = argparse.ArgumentParser(description="Airtest 自动化测试入口")
    parser.add_argument("--game", type=str, choices=["cf", "mt"], default="mt",
                        help="目标游戏模块 (默认: mt)")
    parser.add_argument("--module", type=str, default="MT_main",
                        help="测试模块名称 (默认: MT_main)")
    parser.add_argument("--serial", type=str, default=None,
                        help="设备序列号 (覆盖配置文件中的默认值)")
    parser.add_argument("--list", action="store_true",
                        help="列出所有可用测试模块")
    
    args = parser.parse_args()
    
    if args.list:
        list_tests()
        return
    
    print(f"开始运行: {args.game.upper()} - {args.module}")
    if args.serial:
        print(f"设备序列号: {args.serial}")
    print("-" * 50)
    
    success = run_test(args.game, args.module, args.serial)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
