# Poco 点击节点调试日志

本仓库提供了可选的点击节点调试日志模块，用于在编写自动化测试节点库时快速收集 Poco 节点路径。

该模块会监听游戏内的触摸/点击事件，反查当前点击到的 UI 节点，并打印可直接复制到 Airtest/Poco 脚本中的节点信息。

## cocos2dx-lua

将 `cocos2dx-lua/poco/PocoDebugTouchLogger.lua` 和现有 Poco Lua SDK 文件一起放入游戏工程，然后在测试/调试入口启动：

```lua
local PocoDebugTouchLogger = require("poco.PocoDebugTouchLogger")
PocoDebugTouchLogger.start()
```

如果项目禁止直接使用 `require`，需要改成项目自己的 `libFile` 加载接口。你们项目里可以优先使用 `loadSrcCode`：

```lua
local PocoDebugTouchLogger = libFile.loadSrcCode("poco.PocoDebugTouchLogger")
PocoDebugTouchLogger.start()
```

如果 `loadSrcCode` 不接受点号路径，可以改成斜杠路径：

```lua
local PocoDebugTouchLogger = libFile.loadSrcCode("poco/PocoDebugTouchLogger")
PocoDebugTouchLogger.start()
```

停止打印：

```lua
PocoDebugTouchLogger.stop()
```

## Cocos Creator

将 `cocos-creator/Poco/PocoDebugTouchLogger.js` 和现有 Creator Poco SDK 文件一起放入游戏工程，然后在测试/调试入口启动：

```javascript
var PocoDebugTouchLogger = require('Poco/PocoDebugTouchLogger')
PocoDebugTouchLogger.start()
```

停止打印：

```javascript
PocoDebugTouchLogger.stop()
```

## 输出内容

日志示例：

```text
[PocoDebug] Clicked node:
name=StartButton
path=Canvas/MainMenu/StartButton
type=Button
text=开始游戏
position=(0.5000, 0.7200)
size=(0.2000, 0.0800)
nodespec=NodeSpec("Canvas", (child("MainMenu"), child("StartButton"),), desc="")
```

默认情况下，如果实际命中的是按钮内部的文字或图片节点，模块会向上回溯到最近的可点击父节点。这样打印出来的通常是更适合自动化脚本使用的按钮节点。

如果想打印最深层的实际命中节点，可以这样启动：

```lua
PocoDebugTouchLogger.start({ preferTouchable = false })
```

```javascript
PocoDebugTouchLogger.start({ preferTouchable: false })
```

建议只在测试包或调试包中启用，不要在正式包中默认启动。
