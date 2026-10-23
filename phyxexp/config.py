"""配置加载：实验声明（config/experiments.json）是 Skill 的可配置来源。"""
import json
import os

_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "experiments.json")


def load_config(path: str | None = None) -> dict:
    p = path or os.environ.get("PHYXEXP_CONFIG") or _DEFAULT
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def find_experiment(config: dict, experiment_id: str) -> dict:
    for e in config.get("experiments", []):
        if e["id"] == experiment_id:
            return e
    raise KeyError(f"未找到实验 {experiment_id!r}，可用实验见 --list")
