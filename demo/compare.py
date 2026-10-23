"""对比演示：裸 LLM vs 受约束 Agent（配置驱动）。

用法：
  python demo/compare.py                # 默认：伏安法测电阻
  python demo/compare.py 弹簧振子        # 弹簧振子
"""
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phyxexp.agent import Conductor
from phyxexp.config import load_config, find_experiment
from phyxexp import viz
from bare_llm import bare_llm_answer

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

DEMO = {
    "ohms_law": {"I": [0.10, 0.20, 0.30, 0.40, 0.50, 0.60],
                 "V": [1.00, 1.97, 2.95, 3.94, 4.93, 5.92]},
    "spring_constant": {"m": [0.10, 0.20, 0.30, 0.40, 0.50, 0.60],
                        "T": [0.636, 0.898, 1.100, 1.270, 1.420, 1.556]},
}


def pick(task):
    t = task.lower()
    if "电阻" in t or "伏安" in t or "欧姆" in t:
        return "ohms_law"
    if "弹簧" in t or "劲度" in t or "振子" in t:
        return "spring_constant"
    return None


def main():
    task = sys.argv[1] if len(sys.argv) > 1 else "伏安法测电阻"
    exp_id = pick(task)
    if exp_id is None:
        print("未知任务，仅支持：伏安法测电阻 / 弹簧振子")
        return

    config = load_config()
    exp = find_experiment(config, exp_id)
    data = DEMO[exp_id]

    print("=" * 66)
    print("任务（同一句话喂给两边）：", task)
    print("=" * 66)

    bare = bare_llm_answer(task)
    print()
    print("[裸 LLM] " + bare["kind"])
    print("  回答  :", bare["answer"])
    print("  不确定度:", bare["claimed_uncertainty"], "  <- 拍脑袋")
    print("  R² / 残差图:", bare["r2"], "/", bare["residual_plot"])
    print("  可复现 :", bare["reproducible"], "  <- 问题:", bare["problem"])

    print()
    print("[受约束 Agent]（配置驱动：config/experiments.json →", exp_id, "）")
    res = Conductor(config).solve_experiment(exp, data)
    rec = res.record
    print("  工具 :", rec.tool, "| run_id:", rec.run_id, "| 输入哈希:", rec.input_hash)
    print("  一致性检查:", res.checks)
    print("  结论 :", res.conclusion)
    print("  grounding 校验:", "通过" if res.grounded else "失败")
    print("  重放结果一致(可复现):", "是" if res.replay_match else "否")

    os.makedirs(OUT, exist_ok=True)
    plots = []
    o = rec.outputs
    if exp_id == "ohms_law":
        plots.append(viz.save_fit_plot(data["I"], data["V"], o["R"], o["b"],
                                       os.path.join(OUT, "伏安法-拟合.png"),
                                       xlabel="I (A)", ylabel="V (V)", title="伏安法测电阻：V = R·I + b"))
        plots.append(viz.save_residual_plot(data["I"], o["residuals"],
                                            os.path.join(OUT, "伏安法-残差.png"),
                                            xlabel="I (A)", title="残差图：随机分布、无趋势"))
    else:
        T2 = [t ** 2 for t in data["T"]]
        plots.append(viz.save_fit_plot(data["m"], T2, o["slope_A"], o["intercept_b"],
                                       os.path.join(OUT, "弹簧振子-拟合.png"),
                                       xlabel="m (kg)", ylabel="T² (s²)", title="弹簧振子：T² = (4π²/k)·m"))
        plots.append(viz.save_residual_plot(data["m"], o["residuals"],
                                            os.path.join(OUT, "弹簧振子-残差.png"),
                                            xlabel="m (kg)", title="残差图：随机分布、无趋势"))
    print()
    print("  已生成图：")
    for p in plots:
        print("   -", p)
    print()
    print("=" * 66)
    print("一句话：裸 LLM 只有点估计；受约束 Agent 给 值±不确定度 + R² + 残差图 + 可复现哈希。")
    print("=" * 66)


if __name__ == "__main__":
    main()
