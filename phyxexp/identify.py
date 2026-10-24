"""实验自动识别 —— 根据「用户提示 + 数据形状」推荐最匹配的实验。

配合宿主大模型使用：大模型带着对话上下文（用户说过的话、文件名等）给出 hint，
本模块用 hint 关键词 + 数据列数做确定性匹配，返回候选实验与建议的列→输入映射。
"""
from typing import Any, Dict, List, Optional


def _data_cols(data: Optional[Dict[str, Any]]) -> int:
    if not isinstance(data, dict):
        return 0
    return sum(1 for v in data.values() if isinstance(v, (list, tuple)))


def identify_experiment(config: Dict[str, Any], data: Optional[Dict[str, Any]] = None,
                        hint: Optional[str] = None) -> List[Dict[str, Any]]:
    data_cols = _data_cols(data)
    candidates = []
    for e in config.get("experiments", []):
        score = 0.0
        reasons: List[str] = []
        kws = [e["id"], e["name"], e["tool"]] + list(e.get("keywords", []))
        if hint:
            hl = hint.lower()
            for kw in kws:
                if kw and kw.lower() in hl:
                    score += 5
                    reasons.append(f"提示命中「{kw}」")
                    break
        data_inputs = [k for k, v in e["inputs"].items() if v.get("kind") == "data"]
        const_inputs = [k for k, v in e["inputs"].items() if v.get("kind") != "data"]
        if data_cols > 0 and len(data_inputs) == data_cols:
            score += 3
            reasons.append(f"数据列数 {data_cols} 与数据型输入 {data_inputs} 一致")
        elif data_cols > 0 and len(data_inputs) > 0:
            score += 1
        candidates.append({
            "id": e["id"], "name": e["name"], "tool": e["tool"],
            "score": score, "reasons": reasons,
            "data_inputs": data_inputs, "constant_inputs": const_inputs,
        })
    candidates.sort(key=lambda c: (-c["score"], c["id"]))
    return candidates
