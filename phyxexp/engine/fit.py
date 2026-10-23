"""通用线性拟合：最小二乘 y = k x + b，含斜率/截距不确定度与残差。

采用经典解析公式（JJF 1059.1 附录中的直线拟合不确定度），不依赖 scipy，可复现。
"""
import math

import numpy as np


def linear_fit(x, y):
    """最小二乘直线拟合。

    返回 dict：k, u_k, b, u_b, r, r2, n, residual_std, residuals, y_pred, x, y。
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("x、y 必须是一维序列")
    if len(x) != len(y):
        raise ValueError("x、y 长度必须一致")
    if len(x) < 3:
        raise ValueError("至少需要 3 组数据")

    n = len(x)
    k, b = float(np.polyfit(x, y, 1)[0]), float(np.polyfit(x, y, 1)[1])
    y_pred = k * x + b
    residuals = y - y_pred
    s = math.sqrt(float(np.sum(residuals ** 2)) / (n - 2))  # 残差标准差（无偏）
    sxx = float(np.sum((x - x.mean()) ** 2))
    u_k = s / math.sqrt(sxx)
    u_b = s * math.sqrt(1.0 / n + x.mean() ** 2 / sxx)
    r = float(np.corrcoef(x, y)[0, 1])
    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else float("nan")

    return {
        "k": k, "u_k": u_k, "b": b, "u_b": u_b,
        "r": r, "r2": r2, "n": n, "residual_std": s,
        "residuals": residuals.tolist(),
        "y_pred": y_pred.tolist(),
        "x": x.tolist(), "y": y.tolist(),
    }
