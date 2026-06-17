#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PocoDebug 点击日志网页监听工具。

用法:
    python cf-airtest/poco_log_node_listener_web.py
    python cf-airtest/poco_log_node_listener_web.py --port 8766
"""

import argparse
import errno
import json
import re
import subprocess
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PROJECT_ROOT = Path(__file__).resolve().parent

LOG_MARKER = "[PocoDebug] Clicked node:"
LUA_PRINT_RE = re.compile(r"\[LUA-print\]\s*(.*)$")
FIELD_RE = re.compile(r"^(name|path|type|text|position|size|nodespec)=(.*)$")
NODESPEC_ROOT_RE = re.compile(r'NodeSpec\("((?:[^"\\]|\\.)*)"')
NODESPEC_CHILD_RE = re.compile(r'child\("((?:[^"\\]|\\.)*)"\)')
NON_WORD_RE = re.compile(r"[^0-9A-Za-z]+")


@dataclass
class ClickNode:
    name: str = ""
    path: str = ""
    node_type: str = ""
    text: str = ""
    position: str = ""
    size: str = ""
    nodespec: str = ""


def _unescape_python_string(value):
    try:
        return bytes(value, "utf-8").decode("unicode_escape")
    except Exception:
        return value


def _python_string(value):
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _is_generated_name(name):
    stripped = name.strip()
    return (
        not stripped
        or stripped.startswith("<Node | Tag =")
        or stripped.startswith("<")
        or stripped == "MainGameScene"
    )


def short_selector_names(names, max_depth=3):
    """只看当前节点和向上两级；其中匿名 Tag 节点不输出，也不向上递补。"""
    candidates = names[-max_depth:]
    return [name for name in candidates if not _is_generated_name(name)]


def _snake_case(value):
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = NON_WORD_RE.sub("_", value).strip("_").lower()
    return value or "node"


def parse_nodespec(nodespec):
    root_match = NODESPEC_ROOT_RE.search(nodespec or "")
    if not root_match:
        return []
    names = [_unescape_python_string(root_match.group(1))]
    names.extend(_unescape_python_string(match.group(1)) for match in NODESPEC_CHILD_RE.finditer(nodespec))
    return names


def stable_names_from_click(click):
    names = parse_nodespec(click.nodespec)
    if not names and click.path:
        names = [part for part in click.path.split("/") if part]
    if not names and click.name:
        names = [click.name]
    return short_selector_names(names)


def build_poco_expr(names):
    if not names:
        return ""
    root, *children = names
    expr = f"poco({_python_string(root)})"
    for child_name in children:
        expr += f".child({_python_string(child_name)})"
    return expr


def build_node_config_expr(names, desc):
    if not names:
        return ""
    root, *children = names
    config = {"root": root, "desc": desc}
    if children:
        config["chain"] = [["child", child_name] for child_name in children]
    return json.dumps(config, ensure_ascii=False)


def build_key(names, prefix):
    if prefix:
        return f"{_snake_case(prefix)}_{_snake_case(names[-1]) if names else 'node'}"
    useful = [name for name in names if not _is_generated_name(name)]
    if len(useful) >= 2:
        return f"{_snake_case(useful[-2])}_{_snake_case(useful[-1])}"
    if useful:
        return _snake_case(useful[-1])
    return "clicked_node"


def describe_click(click, names, prefix):
    desc_parts = []
    if prefix:
        desc_parts.append(prefix.replace("_", " "))
    if click.name:
        desc_parts.append(click.name)
    return " ".join(desc_parts) or (names[-1] if names else "Poco 点击节点")


def format_click(click, prefix="", output="all"):
    names = stable_names_from_click(click)
    if not names:
        return "未解析到可用节点路径。"

    key = build_key(names, prefix)
    desc = describe_click(click, names, prefix)
    node_config_expr = build_node_config_expr(names, desc)
    poco_expr = build_poco_expr(names)

    blocks = []
    if output in {"all", "entry"}:
        blocks.append(f'"{key}": {node_config_expr},')
    if output in {"all", "poco"}:
        blocks.append(f"{poco_expr}.click()")
    if output in {"all", "script"}:
        blocks.append(f"if_click({poco_expr}, {_python_string(desc)}, timeout=2)")
    return "\n".join(blocks)


INDEX_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Poco 点击日志生成器</title>
  <style>
    :root {
      --bg: #f6f7fb;
      --panel: #ffffff;
      --border: #d8dee9;
      --text: #20242a;
      --muted: #687385;
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --danger: #dc2626;
      --ok: #15803d;
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
      grid-template-columns: minmax(360px, 0.8fr) minmax(520px, 1.2fr);
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

    .toolbar, .form {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 12px;
      border-bottom: 1px solid var(--border);
      flex-wrap: wrap;
    }

    .form {
      align-items: stretch;
      flex-direction: column;
    }

    label {
      color: var(--muted);
      font-size: 13px;
    }

    input, select {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 14px;
    }

    .row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
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
    button.danger { background: var(--danger); }
    button:disabled {
      cursor: not-allowed;
      opacity: 0.65;
    }

    .status {
      color: var(--muted);
      font-size: 13px;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
    }

    .status.running { color: var(--ok); }
    .status.error { color: var(--danger); }

    .device-list {
      padding: 12px;
      overflow: auto;
      min-height: 90px;
      border-bottom: 1px solid var(--border);
    }

    .device {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 8px 10px;
      margin-bottom: 8px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 13px;
    }

    .muted {
      color: var(--muted);
      font-size: 12px;
    }

    .history {
      flex: 1;
      overflow: auto;
      padding: 12px;
    }

    .card {
      border: 1px solid var(--border);
      border-radius: 12px;
      margin-bottom: 12px;
      overflow: hidden;
      background: #fff;
    }

    .card-head {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      align-items: center;
    }

    .card-title {
      font-weight: 650;
      font-size: 14px;
    }

    .path {
      color: var(--muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
      overflow-wrap: anywhere;
      padding: 0 12px 10px;
    }

    pre {
      margin: 0;
      padding: 12px;
      background: var(--code);
      color: var(--code-text);
      overflow: auto;
      font-size: 13px;
      line-height: 1.5;
    }

    .logs {
      height: 160px;
      overflow: auto;
      border-top: 1px solid var(--border);
      background: #111827;
      color: #d1d5db;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
      padding: 10px;
      white-space: pre-wrap;
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
    <h1>Poco 点击日志生成器</h1>
    <div class="hint">选择 adb 设备端口后开始监听，点击游戏节点时会实时生成可复制的 JSON 节点配置和 Poco 调用代码。</div>
  </header>

  <main>
    <section>
      <div class="form">
        <div>
          <label for="serialInput">adb serial / 端口</label>
          <input id="serialInput" placeholder="例如 127.0.0.1:7555；留空表示 adb 默认设备" />
        </div>
        <div class="row">
          <div>
            <label for="prefixInput">节点名前缀</label>
            <input id="prefixInput" placeholder="例如 login_bonus / guide" />
          </div>
          <div>
            <label for="outputSelect">输出格式</label>
            <select id="outputSelect">
              <option value="all">全部</option>
              <option value="entry">JSON 配置条目</option>
              <option value="poco">poco(...).click()</option>
              <option value="script">if_click 示例</option>
            </select>
          </div>
        </div>
        <label><input id="clearCheckbox" type="checkbox" checked /> 开始前清空当前设备 logcat</label>
        <div class="toolbar" style="padding: 0; border-bottom: 0;">
          <button id="startBtn">开始监听</button>
          <button id="stopBtn" class="danger" disabled>停止</button>
          <button id="refreshBtn" class="secondary">刷新设备</button>
          <button id="clearBtn" class="secondary">清空结果</button>
        </div>
      </div>
      <div id="status" class="status">未开始监听。</div>
      <div id="devices" class="device-list">
        <div class="muted">点击“刷新设备”查看当前 adb devices。</div>
      </div>
      <div id="logs" class="logs"></div>
    </section>

    <section>
      <div class="toolbar">
        <button id="copyLatestBtn">复制最新代码</button>
        <button id="copyAllBtn" class="secondary">复制全部代码</button>
      </div>
      <div id="history" class="history">
        <div class="muted">监听中点击游戏节点后，生成结果会显示在这里。</div>
      </div>
    </section>
  </main>

  <script>
    const serialInput = document.getElementById("serialInput");
    const prefixInput = document.getElementById("prefixInput");
    const outputSelect = document.getElementById("outputSelect");
    const clearCheckbox = document.getElementById("clearCheckbox");
    const startBtn = document.getElementById("startBtn");
    const stopBtn = document.getElementById("stopBtn");
    const refreshBtn = document.getElementById("refreshBtn");
    const clearBtn = document.getElementById("clearBtn");
    const statusEl = document.getElementById("status");
    const devicesEl = document.getElementById("devices");
    const logsEl = document.getElementById("logs");
    const historyEl = document.getElementById("history");
    const copyLatestBtn = document.getElementById("copyLatestBtn");
    const copyAllBtn = document.getElementById("copyAllBtn");

    let source = null;
    let latestCode = "";
    let allCodes = [];

    function setStatus(text, cls = "") {
      statusEl.className = `status ${cls}`;
      statusEl.textContent = text;
    }

    function appendLog(text) {
      logsEl.textContent += `${text}\n`;
      logsEl.scrollTop = logsEl.scrollHeight;
    }

    function escapeHtml(value) {
      return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    async function copyText(text) {
      if (!text) return;
      await navigator.clipboard.writeText(text);
      appendLog("已复制代码。");
    }

    async function refreshDevices() {
      devicesEl.innerHTML = '<div class="muted">正在读取 adb devices...</div>';
      try {
        const res = await fetch("/api/devices");
        const data = await res.json();
        if (!data.ok) throw new Error(data.error || "读取失败");
        if (!data.devices.length) {
          devicesEl.innerHTML = '<div class="muted">没有发现 device 状态的 adb 设备。</div>';
          return;
        }
        devicesEl.innerHTML = data.devices.map((device) => `
          <div class="device">
            <span>${escapeHtml(device.serial)}</span>
            <button class="secondary" data-serial="${escapeHtml(device.serial)}">使用</button>
          </div>
        `).join("");
        devicesEl.querySelectorAll("button[data-serial]").forEach((button) => {
          button.addEventListener("click", () => {
            serialInput.value = button.dataset.serial;
          });
        });
      } catch (err) {
        devicesEl.innerHTML = `<div class="muted">读取设备失败：${escapeHtml(err.message)}</div>`;
      }
    }

    function addClickCard(payload) {
      latestCode = payload.code || "";
      if (latestCode) allCodes.push(latestCode);
      const empty = historyEl.querySelector(".muted");
      if (empty) empty.remove();

      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div class="card-head">
          <div>
            <div class="card-title">${escapeHtml(payload.time)} ${escapeHtml(payload.name || "-")}</div>
            <div class="muted">点击后生成，可直接复制</div>
          </div>
          <button class="secondary">复制</button>
        </div>
        <div class="path">${escapeHtml(payload.path || "-")}</div>
        <pre>${escapeHtml(payload.code || "")}</pre>
      `;
      card.querySelector("button").addEventListener("click", () => copyText(payload.code));
      historyEl.prepend(card);
    }

    function startListen() {
      if (source) source.close();
      const params = new URLSearchParams({
        serial: serialInput.value.trim(),
        prefix: prefixInput.value.trim(),
        output: outputSelect.value,
        clear: clearCheckbox.checked ? "1" : "0",
      });
      setStatus("正在连接 adb logcat...", "running");
      appendLog("开始监听。");
      source = new EventSource(`/api/listen?${params.toString()}`);

      source.addEventListener("status", (event) => {
        const payload = JSON.parse(event.data);
        setStatus(payload.message, payload.level || "running");
        appendLog(payload.message);
      });
      source.addEventListener("click", (event) => {
        addClickCard(JSON.parse(event.data));
      });
      source.addEventListener("log", (event) => {
        const payload = JSON.parse(event.data);
        appendLog(payload.message);
      });
      source.onerror = () => {
        setStatus("监听连接已断开。", "error");
        stopListen(false, false);
      };

      startBtn.disabled = true;
      stopBtn.disabled = false;
    }

    function stopListen(writeLog = true, resetStatus = true) {
      if (source) {
        source.close();
        source = null;
      }
      startBtn.disabled = false;
      stopBtn.disabled = true;
      if (writeLog) appendLog("已停止监听。");
      if (resetStatus) setStatus("未开始监听。");
    }

    startBtn.addEventListener("click", startListen);
    stopBtn.addEventListener("click", () => stopListen(true));
    refreshBtn.addEventListener("click", refreshDevices);
    clearBtn.addEventListener("click", () => {
      latestCode = "";
      allCodes = [];
      historyEl.innerHTML = '<div class="muted">监听中点击游戏节点后，生成结果会显示在这里。</div>';
      logsEl.textContent = "";
    });
    copyLatestBtn.addEventListener("click", () => copyText(latestCode));
    copyAllBtn.addEventListener("click", () => copyText(allCodes.join("\n\n")));

    refreshDevices();
  </script>
</body>
</html>
"""


def sse_send(handler, event, data):
    payload = json.dumps(data, ensure_ascii=False)
    handler.wfile.write(f"event: {event}\n".encode("utf-8"))
    handler.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
    handler.wfile.flush()


def list_adb_devices():
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return {
            "ok": False,
            "error": (result.stderr or result.stdout or "adb devices 执行失败").strip(),
            "devices": [],
        }

    devices = []
    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append({"serial": parts[0], "state": parts[1]})
    return {"ok": True, "devices": devices}


def clear_logcat(serial):
    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["logcat", "-c"])
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.returncode, (result.stderr or result.stdout or "").strip()


def start_logcat(serial):
    cmd = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(["logcat", "-v", "time"])
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)


def stream_logcat(handler, serial, prefix, output, clear):
    if clear:
        code, message = clear_logcat(serial)
        if code != 0:
            sse_send(handler, "status", {"level": "error", "message": f"清空 logcat 失败：{message}"})
            return

    process = start_logcat(serial)
    serial_text = serial or "adb 默认设备"
    sse_send(handler, "status", {"level": "running", "message": f"正在监听 {serial_text} 的 adb logcat..."})

    current = None
    try:
        for raw_line in process.stdout:
            line = raw_line.rstrip("\n")
            lua_match = LUA_PRINT_RE.search(line)
            if not lua_match:
                lowered = line.lower()
                if any(word in lowered for word in ("error", "failed", "more than one device", "no devices", "unauthorized")):
                    sse_send(handler, "log", {"message": line})
                continue

            message = lua_match.group(1).strip()
            if message == LOG_MARKER:
                current = ClickNode()
                continue

            if current is None:
                continue

            field_match = FIELD_RE.match(message)
            if not field_match:
                continue

            key, value = field_match.groups()
            if key == "type":
                current.node_type = value
            else:
                setattr(current, key, value)

            if key == "nodespec":
                now = datetime.now().strftime("%H:%M:%S")
                sse_send(handler, "click", {
                    "time": now,
                    "name": current.name,
                    "path": current.path,
                    "code": format_click(current, prefix=prefix, output=output),
                })
                current = None

        return_code = process.wait()
        sse_send(handler, "status", {
            "level": "error" if return_code else "",
            "message": f"adb logcat 已退出，退出码：{return_code}",
        })
    except (BrokenPipeError, ConnectionResetError):
        pass
    finally:
        if process.poll() is None:
            process.terminate()


class PocoLogWebHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[web] {self.address_string()} - {fmt % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
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
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ("/", "/index.html"):
            self.send_html()
            return
        if path == "/api/devices":
            self.send_json(list_adb_devices())
            return
        if path == "/api/listen":
            query = parse_qs(parsed.query)
            serial = query.get("serial", [""])[0].strip()
            prefix = query.get("prefix", [""])[0].strip()
            output = query.get("output", ["all"])[0].strip() or "all"
            clear = query.get("clear", ["0"])[0] == "1"
            if output not in {"all", "entry", "poco", "script"}:
                output = "all"

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            stream_logcat(self, serial=serial, prefix=prefix, output=output, clear=clear)
            return
        self.send_error(404, "Not found")


def parse_args():
    parser = argparse.ArgumentParser(description="启动 Poco 点击日志网页生成器")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址，默认 127.0.0.1")
    parser.add_argument("--port", type=int, default=8766, help="网页端口，默认 8766")
    parser.add_argument("--no-open", action="store_true", help="启动后不自动打开浏览器")
    return parser.parse_args()


def create_server(host, port, max_attempts=20):
    for offset in range(max_attempts):
        candidate_port = port + offset
        try:
            server = ThreadingHTTPServer((host, candidate_port), PocoLogWebHandler)
            if offset:
                print(f"端口 {port} 已被占用，已自动切换到 {candidate_port}。")
            return server, candidate_port
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE:
                raise
    raise OSError(f"{host}:{port}-{port + max_attempts - 1} 都被占用，请用 --port 指定其他端口")


def main():
    args = parse_args()
    server, actual_port = create_server(args.host, args.port)
    url = f"http://{args.host}:{actual_port}"
    print(f"Poco 点击日志生成器已启动：{url}")
    print("在网页选择 adb serial/端口后开始监听，点击游戏节点即可生成代码。")
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止 Poco 点击日志生成器。")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
