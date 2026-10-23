"""编排层 —— LLM 只负责「选实验 + 传数据」，绝不碰计算。"""
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .guard import ground_template
from .runner import run_tool, Record, replay
from ..format import format_quantity


@dataclass
class ConductorResult:
    experiment: Dict[str, Any]
    record: Record
    checks: List[str]
    metrics: Dict[str, Any]
    conclusion: str
    grounded: bool
    replay_match: bool


def _derived_ctx(outputs: Dict[str, Any], expansion_k: int = 2) -> Dict[str, Any]:
    ctx = dict(outputs)
    if "intercept_ok" in ctx:
        ctx["intercept_ok_cn"] = "通过" if ctx["intercept_ok"] else "不通过"
    for key, val in list(outputs.items()):
        if key.startswith("u_") and isinstance(val, (int, float)):
            base = key[2:]
            ctx[f"{key}_k{expansion_k}"] = expansion_k * val
            if base in outputs and isinstance(outputs[base], (int, float)) and outputs[base] != 0:
                ctx[f"{key}_rel"] = val / outputs[base] * 100.0
                ctx[f"{base}_fmt"] = format_quantity(outputs[base], val, expansion_k)
        if key == "share" and isinstance(val, dict):
            for sk, sv in val.items():
                ctx[f"share_{sk}"] = float(sv) * 100.0
            labels = outputs.get("share_labels") or {}
            top = max(val, key=val.get)
            ctx["dominant"] = f"{labels.get(top, top)}（{val[top] * 100:.1f}%）"
    return ctx


class Conductor:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def solve_experiment(self, experiment: Dict[str, Any], data: Dict[str, Any]) -> ConductorResult:
        record = run_tool(experiment["tool"], data)
        checks = self._run_postconditions(experiment.get("checks", []), record)
        expansion_k = int(self.config.get("defaults", {}).get("expansion_k", 2))
        ctx = _derived_ctx(record.outputs, expansion_k)
        template = experiment.get("conclusion", "")
        conclusion = template.format(**ctx) if template else ""
        grounded = ground_template(template, ctx)
        replay_out = replay(record)
        replay_match = replay_out == record.outputs
        return ConductorResult(experiment, record, checks, ctx, conclusion, grounded, replay_match)

    @staticmethod
    def _run_postconditions(checks: List[str], record: Record) -> List[str]:
        o = record.outputs
        results = []
        for cond in checks:
            passed = True
            try:
                if cond == "intercept_ok":
                    passed = bool(o.get("intercept_ok"))
                else:
                    m = re.match(r"^([A-Za-z_]\w*)\s*(>=|<=|==|!=|>|<)\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)$", cond.strip())
                    if m:
                        key, op, num = m.group(1), m.group(2), float(m.group(3))
                        val = float(o[key])
                        passed = {
                            ">": val > num, ">=": val >= num, "<": val < num,
                            "<=": val <= num, "==": val == num, "!=": val != num,
                        }[op]
                    else:
                        passed = True
            except Exception:
                passed = False
            results.append(f"{'通过' if passed else '不通过'} · {cond}")
        return results
