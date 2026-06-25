# -*- coding: utf-8 -*-
"""CF 轻量状态机。

复用 CF_nodes.json 中的节点定义识别页面状态，并把通用弹窗处理、
状态等待和 UNKNOWN 现场留证据收口到一个模块里。
"""

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from airtest.core.api import sleep, snapshot

import CF_nodes
from CF_nodes import if_click, node_exists


CF_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CF_DIR.parent
STATES_CONFIG_PATH = CF_DIR / "CF_states.json"
STATE_DUMP_DIR = PROJECT_ROOT / "node_dumps" / "CF" / "state_machine"
SCREENSHOT_DIR = CF_DIR / "screenshots"


@dataclass(frozen=True)
class StateMatch:
    """一次状态识别结果。"""

    name: str
    hits: int = 0
    total: int = 0
    matched_features: tuple = ()
    desc: str = ""

    @property
    def is_unknown(self):
        return self.name == "UNKNOWN"


def _safe_filename(value):
    return re.sub(r"[^0-9A-Za-z_\u4e00-\u9fa5-]+", "_", value).strip("_") or "unknown"


class CFStateMachine:
    """基于节点特征的 CF 最小可用状态机。"""

    def __init__(self, config_path=STATES_CONFIG_PATH, poco_driver=None):
        self.config_path = Path(config_path)
        if poco_driver is not None:
            CF_nodes.poco = poco_driver
        self.poco = poco_driver or CF_nodes.poco
        self.state_config = self.load_config()
        self.last_state = StateMatch("UNKNOWN")

    def load_config(self):
        with self.config_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def resolve_feature(self, feature):
        return CF_nodes.resolve_node(feature)

    def feature_exists(self, feature):
        try:
            return node_exists(self.resolve_feature(feature))
        except Exception as e:
            print(f"状态特征检查失败：{feature} | {e}")
            return False

    def detect_state(self, verbose=False):
        """识别当前页面状态，返回 StateMatch。"""
        candidates = []
        for state_name, config in self.state_config.items():
            features = config.get("features", [])
            matched = tuple(
                feature
                for feature in features
                if self.feature_exists(feature)
            )
            min_hits = int(config.get("min_hits", 1))
            if len(matched) >= min_hits:
                candidates.append(
                    (
                        int(config.get("priority", 0)),
                        len(matched),
                        StateMatch(
                            state_name,
                            hits=len(matched),
                            total=len(features),
                            matched_features=matched,
                            desc=config.get("desc", ""),
                        ),
                    )
                )

        if not candidates:
            self.last_state = StateMatch("UNKNOWN")
        else:
            _, _, self.last_state = max(candidates, key=lambda item: (item[0], item[1]))

        if verbose:
            print(
                f"当前状态：{self.last_state.name} "
                f"({self.last_state.hits}/{self.last_state.total}) "
                f"{list(self.last_state.matched_features)}"
            )
        return self.last_state

    def click_feature(self, feature, label=None):
        try:
            return if_click(self.resolve_feature(feature), label=label)
        except Exception as e:
            print(f"状态机点击失败：{feature} | {e}")
            return False

    def recover_blockers(self, max_tries=3):
        """处理通用弹窗/遮罩，返回是否处理过阻塞。"""
        recovered = False
        blocker_actions = (
            "cashgo.collect_btn",
            "common.btn_collect",
            "cashgo.btn_close",
            "common.btn_close",
            "common.close_btn",
            "common.mask_close",
            "common.btn_confirm",
        )

        for _ in range(max_tries):
            state = self.detect_state()
            if state.name != "POPUP_BLOCKING":
                break

            clicked = False
            for feature in blocker_actions:
                if self.click_feature(feature, label=f"blocker:{feature}"):
                    sleep(0.5)
                    clicked = True
                    recovered = True
                    break

            if not clicked:
                break

        return recovered

    def wait_for_state(self, expected_states, timeout=10, interval=0.5, recover=True):
        """等待进入目标状态；过程中遇到通用弹窗会先处理。"""
        if isinstance(expected_states, str):
            expected_states = {expected_states}
        else:
            expected_states = set(expected_states)

        end_time = time.time() + timeout
        while time.time() < end_time:
            state = self.detect_state(verbose=True)
            if state.name in expected_states:
                return state
            if recover and state.name == "POPUP_BLOCKING":
                self.recover_blockers()
            sleep(interval)

        state = self.detect_state(verbose=True)
        if state.name not in expected_states:
            self.dump_unknown(f"wait_for_{'_'.join(sorted(expected_states))}_got_{state.name}", state=state)
        return state

    def go_to(self, expected_states, action, timeout=10, recover=True):
        """执行动作并等待目标状态。"""
        if recover:
            self.recover_blockers()
        action()
        return self.wait_for_state(expected_states, timeout=timeout, recover=recover)

    def capture_screen(self, reason):
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        file_path = SCREENSHOT_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{_safe_filename(reason)}.png"
        try:
            snapshot(filename=str(file_path), msg=reason)
            print(f"状态机截图：{file_path}")
            return str(file_path)
        except Exception as e:
            print(f"状态机截图失败：{reason} | {e}")
            return None

    def dump_unknown(self, reason="unknown_state", state=None):
        """保存 UNKNOWN 或未达预期状态的截图和节点树，方便后续反哺规则。"""
        STATE_DUMP_DIR.mkdir(parents=True, exist_ok=True)
        state = state or self.detect_state()
        screenshot_path = self.capture_screen(reason)
        file_path = STATE_DUMP_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{_safe_filename(reason)}.json"

        try:
            hierarchy = self.poco.agent.hierarchy.dump()
        except Exception as e:
            print(f"状态机节点树导出失败：{e}")
            hierarchy = None

        data = {
            "reason": reason,
            "state": state.name,
            "state_desc": state.desc,
            "matched_features": list(state.matched_features),
            "screenshot": screenshot_path,
            "hierarchy": hierarchy,
        }
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2, default=str)
        print(f"状态机已导出现场：{file_path}")
        return file_path


def create_state_machine(poco_driver=None):
    return CFStateMachine(poco_driver=poco_driver)
