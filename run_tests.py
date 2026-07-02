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
import json
from datetime import datetime
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
    except RuntimeError as e:
        message = str(e)
        if "未检测到在线 Android 设备" in message:
            # 设备未连接是常见运行环境问题，入口层只提示处理方式，不输出完整 traceback。
            print(f"❌ {message}")
            print("请连接 Android 设备/模拟器，确认 USB 调试已授权，并通过 `adb devices` 可见。")
            return False
        raise
    finally:
        sys.argv = old_argv

    return True


def load_testlist(path):
    """读取测试清单，支持 JSON 和 YAML。"""
    file_path = Path(path).expanduser()
    if not file_path.is_absolute():
        file_path = PROJECT_ROOT / file_path

    if not file_path.exists():
        raise FileNotFoundError(f"找不到测试清单文件: {file_path}")

    suffix = file_path.suffix.lower()
    raw = file_path.read_text(encoding="utf-8")

    if suffix == ".json":
        data = json.loads(raw)
    elif suffix in {".yml", ".yaml"}:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("解析 YAML 需要安装 PyYAML: pip install pyyaml") from exc
        data = yaml.safe_load(raw)
    else:
        raise ValueError(f"暂不支持的测试清单格式: {suffix}，请使用 .json/.yaml")

    if not isinstance(data, dict):
        raise ValueError("测试清单根节点必须是对象，且包含 tests 数组")
    return file_path, data


def validate_testlist(data):
    """校验测试清单结构，返回可执行条目和错误信息。"""
    errors = []
    normalized_items = []

    tests = data.get("tests")
    if not isinstance(tests, list):
        return [], ["tests 字段缺失或不是数组"]

    seen_ids = set()
    for index, item in enumerate(tests, start=1):
        case_prefix = f"tests[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{case_prefix} 不是对象")
            continue

        case_id = str(item.get("id", "")).strip()
        game = str(item.get("game", "")).strip().lower()
        module = str(item.get("module", "")).strip()
        enabled = item.get("enabled", True)
        serial = item.get("serial")
        note = str(item.get("note", "")).strip()
        case_valid = True

        if not case_id:
            errors.append(f"{case_prefix}.id 不能为空")
            case_valid = False
        elif case_id in seen_ids:
            errors.append(f"{case_prefix}.id 重复: {case_id}")
            case_valid = False
        else:
            seen_ids.add(case_id)

        if game not in {"cf", "mt"}:
            errors.append(f"{case_prefix}.game 非法: {game}，仅支持 cf/mt")
            case_valid = False
        if not module:
            errors.append(f"{case_prefix}.module 不能为空")
            case_valid = False
        if not isinstance(enabled, bool):
            errors.append(f"{case_prefix}.enabled 必须是布尔值")
            case_valid = False

        if serial is not None and not isinstance(serial, str):
            errors.append(f"{case_prefix}.serial 必须是字符串")
            case_valid = False

        # 仅对通过基础校验的数据做标准化，避免执行层反复做字段兜底。
        if case_valid:
            normalized_items.append(
                {
                    "id": case_id,
                    "game": game,
                    "module": module,
                    "enabled": enabled,
                    "serial": serial,
                    "note": note,
                }
            )

    return normalized_items, errors


def write_testlist_report(list_path, list_name, summary):
    """写出测试清单运行结果，便于后续接 AI 分析。"""
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = PROJECT_ROOT / "log" / "testlist_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{run_id}_{list_name}.json"

    payload = {
        "run_id": run_id,
        "testlist_path": str(list_path),
        "summary": summary,
    }
    report_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report_path


def run_testlist(testlist_path, validate_only=False, stop_on_fail=False):
    """按测试清单批量执行模块，并输出汇总结果。"""
    try:
        file_path, data = load_testlist(testlist_path)
    except (FileNotFoundError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"❌ 读取测试清单失败: {exc}")
        return False

    items, errors = validate_testlist(data)
    if errors:
        print("❌ 测试清单校验失败:")
        for msg in errors:
            print(f"   - {msg}")
        return False

    print(f"✅ 测试清单校验通过: {file_path}")
    if validate_only:
        return True

    enabled_items = [item for item in items if item["enabled"]]
    disabled_count = len(items) - len(enabled_items)
    if not enabled_items:
        print("⚠️ 测试清单中没有可执行项（可能都被 enabled=false 禁用了）")
        return True

    results = []
    for index, item in enumerate(enabled_items, start=1):
        print(
            f"[{index}/{len(enabled_items)}] "
            f"{item['id']} -> {item['game'].upper()}:{item['module']}"
        )
        if item["note"]:
            print(f"   说明: {item['note']}")
        success = run_test(item["game"], item["module"], item["serial"])
        results.append(
            {
                "id": item["id"],
                "game": item["game"],
                "module": item["module"],
                "serial": item["serial"],
                "status": "passed" if success else "failed",
            }
        )
        if (not success) and stop_on_fail:
            print("⏹️ 命中失败即停策略，后续用例不再执行")
            break

    passed = sum(1 for result in results if result["status"] == "passed")
    failed = sum(1 for result in results if result["status"] == "failed")
    summary = {
        "name": str(data.get("name") or file_path.stem),
        "total_cases": len(items),
        "enabled_cases": len(enabled_items),
        "disabled_cases": disabled_count,
        "executed_cases": len(results),
        "passed_cases": passed,
        "failed_cases": failed,
        "results": results,
    }
    report_path = write_testlist_report(file_path, file_path.stem, summary)

    print("-" * 50)
    print("测试清单执行完成:")
    print(f"  清单名称: {summary['name']}")
    print(f"  总条目: {summary['total_cases']}")
    print(f"  执行条目: {summary['executed_cases']}")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  报告: {report_path}")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="Airtest 自动化测试入口")
    parser.add_argument("--game", type=str, choices=["cf", "mt"], default="mt",
                        help="目标游戏模块 (默认: mt)")
    parser.add_argument("--module", type=str, default="MT_main",
                        help="测试模块名称 (默认: MT_main)")
    parser.add_argument("--testlist", type=str, default="",
                        help="测试清单文件路径(.json/.yaml)，用于批量执行")
    parser.add_argument("--validate-testlist", action="store_true",
                        help="仅校验测试清单结构，不执行脚本")
    parser.add_argument("--stop-on-fail", action="store_true",
                        help="批量执行时遇到失败立即停止")
    parser.add_argument("--serial", type=str, default=None,
                        help="设备序列号 (覆盖自动检测结果)")
    parser.add_argument("--list", action="store_true",
                        help="列出所有可用测试模块")
    
    args = parser.parse_args()
    
    if args.list:
        list_tests()
        return

    if args.validate_testlist and not args.testlist:
        print("❌ --validate-testlist 需要和 --testlist 一起使用")
        sys.exit(1)

    if args.testlist:
        print(f"开始处理测试清单: {args.testlist}")
        print("-" * 50)
        success = run_testlist(
            args.testlist,
            validate_only=args.validate_testlist,
            stop_on_fail=args.stop_on_fail,
        )
        sys.exit(0 if success else 1)
    
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
    print("""Airtest 自动化测试统一入口。用法:
    python run_tests.py                          # 运行 MT 维护流程测试
    python run_tests.py --game cf                # 运行 CF 系列测试
    python run_tests.py --game mt                # 运行 MT 系列测试
    python run_tests.py --game cf --module CashGo  # 运行 CF CashGo 模块
    python run_tests.py --testlist testlists/smoke.json           # 按清单批量执行
    python run_tests.py --testlist testlists/smoke.json --validate-testlist # 仅校验清单
    python run_tests.py --serial YOUR_DEVICE_ID   # 指定设备序列号
    python run_tests.py --list                   # 列出所有可用测试
""")
    main()