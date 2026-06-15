# -*- encoding=utf8 -*-
"""
node_manager - UI 节点管理统一工具

功能：
1. dump_current_nodes  -- 截图 + 导出当前 Poco 节点树为 JSON
2. search_nodes        -- 在已建立的 UI 节点库中检索匹配节点
3. update_catalog      -- 将新验证的节点追加到 catalog 文件
4. node_library        -- 统一的节点库抽象（JSON 格式）

供 CF 和 MT 两项目复用。
"""

from .base import (
    dump_current_nodes,
    capture_screen,
    get_poco_hierarchy,
    flatten_hierarchy,
)
from .catalog import (
    load_catalog,
    save_catalog,
    search_nodes,
    add_verified_node,
    get_page_info,
    list_pages,
    update_page_state,
)

__all__ = [
    "dump_current_nodes",
    "capture_screen",
    "get_poco_hierarchy",
    "flatten_hierarchy",
    "load_catalog",
    "save_catalog",
    "search_nodes",
    "add_verified_node",
    "get_page_info",
    "list_pages",
    "update_page_state",
]
