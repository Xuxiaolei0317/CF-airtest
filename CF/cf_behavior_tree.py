# -*- coding: utf-8 -*-
"""Small behavior tree primitives for CF automation flows."""

from dataclasses import dataclass, field
from enum import Enum


class BTStatus(str, Enum):
    """Behavior tree node result."""

    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"


@dataclass
class BehaviorContext:
    """Shared runtime context passed to every behavior tree node."""

    state_machine: object
    data: dict = field(default_factory=dict)


class BehaviorNode:
    """Base behavior tree node."""

    def __init__(self, name):
        self.name = name

    def tick(self, context):
        raise NotImplementedError


def to_status(result):
    """Normalize action return values to BTStatus."""
    if isinstance(result, BTStatus):
        return result
    if result is None:
        return BTStatus.SUCCESS
    return BTStatus.SUCCESS if result else BTStatus.FAILURE


class Condition(BehaviorNode):
    """A leaf node that succeeds when predicate(context) is truthy."""

    def __init__(self, name, predicate):
        super().__init__(name)
        self.predicate = predicate

    def tick(self, context):
        return BTStatus.SUCCESS if self.predicate(context) else BTStatus.FAILURE


class Action(BehaviorNode):
    """A leaf node that runs an automation action."""

    def __init__(self, name, action):
        super().__init__(name)
        self.action = action

    def tick(self, context):
        return to_status(self.action(context))


class Sequence(BehaviorNode):
    """Run children in order; fail on the first failure."""

    def __init__(self, name, children):
        super().__init__(name)
        self.children = children

    def tick(self, context):
        for child in self.children:
            status = child.tick(context)
            if status != BTStatus.SUCCESS:
                return status
        return BTStatus.SUCCESS


class Selector(BehaviorNode):
    """Run children in order; succeed on the first success."""

    def __init__(self, name, children):
        super().__init__(name)
        self.children = children

    def tick(self, context):
        for child in self.children:
            status = child.tick(context)
            if status != BTStatus.FAILURE:
                return status
        return BTStatus.FAILURE
