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
│   ├── CF_theme_traversal.py    # CF 主题列表遍历/Loading 异常记录脚本
│   ├── CF_theme_traversal_tree.py # CF 主题遍历专用行为树
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

# 运行 CF 主题遍历脚本；主题列表可在脚本 THEME_IDS 中维护
python run_tests.py --game cf --module theme_traversal

# 指定设备序列号
python run_tests.py --serial YOUR_DEVICE_ID

# 直接运行业务脚本时也支持指定设备
python MT/MT_test.py --serial YOUR_DEVICE_ID

# 直接运行 CF 主题遍历脚本时，可临时覆盖主题列表和停留时长
python CF/CF_theme_traversal.py --theme-ids 122,123,124 --stay-seconds 15
```

## 节点与脚本分层

`CF_nodes.py` / `MT_nodes.py` 是节点文件，将获取到的 Poco 节点、Template 图片节点按页面或模块封装成类，后续测试文件直接调用。

MT 项目约定：

- `MT_nodes.py`：只维护 MT 项目所有节点信息，包括主界面、slot、build、guild、stamp、store、quest 等节点分组，以及必要的旧字段兼容别名。
- `MT_main.py`：维护 MT 项目对应模块的方法和通用函数，包括启动/关闭游戏、Poco 重连、点号路径节点点击、文本读取、数值转换、弹窗关闭、spin/build/attack/steal/quest 等流程方法。
- `MT_*.py` 测试脚本：只放具体测试用例或场景编排，优先通过 `MT_main.py` 的 `GameActions` 点号路径入口执行。

CF / MT 节点引用统一约定：

- 节点配置 API 只使用 `group.key` 点号路径，例如 `theme.theme_bet_label`、`main.footer_spin`。
- `CF_nodes.py` / `MT_nodes.py` 的 `node_spec()`、`resolve_node()`、`node_text()` 都只接收点号路径，不再使用 `group, key` 两个参数。
- 状态机 JSON 的 `features` 也只写点号路径字符串，不再写 `["group", "key"]` 数组。
- `common_nodes` 只作为节点类入口，复杂流程脚本优先使用 `GameActions` 的点号路径方法。

CF / MT 测试脚本优先使用 `GameActions` 的点号路径快捷入口：

```python
game_actions.click("theme.theme_bet_label")
bet_text = game_actions.text("theme.theme_bet_label")
bet_num = game_actions.extract_number(bet_text)
```

## CF 主题遍历脚本

`CF/CF_theme_traversal.py` 用于遍历大厅主题列表。脚本会按主题 ID 顺序执行：先确认当前在大厅，再通过 `CF/CF_theme_traversal_tree.py` 的主题遍历行为树调用 Lua 打开主题选 bet 界面、点击高级房进入按钮，并验证是否进入主题；如果进入动作后能处理到主题内弹窗，也会直接判定为进入成功。进入主题后默认不额外停留，会快速清理遮挡弹窗、点击返回大厅按钮并验证是否真正回到 `LOBBY_HOME`，然后继续下一个主题。失败留证时再导出现场，便于定位卡在 loading 进不去的主题。

- 默认主题列表维护在脚本内 `THEME_IDS`。
- 直接运行脚本时可以用 `--theme-ids 122,123`、`--theme-file theme_ids.txt` 或环境变量 `CF_THEME_IDS=122,123` 临时覆盖。
- 如果 Lua 后没有高级房入口，脚本会打印该主题并直接继续下一个主题。
- 如果主题进入超时，脚本会记录该主题 ID，重启游戏后继续验证下一个主题；默认超时 10 秒，可用 `CF_THEME_LOAD_TIMEOUT` 覆盖。
- 运行日志会输出 `[PERF]` 耗时点，包括设备检测/Poco 初始化、准备大厅、开始执行进入主题、Lua 打开选房、高级房点击、进入主题结果和返回大厅耗时，便于定位界面卡帧或初始化耗时。
- 每次触发进入主题前都会确认当前在大厅；大厅优先通过根节点 `LobbyScene`，并辅以设置/中部入口节点判断。如果不在大厅，会先清理通用弹窗，仍未恢复则重启游戏后继续。
- `loading2` 只用于进入动作后的异常识别：如果主题 Home 未出现、主题内弹窗也处理不到，并且 `loading2` 一直可见到超时，就记录为进入失败主题。
- 如需进入主题后停留并检查 Lua/Char Error，可通过 `--stay-seconds` 指定停留秒数；检测到时会保存截图并打印最近的 logcat 关键日志。
- 进入失败记录输出到 `log/theme_traversal/failed_theme_ids_*.txt`。
- 重启游戏优先使用 `CF_APP_PACKAGE`；未设置时会尝试读取当前前台应用包名，兜底值为 `slots.pcg.casino.games.free.android`。重启后如果停在 debug 启动页，脚本默认按横屏坐标使用 `CF_LAUNCH_CONFIRM_TAP=0.500,0.940` 点击居中靠下的 Confirm，避免启动页图片误识别；坐标不准时可通过环境变量覆盖。

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
