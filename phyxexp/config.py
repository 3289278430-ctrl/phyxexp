"""配置加载：实验声明是 Skill 的可配置来源。

查找顺序：PHYXEXP_CONFIG 环境变量 → 源码树 config/ → 包内 data/（pip 安装时）。
"""
import json
import os


def _candidates():
    yield os.environ.get("PHYXEXP_CONFIG")
    here = os.path.dirname(os.path.abspath(__file__))
    yield os.path.join(here, "..", "config", "experiments.json")   # 源码树
    yield os.path.join(here, "data", "experiments.json")           # 打包副本


def load_config(path: str | None = None) -> dict:
    if path:
        p = path
    else:
        p = next((c for c in _candidates() if c and os.path.exists(c)), None)
        if p is None:
            raise FileNotFoundError("找不到 experiments.json：设置 PHYXEXP_CONFIG，或确认 config/ 存在")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def find_experiment(config: dict, experiment_id: str) -> dict:
    for e in config.get("experiments", []):
        if e["id"] == experiment_id:
            return e
    raise KeyError(f"未找到实验 {experiment_id!r}，可用实验见 --list")
