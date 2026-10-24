"""领域物理模型（审查过、带量纲与误差预算）。

每个模型返回 {目标量, u_目标量, share(误差贡献占比), share_labels(中文标签)}。
不确定度一律用一阶偏导传播（中心差分），可复现、无 CAS 依赖。
"""
import math

import numpy as np

from .fit import linear_fit
from .uncertainty import propagate, type_a, type_b, combine

E_CHARGE = 1.602176634e-19  # 元电荷 C
G_STD = 9.794               # 本地重力加速度 m/s²（演示默认）


# ---------- 电学 ----------
def ohms_law_resistance(I, V):
    """伏安法测电阻：V = R·I + b，斜率即电阻，截距应近零。"""
    I = np.asarray(I, dtype=float)
    V = np.asarray(V, dtype=float)
    fit = linear_fit(I, V)
    v_span = float(np.ptp(V)) if len(V) else 1.0
    intercept_ratio = abs(fit["b"]) / v_span if v_span else float("inf")
    return {
        "R": fit["k"], "u_R": fit["u_k"], "b": fit["b"], "u_b": fit["u_b"],
        "r": fit["r"], "r2": fit["r2"], "n": fit["n"],
        "residuals": fit["residuals"],
        "intercept_ratio": intercept_ratio,
        "intercept_ok": bool(intercept_ratio < 0.02),
    }


def wheatstone_bridge(R0, l1, l2, u_R0, u_l1, u_l2):
    """惠斯通电桥测电阻：Rx = R0·l1/l2。"""
    def fn(R0=R0, l1=l1, l2=l2):
        return R0 * l1 / l2
    Rx, u_Rx, share = propagate(fn, {"R0": R0, "l1": l1, "l2": l2},
                                 {"R0": u_R0, "l1": u_l1, "l2": u_l2})
    return {"Rx": Rx, "u_Rx": u_Rx, "share": share,
            "share_labels": {"R0": "标准电阻 R0", "l1": "桥臂 l1", "l2": "桥臂 l2"}}


def hall_carrier_density(I, B, d, UH, u_I, u_B, u_d, u_UH):
    """霍尔效应载流子浓度：n = I·B/(e·d·UH)。"""
    def fn(I=I, B=B, d=d, UH=UH):
        return I * B / (E_CHARGE * d * UH)
    n, u_n, share = propagate(fn, {"I": I, "B": B, "d": d, "UH": UH},
                               {"I": u_I, "B": u_B, "d": u_d, "UH": u_UH})
    return {"n": n, "u_n": u_n, "share": share,
            "share_labels": {"I": "电流 I", "B": "磁感应强度 B", "d": "样品厚度 d", "UH": "霍尔电压 UH"}}


# ---------- 力学 ----------
def spring_constant(m, T):
    """弹簧振子：T² = (4π²/k)·m，斜率 A=4π²/k。"""
    m = np.asarray(m, dtype=float)
    T = np.asarray(T, dtype=float)
    T2 = T ** 2
    fit = linear_fit(m, T2)
    A, u_A = fit["k"], fit["u_k"]
    if A == 0:
        raise ValueError("斜率 A 为 0")
    k = 4.0 * math.pi ** 2 / A
    u_k = abs(k) * (u_A / abs(A))
    intercept_ratio = abs(fit["b"]) / float(np.ptp(T2)) if len(T2) else float("inf")
    return {
        "k": k, "u_k": u_k, "slope_A": A, "u_slope_A": u_A,
        "intercept_b": fit["b"], "u_intercept_b": fit["u_b"],
        "r": fit["r"], "r2": fit["r2"], "n": fit["n"],
        "residuals": fit["residuals"],
        "intercept_ratio": intercept_ratio,
        "intercept_ok": bool(intercept_ratio < 0.05),
    }


def simple_pendulum(L, T, u_L, u_T):
    """单摆测重力加速度：g = 4π²L/T²。"""
    def fn(L=L, T=T):
        return 4.0 * math.pi ** 2 * L / T ** 2
    g, u_g, share = propagate(fn, {"L": L, "T": T}, {"L": u_L, "T": u_T})
    return {"g": g, "u_g": u_g, "share": share,
            "share_labels": {"L": "摆长 L", "T": "周期 T"}}


def falling_ball_viscosity(rho_ball, rho_liquid, d, L, t, u_rho_ball, u_rho_liquid, u_d, u_L, u_t, g=G_STD):
    """落球法黏滞系数：η = (ρ-ρ0)·g·d²·t/(18L)（演示用，未加壁面修正）。"""
    def fn(rho_ball=rho_ball, rho_liquid=rho_liquid, d=d, L=L, t=t):
        return (rho_ball - rho_liquid) * g * d ** 2 * t / (18.0 * L)
    eta, u_eta, share = propagate(fn,
        {"rho_ball": rho_ball, "rho_liquid": rho_liquid, "d": d, "L": L, "t": t},
        {"rho_ball": u_rho_ball, "rho_liquid": u_rho_liquid, "d": u_d, "L": u_L, "t": u_t})
    return {"eta": eta, "u_eta": u_eta, "share": share,
            "share_labels": {"rho_ball": "钢球密度 ρ", "rho_liquid": "液体密度 ρ0",
                             "d": "球直径 d", "L": "下落距离 L", "t": "时间 t"}}


# ---------- 光学 ----------
def newton_rings(Dm, Dn, m, n, wavelength, u_Dm, u_Dn, u_wavelength):
    """牛顿环曲率半径：R = (Dm²-Dn²)/(4(m-n)λ)，D 为环直径。"""
    def fn(Dm=Dm, Dn=Dn, wavelength=wavelength):
        return (Dm ** 2 - Dn ** 2) / (4.0 * (m - n) * wavelength)
    R, u_R, share = propagate(fn, {"Dm": Dm, "Dn": Dn, "wavelength": wavelength},
                               {"Dm": u_Dm, "Dn": u_Dn, "wavelength": u_wavelength})
    return {"R": R, "u_R": u_R, "share": share,
            "share_labels": {"Dm": "第m环直径 Dm", "Dn": "第n环直径 Dn", "wavelength": "波长 λ"}}


def grating_wavelength(d, theta, k, u_d, u_theta):
    """光栅衍射测波长：λ = d·sinθ/k（θ 用弧度）。"""
    def fn(d=d, theta=theta):
        return d * math.sin(theta) / k
    lam, u_lam, share = propagate(fn, {"d": d, "theta": theta}, {"d": u_d, "theta": u_theta})
    return {"wavelength": lam, "u_wavelength": u_lam, "share": share,
            "share_labels": {"d": "光栅常数 d", "theta": "衍射角 θ"}}


# ---------- 热学 ----------
def linear_expansion(L0, delta_L, delta_t, u_L0, u_delta_L, u_delta_t):
    """金属线膨胀系数：α = ΔL/(L0·Δt)。"""
    def fn(L0=L0, delta_L=delta_L, delta_t=delta_t):
        return delta_L / (L0 * delta_t)
    a, u_a, share = propagate(fn, {"L0": L0, "delta_L": delta_L, "delta_t": delta_t},
                               {"L0": u_L0, "delta_L": u_delta_L, "delta_t": u_delta_t})
    return {"alpha": a, "u_alpha": u_a, "share": share,
            "share_labels": {"L0": "原长 L0", "delta_L": "伸长量 ΔL", "delta_t": "温差 Δt"}}


# ---------- 杨氏模量 ----------
def youngs_modulus(m, g, L0, D, b, d, dn, u_m, u_g, u_L0, u_D, u_b, u_d, u_dn):
    """杨氏模量（光杠杆法）：E = 8mgL0D/(πd²b·dn)。"""
    def fn(m=m, g=g, L0=L0, D=D, b=b, d=d, dn=dn):
        return 8.0 * m * g * L0 * D / (math.pi * d * d * b * dn)
    values = {"m": m, "g": g, "L0": L0, "D": D, "b": b, "d": d, "dn": dn}
    uncertainties = {"m": u_m, "g": u_g, "L0": u_L0, "D": u_D, "b": u_b, "d": u_d, "dn": u_dn}
    E, u_E, share = propagate(fn, values, uncertainties)
    return {"E": E, "u_E": u_E, "share": share,
            "share_labels": {"m": "砝码质量 m", "g": "重力加速度 g", "L0": "钢丝原长 L0",
                             "D": "望远镜到标尺 D", "b": "光杠杆前后脚 b", "d": "钢丝直径 d", "dn": "标尺读数差 dn"}}


def diameter_uncertainty(values_mm, instrument_error_mm=0.004):
    """直径多次读数：A 类（随机）+ B 类（千分尺仪器误差）合成。"""
    vals = [v / 1000.0 for v in values_mm]
    dm, s, uA = type_a(vals)
    uB = type_b(instrument_error_mm / 1000.0)
    ud = combine(uA, uB)
    return {"d_mean": dm, "s": s, "u_A": uA, "u_B": uB, "u_d": ud}
