"""结果规范表示（大学物理实验约定）。

不确定度保留 1~2 位有效数字（首位为 1/2 时保留 2 位），测量值末位与不确定度对齐；
默认给出扩展不确定度（k=2）。这是相对免费 AI 的可见优势：不再输出 15 位小数。
"""
import math


def _sig_round(x, sig):
    if x == 0:
        return 0.0
    d = sig - 1 - int(math.floor(math.log10(abs(x))))
    return round(x, -d) if d <= 0 else round(x, d)


def _u_sigfigs(u):
    """不确定度保留位数：首位 1 或 2 保留 2 位，否则保留 1 位。"""
    mant = abs(u) / 10 ** math.floor(math.log10(abs(u)))
    return 2 if mant < 3 else 1


def format_quantity(value, u, expansion_k=2):
    """返回 '9.85 ± 0.04' 或 '(2.00 ± 0.25)×10^11'（扩展不确定度，末位对齐）。"""
    u = abs(u) * expansion_k
    v = float(value)
    if u == 0:
        return f"{v:.6g}"
    sig = _u_sigfigs(u)
    u_round = _sig_round(u, sig)
    e = int(math.floor(math.log10(u_round))) - (sig - 1)   # 末位所在十进制位
    v_round = round(v, -e)
    u_round = round(u_round, -e)
    if abs(v_round) >= 1e6 or (abs(v_round) < 1e-3 and v_round != 0):
        exp = int(math.floor(math.log10(abs(v_round))))
        bv = v_round / 10 ** exp
        bu = u_round / 10 ** exp
        nd = max(0, exp - e)
        return f"({bv:.{nd}f} ± {bu:.{nd}f})×10^{exp}"
    nd = max(0, -e)
    return f"{v_round:.{nd}f} ± {u_round:.{nd}f}"
