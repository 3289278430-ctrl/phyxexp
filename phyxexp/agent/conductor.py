"""编排层 —— LLM 只负责「选实验 + 传数据」，绝不碰计算。

支持两种实验：
- 单步：一个实验 = 一个白名单工具（solve_experiment）
- 多步管线：一个实验 = 若干工具 + 派生量按序执行（solve_pipeline）
"""
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


def _resolve(ref, data: Dict[str, Any], ctx: Dict[str, Any]):
    """解析管线引用：data.x / alias.field / 字面量。"""
    if isinstance(ref, (int, float)):
        return ref
    if not isinstance(ref, str):
        return ref
    if ref.startswith("data."):
        return data[ref[5:]]
    if "." in ref:
        head, field = ref.split(".", 1)
        if head in ctx and isinstance(ctx[head], dict):
            return ctx[head][field]
    if ref in data:
        return data[ref]
    if ref in ctx:
        return ctx[ref]
    try:
        return float(ref)
    except Exception:
        return ref


class Conductor:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    # ---------- 单步实验 ----------
    def solve_experiment(self, experiment: Dict[str, Any], data: Dict[str, Any]) -> ConductorResult:
        record = run_tool(experiment["tool"], data)
        return self._finish(experiment, record, replay(record) == record.outputs)

    # ---------- 多步管线 ----------
    def solve_pipeline(self, experiment: Dict[str, Any], data: Dict[str, Any]) -> ConductorResult:
        last_record, final = self._exec_pipeline(experiment, data)
        replay_last, replay_final = self._exec_pipeline(experiment, data)
        return self._finish(experiment, last_record, replay_final == final)

    def _exec_pipeline(self, experiment: Dict[str, Any], data: Dict[str, Any]):
        ctx: Dict[str, Any] = {}
        last_record = None
        for step in experiment["pipeline"]:
            if "tool" in step:
                params = {k: _resolve(v, data, ctx) for k, v in step["params"].items()}
                rec = run_tool(step["tool"], params)
                if step.get("as"):
                    ctx[step["as"]] = rec.outputs
                ctx["_last"] = rec.outputs
                last_record = rec
            elif "derive" in step:
                d = step["derive"]
                a = _resolve(d["a"], data, ctx)
                b = _resolve(d["b"], data, ctx)
                val = {"mul": a * b, "div": a / b, "add": a + b, "sub": a - b}[d["op"]]
                ctx[d["as"]] = val * float(d.get("scale", 1.0))
        return last_record, ctx["_last"]

    def _finish(self, experiment, record, replay_match):
        checks = self._run_postconditions(experiment.get("checks", []), record)
        expansion_k = int(self.config.get("defaults", {}).get("expansion_k", 2))
        ctx = _derived_ctx(record.outputs, expansion_k)
        template = experiment.get("conclusion", "")
        conclusion = template.format(**ctx) if template else ""
        grounded = ground_template(template, ctx)
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
                        passed = {">": val > num, ">=": val >= num, "<": val < num,
                                  "<=": val <= num, "==": val == num, "!=": val != num}[op]
                    else:
                        passed = True
            except Exception:
                passed = False
            results.append(f"{'通过' if passed else '不通过'} · {cond}")
        return results
