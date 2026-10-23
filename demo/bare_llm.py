"""模拟"免费 LLM"做数据分析的典型失败模式（用于对比演示）。

真实免费 AI（无约束）会：直接给 15 位小数、误差拍脑袋、无 R²/残差/误差预算、不可复现。
这里用确定性脚本复现这些典型失败，便于录屏对比。注意：这是「模拟」，不是真调用大模型。
"""


def bare_llm_answer(task: str):
    t = task.lower()
    if "电阻" in t or "伏安" in t or "欧姆" in t:
        return {
            "kind": "免费 AI（直接回答）",
            "answer": "R = 9.848571428571425 Ω（15 位小数）",
            "claimed_uncertainty": "约 ±0.5 Ω（拍脑袋，无传播）",
            "r2": None,
            "residual_plot": None,
            "reproducible": False,
            "problem": "有效数字错（15位小数）；不确定度拍脑袋；无 R²/残差图/误差预算；不可复现。",
        }
    if "弹簧" in t or "劲度" in t or "振子" in t:
        return {
            "kind": "免费 AI（直接回答）",
            "answer": "k = 9.788438667657145 N/m（15 位小数）",
            "claimed_uncertainty": "约 ±0.3 N/m（拍脑袋）",
            "r2": None,
            "residual_plot": None,
            "reproducible": False,
            "problem": "有效数字错；不确定度拍脑袋；无 R²/残差图/误差预算；不可复现。",
        }
    return {
        "kind": "免费 AI（直接回答）",
        "answer": "（给出一个看似合理但无依据的数）",
        "claimed_uncertainty": None,
        "r2": None,
        "residual_plot": None,
        "reproducible": False,
        "problem": "无依据、不可复现。",
    }
