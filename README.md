# cf-airtest

Airtest 自动化测试框架，基于 Cocos2d-x 多平台游戏开发。

## 目录结构

```
cf-airtest/
├── README.md                    # 项目说明文档
├── __init__.py
├── airtest_booststrap.py        # Airtest/Poco 公共初始化配置
├── run_tests.py                 # 统一测试入口
├── requirements.txt             # Python 依赖
├── node_generator_web.py        # 本地 Poco 节点生成网页工具
├── poco_node_listener_web.py    # PocoDebug 点击日志网页监听工具
├── node_dumps/                  # Poco 节点转储数据
├── CF/                          # Cash Frenzy 测试模块
│   ├── __init__.py
│   ├── CF_nodes.json            # CF 节点库 JSON 数据
│   ├── CF_nodes.py              # CF 节点定义
│   ├── CF_test.py               # CF 主测试
│   ├── CF_test_theme.py         # CF 主题相关测试
│   ├── CF_CashGo.py             # CF CashGo 模块
│   ├── CF_quest.py              # CF 任务模块
│   ├── CF_CashGoFlow.py         # CF CashGo 流程编排
│   ├── CF_state_machine.py      # CF 状态机流程
│   ├── cf_behavior_tree.py      # CF 行为树流程
│   ├── cf_flow_runner.py        # CF 流程运行器
│   └── cash_go_build.py         # CashGo build 流程脚本
├── MT/                          # Mega Tycoon 测试模块
│   ├── __init__.py
│   ├── MT_nodes.json            # MT 节点库 JSON 数据
│   ├── MT_states.json           # MT 状态机配置
│   ├── MT_nodes.py              # MT 节点定义
│   ├── MT_main.py               # MT 通用方法和模块流程
│   ├── MT_test.py               # MT 测试用例入口/示例
│   ├── MT_new_user.py           # MT 新用户流程脚本
│   ├── MT_quest_test.py         # MT 任务测试
│   ├── MT_state_machine.py      # MT 状态机流程
│   └── MT_state_demo.py         # MT 状态机示例
└── log/                         # Airtest 日志
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 连接设备

```bash
# 设置设备序列号或别名 (可选；只连接一台 Android 设备时会自动检测)
export ANDROID_SERIAL=YOUR_DEVICE_ID
```

### 3. 运行测试

```bash
# 列出所有可用测试
python run_tests.py --list

# 运行 MT 默认入口 (MT_main)
python run_tests.py --game mt

# 运行 CF CashGo 模块，模块名可写 CashGo 或 CF_CashGo
python run_tests.py --game cf --module CashGo

# 指定设备序列号
python run_tests.py --serial YOUR_DEVICE_ID
```

## 节点与脚本分层

`CF_nodes.py` / `MT_nodes.py` 是节点文件，将获取到的 Poco 节点、Template 图片节点按页面或模块封装成类，后续测试文件直接调用。

MT 项目约定：

- `MT_nodes.py`：只维护 MT 项目所有节点信息，包括主界面、slot、build、guild、stamp、store、quest 等节点分组，以及必要的旧字段兼容别名。
- `MT_main.py`：维护 MT 项目对应模块的方法和通用函数，包括启动/关闭游戏、Poco 重连、节点点击、文本读取、数值转换、弹窗关闭、spin/build/attack/steal/quest 等流程方法。
- `MT_*.py` 测试脚本：只放具体测试用例或场景编排，通过导入 `MT_nodes.py` 的节点和 `MT_main.py` 的方法来执行。

## 功能模块的自动化脚本命名规则

每个功能模块对应一个自动化脚本，脚本名称为 `CF_功能模块名.py` 或 `MT_功能模块名.py`。

## 项目 Agent Skill

项目级 Cursor Agent Skill 位于 `.cursor/skills/airtest-change-guidelines/SKILL.md`，用于约束后续 Airtest 自动化变更：

- 每次新增一些功能或者逻辑的时候添加中文注释
- 更新项目说明文档

## 新脚本初始化方式

后续新增自动化脚本统一复用 `airtest_booststrap.py` 中的设备连接、Airtest 参数和 Poco 初始化配置。直接导入时会自动连接设备并初始化 `poco`；需要指定设备时，可先设置 `ANDROID_SERIAL`，或通过 `run_tests.py --serial` 传入。

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, dev, poco, close_all_popups

ST.SAVE_IMAGE = True  # 调试阶段打开截图
```

## 多设备切换

在 `airtest_booststrap.py` 的 `DEVICE_MAP` 中配置设备别名。设备解析优先级为：函数参数或 `--serial` > `ANDROID_SERIAL` > adb 自动检测单台在线 Android 设备。

```python
DEVICE_MAP = {
    "dev1": "R5CYA29D4SP",
    "dev2": "YOUR_DEV2_SERIAL",
    "ci": "CI_DEVICE_SERIAL",
}
```

然后使用:

```bash
# 方式1: 环境变量
ANDROID_SERIAL=dev1 python run_tests.py --game mt

# 方式2: 参数
python run_tests.py --serial dev1
```

```python
# 方式3: 业务代码中手动初始化
from airtest_booststrap import init_device, init_poco

dev = init_device("dev1")
poco = init_poco(dev)
```

## Git 忽略

如果日志文件夹下生成的 png 图片太多，可以添加到全局 gitignore:

```bash
git config --global core.excludesfile ~/.gitignore_global
echo "log/" >> ~/.gitignore_global
```
