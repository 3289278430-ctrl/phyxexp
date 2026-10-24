#!/usr/bin/env python3
"""phyxexp Skill 运行时入口 —— 宿主大模型唯一被允许调用的计算入口。

支持：
  --list                  列出可用实验（含各输入的标签与单位）
  -e <id> --data <json>   指定实验执行
  --identify --data <json> [--hint 提示]   识别数据对应实验（不执行）
  --auto --data <json> [--hint 提示]       自动识别实验并执行
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phyxexp.agent import Conductor
from phyxexp.config import load_config, find_experiment
from phyxexp.identify import identify_experiment


def _load_data(args):
    if args.data_file:
        with open(args.data_file, encoding="utf-8") as f:
            return json.load(f)
    if args.data:
        return json.loads(args.data)
    return None


def _solve(config, exp, data):
    c = Conductor(config)
    if "pipeline" in exp:
        return c.solve_pipeline(exp, data)
    return c.solve_experiment(exp, data)


def main(argv=None):
    ap = argparse.ArgumentParser(description="phyxexp 受约束实验数据处理")
    ap.add_argument("--experiment", "-e", help="实验 id（见 --list）")
    ap.add_argument("--data", help="输入数据 JSON")
    ap.add_argument("--data-file", help="输入数据 JSON 文件路径")
    ap.add_argument("--hint", help="提示词（如「杨氏模量」），用于自动识别实验")
    ap.add_argument("--list", action="store_true", help="列出可用实验")
    ap.add_argument("--identify", action="store_true", help="识别数据对应的实验（不执行）")
    ap.add_argument("--auto", action="store_true", help="自动识别实验并执行")
    ap.add_argument("--ingest", help="从文档/图片识别数据表（配合 --hint）")
    args = ap.parse_args(argv)

    config = load_config()

    if args.list:
        print(json.dumps({
            "standard": config["defaults"]["uncertainty_standard"],
            "experiments": [
                {"id": e["id"], "name": e["name"], "tool": e["tool"],
                 "inputs": e["inputs"], "checks": e.get("checks", []),
                 "keywords": e.get("keywords", [])}
                for e in config["experiments"]
            ],
        }, ensure_ascii=False, indent=2))
        return 0

    data = _load_data(args)

    if args.identify:
        cands = identify_experiment(config, data, args.hint)
        print(json.dumps({
            "hint": args.hint,
            "data_columns": (len(data) if isinstance(data, dict) else None),
            "candidates": cands[:6],
        }, ensure_ascii=False, indent=2))
        return 0

    if args.auto:
        if data is None:
            ap.error("--auto 需要 --data 或 --data-file")
        cands = identify_experiment(config, data, args.hint)
        best = cands[0] if cands else None
        if not best or best["score"] <= 0:
            print(json.dumps({"error": "无法识别实验，请用 --hint 补充提示", "candidates": cands},
                             ensure_ascii=False, indent=2))
            return 1
        cols = [k for k, v in data.items() if isinstance(v, (list, tuple))]
        if best["data_inputs"] and len(best["data_inputs"]) == len(cols):
            params = dict(zip(best["data_inputs"], [data[c] for c in cols]))
            exp = find_experiment(config, best["id"])
            res = _solve(config, exp, params)
            print(json.dumps({
                "identified": {"id": best["id"], "name": best["name"], "score": best["score"],
                               "reasons": best["reasons"]},
                "mapping": params,
                "conclusion": res.conclusion,
                "run_id": res.record.run_id, "input_hash": res.record.input_hash,
                "checks": res.checks, "grounded": res.grounded, "replay_match": res.replay_match,
            }, ensure_ascii=False, indent=2, default=str))
            return 0
        # 识别到了实验，但数据是它的中间步骤（如线性拟合），而不是直接常量输入
        print(json.dumps({
            "identified": {"id": best["id"], "name": best["name"], "reasons": best["reasons"]},
            "note": "识别到该实验，但你的数据列不是它的直接输入（该实验需要单次测量常量）",
            "required_constants": best["constant_inputs"],
            "suggestion": "若数据是两列（如拉力-读数），可先跑线性拟合：--auto --data '<json>' --hint '线性拟合' 得斜率；再补常量后调用 -e " + best["id"],
        }, ensure_ascii=False, indent=2))
        return 0

    if args.ingest:
        from phyxexp.ingest import ingest, numeric_columns
        res = ingest(args.ingest)
        cands = identify_experiment(config, None, args.hint)
        out = {
            "source": args.ingest,
            "source_type": res["source_type"],
            "identified": [{"id": c["id"], "name": c["name"], "score": c["score"]} for c in cands[:4]],
            "tables": [],
        }
        for t in res["tables"]:
            grid = t["rows"]
            out["tables"].append({
                "sheet": t["sheet"],
                "numeric_columns": numeric_columns(grid),
                "rows_preview": grid[:40],
            })
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return 0

    if not args.experiment:
        ap.error("需要 --experiment / --identify / --auto / --list")

    exp = find_experiment(config, args.experiment)
    if data is None:
        ap.error("需要 --data 或 --data-file")
    res = _solve(config, exp, data)
    print(json.dumps({
        "experiment": {"id": exp["id"], "name": exp["name"], "tool": exp["tool"]},
        "run_id": res.record.run_id, "input_hash": res.record.input_hash,
        "standard": config["defaults"]["uncertainty_standard"],
        "checks": res.checks, "conclusion": res.conclusion,
        "metrics": {k: v for k, v in res.metrics.items() if not isinstance(v, (list, dict))},
        "grounded": res.grounded, "replay_match": res.replay_match,
    }, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
