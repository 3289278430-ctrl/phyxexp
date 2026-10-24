# -*- coding: utf-8 -*-
"""一键运行 examples/ 下的全部示例，打印结论与溯源状态。"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable

CASES = [
    ("ohms_law", "ohms_law.json"),
    ("spring_constant", "spring_oscillator.json"),
    ("youngs_modulus_raw", "youngs_modulus_raw.json"),
]

def main():
    ok = 0
    for exp, fn in CASES:
        print("=" * 60)
        print("示例:", exp, "->", fn)
        r = subprocess.run(
            [PY, os.path.join(ROOT, "scripts", "run.py"), "-e", exp,
             "--data-file", os.path.join(HERE, fn)],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        if r.returncode != 0:
            print("  失败:", (r.stderr or "")[-400:])
            continue
        out = json.loads(r.stdout)
        print("  结论:", out.get("conclusion"))
        print("  检查:", out.get("checks"), "| grounded:", out.get("grounded"),
              "| replay:", out.get("replay_match"))
        ok += 1
    print("=" * 60)
    print("完成:", ok, "/", len(CASES))
    return 0 if ok == len(CASES) else 1

if __name__ == "__main__":
    raise SystemExit(main())
