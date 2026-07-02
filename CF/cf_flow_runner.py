# -*- coding: utf-8 -*-
"""Flow runner for UI automation test cases."""

from dataclasses import dataclass

from airtest.core.api import sleep

from cf_behavior_tree import BTStatus, BehaviorContext


@dataclass
class FlowStep:
    """One named step in a test flow."""

    name: str
    action: object


class FlowRunner:
    """Runs high-level test flow steps on top of a state machine."""

    def __init__(self, state_machine):
        # 统一复用外部注入的状态机，FlowRunner 只负责流程编排。
        self.state_machine = state_machine

    def run(self, steps):
        # 顺序执行步骤：任一步骤返回 False 即视为流程失败并立即中断。
        for step in steps:
            print(f"[FLOW] start: {step.name}")
            result = step.action()
            if result is False:
                # 失败时抓取当前未知页面，便于回溯 UI 停在了哪里。
                self.state_machine.dump_unknown(f"flow_step_failed_{step.name}")
                print(f"[FLOW] failed: {step.name}")
                return False
            print(f"[FLOW] done: {step.name}")
        return True

    def wait_state(self, expected_states, timeout=10):
        def action():
            # 等待状态机进入期望状态（支持单个字符串或状态集合）。
            state = self.state_machine.wait_for_state(expected_states, timeout=timeout)
            if isinstance(expected_states, str):
                expected = {expected_states}
            else:
                expected = set(expected_states)
            # 仅当最终状态命中期望集合时，步骤判定成功。
            return state.name in expected

        return action

    def click_feature(self, feature, expected_states=None, timeout=10):
        def action():
            # 先点击功能入口；点击失败直接返回，避免误判后续状态。
            if not self.state_machine.click_feature(feature, label=feature):
                return False
            if not expected_states:
                # 未指定后置状态时，只以点击结果作为成功条件。
                return True
            # 指定了后置状态时，继续等待页面跳转完成。
            return self.wait_state(expected_states, timeout=timeout)()

        return action

    def run_tree(self, tree, context=None, max_ticks=60, interval=0.5, dump_reason="behavior_tree_failed"):
        # 未传上下文时自动创建，确保行为树节点共享同一份运行数据。
        context = context or BehaviorContext(self.state_machine)

        def action():
            # 轮询 tick 行为树，直到成功(done=True)、失败或超时。
            for index in range(max_ticks):
                print(f"[BT] tick {index + 1}/{max_ticks}: {tree.name}")
                status = tree.tick(context)
                if status == BTStatus.SUCCESS and context.data.get("done"):
                    # 约定 done=True 代表业务流程真正完成，避免提前成功。
                    return True
                if status == BTStatus.FAILURE:
                    # 行为树显式失败时抓取现场，便于定位失败节点。
                    self.state_machine.dump_unknown(dump_reason)
                    return False
                sleep(interval)
            # 达到最大轮询次数仍未结束，按超时失败处理。
            self.state_machine.dump_unknown(f"{dump_reason}_timeout")
            return False

        return action
