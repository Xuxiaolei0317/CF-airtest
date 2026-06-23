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
│   ├── CF_nodes.py              # CF 节点定义
│   ├── CF_test.py               # CF 主测试
│   ├── CF_CashGo.py             # CF CashGo 模块
│   ├── CF_Mansionquest.py       # CF MansionQuest 模块
│   ├── CF_quest.py              # CF 任务模块
│   ├── CF_deljp.py              # CF 删除节点模块
│   └── cash_go_build.py         # CashGo build 流程脚本
├── MT/                          # Mega Tycoon 测试模块
│   ├── __init__.py
│   ├── MT_nodes.py              # MT 节点定义
│   ├── MT_main.py               # MT 通用方法和模块流程
│   ├── MT_test.py               # MT 测试用例入口/示例
│   ├── MT_new_user.py           # MT 新用户流程脚本
│   ├── MT_node_maintenance.py   # MT 节点维护测试
│   └── MT_quest_test.py         # MT 任务测试
├── node_manager/                # 节点库管理与 Poco 节点导出工具
│   ├── __init__.py
│   ├── base.py                  # 截图、节点树导出和层级展平工具
│   └── catalog.py               # 节点库 JSON 读写、检索和更新
├── test/                        # 测试和辅助脚本
│   ├── test.py
│   └── install_CGJS.py
└── log/                         # Airtest 日志
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 连接设备

```bash
# 设置设备序列号 (可选，默认 R5CYA29D4SP)
export ANDROID_SERIAL=YOUR_DEVICE_ID
```

### 3. 运行测试

```bash
# 列出所有可用测试
python run_tests.py --list

# 运行 MT 主流程测试
python run_tests.py --game mt

# 运行 CF CashGo 模块
python run_tests.py --game cf --module CF_CashGo

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

## 新脚本初始化方式

后续新增自动化脚本统一复用 `airtest_booststrap.py` 中的设备连接、Airtest 参数和 Poco 初始化配置。

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, dev, poco

ST.SAVE_IMAGE = True  # 调试阶段打开截图
```

## 多设备切换

在 `airtest_booststrap.py` 的 `DEVICE_MAP` 中配置设备别名：

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

# 方式3: 直接修改 _DEFAULT_ANDROID_SERIAL
```

## Git 忽略

如果日志文件夹下生成的 png 图片太多，可以添加到全局 gitignore:

```bash
git config --global core.excludesfile ~/.gitignore_global
echo "log/" >> ~/.gitignore_global
```
