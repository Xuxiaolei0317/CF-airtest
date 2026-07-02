# cf-airtest

Airtest 自动化测试框架，基于 Cocos2d-x 多平台游戏开发。

## 目录结构

```
cf-airtest/
├── README.md                    # 项目说明文档
├── airtest_booststrap.py        # Airtest/Poco 公共初始化配置
├── run_tests.py                 # 统一测试入口
├── requirements.txt             # Python 依赖
├── docs/                        # 工程规范和补充文档
│   └── project_conventions.md   # 项目结构/命名/入口约定
├── testlists/                   # 业务测试点清单（批量执行编排）
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
├── cocos2dx-lua/                  # Cocos2d-x Lua Poco SDK 接入文件
│   ├── README.md                  # SDK 接入说明
│   ├── DEBUG_CLICK_LOGGER.md      # 点击节点调试日志说明
│   └── poco/                      # 游戏工程内接入的 Poco Lua SDK
└── log/                         # Airtest 日志
```

## 快速开始

### 1. 安装 Python

推荐使用 Python 3.10 或 Python 3.11。Airtest、Poco、OpenCV 等自动化依赖对较新的 Python 版本可能存在兼容差异，不建议直接使用 Python 3.13/3.14。

```bash
python --version
# 或
python3 --version
```

### 2. 创建虚拟环境

建议在项目根目录创建独立虚拟环境，避免和本机其他 Python 项目的依赖冲突。

```bash
cd cf-airtest
python3 -m venv .venv
```

macOS / Linux 激活方式：

```bash
source .venv/bin/activate
```

Windows 激活方式：

```bash
.venv\Scripts\activate
```

### 3. 安装 Python 依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

项目依赖主要包括：

- `airtest`：Airtest 自动化框架，用于设备连接、截图、点击和图像识别。
- `pocoui` / `pocosdk`：Poco 控件树访问能力，用于读取和操作游戏 UI 节点。
- `opencv-python` / `numpy` / `Pillow`：图像识别和截图处理依赖。
- `requests`：HTTP 请求工具库。
- `pytest` / `pytest-html` / `allure-pytest`：测试执行和报告生成依赖。

安装完成后可以用下面命令快速验证 Python 依赖是否可用：

```bash
python -c "import airtest; import poco; import cv2; print('env ok')"
```

### 4. 安装 ADB

Android 自动化需要本机可用 `adb` 命令。

macOS 可通过 Homebrew 安装：

```bash
brew install android-platform-tools
```

Windows 可安装 Android SDK Platform Tools，并将 `adb.exe` 所在目录加入系统环境变量 `PATH`。

安装后检查：

```bash
adb version
adb devices
```

### 5. 连接设备

Android 设备需要开启开发者选项和 USB 调试，并在首次连接时允许当前电脑调试。

```bash
# 设置设备序列号或别名 (可选；只连接一台 Android 设备时会自动检测)
export ANDROID_SERIAL=YOUR_DEVICE_ID
```

Windows 可使用：

```bash
set ANDROID_SERIAL=YOUR_DEVICE_ID
```

如果 `adb devices` 能看到设备状态为 `device`，说明设备连接正常。多台设备在线时，需要通过 `ANDROID_SERIAL` 或 `--serial` 指定目标设备。运行入口未检测到在线设备时会直接提示连接和授权检查项，并以失败码退出，不再输出完整 traceback。

被测游戏包需要开启 Poco SDK，否则 Airtest 可以连接设备，但脚本无法读取游戏 UI 控件树。CF / MT 项目请使用最新 debug 包，启动页勾选 Poco debug 按钮后再进入游戏。

### 6. 接入 Cocos2d-x Lua Poco SDK

当前仓库保留了一份已接入使用的 Cocos2d-x Lua Poco SDK 文件，位于 `cocos2dx-lua/poco/`。如果游戏工程需要补齐或对齐 Poco SDK，可将该目录作为整体放入游戏工程的 Lua 代码路径，并在测试包或 debug 包启动阶段初始化：

```lua
local PocoManager = require("poco.poco_manager")
PocoManager:init_server(15004)
```

如果游戏工程不能直接使用 `require`，请改用项目内的 Lua 加载接口，例如 `libFile.loadSrcCode("poco.poco_manager")` 或对应的斜杠路径。SDK 默认监听 `15004` 端口，Airtest/Poco 连接游戏控件树时会通过该端口读取节点、截图和屏幕尺寸等信息。

该 SDK 版本记录在 `cocos2dx-lua/poco/POCO_SDK_VERSION.lua`。当前版本额外包含 `RunLua` RPC 能力，只允许在 `bole.isPocoPackage` 或 `appDebugMode == true` 时执行，避免正式包误开放 Lua 执行入口。

### 7. 运行测试

团队默认使用 `run_tests.py` 作为统一入口（单模块、批量 testlist、CI 都从该入口触发）。  
业务脚本中的 `if __name__ == "__main__"` 主要用于开发期本地调试，不作为团队规范执行方式。

```bash
# 列出所有可用测试
python run_tests.py --list

# 运行 MT 默认入口 (MT_main)
python run_tests.py --game mt

# 运行 CF CashGo 模块，模块名可写 CashGo 或 CF_CashGo
python run_tests.py --game cf --module CashGo

# 运行 CF 主题遍历脚本；主题列表可在脚本 THEME_IDS 中维护
python run_tests.py --game cf --module theme_traversal

# 按测试清单批量执行（支持 .json/.yaml）
python run_tests.py --testlist testlists/smoke.json

# 仅校验测试清单结构（不执行）
python run_tests.py --testlist testlists/smoke.json --validate-testlist

# 批量执行遇到失败立即停止
python run_tests.py --testlist testlists/smoke.json --stop-on-fail

# 指定设备序列号
python run_tests.py --serial YOUR_DEVICE_ID

# 直接运行业务脚本时也支持指定设备
python MT/MT_test.py --serial YOUR_DEVICE_ID

# 直接运行 CF 主题遍历脚本时，可临时覆盖主题列表和停留时长
python CF/CF_theme_traversal.py --theme-ids 122,123,124 --stay-seconds 15
```

### 测试清单（testlist）批量执行

`run_tests.py` 支持通过测试清单一次编排多个模块脚本，适合你按“业务测试点清单”做批量回归。当前支持 `.json/.yaml` 两种格式：

```json
{
  "name": "基础冒烟清单",
  "tests": [
    {
      "id": "cf_theme_traversal_smoke",
      "game": "cf",
      "module": "theme_traversal",
      "enabled": true,
      "serial": "R5CYA29D4SP",
      "note": "可选：备注说明"
    }
  ]
}
```

字段约定：

- `name`：清单名称（可选，不填默认使用文件名）
- `tests`：测试条目数组（必填）
- `id`：条目唯一标识（必填，不能重复）
- `game`：目标游戏（必填，仅支持 `cf` / `mt`）
- `module`：模块名（必填，规则与 `--module` 一致）
- `enabled`：是否执行（可选，默认 `true`）
- `serial`：设备序列号（可选，单条覆盖）
- `note`：备注（可选）

校验与报告：

- 使用 `--validate-testlist` 时只做结构校验，不执行脚本。
- 运行后会在 `log/testlist_reports/` 生成 JSON 汇总，包含通过/失败统计和每条执行结果，便于后续 AI 分析接入。

更多结构和命名规范见：`docs/project_conventions.md`。

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
- 更新 `CF_nodes.json` / `MT_nodes.json` 中会影响页面识别的节点时，需要同步检查对应的 `CF_states.json` / `MT_states.json`，避免状态机仍引用旧节点。
- `common_nodes` 只作为节点类入口，复杂流程脚本优先使用 `GameActions` 的点号路径方法。

CF / MT 测试脚本优先使用 `GameActions` 的点号路径快捷入口：

```python
game_actions.click("theme.theme_bet_label")
bet_text = game_actions.text("theme.theme_bet_label")
bet_num = game_actions.extract_number(bet_text)
```

## CF 主题遍历脚本

`CF/CF_theme_traversal.py` 用于遍历大厅主题列表。脚本会按主题 ID 顺序执行：先确认当前在大厅，再优先检测 Android 原生 Lua Error 弹窗，然后通过 `CF/CF_theme_traversal_tree.py` 的主题遍历行为树调用 Lua 打开主题选 bet 界面；Lua 后会等待 `THEME_SELECT` 状态出现，如果选 bet 弹窗未出现且仍停留大厅，会按主题未配置跳过并导出 `select_popup_missing` 现场。bet 界面打开后、高级房点击前会再查一次 Lua Error，然后点击高级房进入按钮，并验证是否进入主题。社交主题从选 bet 进入后如果出现角色选择页，脚本会先点击角色确认按钮，再在机台选择页选择机台进入主题，默认选择 0 号机台。进入动作触发后如果停在 `loading2` 等待阶段，行为树会额外检测一次 Lua Error；如果进入动作后能处理到主题内弹窗，也会直接判定为进入成功。进入主题后默认不额外停留，关闭主题/返回大厅前会再次优先检测 Lua Error，然后快速清理遮挡弹窗、先点击 2 次主题内 `spin`，再点击返回大厅按钮并验证是否真正回到 `LOBBY_HOME`，然后继续下一个主题。失败留证时再导出现场，便于定位卡在 loading 进不去的主题。

- 默认主题列表维护在脚本内 `THEME_IDS`。
- 直接运行脚本时可以用 `--theme-ids 122,123`、`--theme-file theme_ids.txt` 或环境变量 `CF_THEME_IDS=122,123` 临时覆盖。
- 如果 Lua 后没有弹出选 bet 界面，或选 bet 界面没有高级房入口，脚本会打印该主题并直接继续下一个主题。
- 如果主题进入超时，脚本会记录该主题 ID 并继续后续流程；默认超时 10 秒，可用 `CF_THEME_LOAD_TIMEOUT` 覆盖。
- 选 bet 界面弹出等待默认复用 `THEME_SELECT_TIMEOUT`，可用 `CF_THEME_SELECT_OPEN_TIMEOUT` 单独覆盖。
- 社交主题会优先等待并点击角色确认，等待不到确认按钮时才直接选择机台；角色确认等待默认 3 秒，可用 `CF_SOCIAL_THEME_ROLE_CONFIRM_TIMEOUT` 覆盖。机台选择默认点击 0 号机台，可用 `CF_SOCIAL_THEME_MACHINE_INDEX=0..7` 覆盖；节点映射兼容 `machine_0 -> lobby_slot1` 到 `machine_7 -> lobby_slot8`，以及 `machine_alt_0 -> slot1` 到 `machine_alt_7 -> slot8`；高级房后进入机台选择页时默认等待 5 秒再点击机台，可用 `CF_SOCIAL_THEME_BEFORE_MACHINE_CLICK_DELAY` 覆盖；社交中间流程等待默认 8 秒，可用 `CF_SOCIAL_THEME_FLOW_TIMEOUT` 覆盖。
- 社交主题从主题内点击返回大厅按钮后会先回到机台选择页，脚本会等待机台页并点击 `lobby.btn_close` 回大厅；等待默认 8 秒，可用 `CF_SOCIAL_THEME_RETURN_TIMEOUT` 覆盖。
- 返回大厅失败后会先清理一次阻塞弹窗并重试，默认额外重试 1 次，可用 `CF_LOBBY_RETURN_RETRY_COUNT` 和 `CF_LOBBY_RETURN_RETRY_DELAY` 覆盖。
- 运行日志会输出 `[PERF]` 耗时点，包括设备检测/Poco 初始化、准备大厅、开始执行进入主题、Lua 打开选房、高级房点击、进入主题结果和返回大厅耗时，便于定位界面卡帧或初始化耗时。
- 每次触发进入主题前都会确认当前在大厅；大厅优先通过根节点 `LobbyScene`，并辅以设置/中部入口节点判断。如果不在大厅，会先清理通用弹窗，仍未恢复则只记录现场并跳过当前主题，不做冷重启。
- `loading2` 只用于进入动作后的异常识别：如果主题 Home 未出现、主题内弹窗也处理不到，并且 `loading2` 一直可见到超时，就记录为进入失败主题并重启游戏。应用冷重启后会重建游戏 Poco 连接并同步给节点、动作和状态机，避免旧 RPC 管道出现 `Broken pipe` 后影响后续检查。
- 如需进入主题后停留并检查 Lua/Char Error，可通过 `--stay-seconds` 指定停留秒数；检测时只通过 `airtest_booststrap.py` 的 Android 原生 Poco 识别系统弹窗，命中后保存截图、打印 `android:id/message` 文本、写入 `log/theme_traversal/lua_error_message_*.txt`（文件头会附带对应截图路径）、输出最近的 logcat 关键日志，并点击 `android:id/button1` 关闭弹窗。
- 进入失败记录输出到 `log/theme_traversal/failed_theme_ids_*.txt`。
- 重启游戏优先使用 `CF_APP_PACKAGE`；未设置时会尝试读取当前前台应用包名，兜底值为 `slots.pcg.casino.games.free.android`。重启后如果停在 debug 启动页，脚本默认按横屏坐标使用 `CF_LAUNCH_CONFIRM_TAP=0.500,0.940` 点击居中靠下的 Confirm，避免启动页图片误识别；坐标不准时可通过环境变量覆盖。

## 功能模块的自动化脚本命名规则

每个功能模块对应一个自动化脚本，脚本名称为 `CF_功能模块名.py` 或 `MT_功能模块名.py`。

## 项目 Agent Skill

项目级 Cursor Agent Skill 位于 `.cursor/skills/airtest-change-guidelines/SKILL.md`，用于约束后续 Airtest 自动化变更：

- 每次新增一些功能或者逻辑的时候添加中文注释
- 更新项目说明文档

## 新脚本初始化方式

后续新增自动化脚本统一复用 `airtest_booststrap.py` 中的设备连接、Airtest 参数和 Poco 初始化配置。直接导入时会自动连接设备并初始化游戏控件树 `poco`；需要识别 Android 原生弹窗时调用 `get_android_poco()` 懒加载原生 UIAutomator Poco。需要指定设备时，可先设置 `ANDROID_SERIAL`，或通过 `run_tests.py --serial` 传入。

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
