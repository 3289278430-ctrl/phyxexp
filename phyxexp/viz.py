"""绘图工具（受约束、可复现）：残差图、拟合图（可选误差棒）。

matplotlib 使用 Agg 后端，仅生成 PNG，不弹窗；字体用 Windows 中文字体。
"""
import os


def _plt():
    import os
    import tempfile
    os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "phyxexp-mpl"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "WenQuanYi Zen Hei"]
    plt.rcParams["axes.unicode_minus"] = False
    return plt


def save_residual_plot(x, residuals, path, xlabel="x", ylabel="残差", title="残差图"):
    """残差图：散点 + 零线。返回输出路径。"""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.axhline(0, color="#888", lw=1)
    ax.scatter(x, residuals, color="#e45756", zorder=3, s=36)
    ax.vlines(x, 0, residuals, color="#e45756", alpha=0.45, lw=1.2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def save_fit_plot(x, y, k, b, path, xlabel="x", ylabel="y", title="线性拟合", yerr=None):
    """拟合图：测量点（可选误差棒）+ 拟合直线。返回输出路径。"""
    import numpy as np
    plt = _plt()
    fig, ax = plt.subplots(figsize=(6, 4))
    if yerr is not None:
        ax.errorbar(x, y, yerr=yerr, fmt="o", color="#4c78a8", capsize=3, zorder=3, label="测量点")
    else:
        ax.scatter(x, y, color="#4c78a8", zorder=3, s=36, label="测量点")
    xf = np.linspace(min(x), max(x), 50)
    ax.plot(xf, k * xf + b, "-", color="#f58518", lw=2, label=f"y = {k:.4f}x + {b:.4f}")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
