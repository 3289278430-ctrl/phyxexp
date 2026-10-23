"""不确定度评定（JJF 1059.1-2012）。

A 类：以贝塞尔公式 s = sqrt(sum (x-xbar)^2 / (n-1))，u_A = s/sqrt(n)。
B 类：均匀分布取允许误差除以 sqrt(3)。
合成：各不确定度分量的方和根。
传播：中心差分数值偏导的一阶传播 u_c^2 = sum (df/dx_i * u_i)^2。
"""
import math

C = math.sqrt(3.0)  # 均匀分布除数


def mean(v):
    return sum(v) / len(v)


def sample_std(v):
    n = len(v)
    if n < 2:
        return 0.0
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))


def type_a(v):
    """返回 (均值, 样本标准差 s, A 类标准不确定度 u_A)。"""
    m = mean(v)
    s = sample_std(v)
    return m, s, s / math.sqrt(len(v))


def type_b(allowance, divisor=C):
    """B 类标准不确定度：|allowance| / divisor（默认均匀分布 sqrt(3)）。"""
    return abs(allowance) / divisor


def combine(*u):
    """方和根合成不确定度。"""
    return math.sqrt(sum(x * x for x in u))


def propagate(fn, values, uncertainties, rel_step=1e-6):
    """一阶不确定度传播（中心差分数值偏导，可复现、无外部 CAS 依赖）。

    fn(**values) -> float
    values: {name: value}
    uncertainties: {name: 1-sigma 标准不确定度}
    返回 (value, u_combined, share)，share 为 {name: 方差贡献占比}。
    """
    val = float(fn(**values))
    terms = {}
    for k, x in values.items():
        h = abs(x) * rel_step
        if h == 0.0:
            h = rel_step
        up = dict(values)
        up[k] = x + h
        dn = dict(values)
        dn[k] = x - h
        fp = float(fn(**up))
        fm = float(fn(**dn))
        dfdx = (fp - fm) / (2.0 * h)
        terms[k] = (dfdx * uncertainties[k]) ** 2
    uc = math.sqrt(sum(terms.values()))
    share = {k: (v / (uc * uc) if uc else 0.0) for k, v in terms.items()}
    return val, uc, share
