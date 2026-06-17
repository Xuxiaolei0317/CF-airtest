#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地 Poco 节点生成网页工具。

用法:
    python cf-airtest/node_generator_web.py
    python cf-airtest/node_generator_web.py --serial R5CYA29D4SP --port 8765
"""

import argparse
import errno
import json
import os
import re
import sys
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parent
NODE_DUMP_DIR = PROJECT_ROOT / "MT" / "node_dumps"

_POCO = None


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Poco 节点生成工具</title>
  <style>
    :root {
      --bg: #f6f7fb;
      --panel: #ffffff;
      --border: #d8dee9;
      --text: #20242a;
      --muted: #687385;
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --code: #0f172a;
      --code-text: #e5e7eb;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    header {
      padding: 18px 24px;
      border-bottom: 1px solid var(--border);
      background: var(--panel);
    }

    h1 {
      margin: 0 0 6px;
      font-size: 20px;
    }

    .hint {
      color: var(--muted);
      font-size: 13px;
    }

    main {
      display: grid;
      grid-template-columns: minmax(420px, 1fr) minmax(420px, 0.9fr);
      gap: 16px;
      padding: 16px;
      height: calc(100vh - 76px);
    }

    section {
      min-height: 0;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: var(--panel);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .toolbar {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
    }

    button {
      border: 0;
      border-radius: 8px;
      background: var(--primary);
      color: #fff;
      cursor: pointer;
      font-size: 14px;
      padding: 8px 12px;
    }

    button:hover { background: var(--primary-dark); }
    button.secondary {
      background: #eef2ff;
      color: var(--primary-dark);
    }
    button.secondary:hover { background: #dbeafe; }
    button:disabled {
      cursor: not-allowed;
      opacity: 0.65;
    }

    input[type="search"], input[type="text"] {
      flex: 1;
      min-width: 180px;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 14px;
    }

    .status {
      color: var(--muted);
      font-size: 13px;
      padding: 0 12px 10px;
      min-height: 24px;
    }

    .tree-wrap {
      overflow: auto;
      padding: 8px 12px 16px;
      flex: 1;
    }

    ul.tree, .tree ul {
      list-style: none;
      margin: 0;
      padding-left: 22px;
    }

    .tree > li { padding-left: 0; }

    details {
      margin: 2px 0;
    }

    summary {
      cursor: pointer;
      border-radius: 8px;
      padding: 4px 6px;
    }

    summary:hover, .leaf:hover {
      background: #f1f5f9;
    }

    .leaf {
      display: flex;
      align-items: center;
      gap: 6px;
      border-radius: 8px;
      padding: 4px 6px;
      margin: 2px 0;
    }

    label.node-line {
      display: inline-flex;
      align-items: baseline;
      gap: 6px;
      cursor: pointer;
      user-select: none;
    }

    .name {
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 13px;
      font-weight: 650;
    }

    .meta {
      color: var(--muted);
      font-size: 12px;
    }

    .badge {
      border-radius: 999px;
      background: #eef2ff;
      color: #3730a3;
      padding: 1px 7px;
      font-size: 11px;
    }

    textarea {
      flex: 1;
      width: 100%;
      border: 0;
      border-top: 1px solid var(--border);
      background: var(--code);
      color: var(--code-text);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 13px;
      line-height: 1.5;
      outline: none;
      padding: 12px;
      resize: none;
    }

    .empty {
      color: var(--muted);
      padding: 16px;
    }

    @media (max-width: 960px) {
      main {
        grid-template-columns: 1fr;
        height: auto;
      }
      section { min-height: 420px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Poco 节点生成工具</h1>
    <div class="hint">点击“打印当前页面节点”拉取当前游戏页面节点树，勾选后生成可粘贴到 MT_nodes.json 对应分组里的节点配置条目。</div>
  </header>

  <main>
    <section>
      <div class="toolbar">
        <button id="loadBtn">打印当前页面节点</button>
        <button id="expandBtn" class="secondary">展开全部</button>
        <button id="collapseBtn" class="secondary">收起全部</button>
        <input id="scopeInput" type="search" placeholder="输入界面/节点名，只显示该层级" />
        <button id="clearScopeBtn" class="secondary">清空层级筛选</button>
        <input id="searchInput" type="search" placeholder="搜索 name / text / path" />
      </div>
      <div id="status" class="status">等待拉取节点。</div>
      <div id="tree" class="tree-wrap"><div class="empty">暂无节点，请先点击“打印当前页面节点”。</div></div>
    </section>

    <section>
      <div class="toolbar">
        <input id="moduleInput" type="text" placeholder="功能模块名，如 guild / quest / store" />
        <button id="generateBtn">生成</button>
        <button id="copyBtn" class="secondary">复制代码</button>
        <button id="clearBtn" class="secondary">清空勾选</button>
      </div>
      <div id="outputStatus" class="status">勾选节点后点击生成。生成结果放到 MT_nodes.json 对应分组里。</div>
      <textarea id="output" spellcheck="false" placeholder='示例："guild_btn_chat": {"root": "bottom_node", "chain": [["child", "btn_node"], ["child", "btn_chat"]], "desc": ""},'></textarea>
    </section>
  </main>

  <script>
    let nodeMap = new Map();
    let hierarchy = null;
    let lastNodeCount = 0;
    let lastDumpPath = "";

    const treeEl = document.getElementById("tree");
    const statusEl = document.getElementById("status");
    const outputStatusEl = document.getElementById("outputStatus");
    const outputEl = document.getElementById("output");
    const loadBtn = document.getElementById("loadBtn");
    const moduleInput = document.getElementById("moduleInput");
    const scopeInput = document.getElementById("scopeInput");
    const searchInput = document.getElementById("searchInput");

    function escapeHtml(value) {
      return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function escapePythonString(value) {
      return String(value ?? "")
        .replace(/\\/g, "\\\\")
        .replace(/"/g, '\\"');
    }

    function nodeTitle(node) {
      return node.name || node.type || "(unnamed)";
    }

    function nodeSearchText(node) {
      return [node.name, node.type, node.text, node.path].join(" ").toLowerCase();
    }

    function toPythonIdentifier(name, fallbackIndex) {
      let ident = String(name || `node_${fallbackIndex}`)
        .normalize("NFKC")
        .replace(/[^\p{L}\p{N}_]/gu, "_")
        .replace(/_+/g, "_")
        .replace(/^_+|_+$/g, "");
      if (!ident) ident = `node_${fallbackIndex}`;
      if (/^\p{N}/u.test(ident)) ident = `node_${ident}`;
      return ident;
    }

    function isGeneratedName(name) {
      const value = String(name || "").trim();
      return !value
        || value === "MainGameScene"
        || value.startsWith("<Node | Tag =")
        || value.startsWith("<");
    }

    function shortSelectorNames(names) {
      if (!names.length) return "";
      return names.slice(-3).filter((name) => !isGeneratedName(name));
    }

    function selectorFromNames(names) {
      const shortNames = shortSelectorNames(names);
      if (!shortNames.length) return "";
      const [root, ...children] = shortNames.map(escapePythonString);
      return `poco("${root}")` + children.map((name) => `.child("${name}")`).join("");
    }

    function nodeConfigFromNames(names, descText) {
      const shortNames = shortSelectorNames(names);
      if (!shortNames.length) return "";
      const [root, ...children] = shortNames;
      const config = { root, desc: descText };
      if (children.length) {
        config.chain = children.map((name) => ["child", name]);
        config.desc = descText;
      }
      return JSON.stringify(config);
    }

    function registerNodes(node) {
      nodeMap.set(node.id, node);
      (node.children || []).forEach(registerNodes);
    }

    function walkNodes(node, callback) {
      callback(node);
      (node.children || []).forEach((child) => walkNodes(child, callback));
    }

    function countNodes(node) {
      let count = 0;
      walkNodes(node, () => count += 1);
      return count;
    }

    function scopeMatches(node, keyword, exact = false) {
      const name = String(node.name || "").toLowerCase();
      if (!name) return false;
      return exact ? name === keyword : name.includes(keyword);
    }

    function renderLine(node) {
      const disabled = node.selector_names.length ? "" : " disabled";
      const title = escapeHtml(nodeTitle(node));
      const text = node.text ? ` text="${escapeHtml(node.text)}"` : "";
      const badge = node.children?.length ? `<span class="badge">${node.children.length}</span>` : "";
      return `
        <label class="node-line">
          <input type="checkbox" value="${node.id}"${disabled} />
          <span class="name">${title}</span>
          ${badge}
          <span class="meta">${escapeHtml(node.type || "")}${text}</span>
        </label>
      `;
    }

    function renderNode(node, depth = 0) {
      const open = depth < 2 ? " open" : "";
      if (node.children && node.children.length) {
        return `
          <li data-node-id="${node.id}" data-search="${escapeHtml(nodeSearchText(node))}">
            <details${open}>
              <summary>${renderLine(node)}</summary>
              <ul>${node.children.map((child) => renderNode(child, depth + 1)).join("")}</ul>
            </details>
          </li>
        `;
      }
      return `
        <li data-node-id="${node.id}" data-search="${escapeHtml(nodeSearchText(node))}">
          <div class="leaf">${renderLine(node)}</div>
        </li>
      `;
    }

    function renderForest(roots) {
      nodeMap = new Map();
      roots.forEach(registerNodes);
      treeEl.innerHTML = `<ul class="tree">${roots.map((root) => renderNode(root)).join("")}</ul>`;
    }

    function renderTree(root) {
      renderForest([root]);
    }

    function scopeRoots(root, rawKeyword) {
      const keyword = rawKeyword.trim().toLowerCase();
      if (!keyword) return [root];

      const exactMatches = [];
      const partialMatches = [];
      walkNodes(root, (node) => {
        if (scopeMatches(node, keyword, true)) {
          exactMatches.push(node);
        } else if (scopeMatches(node, keyword, false)) {
          partialMatches.push(node);
        }
      });
      return exactMatches.length ? exactMatches : partialMatches;
    }

    function updateBaseStatus() {
      statusEl.textContent = lastNodeCount
        ? `已打印当前页面节点：${lastNodeCount} 个，JSON 已保存到 ${lastDumpPath}`
        : "等待拉取节点。";
    }

    function applyScopeFilter() {
      if (!hierarchy) return;

      const keyword = scopeInput.value.trim();
      if (!keyword) {
        renderTree(hierarchy);
        updateBaseStatus();
        filterTree();
        return;
      }

      const roots = scopeRoots(hierarchy, keyword);
      if (!roots.length) {
        nodeMap = new Map();
        treeEl.innerHTML = `<div class="empty">没有找到节点名包含“${escapeHtml(keyword)}”的层级。</div>`;
        statusEl.textContent = `层级筛选无结果：${keyword}`;
        return;
      }

      renderForest(roots);
      const scopedCount = roots.reduce((total, root) => total + countNodes(root), 0);
      statusEl.textContent = `已筛选“${keyword}”层级：匹配 ${roots.length} 个根节点，显示 ${scopedCount} 个节点。`;
      filterTree();
    }

    function selectedNodes() {
      return [...treeEl.querySelectorAll('input[type="checkbox"]:checked')]
        .map((checkbox) => nodeMap.get(Number(checkbox.value)))
        .filter(Boolean);
    }

    function generateCode() {
      const nodes = selectedNodes();
      const usedNames = new Map();
      const rawModuleName = moduleInput.value.trim();
      const modulePrefix = rawModuleName ? `${toPythonIdentifier(rawModuleName, "module")}_` : "";
      const lines = nodes.map((node, index) => {
        const baseName = `${modulePrefix}${toPythonIdentifier(node.name, index + 1)}`;
        const count = (usedNames.get(baseName) || 0) + 1;
        usedNames.set(baseName, count);
        const nodeKey = count === 1 ? baseName : `${baseName}_${count}`;
        return `    "${nodeKey}": ${nodeConfigFromNames(node.selector_names, "")},`;
      });
      outputEl.value = lines.join("\n");
      outputStatusEl.textContent = lines.length
        ? `已生成 ${lines.length} 行 JSON 配置条目。粘到 MT_nodes.json 对应分组中。`
        : "没有勾选任何可生成的节点。";
    }

    async function loadNodes() {
      loadBtn.disabled = true;
      statusEl.textContent = "正在拉取当前 Poco 节点树...";
      try {
        const response = await fetch("/api/nodes", { method: "POST" });
        const data = await response.json();
        if (!response.ok || !data.ok) throw new Error(data.error || `HTTP ${response.status}`);
        hierarchy = data.hierarchy;
        lastNodeCount = data.node_count;
        lastDumpPath = data.dump_path;
        applyScopeFilter();
      } catch (error) {
        statusEl.textContent = `拉取失败：${error.message}`;
      } finally {
        loadBtn.disabled = false;
      }
    }

    function filterTree() {
      const keyword = searchInput.value.trim().toLowerCase();
      const items = [...treeEl.querySelectorAll("li[data-search]")];
      if (!keyword) {
        items.forEach((item) => item.style.display = "");
        return;
      }
      items.forEach((item) => {
        const matched = item.dataset.search.includes(keyword);
        const hasMatchedChild = [...item.querySelectorAll("li[data-search]")]
          .some((child) => child.dataset.search.includes(keyword));
        item.style.display = matched || hasMatchedChild ? "" : "none";
        if (matched || hasMatchedChild) {
          const details = item.querySelector(":scope > details");
          if (details) details.open = true;
        }
      });
    }

    loadBtn.addEventListener("click", loadNodes);
    document.getElementById("generateBtn").addEventListener("click", generateCode);
    document.getElementById("copyBtn").addEventListener("click", async () => {
      await navigator.clipboard.writeText(outputEl.value);
      outputStatusEl.textContent = "已复制生成代码。";
    });
    document.getElementById("clearBtn").addEventListener("click", () => {
      treeEl.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => checkbox.checked = false);
      outputStatusEl.textContent = "已清空勾选。";
    });
    document.getElementById("expandBtn").addEventListener("click", () => {
      treeEl.querySelectorAll("details").forEach((details) => details.open = true);
    });
    document.getElementById("collapseBtn").addEventListener("click", () => {
      treeEl.querySelectorAll("details").forEach((details) => details.open = false);
    });
    document.getElementById("clearScopeBtn").addEventListener("click", () => {
      scopeInput.value = "";
      applyScopeFilter();
    });
    scopeInput.addEventListener("input", applyScopeFilter);
    searchInput.addEventListener("input", filterTree);
  </script>
</body>
</html>
"""


def get_poco():
    """延迟初始化 Poco，避免打开网页服务时立即连接设备。"""
    global _POCO
    if _POCO is None:
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from airtest_booststrap import poco

        _POCO = poco
    return _POCO


def node_value(node, key, default=""):
    payload = node.get("payload") if isinstance(node.get("payload"), dict) else {}
    return payload.get(key, node.get(key, default))


def build_tree(node, path_names=None, path="root", counter=None):
    """把 Poco dump 转成网页可直接渲染和生成代码的树结构。"""
    if counter is None:
        counter = {"value": 0}
    if path_names is None:
        path_names = []

    counter["value"] += 1
    node_id = counter["value"]

    if not isinstance(node, dict):
        return {
            "id": node_id,
            "name": "",
            "type": type(node).__name__,
            "text": str(node),
            "path": path,
            "selector_names": path_names,
            "children": [],
        }

    name = node.get("name") or ""
    node_type = node.get("type") or ""
    text = node_value(node, "text", "") or ""
    current_path = f"{path}/{name or node_type or node_id}"
    selector_names = path_names + ([name] if name else [])
    children = [
        build_tree(child, selector_names, current_path, counter)
        for child in (node.get("children") or [])
    ]

    return {
        "id": node_id,
        "name": name,
        "type": node_type,
        "text": text,
        "visible": node_value(node, "visible", ""),
        "clickable": node_value(node, "clickable", ""),
        "pos": node_value(node, "pos", ""),
        "path": current_path,
        "selector_names": selector_names,
        "children": children,
    }


def flatten_tree(node):
    rows = []

    def walk(item, depth=0):
        rows.append({
            "depth": depth,
            "name": item.get("name", ""),
            "type": item.get("type", ""),
            "text": item.get("text", ""),
            "path": item.get("path", ""),
            "selector": item.get("selector_names", []),
        })
        for child in item.get("children", []):
            walk(child, depth + 1)

    walk(node)
    return rows


def save_dump(raw_hierarchy, web_tree, flat_nodes):
    NODE_DUMP_DIR.mkdir(parents=True, exist_ok=True)
    file_path = NODE_DUMP_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_web_node_generator.json"
    payload = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "node_count": len(flat_nodes),
        "flat_nodes": flat_nodes,
        "web_tree": web_tree,
        "hierarchy": raw_hierarchy,
    }
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2, default=str)
    return file_path


def dump_current_page_nodes():
    raw_hierarchy = get_poco().agent.hierarchy.dump()
    web_tree = build_tree(raw_hierarchy)
    flat_nodes = flatten_tree(web_tree)
    dump_path = save_dump(raw_hierarchy, web_tree, flat_nodes)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 当前页面节点：{len(flat_nodes)} 个")
    for row in flat_nodes:
        indent = "  " * row["depth"]
        title = row["name"] or row["type"] or "(unnamed)"
        text = f" | text={row['text']}" if row["text"] else ""
        print(f"{indent}- {title}{text} | path={row['path']}")
    print(f"已保存节点 JSON：{dump_path}\n")

    return {
        "ok": True,
        "node_count": len(flat_nodes),
        "dump_path": str(dump_path),
        "hierarchy": web_tree,
    }


class NodeGeneratorHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[web] {self.address_string()} - {fmt % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self):
        body = INDEX_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self.send_html()
            return
        self.send_error(404, "Not found")

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/nodes":
            self.send_error(404, "Not found")
            return
        try:
            self.send_json(dump_current_page_nodes())
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=500)


def parse_args():
    parser = argparse.ArgumentParser(description="启动 Poco 节点生成网页工具")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认 127.0.0.1")
    parser.add_argument("--port", type=int, default=8765, help="监听端口，默认 8765")
    parser.add_argument("--serial", default=None, help="设备序列号或 airtest_booststrap.py 中配置的别名")
    parser.add_argument("--no-open", action="store_true", help="启动后不自动打开浏览器")
    return parser.parse_args()


def create_server(host, port, max_attempts=20):
    """端口被占用时自动尝试后续端口。"""
    for offset in range(max_attempts):
        candidate_port = port + offset
        try:
            server = ThreadingHTTPServer((host, candidate_port), NodeGeneratorHandler)
            if offset:
                print(f"端口 {port} 已被占用，已自动切换到 {candidate_port}。")
            return server, candidate_port
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise
    raise OSError(f"{host}:{port}-{port + max_attempts - 1} 都被占用，请用 --port 指定其他端口")


def main():
    args = parse_args()
    if args.serial:
        os.environ["ANDROID_SERIAL"] = args.serial

    server, actual_port = create_server(args.host, args.port)
    url = f"http://{args.host}:{actual_port}"
    print(f"节点生成工具已启动：{url}")
    print("在网页点击“打印当前页面节点”时会连接设备并拉取 Poco 层级。")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止节点生成工具。")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
