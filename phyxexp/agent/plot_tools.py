"""把绘图也纳入白名单工具链（误差棒绘图是审查过的能力）。"""
from .registry import register, Tool
from .. import viz

register(Tool(
    name="plot_residuals",
    description="生成残差图（散点 + 零线），用于检查残差是否随机、无趋势。",
    schema={"x": "list[float]", "residuals": "list[float]", "path": "str"},
    fn=viz.save_residual_plot,
    cite="残差分析",
))

register(Tool(
    name="plot_fit",
    description="生成拟合图（测量点 + 拟合直线，可选误差棒）。",
    schema={"x": "list[float]", "y": "list[float]", "k": "float", "b": "float", "path": "str"},
    fn=viz.save_fit_plot,
    cite="线性拟合可视化",
))
