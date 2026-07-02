local function loadModule(moduleName)
    local libFile = _G.libFile
    if libFile ~= nil then
        local methodNames = {'loadSrcCode', 'loadResCode', 'loadCppCode', 'require', 'import', 'load'}
        local moduleNames = {
            moduleName,
            moduleName:gsub('%.', '/'),
            moduleName:gsub('%.', '/') .. '.lua',
        }
        for _, methodName in ipairs(methodNames) do
            local method = libFile[methodName]
            if type(method) == 'function' then
                for _, name in ipairs(moduleNames) do
                    local ok, ret = pcall(method, name)
                    if ok and ret ~= nil then
                        return ret
                    end

                    ok, ret = pcall(method, libFile, name)
                    if ok and ret ~= nil then
                        return ret
                    end
                end
            end
        end
    end

    return require(moduleName)
end

-- import
function import(moduleName, currentModuleName)
    local currentModuleNameParts
    local moduleFullName = moduleName
    local offset = 1

    while true do
        if string.byte(moduleName, offset) ~= 46 then
            moduleFullName = string.sub(moduleName, offset)
            if currentModuleNameParts and #currentModuleNameParts > 0 then
                moduleFullName = table.concat(currentModuleNameParts, ".") .. "." .. moduleFullName
            end
            break
        end
        offset = offset + 1

        if not currentModuleNameParts then
            if not currentModuleName then
                local n, v = debug.getlocal(3, 1)
                currentModuleName = v
            end
            currentModuleNameParts = string.split(currentModuleName, ".")
        end
        table.remove(currentModuleNameParts, #currentModuleNameParts)
    end

    return loadModule(moduleFullName)
end

local cc = _G.cc or loadModule('cc')
local Cocos2dxNode = import('.Cocos2dxNode')

local Logger = {}

Logger._listener = nil
Logger._options = nil

local function safeCall(fn, default)
    local ok, ret = pcall(fn)
    if ok then
        return ret
    end
    return default
end

local function getNodeName(node)
    local name = safeCall(function() return node:getName() end, nil)
    if name == nil or name == '' then
        name = safeCall(function() return node:getDescription() end, nil)
    end
    if name == nil or name == '' then
        name = safeCall(function() return tolua.type(node) end, nil)
    end
    return name or '<no-name>'
end

local function getChildren(node)
    return safeCall(function() return node:getChildren() end, {}) or {}
end

local function isVisibleInHierarchy(node)
    local current = node
    while current do
        local visible = safeCall(function() return current:isVisible() end, true)
        if not visible then
            return false
        end
        current = safeCall(function() return current:getParent() end, nil)
    end
    return true
end

local function containsWorldPoint(node, worldPoint)
    local size = safeCall(function() return node:getContentSize() end, nil)
    if size == nil or size.width == nil or size.height == nil then
        return false
    end
    if size.width <= 0 or size.height <= 0 then
        return false
    end

    local anchor = safeCall(function() return node:getAnchorPoint() end, cc.p(0.5, 0.5))
    local localPoint = safeCall(function() return node:convertToNodeSpaceAR(worldPoint) end, nil)
    if localPoint == nil then
        return false
    end

    local left = -anchor.x * size.width
    local right = (1 - anchor.x) * size.width
    local bottom = -anchor.y * size.height
    local top = (1 - anchor.y) * size.height
    return localPoint.x >= left and localPoint.x <= right and localPoint.y >= bottom and localPoint.y <= top
end

local function isTouchable(node)
    local touchable = safeCall(function()
        if node.isTouchEnabled then
            return node:isTouchEnabled()
        end
        return false
    end, false)
    if not touchable then
        return false
    end

    local enabled = safeCall(function()
        if node.isEnabled then
            return node:isEnabled()
        end
        return true
    end, true)
    return enabled
end

local function sortChildrenForHitTest(children)
    table.sort(children, function(a, b)
        local za = safeCall(function() return a:getLocalZOrder() end, 0) or 0
        local zb = safeCall(function() return b:getLocalZOrder() end, 0) or 0
        return za < zb
    end)
end

local function findDeepestNode(node, worldPoint)
    if node == nil or not isVisibleInHierarchy(node) then
        return nil
    end

    local children = getChildren(node)
    sortChildrenForHitTest(children)
    for i = #children, 1, -1 do
        local matched = findDeepestNode(children[i], worldPoint)
        if matched ~= nil then
            return matched
        end
    end

    if containsWorldPoint(node, worldPoint) then
        return node
    end
    return nil
end

local function preferTouchableAncestor(node)
    local current = node
    while current do
        if isTouchable(current) then
            return current
        end
        current = safeCall(function() return current:getParent() end, nil)
    end
    return node
end

local function buildPathParts(node)
    local parts = {}
    local current = node
    while current do
        table.insert(parts, 1, getNodeName(current))
        current = safeCall(function() return current:getParent() end, nil)
    end
    return parts
end

local function quoteLuaString(value)
    value = tostring(value or '')
    value = value:gsub('\\', '\\\\'):gsub('"', '\\"')
    return '"' .. value .. '"'
end

local function buildNodeSpec(pathParts)
    if #pathParts == 0 then
        return nil
    end

    local root = pathParts[1]
    local chain = {}
    for i = 2, #pathParts do
        table.insert(chain, 'child(' .. quoteLuaString(pathParts[i]) .. ')')
    end

    if #chain == 0 then
        return 'NodeSpec(' .. quoteLuaString(root) .. ', desc="")'
    end
    return 'NodeSpec(' .. quoteLuaString(root) .. ', (' .. table.concat(chain, ', ') .. ',), desc="")'
end

local function getAttr(node, attrName)
    local director = cc.Director:getInstance()
    local winSize = director:getWinSize()
    local wrapper = Cocos2dxNode:new(node, winSize.width, winSize.height)
    return wrapper:getAttr(attrName)
end

local function formatVec2(vec)
    if type(vec) ~= 'table' then
        return tostring(vec)
    end
    return string.format('(%.4f, %.4f)', vec[1] or 0, vec[2] or 0)
end

local function printNodeInfo(node)
    local pathParts = buildPathParts(node)
    local text = getAttr(node, 'text')
    local pos = getAttr(node, 'pos')
    local size = getAttr(node, 'size')
    local nodeSpec = buildNodeSpec(pathParts)

    print('[PocoDebug] Clicked node:')
    print('name=' .. tostring(getAttr(node, 'name') or getNodeName(node)))
    print('path=' .. table.concat(pathParts, '/'))
    print('type=' .. tostring(getAttr(node, 'type')))
    print('text=' .. tostring(text or ''))
    print('position=' .. formatVec2(pos))
    print('size=' .. formatVec2(size))
    if nodeSpec ~= nil then
        print('nodespec=' .. nodeSpec)
    end
end

function Logger.start(options)
    options = options or {}
    Logger.stop()
    Logger._options = options

    local listener = cc.EventListenerTouchOneByOne:create()
    listener:setSwallowTouches(false)
    listener:registerScriptHandler(function(touch, event)
        local scene = cc.Director:getInstance():getRunningScene()
        local worldPoint = touch:getLocation()
        local matched = findDeepestNode(scene, worldPoint)
        if matched ~= nil and options.preferTouchable ~= false then
            matched = preferTouchableAncestor(matched)
        end
        if matched ~= nil then
            printNodeInfo(matched)
        else
            print(string.format('[PocoDebug] Clicked empty area: position=(%.4f, %.4f)', worldPoint.x, worldPoint.y))
        end
        return false
    end, cc.Handler.EVENT_TOUCH_BEGAN)

    cc.Director:getInstance():getEventDispatcher():addEventListenerWithFixedPriority(listener, -9999)
    Logger._listener = listener
    print('[PocoDebug] touch logger started')
end

function Logger.stop()
    if Logger._listener ~= nil then
        cc.Director:getInstance():getEventDispatcher():removeEventListener(Logger._listener)
        Logger._listener = nil
        print('[PocoDebug] touch logger stopped')
    end
end

return Logger
