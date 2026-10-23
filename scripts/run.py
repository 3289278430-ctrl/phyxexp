#!/usr/bin/env python3
"""phyxexp Skill 运行时入口 —— 宿主大模型唯一被允许调用的计算入口。

大模型只做「选实验 + 传数据」，数值一律由受约束工具链产出并带溯源。
用法见 SKILL.md。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phyxexp.agent import Conductor
from phyxexp.config import load_config, find_experiment


def main(argv=None):
    ap = argparse.ArgumentParser(description="phyxexp 受约束实验数据处理")
    ap.add_argument("--experiment", "-e", help="实验 id（见 --list）")
    ap.add_argument("--data", help="输入数据 JSON（字段名见 --list 各实验的 inputs）")
    ap.add_argument("--data-file", help="输入数据 JSON 文件路径")
    ap.add_argument("--list", action="store_true", help="列出可用实验")
    args = ap.parse_args(argv)

    config = load_config()

    if args.list:
        print(json.dumps({
            "standard": config["defaults"]["uncertainty_standard"],
            "experiments": [
                {"id": e["id"], "name": e["name"], "tool": e["tool"],
                 "inputs": e["inputs"], "checks": e.get("checks", [])}
                for e in config["experiments"]
            ],
        }, ensure_ascii=False, indent=2))
        return 0

    if not args.experiment:
        ap.error("需要 --experiment（或 --list 查看可用实验）")

    exp = find_experiment(config, args.experiment)

    if args.data_file:
        with open(args.data_file, encoding="utf-8") as f:
            data = json.load(f)
    elif args.data:
        data = json.loads(args.data)
    else:
        ap.error("需要 --data 或 --data-file 提供输入数据")

    res = Conductor(config).solve_experiment(exp, data)
    out = {
        "experiment": {"id": exp["id"], "name": exp["name"], "tool": exp["tool"]},
        "run_id": res.record.run_id,
        "input_hash": res.record.input_hash,
        "standard": config["defaults"]["uncertainty_standard"],
        "checks": res.checks,
        "conclusion": res.conclusion,
        "metrics": {k: v for k, v in res.metrics.items() if not isinstance(v, (list, dict))},
        "grounded": res.grounded,
        "replay_match": res.replay_match,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
