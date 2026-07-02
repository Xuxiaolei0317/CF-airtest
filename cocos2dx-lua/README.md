# Cocos2d-x Lua Poco SDK

该目录保存当前项目接入使用的 Cocos2d-x Lua Poco SDK 文件，用于让 Airtest/Poco 读取游戏 UI 控件树、截图、屏幕尺寸，并支持测试包中的调试 RPC。

## 目录说明

```text
cocos2dx-lua/
├── README.md
├── DEBUG_CLICK_LOGGER.md
└── poco/
    ├── poco_manager.lua           # Poco SDK 服务入口
    ├── POCO_SDK_VERSION.lua       # SDK 版本号
    ├── Cocos2dxDumper.lua         # 节点树导出
    ├── Cocos2dxFrozenDumper.lua   # 带节点缓存的节点树导出
    ├── Cocos2dxNode.lua           # Cocos2d-x 节点属性封装
    ├── Cocos2dxFrozenNode.lua     # 冻结节点属性封装
    ├── Cocos2dxScreen.lua         # 截图和屏幕尺寸能力
    ├── ClientConnection.lua       # Poco RPC 连接处理
    ├── PocoDebugTouchLogger.lua   # 点击节点调试日志工具
    ├── sdk/                       # Poco 基础抽象和匹配能力
    └── support/                   # json/base64/struct 支持库
```

## 接入方式

将 `poco/` 目录整体放入游戏工程的 Lua 代码路径，确保可以按 `poco.xxx` 路径加载。测试包或 debug 包启动时初始化 Poco 服务：

```lua
local PocoManager = require("poco.poco_manager")
PocoManager:init_server(15004)
```

如果项目不允许直接使用 `require`，可以替换为项目自己的 Lua 加载接口，例如：

```lua
local PocoManager = libFile.loadSrcCode("poco.poco_manager")
PocoManager:init_server(15004)
```

部分工程加载接口只接受斜杠路径时，可使用：

```lua
local PocoManager = libFile.loadSrcCode("poco/poco_manager")
PocoManager:init_server(15004)
```

初始化成功后，日志中会出现类似 `[poco] server listens on tcp://*:15004` 的输出。Airtest 侧使用项目现有的 `airtest_booststrap.py` 初始化封装，通过 `StdPoco` 连接游戏控件树。

## 调试能力

- `POCO_SDK_VERSION.lua` 当前返回 `1.0.7`。
- `poco_manager.lua` 默认监听 `15004` 端口。
- `RunLua` RPC 仅在 `bole.isPocoPackage` 或 `appDebugMode == true` 时允许执行，避免正式包误开放 Lua 执行入口。
- `PocoDebugTouchLogger.lua` 可在游戏内点击时打印节点路径、文本、坐标和 `NodeSpec`，具体用法见 `DEBUG_CLICK_LOGGER.md`。

建议只在测试包或 debug 包中接入和启用调试能力，不要在正式包中默认启动 Poco SDK 服务。
