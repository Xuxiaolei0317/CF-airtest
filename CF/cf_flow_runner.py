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
        self.state_machine = state_machine

    def run(self, steps):
        for step in steps:
            print(f"[FLOW] start: {step.name}")
            result = step.action()
            if result is False:
                self.state_machine.dump_unknown(f"flow_step_failed_{step.name}")
                print(f"[FLOW] failed: {step.name}")
                return False
            print(f"[FLOW] done: {step.name}")
        return True

    def wait_state(self, expected_states, timeout=10):
        def action():
            state = self.state_machine.wait_for_state(expected_states, timeout=timeout)
            if isinstance(expected_states, str):
                expected = {expected_states}
            else:
                expected = set(expected_states)
            return state.name in expected

        return action

    def click_feature(self, feature, expected_states=None, timeout=10):
        def action():
            if not self.state_machine.click_feature(feature, label=f"{feature[0]}.{feature[1]}"):
                return False
            if not expected_states:
                return True
            return self.wait_state(expected_states, timeout=timeout)()

        return action

    def run_tree(self, tree, context=None, max_ticks=60, interval=0.5, dump_reason="behavior_tree_failed"):
        context = context or BehaviorContext(self.state_machine)

        def action():
            for index in range(max_ticks):
                print(f"[BT] tick {index + 1}/{max_ticks}: {tree.name}")
                status = tree.tick(context)
                if status == BTStatus.SUCCESS and context.data.get("done"):
                    return True
                if status == BTStatus.FAILURE:
                    self.state_machine.dump_unknown(dump_reason)
                    return False
                sleep(interval)
            self.state_machine.dump_unknown(f"{dump_reason}_timeout")
            return False

        return action
