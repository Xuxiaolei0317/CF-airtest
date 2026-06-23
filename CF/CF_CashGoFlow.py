#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cash Go flow + behavior tree example.

Run:
    python run_tests.py --game cf --module CashGoFlow
"""

import re
import sys
from pathlib import Path

from airtest.core.api import log, sleep

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from airtest_booststrap import ST, poco

import CF_nodes
from CF_nodes import GameActions, node_text
from CF_state_machine import create_state_machine
from cf_behavior_tree import Action, BehaviorContext, Condition, Selector, Sequence
from cf_flow_runner import FlowRunner, FlowStep


ST.SAVE_IMAGE = True
CF_nodes.poco = poco

GAME = GameActions(poco)
SM = create_state_machine(poco)
FLOW = FlowRunner(SM)

CASH_GO_STATES = {"CASH_GO_BUILD", "CASH_GO_COMPLETE", "CASH_GO_OOC"}


def current_state(context, verbose=True):
    state = context.state_machine.detect_state(verbose=verbose)
    context.data["state"] = state
    return state


def state_is(*names):
    expected = set(names)

    def predicate(context):
        return current_state(context).name in expected

    return predicate


def cashgo_level(default=0):
    text = node_text("cashgo", "rank_label", "")
    match = re.search(r"#?\s*(\d+)", text or "")
    return int(match.group(1)) if match else default


def enter_cash_go():
    SM.recover_blockers()
    state = SM.detect_state(verbose=True)
    if state.name in CASH_GO_STATES:
        return True
    if state.name != "LOBBY_HOME":
        SM.dump_unknown("cashgo_flow_not_at_lobby", state=state)
        return False
    return FLOW.click_feature(("lobby", "cash_go"), expected_states=CASH_GO_STATES, timeout=10)()


def handle_popup(context):
    return context.state_machine.recover_blockers(max_tries=3)


def handle_ooc(context):
    """Buy coins from the OOC/shop path and return to build."""
    sm = context.state_machine
    sm.click_feature(("cashgo", "btn_close"), label="cashgo.ooc.close")
    sleep(0.5)
    sm.click_feature(("cashgo", "top_coin_add_btn"), label="cashgo.top_coin_add")
    sleep(0.5)
    for _ in range(3):
        clicked = (
            sm.click_feature(("cashgo", "shop_price_9999"), label="cashgo.shop_price_9999")
            or sm.click_feature(("cashgo", "buy_btn"), label="cashgo.buy_btn")
            or sm.click_feature(("cashgo", "prize_label"), label="cashgo.prize_label")
        )
        if not clicked:
            break
        sleep(0.5)
    sm.click_feature(("cashgo", "slot_build_menu"), label="cashgo.back_to_build")
    sm.wait_for_state(CASH_GO_STATES, timeout=8)
    return True


def handle_complete(context):
    target_level = int(context.data.get("target_level", 0))
    level = cashgo_level()
    print(f"[CashGo] current level: {level}, target: {target_level}")
    context.state_machine.click_feature(("cashgo", "collect_btn"), label="cashgo.collect")
    sleep(1)
    if target_level and level >= target_level:
        context.data["done"] = True
    return True


def tap_build(context):
    if not context.state_machine.click_feature(("cashgo", "build_btn"), label="cashgo.build"):
        return False
    sleep(0.5)
    return True


def dump_unknown(context):
    state = context.state_machine.detect_state(verbose=True)
    context.state_machine.dump_unknown("cashgo_behavior_tree_unknown", state=state)
    return False


def create_cashgo_tree():
    return Selector(
        "cashgo_build_tree",
        [
            Sequence(
                "handle_ooc",
                [
                    Condition("is_ooc", state_is("CASH_GO_OOC")),
                    Action("buy_coins_and_back", handle_ooc),
                ],
            ),
            Sequence(
                "handle_complete",
                [
                    Condition("is_complete", state_is("CASH_GO_COMPLETE")),
                    Action("collect_reward", handle_complete),
                ],
            ),
            Sequence(
                "handle_build",
                [
                    Condition("is_build", state_is("CASH_GO_BUILD")),
                    Action("tap_build", tap_build),
                ],
            ),
            Sequence(
                "handle_popup",
                [
                    Condition("is_popup", state_is("POPUP_BLOCKING")),
                    Action("recover_popup", handle_popup),
                ],
            ),
            Action("dump_unknown", dump_unknown),
        ],
    )


def build_until(target_level=180, max_ticks=300):
    context = BehaviorContext(SM, data={"target_level": target_level})
    tree = create_cashgo_tree()
    return FLOW.run(
        [
            FlowStep("enter_cash_go", enter_cash_go),
            FlowStep(
                "build_until_target",
                FLOW.run_tree(
                    tree,
                    context=context,
                    max_ticks=max_ticks,
                    interval=0.5,
                    dump_reason="cashgo_build_tree_failed",
                ),
            ),
        ]
    )


if __name__ == "__main__":
    log("==== CashGo flow start ====")
    build_until(target_level=180)
    log("==== CashGo flow end ====")
