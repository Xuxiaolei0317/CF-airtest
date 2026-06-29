#!/usr/bin/env python3
# -*- encoding=utf8 -*-
"""CF 主题遍历专用行为树。

这个模块只处理主题遍历里的“动作后必须验状态”闭环：
进入主题必须最终到 THEME_HOME，返回大厅必须最终到 LOBBY_HOME。
"""

import time
from dataclasses import dataclass
from typing import Callable

from airtest.core.api import sleep

from cf_behavior_tree import BTStatus


@dataclass
class ThemeTraversalCallbacks:
    """主题遍历行为树依赖的外部动作，便于复用现有节点和状态机。"""

    is_theme_home: Callable[[], bool]
    is_theme_loading: Callable[[], bool]
    is_lobby_home: Callable[[], bool]
    detect_state: Callable[[], object]
    recover_blockers: Callable[[int], bool]
    close_popups: Callable[[int], bool]
    dump_unknown: Callable[[str], object]
    open_theme_select: Callable[[int], bool]
    click_high_enter: Callable[[], bool]
    click_return_lobby: Callable[[], bool]


@dataclass
class GoalResult:
    """一次行为树目标执行结果。"""

    status: BTStatus
    action_failed: bool = False
    attempts: int = 0


class ThemeTraversalTree:
    """主题遍历专用行为树，负责把点击动作和页面结果绑定校验。"""

    def __init__(
        self,
        callbacks,
        interval=0.5,
        state_check_interval=2,
        action_retry_interval=3,
        popup_recover_tries=4,
        expected_stable_seconds=0,
        wait_log_interval=5,
    ):
        self.callbacks = callbacks
        self.interval = interval
        self.state_check_interval = state_check_interval
        self.action_retry_interval = action_retry_interval
        self.popup_recover_tries = popup_recover_tries
        self.expected_stable_seconds = expected_stable_seconds
        self.wait_log_interval = wait_log_interval

    def enter_theme(self, theme_id, timeout):
        """进入主题：点击高级房后必须验证到 THEME_HOME，否则返回明确失败类型。"""
        result = self._run_goal(
            name=f"enter_theme_{theme_id}",
            is_expected=self.callbacks.is_theme_home,
            should_wait=self.callbacks.is_theme_loading,
            action=lambda: self._click_theme_entry(theme_id),
            timeout=timeout,
            fail_on_action_false=True,
            retry_after_success=False,
            success_on_recover=True,
        )

        if result.status == BTStatus.SUCCESS:
            return "success"

        if result.action_failed:
            self.callbacks.dump_unknown(f"theme_{theme_id}_high_enter_missing")
            return "no_config"

        self.callbacks.dump_unknown(f"theme_{theme_id}_enter_timeout")
        return "enter_failed"

    def return_to_lobby(self, theme_id, timeout):
        """返回大厅：点击返回按钮后必须验证到 LOBBY_HOME，避免只信点击结果。"""
        result = self._run_goal(
            name=f"return_lobby_{theme_id}",
            is_expected=self.callbacks.is_lobby_home,
            action=lambda: self._click_return_lobby(theme_id),
            timeout=timeout,
            fail_on_action_false=True,
            retry_after_success=True,
            success_on_recover=False,
        )

        if result.status == BTStatus.SUCCESS:
            return True

        if result.action_failed:
            self.callbacks.dump_unknown(f"theme_{theme_id}_return_button_missing")
        else:
            self.callbacks.dump_unknown(f"theme_{theme_id}_return_lobby_timeout")
        return False

    def _run_goal(
        self,
        name,
        is_expected,
        action,
        timeout,
        fail_on_action_false=False,
        retry_after_success=False,
        success_on_recover=False,
        should_wait=None,
    ):
        """按行为树思路循环：先验目标，再处理弹窗，最后执行动作并等待结果。"""
        end_time = time.time() + timeout
        next_state_check_at = 0
        next_action_at = 0
        attempts = 0
        successful_actions = 0
        expected_since = None
        next_wait_log_at = 0

        while time.time() < end_time:
            now = time.time()
            if is_expected():
                if expected_since is None:
                    expected_since = now
                if now - expected_since >= self.expected_stable_seconds:
                    print(f"[THEME_BT] success: {name}")
                    return GoalResult(BTStatus.SUCCESS, attempts=attempts)
            else:
                expected_since = None

            if now >= next_state_check_at and self._recover_if_blocked():
                if success_on_recover and successful_actions > 0:
                    # 进入主题后能处理到主题内弹窗，说明已越过 loading，直接进入返回大厅流程。
                    print(f"[THEME_BT] success after popup recover: {name}")
                    return GoalResult(BTStatus.SUCCESS, attempts=attempts)
                # 其他目标仍需重新验目标，不把刚才的点击结果直接当成功。
                expected_since = None
                next_action_at = now + self.action_retry_interval
                next_state_check_at = now + self.state_check_interval
                sleep(self.interval)
                continue

            if should_wait and successful_actions > 0 and should_wait():
                # 进入动作已触发但 loading2 仍可见，说明主题还没真正进入；超时后记录失败主题。
                if now >= next_wait_log_at:
                    print(f"[THEME_BT] still loading2: {name}")
                    next_wait_log_at = now + self.wait_log_interval
                next_action_at = now + self.action_retry_interval
                sleep(self.interval)
                continue

            if now >= next_action_at and (retry_after_success or successful_actions == 0):
                attempts += 1
                print(f"[THEME_BT] action {attempts}: {name}")
                if not action():
                    print(f"[THEME_BT] action failed: {name}")
                    if fail_on_action_false and successful_actions == 0:
                        return GoalResult(BTStatus.FAILURE, action_failed=True, attempts=attempts)
                else:
                    successful_actions += 1
                next_action_at = now + self.action_retry_interval

            next_state_check_at = max(next_state_check_at, now + self.state_check_interval)
            sleep(self.interval)

        print(f"[THEME_BT] timeout: {name}")
        return GoalResult(BTStatus.FAILURE, attempts=attempts)

    def _recover_if_blocked(self):
        """快速尝试关闭阻塞弹窗，避免完整状态机扫描拖慢主题等待。"""
        try:
            recovered = self.callbacks.recover_blockers(self.popup_recover_tries)
        except Exception as e:
            print(f"[THEME_BT] 快速弹窗恢复异常，继续行为树流程：{e}")
            return False

        if not recovered:
            return False

        print("[THEME_BT] 已快速处理弹窗阻塞，继续判断目标状态")
        return True

    def _click_theme_entry(self, theme_id):
        """打开主题选房并点击高级房，后续由行为树验证是否真的进入主题。"""
        self.callbacks.open_theme_select(theme_id)
        return self.callbacks.click_high_enter()

    def _click_return_lobby(self, theme_id):
        """返回前先清理主题内弹窗，避免返回按钮被遮挡导致假点击。"""
        self.callbacks.close_popups(self.popup_recover_tries)
        return self.callbacks.click_return_lobby()
