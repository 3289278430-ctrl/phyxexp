"""绘图工具（受约束、可复现）：残差图、拟合图（可选误差棒）。"""
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


FOOTER = "由 phyxexp 生成 · 不确定度依据 JJF 1059.1-2012"


def _footer(fig):
    fig.text(0.5, 0.015, FOOTER, ha="center", va="bottom", fontsize=9, color="#888888")


def save_residual_plot(x, residuals, path, xlabel="x", ylabel="残差", title="残差图"):
    plt = _plt()
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.axhline(0, color="#888", lw=1)
    ax.scatter(x, residuals, color="#e45756", zorder=3, s=36)
    ax.vlines(x, 0, residuals, color="#e45756", alpha=0.45, lw=1.2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    _footer(fig)
    fig.subplots_adjust(bottom=0.18)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def save_fit_plot(x, y, k, b, path, xlabel="x", ylabel="y", title="线性拟合", yerr=None, r2=None):
    import numpy as np
    plt = _plt()
    fig, ax = plt.subplots(figsize=(6, 4.2))
    if yerr is not None:
        ax.errorbar(x, y, yerr=yerr, fmt="o", color="#1F3864", capsize=3, zorder=3, label="测量点")
    else:
        ax.scatter(x, y, color="#1F3864", zorder=3, s=36, label="测量点")
    xf = np.linspace(min(x), max(x), 50)
    ax.plot(xf, k * xf + b, "-", color="#f58518", lw=2, label="拟合 y = %.4fx + %.4f" % (k, b))
    if r2 is not None:
        ax.text(0.03, 0.03, "R² = %.5f" % r2, transform=ax.transAxes,
                fontsize=11, color="#1F3864",
                bbox=dict(boxstyle="round,pad=0.3", fc="#EDF1F7", ec="#c9d4e4", alpha=0.9))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend()
    _footer(fig)
    fig.subplots_adjust(bottom=0.18)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
