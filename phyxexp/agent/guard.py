"""守卫 —— 「约束本身就是可信度的来源」。

1. 白名单守卫：只允许 TOOL_REGISTRY 里的工具；拒绝一切任意代码执行/自行算数。
2. grounding：结论模板的每个字段都必须能溯源到工具输出（否则拒绝）。
"""
import re
from typing import Any, Dict

from .registry import TOOL_REGISTRY


class GuardError(RuntimeError):
    """约束被违反。"""


def assert_allowed(name: str) -> None:
    if name not in TOOL_REGISTRY:
        raise GuardError(
            f"拒绝执行：工具 {name!r} 不在审查过的领域工具链中。"
            "Agent 不允许自行写代码/算数，只能调用白名单工具。"
        )


def ground_template(template: str, ctx: Dict[str, Any]) -> bool:
    """结论模板中的每个占位字段，都必须能在工具输出/派生上下文中溯源。"""
    if not template:
        return True
    fields = re.findall(r"\{([^{}:]+)(?::[^{}]*)?\}", template)
    return all(f in ctx for f in fields)


def ground(conclusion: Dict[str, Any], record_outputs: Dict[str, Any]) -> bool:
    """（兼容）校验结论字典中的每个数值指标都能在工具输出中溯源。"""
    return all(
        key in record_outputs
        for key, val in conclusion.items()
        if isinstance(val, (int, float))
    )
