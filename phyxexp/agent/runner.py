"""执行器 —— 把一次工具调用变成可复现、可溯源的 Record。"""
import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict

from .guard import assert_allowed
from .registry import TOOL_REGISTRY


def _canonical(params: Dict[str, Any]) -> str:
    return json.dumps(params, sort_keys=True, ensure_ascii=False, default=str)


def _input_hash(params: Dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(params).encode("utf-8")).hexdigest()[:16]


@dataclass
class Record:
    run_id: str
    tool: str
    params: Dict[str, Any]
    outputs: Dict[str, Any]
    input_hash: str
    timestamp: str
    recipe: Dict[str, Any]


def run_tool(name: str, params: Dict[str, Any]) -> Record:
    assert_allowed(name)
    tool = TOOL_REGISTRY[name]
    outputs = tool.fn(**params)
    record = Record(
        run_id=uuid.uuid4().hex[:12],
        tool=name,
        params=params,
        outputs=outputs,
        input_hash=_input_hash(params),
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        recipe={"tool": name, "params": params},
    )
    return record


def replay(record: Record) -> Dict[str, Any]:
    """用 recipe 重放一次，验证可复现性。"""
    tool = TOOL_REGISTRY[record.tool]
    return tool.fn(**record.recipe["params"])
