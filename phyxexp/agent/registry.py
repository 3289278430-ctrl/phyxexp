"""工具注册表 —— 受约束 Agent 唯一可用的领域工具链。"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from ..engine import models as _m
from ..engine.uncertainty import type_a as _type_a, type_b as _type_b, combine as _combine
from ..engine.fit import linear_fit as _linear_fit


@dataclass
class Tool:
    name: str
    description: str
    schema: Dict[str, Any]
    fn: Callable[..., Any]
    postconditions: List[str] = field(default_factory=list)
    cite: str = ""


TOOL_REGISTRY: Dict[str, Tool] = {}


def register(tool: Tool) -> Tool:
    TOOL_REGISTRY[tool.name] = tool
    return tool


register(Tool("type_a", "A 类标准不确定度：均值、样本标准差 s、u_A=s/√n。",
              {"values": "list[float]"}, _type_a, [], "JJF 1059.1-2012"))
register(Tool("type_b", "B 类标准不确定度：允许误差除以 √3（均匀分布）。",
              {"allowance": "float"}, _type_b, [], "JJF 1059.1-2012"))
register(Tool("combine", "方和根合成不确定度。",
              {"components": "list[float]"}, _combine, [], "JJF 1059.1-2012"))
register(Tool("linear_fit", "通用最小二乘直线拟合（k、u_k、b、u_b、r、R²、残差）。",
              {"x": "list[float]", "y": "list[float]"}, _linear_fit, ["r2 >= 0", "n >= 3"], "最小二乘 + JJF 1059.1"))

# 电学
register(Tool("ohms_law_resistance", "伏安法测电阻：V=R·I+b，斜率即电阻，截距应近零。",
              {"I": "list[float]", "V": "list[float]"}, _m.ohms_law_resistance, ["R > 0", "intercept_ok"], "欧姆定律 V=R·I"))
register(Tool("wheatstone_bridge", "惠斯通电桥测电阻：Rx=R0·l1/l2。",
              {"R0": "float", "l1": "float", "l2": "float", "u_R0": "float", "u_l1": "float", "u_l2": "float"},
              _m.wheatstone_bridge, ["Rx > 0"], "惠斯通电桥平衡条件"))
register(Tool("hall_carrier_density", "霍尔效应载流子浓度：n=I·B/(e·d·UH)。",
              {"I": "float", "B": "float", "d": "float", "UH": "float",
               "u_I": "float", "u_B": "float", "u_d": "float", "u_UH": "float"},
              _m.hall_carrier_density, ["n > 0"], "霍尔效应"))

# 力学
register(Tool("diameter_uncertainty", "直径多次读数：A类+仪器B类合成不确定度。",
              {"values_mm": "list[float]", "instrument_error_mm": "float"},
              _m.diameter_uncertainty, ["d_mean > 0"], "JJF 1059.1-2012"))
register(Tool("spring_constant", "弹簧振子：T²=(4π²/k)·m，斜率 A=4π²/k。",
              {"m": "list[float]", "T": "list[float]"}, _m.spring_constant, ["k > 0", "intercept_ok"], "T=2π√(m/k)"))
register(Tool("simple_pendulum", "单摆测重力加速度：g=4π²L/T²。",
              {"L": "float", "T": "float", "u_L": "float", "u_T": "float"},
              _m.simple_pendulum, ["g > 0"], "单摆周期公式"))
register(Tool("falling_ball_viscosity", "落球法黏滞系数：η=(ρ-ρ0)g·d²·t/(18L)。",
              {"rho_ball": "float", "rho_liquid": "float", "d": "float", "L": "float", "t": "float",
               "u_rho_ball": "float", "u_rho_liquid": "float", "u_d": "float", "u_L": "float", "u_t": "float"},
              _m.falling_ball_viscosity, ["eta > 0"], "斯托克斯定律（演示，无壁修正）"))

# 光学
register(Tool("newton_rings", "牛顿环曲率半径：R=(Dm²-Dn²)/(4(m-n)λ)。",
              {"Dm": "float", "Dn": "float", "m": "float", "n": "float", "wavelength": "float",
               "u_Dm": "float", "u_Dn": "float", "u_wavelength": "float"},
              _m.newton_rings, ["R > 0"], "牛顿环干涉"))
register(Tool("grating_wavelength", "光栅衍射测波长：λ=d·sinθ/k（θ 用弧度）。",
              {"d": "float", "theta": "float", "k": "float", "u_d": "float", "u_theta": "float"},
              _m.grating_wavelength, ["wavelength > 0"], "光栅方程 d·sinθ=kλ"))

# 热学
register(Tool("linear_expansion", "金属线膨胀系数：α=ΔL/(L0·Δt)。",
              {"L0": "float", "delta_L": "float", "delta_t": "float",
               "u_L0": "float", "u_delta_L": "float", "u_delta_t": "float"},
              _m.linear_expansion, ["alpha > 0"], "线膨胀定义"))

# 杨氏模量
register(Tool("youngs_modulus", "杨氏模量（光杠杆法）：E=8mgL0D/(πd²b·dn)。",
              {"m": "float", "g": "float", "L0": "float", "D": "float", "b": "float", "d": "float", "dn": "float",
               "u_m": "float", "u_g": "float", "u_L0": "float", "u_D": "float", "u_b": "float", "u_d": "float", "u_dn": "float"},
              _m.youngs_modulus, ["E > 0"], "杨氏模量定义 + JJF 1059.1 传播"))
